"""
generate_blueprints.py — generate image-based "blueprint" recipes from the BPC taxonomy.

A blueprint recipe is `recipe_type: prompt+blueprint`. The reader pastes a workflow
diagram into Cowork and pastes the prompt in the same message:

    blueprint (SHAPE)  +  prompt (BINDINGS)  +  guardrails

The diagram is generated deterministically from taxonomy/business-processes.yaml: an L2
"area" node's L3 "process" children, ordered by sequence_id, ARE the process steps. The
only things the BPC does not encode are gateways, notifications, and input variables —
those live in the hand-authored BLUEPRINTS spec below and are what the human reviews.

Why input bindings matter: an unbound variable is exactly what makes Cowork stop and ask
a clarifying question. The build-catalog step fails the build if a declared input value
never appears in prompt.md, so the diagram and the prompt cannot drift apart.

Outputs per recipe:
    recipes/<area>/<rid>/recipe.yaml
    recipes/<area>/<rid>/prompt.md
    recipes/<area>/<rid>/README.md
    recipes/<area>/<rid>/blueprint.mmd
    recipes/<area>/<rid>/blueprint.png      (with --render)
    recipes/<area>/<rid>/screenshots/01-placeholder.svg

Run:
    python scripts/generate_blueprints.py                 # emit .mmd only
    python scripts/generate_blueprints.py --render        # also render PNG via mermaid-cli
    python scripts/generate_blueprints.py --only blueprint-financial-period-close
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
TAXONOMY = REPO / "taxonomy" / "business-processes.yaml"
TODAY = "2026-08-20"

# Mermaid renders ~15-20 nodes legibly at paste-into-chat scale. Past that the label
# text shrinks below what vision models read reliably.
MAX_NODES = 20

# Vision APIs downscale to fit a bounding box, so an elongated image loses label fidelity
# even at high resolution. Keep the long:short ratio under this.
# NOTE: inferred from how vision models resize, NOT measured against Cowork. Treat the
# warning as a prompt to verify, not as an established fact.
MAX_ASPECT = 2.5

# Single-session budget. A blueprint must complete in ONE Cowork run — the cookbook's
# invariant is one recipe, one paste, one result. Thresholds come from the 29-recipe
# live-tenant validation pass: plans past ~6 steps tend to stall and return a methodology
# doc instead of artifacts, and Cowork reliably lands one workbook plus one email draft.
MAX_STEPS = 6
MAX_GATEWAYS = 2
MAX_OUTPUT_FILES = 2


# --------------------------------------------------------------------------------------
# Taxonomy loading
# --------------------------------------------------------------------------------------

@dataclass
class TaxNode:
    id: str
    title: str
    level: str
    parent: Optional[str] = None
    sequence_id: Optional[str] = None
    learn_url: Optional[str] = None
    description: Optional[str] = None


def load_taxonomy() -> Dict[str, TaxNode]:
    """Parse the flat `nodes:` list. Hand-rolled so the script has no third-party deps."""
    nodes: Dict[str, TaxNode] = {}
    current: Optional[Dict[str, str]] = None

    def flush() -> None:
        if current and "id" in current:
            nodes[current["id"]] = TaxNode(
                id=current["id"],
                title=current.get("title", current["id"]),
                level=current.get("level", ""),
                parent=current.get("parent"),
                sequence_id=current.get("sequence_id"),
                learn_url=current.get("learn_url"),
                description=current.get("description"),
            )

    for raw in TAXONOMY.read_text(encoding="utf-8").splitlines():
        if raw.startswith("  - id:"):
            flush()
            current = {"id": raw.split(":", 1)[1].strip()}
            continue
        if current is None:
            continue
        m = re.match(r"^    ([a-z_]+):\s*(.*)$", raw)
        if m:
            current[m.group(1)] = m.group(2).strip().strip("'\"")
    flush()
    return nodes


def children_of(nodes: Dict[str, TaxNode], parent_id: str) -> List[TaxNode]:
    kids = [n for n in nodes.values() if n.parent == parent_id and n.level == "process"]
    return sorted(kids, key=lambda n: n.sequence_id or n.id)


# --------------------------------------------------------------------------------------
# Blueprint spec
# --------------------------------------------------------------------------------------

@dataclass
class Gateway:
    """A decision the BPC does not encode. Yes continues the spine; No halts and notifies."""
    after: str          # leaf slug of the L3 child this decision follows
    question: str
    no_label: str
    no_action: str


@dataclass
class BlueprintSpec:
    rid: str
    area: str           # recipes/<area>/ folder
    node: str           # L2 taxonomy area node id
    title: str
    summary: str
    business_value: str
    trigger: str
    # (phase label, [L3 leaf slugs]) in the order they run.
    phases: List[Tuple[str, List[str]]]
    # (name, value, description) — every value MUST appear verbatim in the prompt.
    inputs: List[Tuple[str, str, str]]
    gateways: List[Gateway]
    outputs: List[str]
    notify: str
    mutates_data: bool
    ootb: List[str]
    plugin_actions: List[Tuple[str, str]]
    guardrails: List[str]
    honest_degrade: str
    prerequisites: List[str]
    expected: str
    # LR renders wide, TD renders tall. Neither wraps — see the subgraph note in build_mermaid.
    direction: str = "TD"
    difficulty: str = "advanced"
    verified: bool = False
    verified_screenshot: str = ""
    verified_against_cowork_build: str = ""
    tenant_caveat: str = ""
    clarifying_questions_asked: Optional[int] = None
    process_tags: List[str] = field(default_factory=list)


# --------------------------------------------------------------------------------------
# Mermaid emission
# --------------------------------------------------------------------------------------

def mm_escape(s: str) -> str:
    return s.replace('"', "'").replace("\n", " ").strip()


def wrap(s: str, width: int = 24) -> str:
    """Soft-wrap a label with mermaid <br/> so nodes stay narrow and the text stays large."""
    words, lines, cur = mm_escape(s).split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return "<br/>".join(lines)


def build_mermaid(spec: BlueprintSpec, nodes: Dict[str, TaxNode]) -> str:
    area = nodes[spec.node]
    gateways = {g.after: g for g in spec.gateways}

    lines: List[str] = [
        f"%% {spec.title}",
        f"%% Generated from Microsoft Business Process Catalog node: {spec.node}",
    ]
    if area.learn_url:
        lines.append(f"%% Reference: {area.learn_url}")
    lines += [
        "%% Source of truth: taxonomy/business-processes.yaml — regenerate, do not hand-edit.",
        f"flowchart {spec.direction}",
        f'    TRIGGER(["{wrap(spec.trigger)}"]):::trigger',
    ]

    input_label = "<br/>".join(f"{n} = {v}" for n, v, _ in spec.inputs)
    lines.append(f'    INPUTS[/"Input variables<br/>{input_label}"/]:::inputs')
    lines.append("    TRIGGER --> INPUTS")

    step_ids: Dict[str, str] = {}
    ordered: List[Tuple[int, str, str, TaxNode]] = []  # (phase_idx, node_id, slug, taxnode)
    counter = 0
    for pi, (_, slugs) in enumerate(spec.phases):
        for slug in slugs:
            tax = nodes.get(f"{spec.node}/{slug}")
            if tax is None:
                raise SystemExit(f"{spec.rid}: '{slug}' is not a child of {spec.node}")
            nid = f"S{counter}"
            step_ids[slug] = nid
            ordered.append((pi, nid, slug, tax))
            counter += 1
    # Phase subgraphs give the agent explicit ordered stages, the way the numbered rail
    # does on a hand-drawn workflow poster.
    # NOTE: mermaid silently ignores a subgraph's `direction` once any edge crosses the
    # subgraph boundary, which is always true for the spine. So steps inherit the outer
    # direction and a linear process renders long on one axis no matter what. Control the
    # aspect ratio by limiting step count, not by nesting directions.
    for pi, (label, _) in enumerate(spec.phases):
        lines.append(f'    subgraph P{pi}["{pi + 1} · {mm_escape(label)}"]')
        for opi, nid, _, tax in ordered:
            if opi == pi:
                lines.append(f'        {nid}["{wrap(tax.title)}"]')
        lines.append("    end")

    # Linear spine, with gateways spliced in after their anchor step. A gateway makes the
    # NEXT spine edge the "Yes" branch; "No" always terminates at a red halt node.
    prev, prev_label = "INPUTS", ""
    for _, nid, slug, _ in ordered:
        edge = f' -- "{prev_label}" --> ' if prev_label else " --> "
        lines.append(f"    {prev}{edge}{nid}")
        gw = gateways.get(slug)
        if gw:
            gid, hid = f"G_{nid}", f"H_{nid}"
            lines.append(f'    {nid} --> {gid}{{"{wrap(gw.question)}"}}')
            lines.append(f'    {gid} -- "{mm_escape(gw.no_label)}" --> {hid}[["{wrap(gw.no_action)}"]]:::halt')
            prev, prev_label = gid, "Yes"
        else:
            prev, prev_label = nid, ""

    # Only the artifact name goes in the diagram; the full description stays in the prompt.
    out_label = "<br/>".join(mm_escape(o.split(" — ")[0]) for o in spec.outputs)
    edge = f' -- "{prev_label}" --> ' if prev_label else " --> "
    lines.append(f'    {prev}{edge}OUTPUT[/"Outputs<br/>{out_label}"/]:::outputs')
    lines.append(f'    OUTPUT --> NOTIFY(["{wrap(spec.notify)}"]):::notify')

    lines += [
        "    classDef trigger fill:#1e3a8a,stroke:#1e3a8a,color:#ffffff,font-weight:bold",
        "    classDef inputs fill:#eff6ff,stroke:#3b82f6,color:#1e3a8a",
        "    classDef outputs fill:#f0fdf4,stroke:#16a34a,color:#14532d",
        "    classDef notify fill:#7c3aed,stroke:#7c3aed,color:#ffffff,font-weight:bold",
        "    classDef halt fill:#fef2f2,stroke:#dc2626,color:#7f1d1d",
    ]
    return "\n".join(lines) + "\n"


def png_size(path: Path) -> Optional[Tuple[int, int]]:
    """Read width/height from the PNG IHDR chunk so the script stays dependency-free."""
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def render_png(mmd_path: Path, png_path: Path) -> bool:
    """Render via mermaid-cli. Kept as an on-demand npx call so the repo carries no puppeteer dep."""
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx:
        print("  WARN: npx not found — skipping PNG render")
        return False
    cmd = [
        npx, "-y", "@mermaid-js/mermaid-cli",
        "-i", str(mmd_path), "-o", str(png_path),
        "-b", "white", "-s", "2", "-w", "1400",
    ]
    print(f"  rendering {png_path.name} …")
    proc = subprocess.run(cmd, capture_output=True, text=True, shell=False)
    if proc.returncode != 0:
        print(f"  WARN: mermaid-cli failed:\n{proc.stderr[-1500:]}")
        return False
    size = png_size(png_path)
    if size:
        w, h = size
        aspect = max(w, h) / max(1, min(w, h))
        print(f"  rendered {w}x{h} (aspect {aspect:.1f}:1)")
        if aspect > MAX_ASPECT:
            print(
                f"  WARN: aspect {aspect:.1f}:1 exceeds {MAX_ASPECT}:1 — Cowork downscales to a"
                " bounding box, so labels lose fidelity. Reduce steps or split into two"
                " blueprints; switching direction does not help (mermaid will not wrap a spine)."
            )
    return True


# --------------------------------------------------------------------------------------
# Recipe emission
# --------------------------------------------------------------------------------------

def build_prompt(spec: BlueprintSpec) -> str:
    bindings = "\n".join(f"- {n}: {v}" for n, v, _ in spec.inputs)
    guardrails = "\n".join(f"- {g}" for g in spec.guardrails)
    outputs = "\n".join(f"- {o}" for o in spec.outputs)
    return (
        "The attached image is a workflow blueprint. Build and run it as an automated task "
        "using the Dynamics 365 ERP plugin. Follow the diagram exactly: execute each phase in "
        "the order shown, honour every decision diamond, and stop at a red halt node if its "
        "condition is met.\n\n"
        "Do not ask me clarifying questions — every input is bound below.\n\n"
        f"## Input variables\n\n{bindings}\n\n"
        f"## Trigger\n\n{spec.trigger}\n\n"
        f"## Outputs\n\n{outputs}\n\n"
        f"## Notification\n\n{spec.notify}\n\n"
        f"## Guardrails\n\n{guardrails}\n\n"
        f"{spec.honest_degrade}\n"
    )


def build_readme(spec: BlueprintSpec, nodes: Dict[str, TaxNode]) -> str:
    area = nodes[spec.node]
    draft_warning = (
        ""
        if spec.verified
        else (
            "\n> ⚠ **Draft recipe — not yet verified.** The blueprint below is generated from the "
            "Business Process Catalog but has not been run against a live Cowork tenant. Validate "
            "before relying on it.\n"
        )
    )
    sandbox_warning = (
        (
            "\n> ⚠ **This recipe modifies Dynamics 365 data.** Run it in a sandbox tenant first and "
            "review every proposed write before approving it.\n"
        )
        if spec.mutates_data
        else ""
    )
    caveat = f"\n> ℹ **Tenant data caveat.** {spec.tenant_caveat}\n" if spec.tenant_caveat else ""
    screenshot = (
        "![Cowork output for {t}](screenshots/01-cowork-output.png \"Captured against a live Cowork tenant.\")"
        if spec.verified and spec.verified_screenshot
        else "![Placeholder screenshot for {t}](screenshots/01-placeholder.svg \"Placeholder — replace with a real screenshot.\")"
    ).format(t=spec.title)

    phases_md = "\n".join(
        f"{i + 1}. **{label}** — "
        + ", ".join(nodes[f"{spec.node}/{s}"].title for s in slugs)
        for i, (label, slugs) in enumerate(spec.phases)
    )
    inputs_md = "\n".join(f"| `{n}` | {v} | {d} |" for n, v, d in spec.inputs)
    qbar = (
        f"\nCowork asked **{spec.clarifying_questions_asked}** clarifying questions during "
        f"verification.\n"
        if spec.clarifying_questions_asked is not None
        else ""
    )

    return (
        f"# {spec.title}\n\n"
        f"{spec.summary}\n"
        f"{draft_warning}{caveat}{sandbox_warning}\n"
        f"## Business value\n\n{spec.business_value}\n\n"
        "## How to run it\n\n"
        "1. Open a new Cowork task and turn the **Dynamics 365 ERP** plugin toggle on.\n"
        "2. Paste the blueprint image below into the message.\n"
        "3. Paste the prompt from `prompt.md` into the **same** message.\n"
        "4. Send. Cowork reads the diagram for structure and the prompt for values.\n"
        f"{qbar}\n"
        "## Blueprint\n\n"
        f"![Workflow blueprint for {spec.title}](blueprint.png "
        f"\"Generated from the Business Process Catalog node {spec.node}.\")\n\n"
        f"Mermaid source: [`blueprint.mmd`](blueprint.mmd)\n\n"
        "## Process phases\n\n"
        f"{phases_md}\n\n"
        f"Derived from the Microsoft Business Process Catalog area **{area.title}** "
        f"(`{spec.node}`)"
        + (f" — [Microsoft Learn]({area.learn_url})" if area.learn_url else "")
        + ".\n\n"
        "## Input bindings\n\n"
        "| Variable | Value | Meaning |\n| --- | --- | --- |\n"
        f"{inputs_md}\n\n"
        "## Guardrails\n\n" + "\n".join(f"- {g}" for g in spec.guardrails) + "\n\n"
        f"## Expected output\n\n{spec.expected}\n\n"
        f"{screenshot}\n\n"
        "## Prerequisites\n\n" + "\n".join(f"- {p}" for p in spec.prerequisites) + "\n\n"
        "## Skills used\n\n"
        f"OOTB: {', '.join(spec.ootb) if spec.ootb else '—'}\n\n"
        f"Plugin actions: {', '.join(f'{p}/{a}' for p, a in spec.plugin_actions)}\n\n"
        "## License\n\nCC-BY-4.0 — see repo `LICENSE`.\n"
    )


def yaml_str(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def build_recipe_yaml(spec: BlueprintSpec, nodes: Dict[str, TaxNode]) -> str:
    tags = spec.process_tags or [spec.node]
    status = (
        f"status: verified\n"
        f'last_verified_on: "{TODAY}"\n'
        f'verified_against_cowork_build: "{spec.verified_against_cowork_build or "live-tenant-" + TODAY}"\n'
        if spec.verified
        else "status: draft\n"
    )
    inputs_yaml = "".join(
        f'    - name: "{yaml_str(n)}"\n      value: "{yaml_str(v)}"\n      description: "{yaml_str(d)}"\n'
        for n, v, d in spec.inputs
    )
    cqa = (
        f"  clarifying_questions_asked: {spec.clarifying_questions_asked}\n"
        if spec.clarifying_questions_asked is not None
        else ""
    )
    return (
        f"id: {spec.rid}\n"
        f"title: {spec.title}\n"
        f"summary: >-\n  {spec.summary}\n"
        f"business_value: >-\n  {spec.business_value}\n"
        f"plugin: dynamics-365-erp\n"
        "process_tags:\n" + "".join(f"  - {t}\n" for t in tags) +
        "recipe_type: prompt+blueprint\n"
        f"difficulty: {spec.difficulty}\n"
        f"mutates_data: {str(spec.mutates_data).lower()}\n"
        'min_plugin_version: "1.0.0"\n'
        "generated_by: copilot\n"
        "reviewed_by: seangalliher\n"
        + status +
        "deprecated: false\n"
        "license: CC-BY-4.0\n"
        "uses_skills:\n"
        "  ootb:\n" + "".join(f"    - {s}\n" for s in spec.ootb) +
        "  plugin:\n" + "".join(f"    - plugin: {p}\n      action: {a}\n" for p, a in spec.plugin_actions) +
        "  custom: []\n"
        "blueprint:\n"
        "  mermaid: blueprint.mmd\n"
        "  image: blueprint.png\n"
        f"  source_node: {spec.node}\n"
        + cqa +
        "  inputs:\n" + inputs_yaml +
        "prerequisites:\n" + "".join(f"  - {p}\n" for p in spec.prerequisites) +
        "youtube: []\n"
        "authors:\n  - github: seangalliher\n    name: Sean Galliher\n"
        f'created: "{TODAY}"\n'
        'version: "1.0.0"\n'
    )


def placeholder_svg(title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img" '
        f'aria-label="Placeholder screenshot for {title}">\n'
        f'  <rect width="800" height="450" fill="#f3f4f6"/>\n'
        f'  <rect x="20" y="20" width="760" height="40" fill="#1f2937"/>\n'
        f'  <text x="40" y="48" fill="#f9fafb" font-family="system-ui, sans-serif" font-size="18" font-weight="600">{title}</text>\n'
        f'  <text x="400" y="240" text-anchor="middle" fill="#6b7280" font-family="system-ui, sans-serif" font-size="16">'
        f'Placeholder — captured screenshot will replace this image.</text>\n'
        f'</svg>\n'
    )


def assert_single_session(spec: BlueprintSpec, declared: set) -> None:
    """Reject a blueprint that cannot plausibly finish in one Cowork run."""
    problems: List[str] = []
    if len(declared) > MAX_STEPS:
        problems.append(f"{len(declared)} steps (max {MAX_STEPS})")
    if len(spec.gateways) > MAX_GATEWAYS:
        problems.append(f"{len(spec.gateways)} gateways (max {MAX_GATEWAYS})")
    if len(spec.outputs) > MAX_OUTPUT_FILES:
        problems.append(f"{len(spec.outputs)} output files (max {MAX_OUTPUT_FILES})")
    if spec.mutates_data:
        problems.append("mutates_data=True (writes hit approval gating and span sessions)")
    if problems:
        raise SystemExit(
            f"{spec.rid}: exceeds the single-session budget — "
            + "; ".join(problems)
            + ". Narrow the scope to one paste, one run, one result."
        )


def write_blueprint(spec: BlueprintSpec, nodes: Dict[str, TaxNode], render: bool) -> None:
    if spec.node not in nodes:
        raise SystemExit(f"{spec.rid}: taxonomy node '{spec.node}' not found")

    declared = {s for _, slugs in spec.phases for s in slugs}
    actual = {n.id.rsplit("/", 1)[-1] for n in children_of(nodes, spec.node)}
    missing = actual - declared
    if missing:
        print(f"  NOTE: {spec.rid} omits BPC children (intentional if out of scope): {sorted(missing)}")
    unknown = declared - actual
    if unknown:
        raise SystemExit(f"{spec.rid}: phases reference non-children: {sorted(unknown)}")

    assert_single_session(spec, declared)

    node_count = len(declared) + len(spec.gateways) + 4
    if node_count > MAX_NODES:
        print(f"  WARN: {spec.rid} has ~{node_count} nodes (> {MAX_NODES}); labels may render too small to read")

    prompt = build_prompt(spec)
    for name, value, _ in spec.inputs:
        if value not in prompt:
            raise SystemExit(f"{spec.rid}: input '{name}' value '{value}' not bound in prompt")

    folder = REPO / "recipes" / spec.area / spec.rid
    (folder / "screenshots").mkdir(parents=True, exist_ok=True)
    for stale in ("recipe.yaml", "prompt.md", "README.md", "blueprint.mmd"):
        p = folder / stale
        if p.exists():
            p.unlink()

    (folder / "blueprint.mmd").write_text(build_mermaid(spec, nodes), encoding="utf-8")
    (folder / "recipe.yaml").write_text(build_recipe_yaml(spec, nodes), encoding="utf-8")
    (folder / "prompt.md").write_text(prompt, encoding="utf-8")
    (folder / "README.md").write_text(build_readme(spec, nodes), encoding="utf-8")

    placeholder = folder / "screenshots" / "01-placeholder.svg"
    if not (spec.verified and spec.verified_screenshot):
        placeholder.write_text(placeholder_svg(spec.title), encoding="utf-8")
    else:
        placeholder.unlink(missing_ok=True)  # a verified recipe must not ship a placeholder
        src = REPO / "scripts" / "seed_assets" / spec.rid / spec.verified_screenshot
        dst = folder / "screenshots" / "01-cowork-output.png"
        if src.exists():
            shutil.copyfile(src, dst)
        elif not dst.exists():
            print(f"  WARN: verified screenshot {src} not found")

    png = folder / "blueprint.png"
    if render:
        render_png(folder / "blueprint.mmd", png)
    if not png.exists():
        print(f"  WARN: {spec.rid}/blueprint.png missing — run with --render before building the catalog")

    print(f"wrote {spec.area}/{spec.rid}")


# --------------------------------------------------------------------------------------
# The specs. One L2 area each. Keep this list small and hand-verified.
# --------------------------------------------------------------------------------------

BLUEPRINTS: List[BlueprintSpec] = [
    BlueprintSpec(
        rid="blueprint-period-close-readiness",
        area="record-to-report",
        node="record-to-report/close-financial-periods",
        title="Period Close Readiness Blueprint",
        summary=(
            "Paste this period-close workflow blueprint into Cowork and it assesses whether the "
            "period is ready to close — unposted work, subledger-to-GL differences, and FX exposure."
        ),
        business_value=(
            "Answers 'can we close?' on demand instead of on business day 5, so the controller "
            "chases the two subledgers that are actually blocking rather than polling every owner."
        ),
        trigger="Trigger: monthly, business day 3",
        phases=[
            (
                "Assess the period",
                [
                    "finalize-and-post-transactions",
                    "reconcile-ledger-and-subledger",
                    "revalue-currency",
                ],
            ),
            ("Report readiness", ["close-periods"]),
        ],
        inputs=[
            ("periodName", "2017-12", "Fiscal period to assess. USMF demo data is mostly FY2017."),
            ("legalEntity", "USMF", "Legal entity to scope every query to."),
            ("materialityThreshold", "10000", "Differences below this are listed but not flagged as blocking."),
        ],
        gateways=[
            Gateway(
                after="finalize-and-post-transactions",
                question="Period has posted activity?",
                no_label="No activity",
                no_action="Report that the period is empty and stop",
            ),
        ],
        outputs=[
            "close-readiness.xlsx — Summary, Unposted, Reconciliation, and FX sheets",
        ],
        notify="Email the readiness summary to me",
        mutates_data=False,
        ootb=["Excel", "Email"],
        plugin_actions=[
            ("dynamics-365-erp", "data_find_entity_type"),
            ("dynamics-365-erp", "data_find_entities_sql"),
        ],
        guardrails=[
            "Read only. Do not post journals, do not lock or close any period, do not run consolidation.",
            "Produce the workbook in this run — do not return a plan or a methodology document instead.",
            "Report readiness and differences; leave every close decision to me.",
        ],
        honest_degrade=(
            "If an entity is not exposed to the plugin or the period has no posted activity, report "
            "exactly which check you could not run and why, list what you did complete, and stop. "
            "Do not fabricate balances."
        ),
        prerequisites=[
            "Dynamics 365 F&SCM access with the General ledger role",
            "Cowork D365 ERP plugin toggled on in the session",
        ],
        expected=(
            "One workbook in `Documents/Cowork/output/` plus an email draft. Where a check is "
            "blocked, Cowork returns a constraint table naming the entity it needed — that table is "
            "itself the deliverable for the admin who has to expose it."
        ),
        process_tags=[
            "record-to-report/close-financial-periods",
            "record-to-report/record-financial-transactions",
        ],
    ),
    BlueprintSpec(
        rid="blueprint-credit-and-collections-review",
        area="order-to-cash",
        node="order-to-cash/manage-credit-and-collections",
        title="Credit & Collections Review Blueprint",
        summary=(
            "Paste this credit-and-collections workflow blueprint into Cowork and it ranks customers "
            "by credit exposure and overdue balance, then proposes a collections worklist."
        ),
        business_value=(
            "Points the collections team at the handful of accounts carrying real exposure instead "
            "of working the aging report top to bottom, which shortens days sales outstanding."
        ),
        trigger="Trigger: weekly, Monday morning",
        phases=[
            (
                "Assess exposure",
                [
                    "assess-customer-credit-risk",
                    "manage-customer-holds",
                    "monitor-customer-credit",
                ],
            ),
            ("Prioritize collections", ["manage-customer-collections"]),
        ],
        inputs=[
            ("legalEntity", "USMF", "Legal entity to scope every query to."),
            ("asOfDate", "2023-11-30", "Aging as-of date. USMF customer AR runs through 2023-11-29."),
            ("riskThreshold", "80", "Percent of credit limit consumed that flags a customer as at-risk."),
        ],
        gateways=[
            Gateway(
                after="assess-customer-credit-risk",
                question="Open AR balances found?",
                no_label="No open AR",
                no_action="Report that there is no open receivable and stop",
            ),
        ],
        outputs=[
            "credit-collections-review.xlsx — At-risk, On-hold, Aging, and Worklist sheets",
        ],
        notify="Email the collections worklist to me",
        mutates_data=False,
        ootb=["Excel", "Email"],
        plugin_actions=[
            ("dynamics-365-erp", "data_find_entity_type"),
            ("dynamics-365-erp", "data_find_entities_sql"),
        ],
        guardrails=[
            "Read only. Do not place or release credit holds, do not post interest, do not contact customers.",
            "Produce the workbook in this run — do not return a plan or a methodology document instead.",
            "Rank and recommend; leave every collections decision to me.",
        ],
        honest_degrade=(
            "If credit limits or aging buckets are not available from the plugin, report exactly which "
            "check you could not run and why, list what you did complete, and stop. Do not estimate "
            "balances you could not read."
        ),
        prerequisites=[
            "Dynamics 365 F&SCM access with the Accounts receivable role",
            "Cowork D365 ERP plugin toggled on in the session",
        ],
        expected=(
            "One workbook in `Documents/Cowork/output/` with At-risk, On-hold, Aging, and Worklist "
            "sheets, plus an emailed summary. Cowork also turns the trigger node into a real "
            "recurring scheduled task, which it creates paused for you to enable."
        ),
        verified=True,
        verified_screenshot="01-cowork-output.png",
        verified_against_cowork_build="m365.cloud.microsoft 2026-08-20",
        clarifying_questions_asked=0,
        tenant_caveat=(
            "Validated end-to-end against a live Cowork tenant on 2026-08-20 with USMF demo data. "
            "Cowork read the blueprint image and ran all four phases with ZERO clarifying questions "
            "— every input was bound by the prompt. The 'Open AR balances found?' gateway passed, so "
            "no halt node was reached, and it produced 'credit-collections-review.xlsx' with At-risk, "
            "On-hold, Aging, and Worklist sheets. Findings: 27 customers carry 3,623,949.93 in open "
            "receivables, all of it past due, with 3,287,971.43 sitting in the 120+ day bucket; 9 "
            "customers scored at or above the riskThreshold of 80, the worst being US-008 Sparrow "
            "Retail at 920% credit utilisation with an item 2,535 days past due; 3 customers already "
            "on hold had no open balance as of the as-of date. Cowork surfaced two data caveats "
            "unprompted: an item counts as fully open unless D365 marked it closed, so a partially "
            "settled invoice shows at full value; and balances are in accounting currency while "
            "credit limits are held per-customer, which only affects DE-001 (no open items). The "
            "read-only guardrails held — no holds placed or released, no interest posted, no customer "
            "contacted. Notably, Cowork converted the diagram's trigger node into a genuine recurring "
            "scheduled task (weekly, Monday 08:00), created in a paused state, and required explicit "
            "approval before sending the email and before creating that schedule."
        ),
        process_tags=["order-to-cash/manage-credit-and-collections"],
    ),
    BlueprintSpec(
        rid="blueprint-procurement-spend-review",
        area="source-to-pay",
        node="source-to-pay/analyze-procurement-and-sourcing",
        title="Procurement Spend & Supplier Risk Blueprint",
        summary=(
            "Paste this procurement-analysis workflow blueprint into Cowork and it profiles spend by "
            "vendor, flags concentration risk, and surfaces payable exposure."
        ),
        business_value=(
            "Shows where spend is concentrated in a handful of suppliers before that concentration "
            "becomes a continuity problem, and does it without waiting on a BI request."
        ),
        trigger="Trigger: quarterly, first business day",
        phases=[
            (
                "Measure spend",
                ["measure-and-analyze-procurement-spend", "manage-supplier-performance"],
            ),
            ("Assess exposure", ["analyze-account-payable", "manage-procurement-risks"]),
        ],
        inputs=[
            ("legalEntity", "USMF", "Legal entity to scope every query to."),
            ("fiscalYear", "2017", "Year to profile. USMF posted activity is mostly FY2017."),
            ("concentrationThreshold", "20", "Percent of total spend with one vendor that flags concentration risk."),
        ],
        gateways=[
            Gateway(
                after="measure-and-analyze-procurement-spend",
                question="Purchase activity found?",
                no_label="No spend data",
                no_action="Report that the entity has no purchase spend and stop",
            ),
        ],
        outputs=[
            "procurement-spend-review.xlsx — Spend, Concentration, Payables, and Risk sheets",
        ],
        notify="Email the spend summary to me",
        mutates_data=False,
        ootb=["Excel", "Email"],
        plugin_actions=[
            ("dynamics-365-erp", "data_find_entity_type"),
            ("dynamics-365-erp", "data_find_entities_sql"),
        ],
        guardrails=[
            "Read only. Do not create or modify vendors, purchase orders, or invoices.",
            "Produce the workbook in this run — do not return a plan or a methodology document instead.",
            "Report concentration and exposure; leave every sourcing decision to me.",
        ],
        honest_degrade=(
            "USMF may have no vendor invoice records at all. If purchase or payable data is missing, "
            "say so explicitly, name the entity you queried, list what you could read from the vendor "
            "master, and stop. Do not infer spend from vendor records alone."
        ),
        prerequisites=[
            "Dynamics 365 F&SCM access with the Procurement and Accounts payable roles",
            "Cowork D365 ERP plugin toggled on in the session",
        ],
        expected=(
            "One workbook plus an email draft. This is the blueprint most likely to hit the halt "
            "node — USMF carries zero VendorInvoiceHeader records, so a clean 'no spend data' report "
            "is the correct outcome and is itself the deliverable."
        ),
        process_tags=["source-to-pay/analyze-procurement-and-sourcing"],
    ),
    BlueprintSpec(
        rid="blueprint-position-and-onboarding-readiness",
        area="hire-to-retire",
        node="hire-to-retire/recruit-and-onboard-talent",
        title="Open Position & Onboarding Readiness Blueprint",
        summary=(
            "Paste this recruit-and-onboard workflow blueprint into Cowork and it reports which "
            "positions are vacant, how long they have been open, and which new hires lack onboarding "
            "records."
        ),
        business_value=(
            "Gives HR and the hiring managers one weekly view of where the pipeline is stalled, so "
            "long-vacant roles get escalated instead of quietly ageing."
        ),
        trigger="Trigger: weekly, Monday morning",
        phases=[
            ("Assess demand", ["budget-workforce", "list-open-positions"]),
            ("Assess pipeline", ["hire-for-open-positions", "onboard-new-employees"]),
        ],
        inputs=[
            ("legalEntity", "USMF", "Legal entity to scope every query to."),
            ("asOfDate", "2017-12-31", "Reporting date. USMF HR data centres on FY2017."),
            ("vacancyAgeDays", "90", "Days a position may stay open before it is flagged as stale."),
        ],
        gateways=[
            Gateway(
                after="list-open-positions",
                question="Open positions found?",
                no_label="All filled",
                no_action="Report that every position is filled and stop",
            ),
        ],
        outputs=[
            "position-readiness.xlsx — Vacancies, Stale, Pipeline, and Onboarding sheets",
        ],
        notify="Email the staffing summary to me",
        mutates_data=False,
        ootb=["Excel", "Email"],
        plugin_actions=[
            ("dynamics-365-erp", "data_find_entity_type"),
            ("dynamics-365-erp", "data_find_entities_sql"),
        ],
        guardrails=[
            "Read only. Do not create or modify positions, workers, or onboarding checklists.",
            "Produce the workbook in this run — do not return a plan or a methodology document instead.",
            "Do not include compensation figures or any other sensitive personal data in the output.",
        ],
        honest_degrade=(
            "If position or onboarding entities are not exposed to the plugin, report exactly which "
            "check you could not run and why, list what you did complete, and stop. Do not infer "
            "vacancies from the worker roster alone."
        ),
        prerequisites=[
            "Dynamics 365 F&SCM access with the Human resources role",
            "Cowork D365 ERP plugin toggled on in the session",
        ],
        expected=(
            "One workbook plus an email draft listing vacancies ranked by days open. USMF has 97 "
            "active workers; if the position hierarchy is sparse, expect a partial report naming "
            "what was readable."
        ),
        process_tags=["hire-to-retire/recruit-and-onboard-talent"],
    ),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--render", action="store_true", help="render blueprint.png via mermaid-cli")
    ap.add_argument("--only", help="generate a single rid")
    args = ap.parse_args()

    nodes = load_taxonomy()
    print(f"taxonomy: {len(nodes)} nodes")

    specs = [s for s in BLUEPRINTS if not args.only or s.rid == args.only]
    if not specs:
        print(f"no blueprint matched --only {args.only}")
        return 1
    for spec in specs:
        write_blueprint(spec, nodes, args.render)
    return 0


if __name__ == "__main__":
    sys.exit(main())
