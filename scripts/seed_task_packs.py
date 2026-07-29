"""
seed_task_packs.py — turn the Microsoft Copilot Cowork Task Packs into Cookbook recipes.

Source: the publicly published "Cowork Task Pack" decks for Sales, Marketing, and
All Functions. Each deck slide carries a task name, tier, plugin, goal, output,
prompt, and execution workflow — which maps almost 1:1 onto a recipe. The prompts
are reproduced as published; only the surrounding recipe scaffolding is ours.

Input:  a JSON dump of the decks (see EXTRACT_NOTE below).
Output: recipes/<area>/<rid>/{recipe.yaml,prompt.md,README.md,screenshots/…}

Every recipe ships status: draft — nobody has run these against our tenant.

Run: python scripts/seed_task_packs.py [path-to-taskpack_tasks.json]
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parents[1]
TODAY = "2026-07-28"

EXTRACT_NOTE = (
    "Produced by walking every <a:p> paragraph of each slide in document order and "
    "splitting on the on-slide labels (Goal:/Output:/Prompt/Execution workflow)."
)

PACK_TITLES = {
    "Sales": "Microsoft Copilot Cowork Task Pack for Sales",
    "Marketing": "Microsoft Copilot Cowork Task Pack for Marketing",
    "All_Functions": "Microsoft Copilot Cowork Task Pack for All Functions",
}

TIER_DIFFICULTY = {
    "Lightweight tasks": "beginner",
    "Everyday workflows": "intermediate",
    "Hard problems": "advanced",
}

# (pack, task number) -> (recipe id, process tag, plugin)
# The process tag is a deliberate choice per task, not derived at runtime. Tasks that
# are genuinely a Dynamics 365 business process stay in their BPC domain; the rest go
# to work-management.
MAPPING: Dict[Tuple[str, int], Tuple[str, str, str]] = {
    # ---------------- Sales ----------------
    ("Sales", 1): ("prep-for-next-customer-meeting", "prospect-to-quote/manage-customer-relationships/maintain-contacts-and-accounts", "dynamics-365-sales"),
    ("Sales", 2): ("catch-up-on-follow-ups-i-owe", "prospect-to-quote/manage-customer-relationships/maintain-contacts-and-accounts", "dynamics-365-sales"),
    ("Sales", 3): ("catch-up-on-what-moved-on-my-deals", "prospect-to-quote/pursue-opportunities/manage-opportunity-process", "dynamics-365-sales"),
    ("Sales", 4): ("pricing-screenshot-to-customer-presentation", "prospect-to-quote/estimate-and-quote-sales/define-sales-quotations", "none"),
    ("Sales", 5): ("weekly-external-customer-email-review", "prospect-to-quote/estimate-and-quote-sales/nurture-trust-relationship-regularly-with-customer", "none"),
    ("Sales", 6): ("find-my-best-expansion-accounts", "prospect-to-quote/estimate-and-quote-sales/conduct-upsell-cross-sell-or-repeat-sale-prompt", "dynamics-365-sales"),
    ("Sales", 7): ("prep-for-my-1-1-with-a-seller", "prospect-to-quote/analyze-sales/provide-insights-into-sales-strategies-and-performance", "dynamics-365-sales"),
    ("Sales", 8): ("stand-up-an-account-plan-board", "prospect-to-quote/manage-customer-relationships/maintain-contacts-and-accounts", "monday-com"),
    ("Sales", 9): ("map-an-account-strategy-on-a-miro-board", "prospect-to-quote/define-sales-strategy-and-policies/define-sales-process", "miro"),
    ("Sales", 10): ("prepare-for-a-customer-meeting-deep", "prospect-to-quote/manage-customer-relationships/maintain-contacts-and-accounts", "dynamics-365-sales"),
    ("Sales", 11): ("product-launch-customer-pitch", "prospect-to-quote/pursue-opportunities/nurture-opportunities-and-finalize-the-sale", "none"),
    ("Sales", 12): ("commit-risk-review", "prospect-to-quote/analyze-sales/analyze-sales-data", "dynamics-365-sales"),
    ("Sales", 13): ("upsell-identification", "prospect-to-quote/estimate-and-quote-sales/conduct-upsell-cross-sell-or-repeat-sale-prompt", "dynamics-365-sales"),
    ("Sales", 14): ("find-the-deals-that-need-my-help", "prospect-to-quote/pursue-opportunities/manage-opportunity-process", "dynamics-365-sales"),
    ("Sales", 15): ("new-customer-onboarding-automation", "prospect-to-quote/estimate-and-quote-sales/conduct-post-sale-follow-up", "none"),
    ("Sales", 16): ("customer-adoption-materials", "prospect-to-quote/estimate-and-quote-sales/conduct-post-sale-follow-up", "none"),
    ("Sales", 17): ("build-an-account-research-brief", "prospect-to-quote/manage-customer-relationships/maintain-contacts-and-accounts", "dynamics-365-sales"),
    ("Sales", 18): ("pipeline-risk-and-next-best-actions-review", "prospect-to-quote/analyze-sales/analyze-sales-data", "dynamics-365-sales"),
    ("Sales", 19): ("roi-and-value-selling-artifact", "prospect-to-quote/pursue-opportunities/nurture-opportunities-and-finalize-the-sale", "none"),
    # ---------------- Marketing ----------------
    ("Marketing", 1): ("weekly-marketing-standup-prep", "concept-to-market/manage-marketing-campaigns/oversee-active-campaigns", "fabric-iq"),
    ("Marketing", 2): ("research-and-insights-alignment-recap", "concept-to-market/develop-marketing-strategy/perform-market-research", "none"),
    ("Marketing", 3): ("pull-whats-relevant-for-another-team", "work-management/create-and-repurpose-content/tailor-content-for-an-audience", "none"),
    ("Marketing", 4): ("turn-source-content-into-campaign-storytelling", "concept-to-market/prepare-marketing-campaigns/create-marketing-material", "prezi"),
    ("Marketing", 5): ("build-a-customer-facing-pitch-deck-on-brand", "concept-to-market/prepare-marketing-campaigns/create-marketing-material", "none"),
    ("Marketing", 6): ("campaign-kick-off", "concept-to-market/prepare-marketing-campaigns/identify-campaign-audiences", "fabric-iq"),
    ("Marketing", 7): ("partner-and-channel-activation-kit", "concept-to-market/prepare-marketing-campaigns/create-marketing-material", "none"),
    ("Marketing", 8): ("stand-up-a-campaign-workspace", "concept-to-market/manage-marketing-campaigns/oversee-active-campaigns", "monday-com"),
    ("Marketing", 9): ("develop-messaging-and-positioning", "concept-to-market/prepare-marketing-campaigns/develop-campaign-themes-and-messages", "monday-com"),
    ("Marketing", 10): ("map-a-customer-journey-for-a-campaign", "concept-to-market/prepare-marketing-campaigns/identify-campaign-audiences", "miro"),
    ("Marketing", 11): ("event-marketing-command-center", "concept-to-market/prepare-marketing-campaigns/plan-events", "fabric-iq"),
    ("Marketing", 12): ("analyst-briefing-prep-and-rehearsal-routing", "concept-to-market/develop-marketing-strategy/define-value-proposition", "none"),
    ("Marketing", 13): ("launch-activation-kit-and-owner-routing", "concept-to-market/prepare-marketing-campaigns/create-marketing-material", "fabric-iq"),
    ("Marketing", 14): ("messaging-drift-audit-and-remediation", "concept-to-market/prepare-marketing-campaigns/develop-campaign-themes-and-messages", "none"),
    ("Marketing", 15): ("competitive-move-response-kit", "concept-to-market/analyze-marketing-operations/conduct-competitive-analysis", "fabric-iq"),
    ("Marketing", 16): ("scheduled-customer-signal-activation", "concept-to-market/analyze-marketing-operations/analyze-marketing-trends", "fabric-iq"),
    ("Marketing", 17): ("post-launch-readout-and-optimization", "concept-to-market/analyze-marketing-operations/evaluate-campaign-performance", "fabric-iq"),
    ("Marketing", 18): ("campaign-narrative-architecture-board", "concept-to-market/prepare-marketing-campaigns/develop-campaign-themes-and-messages", "miro"),
    # ---------------- All Functions ----------------
    ("All_Functions", 1): ("rebalance-your-week-and-protect-focus-time", "work-management/plan-and-prioritize-work/manage-time-and-focus", "none"),
    ("All_Functions", 2): ("wrap-up-projects-and-organize-related-work", "work-management/organize-information/archive-completed-work", "none"),
    ("All_Functions", 3): ("turn-a-document-into-a-visual-framework", "work-management/create-and-repurpose-content/visualize-concepts-and-frameworks", "miro"),
    ("All_Functions", 4): ("map-a-workflow-from-a-process-description", "work-management/create-and-repurpose-content/diagram-processes-and-workflows", "miro"),
    ("All_Functions", 5): ("turn-source-content-into-a-deck", "work-management/create-and-repurpose-content/build-presentations-from-source-material", "prezi"),
    ("All_Functions", 6): ("catch-up-on-messages-and-send-replies", "work-management/manage-communications/triage-and-respond-to-messages", "none"),
    ("All_Functions", 7): ("generate-and-send-your-weekly-status", "work-management/manage-communications/produce-recurring-status-updates", "fabric-iq"),
    ("All_Functions", 8): ("turn-inbox-noise-into-an-intelligence-brief", "work-management/research-and-synthesize/curate-information-briefs", "none"),
    ("All_Functions", 9): ("build-a-project-board-from-work-context", "work-management/coordinate-team-work/set-up-project-boards", "monday-com"),
    ("All_Functions", 10): ("build-a-visual-project-plan-from-work-context", "work-management/coordinate-team-work/build-project-plans", "miro"),
    ("All_Functions", 11): ("pull-whats-relevant-for-your-team", "work-management/create-and-repurpose-content/tailor-content-for-an-audience", "none"),
    ("All_Functions", 12): ("prepare-a-complete-out-of-office-handoff", "work-management/coordinate-team-work/hand-off-work-during-absence", "none"),
    ("All_Functions", 13): ("analyze-and-optimize-your-onedrive-at-scale", "work-management/organize-information/catalog-and-clean-up-file-stores", "none"),
    ("All_Functions", 14): ("build-your-executive-command-center", "work-management/research-and-synthesize/build-personal-insight-dashboards", "fabric-iq"),
    ("All_Functions", 15): ("run-deep-research-with-a-citation-map", "work-management/research-and-synthesize/conduct-deep-research", "fabric-iq"),
    ("All_Functions", 16): ("audit-and-surface-against-a-standard", "work-management/review-against-standards/audit-content-against-a-standard", "none"),
    ("All_Functions", 17): ("onboard-a-new-hire-with-a-30-60-90-plan", "hire-to-retire/recruit-and-onboard-talent/onboard-new-employees", "none"),
    ("All_Functions", 18): ("automate-recurring-project-reporting", "work-management/coordinate-team-work/automate-recurring-reporting", "monday-com"),
    ("All_Functions", 19): ("find-patterns-across-your-meetings", "work-management/research-and-synthesize/analyze-collaboration-patterns", "none"),
    ("All_Functions", 20): ("prepare-a-leadership-update", "work-management/manage-communications/prepare-leadership-updates", "none"),
}

# OOTB skill detection — matched against the prompt + output text.
OOTB_PATTERNS = [
    ("Word", r"\bword\b|\.docx\b|written brief"),
    ("Excel", r"\bexcel\b|\.xlsx\b|spreadsheet"),
    ("PowerPoint", r"\bpowerpoint\b|\bdeck\b|\bslide|presentation|\.pptx\b"),
    ("PDF", r"\bpdf\b"),
    ("Email", r"\bemail|\binbox\b|outlook|draft repl|\bsend\b"),
    ("Calendar Management", r"\bcalendar\b|\binvite\b|out-of-office|reschedul"),
    ("Scheduling", r"\bschedule\b|\brecurring\b|every (monday|friday|week)"),
    ("Meetings", r"\bmeeting"),
    ("Communications", r"\bteams\b|stakeholder|announce|update to"),
    ("Deep Research", r"deep research|research across|citation"),
    ("Enterprise Search", r"across (my|our) (files|documents|org)|sharepoint"),
    ("Adaptive Cards", r"adaptive card"),
]

VALID_OOTB = {
    "Word", "Excel", "PowerPoint", "PDF", "Email", "Scheduling", "Calendar Management",
    "Meetings", "Daily Briefing", "Enterprise Search", "Deep Research", "Communications",
    "Adaptive Cards",
}

PLUGIN_PREREQ = {
    "dynamics-365-sales": "Dynamics 365 Sales plugin enabled in your Cowork session, bound to your CRM environment",
    "fabric-iq": "Fabric IQ plugin enabled in your Cowork session",
    "monday-com": "monday.com plugin enabled and connected to your workspace",
    "miro": "Miro plugin enabled and connected to your workspace",
    "prezi": "Prezi plugin enabled and connected to your account",
}


def yaml_str(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def one_line(s: str) -> str:
    return " ".join(s.split())


def detect_ootb(text: str) -> List[str]:
    low = text.lower()
    found = [name for name, pat in OOTB_PATTERNS if re.search(pat, low)]
    return [f for f in found if f in VALID_OOTB][:6]


def clip(s: str, n: int) -> str:
    s = one_line(s)
    if len(s) <= n:
        return s
    cut = s[: n - 1].rsplit(" ", 1)[0]
    return cut + "."


def write_recipe(task: dict, rid: str, tag: str, plugin: str) -> str:
    area = tag.split("/")[0]
    folder = REPO / "recipes" / area / rid
    (folder / "screenshots").mkdir(parents=True, exist_ok=True)

    pack_title = PACK_TITLES[task["pack"]]
    title = task["title"]
    goal = task["goal"]
    output = task["output"]
    prompt = task["prompt"]
    workflow = task["workflow"]
    notes = task.get("notes") or []
    difficulty = TIER_DIFFICULTY.get(task["tier"], "intermediate")
    ootb = detect_ootb(prompt + " " + output)

    summary = clip(goal or output, 275)
    business_value = clip(f"{goal} {output}" if goal and output else (goal or output), 495)

    prereqs = ["Microsoft 365 Copilot licence with access to Cowork"]
    if plugin in PLUGIN_PREREQ:
        prereqs.append(PLUGIN_PREREQ[plugin])
    if plugin == "dynamics-365-sales":
        prereqs.append("A Dynamics 365 Sales licence")

    ootb_block = ("  ootb:\n" + "\n".join(f"    - {o}" for o in ootb)) if ootb else "  ootb: []"

    recipe_yaml = (
        f"id: {rid}\n"
        f"title: \"{yaml_str(title)}\"\n"
        f"summary: >-\n  {summary}\n"
        f"business_value: >-\n  {business_value}\n"
        f"plugin: {plugin}\n"
        f"process_tags:\n  - {tag}\n"
        f"recipe_type: prompt\n"
        f"difficulty: {difficulty}\n"
        f"mutates_data: false\n"
        f"generated_by: human\n"
        f"reviewed_by: seangalliher\n"
        f"status: draft\n"
        f"deprecated: false\n"
        f"license: CC-BY-4.0\n"
        f"uses_skills:\n{ootb_block}\n  plugin: []\n  custom: []\n"
        f"prerequisites:\n" + "".join(f"  - {p}\n" for p in prereqs) +
        f"youtube: []\n"
        f"authors:\n  - github: seangalliher\n    name: Sean Galliher\n"
        f"created: \"{TODAY}\"\n"
        f"version: \"1.0.0\"\n"
    )
    (folder / "recipe.yaml").write_text(recipe_yaml, encoding="utf-8")
    (folder / "prompt.md").write_text(prompt.strip() + "\n", encoding="utf-8")

    steps = [
        "Open Cowork and start a new task.",
    ]
    if plugin in PLUGIN_PREREQ:
        steps.append(f"Confirm the required plugin is turned on under **+ > Customize**: {PLUGIN_PREREQ[plugin]}.")
    steps += [
        "Paste the prompt from `prompt.md`, replacing anything in square brackets with your own values.",
        "Review the plan Cowork proposes before letting it run.",
        "Check any drafted email or calendar change before approving it — the prompt holds them for review rather than sending.",
    ]

    workflow_md = ""
    if workflow:
        workflow_md = "## How Cowork works through it\n\n" + "\n".join(f"{i}. {w}" for i, w in enumerate(workflow, 1)) + "\n\n"
    notes_md = ("> **Tip.** " + " ".join(notes) + "\n\n") if notes else ""

    readme = (
        f"# {title}\n\n"
        f"{summary}\n\n"
        f"> ⚠ **Draft recipe — not yet verified.** This prompt is reproduced from the "
        f"{pack_title}. It has not been run against our tenant, so the output described below is "
        f"the pack's stated expectation rather than an observed result. Validate before relying on it.\n\n"
        f"{notes_md}"
        f"## Business value\n\n{business_value}\n\n"
        f"## What it does\n\n{output}\n\n"
        f"## Prerequisites\n\n" + "\n".join(f"- {p}" for p in prereqs) + "\n\n"
        f"## Step-by-step\n\n" + "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1)) + "\n\n"
        f"{workflow_md}"
        f"## Expected output\n\n{output}\n\n"
        f"![Placeholder screenshot for {title}](screenshots/01-placeholder.svg "
        f"\"Placeholder — replace with a real screenshot captured against your tenant.\")\n\n"
        f"## Source\n\n"
        f"Adapted from the **{pack_title}**, a task pack Microsoft publishes for customers. "
        f"The prompt is reproduced as published; the surrounding recipe metadata, process "
        f"tagging, and guidance are the Cookbook's.\n\n"
        f"## Skills used\n\n"
        f"OOTB: {', '.join(ootb) if ootb else '—'}\n\n"
        f"Plugin: {plugin if plugin != 'none' else 'none required'}\n\n"
        f"## License\n\nCC-BY-4.0 — see repo `LICENSE`.\n"
    )
    (folder / "README.md").write_text(readme, encoding="utf-8")

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img" '
        f'aria-label="Placeholder screenshot for {title}">\n'
        f'  <rect width="800" height="450" fill="#f3f4f6"/>\n'
        f'  <rect x="20" y="20" width="760" height="40" fill="#1f2937"/>\n'
        f'  <text x="40" y="48" fill="#f9fafb" font-family="system-ui, sans-serif" font-size="18" '
        f'font-weight="600">{title[:80]}</text>\n'
        f'  <text x="400" y="240" text-anchor="middle" fill="#6b7280" '
        f'font-family="system-ui, sans-serif" font-size="16">'
        f'Placeholder - replace with a real screenshot once captured.</text>\n'
        f'</svg>\n'
    )
    (folder / "screenshots" / "01-placeholder.svg").write_text(svg, encoding="utf-8")
    return f"{area}/{rid}"


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(os.environ["TEMP"]) / "taskpack_tasks.json"
    tasks = json.loads(src.read_text(encoding="utf-8"))

    existing = {p.parent.name for p in REPO.glob("recipes/*/*/recipe.yaml")}
    written, skipped, collisions = [], [], []

    for t in tasks:
        key = (t["pack"], t["num"])
        if key not in MAPPING:
            skipped.append(f"{t['pack']} {t['num']}: no mapping")
            continue
        rid, tag, plugin = MAPPING[key]
        if rid in existing:
            collisions.append(rid)
            continue
        written.append(write_recipe(t, rid, tag, plugin))

    for w in sorted(written):
        print(f"  wrote {w}")
    print(f"\n{len(written)} recipes written")
    if collisions:
        print(f"COLLISION with existing recipe ids (skipped): {collisions}")
    if skipped:
        print(f"skipped: {skipped}")


if __name__ == "__main__":
    main()
