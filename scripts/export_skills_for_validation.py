"""Generate scripts/skills_validation_data.json — a single JSON file containing all 30 skill rids + SKILL.md content. Used by the Playwright driver."""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
skills = []
for recipe_yaml in sorted(REPO.rglob("recipes/*/d365-*/recipe.yaml")):
    folder = recipe_yaml.parent
    rid = folder.name
    area = folder.parent.name
    skill_md = folder / "skill" / "SKILL.md"
    if not skill_md.exists():
        continue
    title_line = next((ln for ln in recipe_yaml.read_text(encoding="utf-8").splitlines() if ln.startswith("title:")), "title: ?")
    title = title_line.split(":", 1)[1].strip()
    skills.append({
        "rid": rid,
        "area": area,
        "title": title,
        "skill_md": skill_md.read_text(encoding="utf-8"),
    })

out = REPO / "scripts" / "skills_validation_data.json"
out.write_text(json.dumps(skills, indent=2), encoding="utf-8")
print(f"wrote {out} - {len(skills)} skills, {out.stat().st_size} bytes")
