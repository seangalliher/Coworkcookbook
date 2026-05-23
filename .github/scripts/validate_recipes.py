"""
Validate every recipe.yaml against schemas/recipe.schema.json plus the two
taxonomy files. Also enforce:
- VERIFICATION.md exists when recipe mutates_data: true
- process_tags reference real taxonomy ids
- Slug folder name matches recipe.id

Fails the build (exit 1) on the first error per file, but reports all files.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas"
RECIPES = ROOT / "recipes"
TAXONOMY = ROOT / "taxonomy"


def load_yaml(p: Path):
    with p.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json(p: Path):
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    errors: list[str] = []

    recipe_schema = load_json(SCHEMAS / "recipe.schema.json")
    bp_schema = load_json(SCHEMAS / "business-processes.schema.json")
    cs_schema = load_json(SCHEMAS / "cowork-skills.schema.json")

    bp_data = load_yaml(TAXONOMY / "business-processes.yaml")
    cs_data = load_yaml(TAXONOMY / "cowork-skills.yaml")

    for label, schema, data, path in (
        ("business-processes", bp_schema, bp_data, TAXONOMY / "business-processes.yaml"),
        ("cowork-skills", cs_schema, cs_data, TAXONOMY / "cowork-skills.yaml"),
    ):
        for e in Draft202012Validator(schema).iter_errors(data):
            errors.append(f"{path}: {list(e.path)} -> {e.message}")

    taxonomy_ids = {n["id"] for n in bp_data["nodes"]}

    recipe_yamls = list(RECIPES.rglob("recipe.yaml"))
    if not recipe_yamls:
        print("WARNING: no recipes found.")
    for ry in recipe_yamls:
        rel = ry.relative_to(ROOT)
        try:
            data = load_yaml(ry)
        except Exception as ex:  # noqa: BLE001
            errors.append(f"{rel}: YAML parse error: {ex}")
            continue
        for e in Draft202012Validator(recipe_schema).iter_errors(data):
            errors.append(f"{rel}: {list(e.path)} -> {e.message}")
        if isinstance(data, dict):
            slug = ry.parent.name
            if data.get("id") and slug != data["id"]:
                errors.append(f"{rel}: folder name '{slug}' != recipe id '{data['id']}'")
            for tag in data.get("process_tags", []):
                if tag not in taxonomy_ids:
                    errors.append(f"{rel}: process_tag '{tag}' not in taxonomy")
            if data.get("mutates_data") is True:
                if not (ry.parent / "VERIFICATION.md").exists():
                    errors.append(
                        f"{rel}: mutates_data:true requires VERIFICATION.md in the same folder"
                    )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"OK ({len(recipe_yamls)} recipes, {len(taxonomy_ids)} taxonomy nodes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
