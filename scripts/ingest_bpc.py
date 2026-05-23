"""Ingest the Microsoft Business Process Catalog xlsx into taxonomy/business-processes.yaml.

The BPC workbook columns are:
  Title 1 = Catalog name (only on row 0)
  Title 2 = End-to-end process
  Title 3 = Process area
  Title 4 = Process
  Title 5 = Scenario (skipped by default in v1)
  ...
  Work item type = "End to end" | "Process area" | "Process" | "Scenario" | "System process" | "Test case"
  Process sequence ID = e.g., "10.05.020.000"
  Microsoft ID = stable Microsoft id ("d6689987c110v0")
  Description = prose
  Microsoft references = URL on learn.microsoft.com

Output: taxonomy/business-processes.yaml with stable kebab-case slug ids.
Run via `python scripts/ingest_bpc.py` from the repo root.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

try:
    import openpyxl  # type: ignore[import-not-found]
except ImportError:
    print("Run: pip install openpyxl pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT.parent / "Cowork Cookbook" / "Reference" / "Business Process Catalog MAR 2026.xlsx"
OUT = ROOT / "taxonomy" / "business-processes.yaml"

# Include levels in v1. Scenarios are 3500+ — skip unless explicitly enabled.
INCLUDE_LEVELS = {"End to end", "Process area", "Process"}


def slugify(text: str) -> str:
    """Lowercase, ASCII, hyphenated. Stable across runs."""
    if not text:
        return ""
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", " ", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:80]


def yq(s: str) -> str:
    """Single-quoted YAML scalar — escape internal single quotes by doubling."""
    return "'" + (s or "").replace("'", "''") + "'"


def main() -> int:
    if not XLSX.exists():
        print(f"Workbook not found: {XLSX}", file=sys.stderr)
        return 1
    wb = openpyxl.load_workbook(XLSX, data_only=True, read_only=True)
    ws = wb["Busines Process Catalog"]

    rows = ws.iter_rows(values_only=True)
    next(rows)
    next(rows)

    nodes: list[dict[str, str]] = []
    e2e_slug: str | None = None
    area_slug: str | None = None

    for r in rows:
        wit = r[4]
        if wit not in INCLUDE_LEVELS:
            continue
        seq_id = (r[1] or "").strip() if isinstance(r[1], str) else (str(r[1]) if r[1] else "")
        ms_id = (r[3] or "").strip() if isinstance(r[3], str) else ""
        title1 = (r[5] or "").strip()
        title2 = (r[6] or "").strip()
        title3 = (r[7] or "").strip()
        title4 = (r[8] or "").strip()
        desc = (r[16] or "").strip().replace("\r\n", " ").replace("\n", " ")
        learn_url = (r[21] or "").strip()

        if wit == "End to end":
            title = title2 or title1
            e2e_slug = slugify(title)
            area_slug = None
            nodes.append({
                "id": e2e_slug,
                "title": title,
                "level": "end-to-end",
                "description": desc,
                "ms_bpc_id": ms_id,
                "sequence_id": seq_id,
                "learn_url": learn_url,
            })
        elif wit == "Process area":
            title = title3 or title2
            if not e2e_slug:
                continue
            area_slug = f"{e2e_slug}/{slugify(title)}"
            nodes.append({
                "id": area_slug,
                "parent": e2e_slug,
                "title": title,
                "level": "area",
                "description": desc,
                "ms_bpc_id": ms_id,
                "sequence_id": seq_id,
                "learn_url": learn_url,
            })
        elif wit == "Process":
            title = title4 or title3 or title2
            if not area_slug:
                continue
            slug = f"{area_slug}/{slugify(title)}"
            nodes.append({
                "id": slug,
                "parent": area_slug,
                "title": title,
                "level": "process",
                "description": desc,
                "ms_bpc_id": ms_id,
                "sequence_id": seq_id,
                "learn_url": learn_url,
            })

    seen: dict[str, int] = {}
    for n in nodes:
        key = n["id"]
        if key in seen:
            seen[key] += 1
            n["id"] = f"{key}-{seen[key]}"
        else:
            seen[key] = 1

    out_lines = [
        "version: '1.0.0'",
        "source: 'Microsoft Business Process Catalog MAR 2026 - https://learn.microsoft.com/en-us/dynamics365/guidance/business-processes/overview'",
        "",
        "nodes:",
    ]
    for n in nodes:
        out_lines.append(f"  - id: {n['id']}")
        out_lines.append(f"    title: {yq(n['title'])}")
        out_lines.append(f"    level: {n['level']}")
        if n.get("parent"):
            out_lines.append(f"    parent: {n['parent']}")
        if n.get("ms_bpc_id"):
            out_lines.append(f"    ms_bpc_id: {yq(n['ms_bpc_id'])}")
        if n.get("sequence_id"):
            out_lines.append(f"    sequence_id: {yq(n['sequence_id'])}")
        if n.get("learn_url"):
            out_lines.append(f"    learn_url: {yq(n['learn_url'])}")
        desc = (n.get("description") or "").strip()
        if desc:
            first_sentence = desc.split(". ")[0][:280]
            out_lines.append(f"    description: {yq(first_sentence)}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for n in nodes:
        counts[n["level"]] = counts.get(n["level"], 0) + 1
    print(f"Wrote {len(nodes)} nodes -> {OUT}")
    print(f"  by level: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
