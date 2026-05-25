"""Migrate the 30 standalone skills under skills/ into prompt+skill recipes under recipes/.

Each skills/<slug>/SKILL.md becomes:
  recipes/<l1>/<slug>/
    recipe.yaml        (recipe_type: prompt+skill, status: draft)
    prompt.md          (short bootstrap prompt that activates the skill)
    skill/SKILL.md     (the original skill content)
    screenshots/01-placeholder.svg
    README.md          (description + usage)

After migration, the skills/ directory is removed.
"""
from __future__ import annotations
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO / "skills"
RECIPES_ROOT = REPO / "recipes"
TODAY = "2026-05-24"

L1_DOMAINS = [
    "acquire-to-dispose", "administer-to-operate", "case-to-resolution",
    "concept-to-market", "design-to-retire", "forecast-to-plan",
    "hire-to-retire", "inventory-to-deliver", "order-to-cash",
    "plan-to-produce", "project-to-profit", "prospect-to-quote",
    "record-to-report", "service-to-deliver", "source-to-pay",
]


def parse_skill_md(text: str) -> tuple[dict, str]:
    """Return (frontmatter dict, body markdown)."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm_raw = m.group(1)
    body = m.group(2)
    fm: dict = {}
    for line in fm_raw.splitlines():
        kv = line.split(":", 1)
        if len(kv) == 2:
            fm[kv[0].strip()] = kv[1].strip()
    return fm, body


def detect_l1(slug: str) -> str:
    """slug is like 'd365-acquire-to-dispose' or 'd365-acquire-to-dispose-acquire-assets'."""
    s = slug
    if s.startswith("d365-"):
        s = s[len("d365-"):]
    for l1 in L1_DOMAINS:
        if s == l1 or s.startswith(l1 + "-"):
            return l1
    raise ValueError(f"Couldn't map slug '{slug}' to an L1 domain")


def is_l1_skill(slug: str) -> bool:
    """True if this is an L1 (end-to-end) scoped skill, False for L2-area scoped."""
    return slug[len("d365-"):] in L1_DOMAINS


def make_summary(name: str, l1: str, is_l1: bool) -> str:
    if is_l1:
        return (
            f"Cowork custom skill that scopes the agent to the {l1.replace('-', ' ')} end-to-end "
            f"process. Drops a SKILL.md into your OneDrive so Cowork loads the domain context automatically."
        )
    return (
        f"Cowork custom skill scoped to a specific {l1.replace('-', ' ')} area. Drops a SKILL.md "
        f"into your OneDrive so Cowork loads the area context automatically."
    )


def make_business_value(name: str) -> str:
    return (
        f"Save time and improve accuracy by giving Cowork a persistent expert context for the "
        f"target domain - it knows the right entities, the USMF tenant data quirks, and the honest-"
        f"degrade options before you even open a task."
    )


def write_recipe(slug: str, fm: dict, body: str) -> None:
    l1 = detect_l1(slug)
    is_l1 = is_l1_skill(slug)
    name = fm.get("name", slug)
    description = fm.get("description", make_summary(name, l1, is_l1))
    # Cap to schema maxLength: summary 280, business_value 500
    summary = description[:280] if description else make_summary(name, l1, is_l1)[:280]
    bv = make_business_value(name)[:500]
    target = RECIPES_ROOT / l1 / slug
    skill_target = target / "skill"
    shots_target = target / "screenshots"
    skill_target.mkdir(parents=True, exist_ok=True)
    shots_target.mkdir(parents=True, exist_ok=True)
    # SKILL.md
    (skill_target / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n{body}",
        encoding="utf-8",
    )
    # Prompt — the bootstrap prompt that tells Cowork to use this skill
    prompt = (
        f"Activate the **{name}** skill for this conversation. From now on, scope your help to "
        f"the {l1.replace('-', ' ')} domain only - use the entities, USMF tenant conventions, and "
        f"honest-degrade options documented in the skill. Lead with: 'Using the Dynamics 365 ERP "
        f"plugin against legal entity USMF, ...' on every D365-touching prompt.\n"
    )
    (target / "prompt.md").write_text(prompt, encoding="utf-8")
    # Recipe yaml
    process_tag = l1 if is_l1 else slug[len("d365-"):]  # L2 slug like 'source-to-pay/manage-supplier-relationships' isn't preserved exactly here
    # For L2 we need the full path. Rebuild from slug: 'd365-source-to-pay-manage-supplier-relationships' -> 'source-to-pay/manage-supplier-relationships'
    if not is_l1:
        rest = slug[len("d365-"):]
        rest = rest[len(l1) + 1:]  # drop "<l1>-"
        process_tag = f"{l1}/{rest}"
    yaml_body = f"""id: {slug}
title: {name}
summary: >-
  {summary}
business_value: >-
  {bv}
plugin: dynamics-365-erp
process_tags:
  - {process_tag}
recipe_type: prompt+skill
difficulty: intermediate
mutates_data: false
min_plugin_version: "1.0.0"
generated_by: copilot
reviewed_by: seangalliher
status: draft
deprecated: false
license: CC-BY-4.0
uses_skills:
  ootb: []
  plugin:
    - plugin: dynamics-365-erp
      action: data_find_entity_type
    - plugin: dynamics-365-erp
      action: data_find_entities_sql
  custom:
    - {slug}
prerequisites:
  - Dynamics 365 F&SCM access with the appropriate role
  - Cowork D365 ERP plugin enabled
youtube: []
authors:
  - github: seangalliher
    name: Sean Galliher
created: "{TODAY}"
version: "1.0.0"
"""
    (target / "recipe.yaml").write_text(yaml_body, encoding="utf-8")
    # README
    readme = (
        f"# {name}\n\n"
        f"{summary}\n\n"
        f"> \u2139 **This is a Cowork custom skill.** Place the contents of the `skill/` folder under "
        f"`Documents/Cowork/skills/{slug}/` in your OneDrive. Cowork auto-discovers custom skills at the "
        f"start of each conversation.\n\n"
        f"## Business value\n\n{bv}\n\n"
        f"## How to install\n\n"
        f"1. Open OneDrive in your browser or sync client.\n"
        f"2. Navigate to `/Documents/Cowork/skills/` (create the folder if it doesn't exist).\n"
        f"3. Create a subfolder named `{slug}`.\n"
        f"4. Download `skill/SKILL.md` from this recipe and place it inside the subfolder.\n"
        f"5. Start a new Cowork task - the skill is auto-loaded.\n\n"
        f"## How to use\n\n"
        f"Once the skill is installed, the bootstrap prompt below activates it for a single conversation:\n\n"
        f"![Placeholder screenshot](screenshots/01-placeholder.svg \"Placeholder - replace with a real screenshot.\")\n\n"
        f"## Skill contents\n\nThe skill file is in `skill/SKILL.md`. It includes:\n\n"
        f"- The real 22-tool D365 ERP MCP surface (data / form / action tools)\n"
        f"- USMF tenant data conventions (date eras, known entity gaps)\n"
        f"- Honest-degrade defaults so the agent stops instead of fabricating\n\n"
        f"## License\n\nCC-BY-4.0 - see repo `LICENSE`.\n"
    )
    (target / "README.md").write_text(readme, encoding="utf-8")
    # SVG placeholder
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img" '
        f'aria-label="Placeholder screenshot for {name}">\n'
        f'  <rect width="800" height="450" fill="#f4f1ff"/>\n'
        f'  <rect x="20" y="20" width="760" height="40" fill="#5a48d4"/>\n'
        f'  <text x="40" y="48" fill="#ffffff" font-family="system-ui, sans-serif" font-size="18" font-weight="600">{name[:80]}</text>\n'
        f'  <text x="400" y="240" text-anchor="middle" fill="#6b5fa8" font-family="system-ui, sans-serif" font-size="16">'
        f'Cowork custom skill (SKILL.md) - install in OneDrive Documents/Cowork/skills/</text>\n'
        f'</svg>\n'
    )
    (shots_target / "01-placeholder.svg").write_text(svg, encoding="utf-8")
    print(f"  wrote {l1}/{slug}")


def main() -> int:
    if not SKILLS_ROOT.exists():
        print(f"No skills directory at {SKILLS_ROOT}; nothing to migrate")
        return 0
    skills = sorted(p for p in SKILLS_ROOT.iterdir() if p.is_dir())
    print(f"Migrating {len(skills)} skills into recipes/")
    for skill_dir in skills:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            print(f"  SKIP {skill_dir.name} (no SKILL.md)")
            continue
        text = skill_md.read_text(encoding="utf-8")
        fm, body = parse_skill_md(text)
        write_recipe(skill_dir.name, fm, body)
    print("Removing skills/ directory")
    shutil.rmtree(SKILLS_ROOT)
    print("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
