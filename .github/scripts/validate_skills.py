"""
Validate Cowork custom skill packages embedded under recipes/**/skill/.
Enforces the Cowork-documented limits:
  - SKILL.md exists, ≤ 1 MB, with YAML frontmatter containing `name` + `description`
  - companion files ≤ 20
  - total size ≤ 10 MB
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
RECIPES = ROOT / "recipes"

FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def main() -> int:
    errors: list[str] = []
    skill_dirs = [p for p in RECIPES.rglob("skill") if p.is_dir() and p.parent.parent.parent == RECIPES.parent / "recipes" or True]
    # narrow to skill folders that are direct children of a recipe folder
    skill_dirs = [p for p in RECIPES.rglob("skill") if p.is_dir() and (p.parent / "recipe.yaml").exists()]

    for d in skill_dirs:
        rel = d.relative_to(ROOT)
        skill_md = d / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"{rel}: missing SKILL.md")
            continue
        size = skill_md.stat().st_size
        if size > 1024 * 1024:
            errors.append(f"{rel}/SKILL.md: {size} bytes > 1 MB limit")
        content = skill_md.read_text(encoding="utf-8")
        m = FM.match(content)
        if not m:
            errors.append(f"{rel}/SKILL.md: missing YAML frontmatter (--- ... ---)")
        else:
            try:
                meta = yaml.safe_load(m.group(1)) or {}
            except Exception as ex:  # noqa: BLE001
                errors.append(f"{rel}/SKILL.md: frontmatter YAML error: {ex}")
                meta = {}
            for key in ("name", "description"):
                if not meta.get(key):
                    errors.append(f"{rel}/SKILL.md: frontmatter missing '{key}'")

        companions = [p for p in d.rglob("*") if p.is_file() and p != skill_md]
        if len(companions) > 20:
            errors.append(f"{rel}: {len(companions)} companion files > 20 limit")
        total = sum(p.stat().st_size for p in [skill_md, *companions])
        if total > 10 * 1024 * 1024:
            errors.append(f"{rel}: total {total} bytes > 10 MB limit")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK ({len(skill_dirs)} skill packages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
