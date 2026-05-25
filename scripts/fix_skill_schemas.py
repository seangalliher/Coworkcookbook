"""Rewrite the 30 skill SKILL.md files to match Cowork's required schema.

Cowork's contract (per the in-app /skills documentation):

    OneDrive path: Cowork/.claude/skills/<slug>/SKILL.md
    Frontmatter:
        ---
        name: <slug>                           # must match folder name exactly (kebab-case)
        description: <one-line with explicit trigger phrases>
        cowork:
          category: <category>
          icon: <Fluent icon name>
        ---
    Required sections (in order):
        ## When to Use     (trigger scenarios)
        ## Workflow        (numbered steps)
        ## When NOT to Use (exclusions)

Also updates each recipe's README.md install steps + recipe.yaml summary
to point at the correct OneDrive path (was Documents/Cowork/skills, must
be Cowork/.claude/skills).
"""
from __future__ import annotations
import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RECIPES = REPO / "recipes"

L1_TITLES = {
    "acquire-to-dispose": "Acquire to dispose",
    "administer-to-operate": "Administer to operate",
    "case-to-resolution": "Case to resolution",
    "concept-to-market": "Concept to market",
    "design-to-retire": "Design to retire",
    "forecast-to-plan": "Forecast to plan",
    "hire-to-retire": "Hire to retire",
    "inventory-to-deliver": "Inventory to deliver",
    "order-to-cash": "Order to cash",
    "plan-to-produce": "Plan to produce",
    "project-to-profit": "Project to profit",
    "prospect-to-quote": "Prospect to quote",
    "record-to-report": "Record to report",
    "service-to-deliver": "Service to deliver",
    "source-to-pay": "Source to pay",
}

# Per-L1 trigger phrases (used in description) and icon picks
L1_TRIGGERS = {
    "acquire-to-dispose": ["fixed assets", "asset depreciation", "asset disposal", "asset acquisition"],
    "administer-to-operate": ["D365 administration", "user access", "system features", "background jobs"],
    "case-to-resolution": ["service case", "customer case", "case management", "service desk"],
    "concept-to-market": ["product launch", "marketing campaign", "product readiness", "go-to-market"],
    "design-to-retire": ["BOM", "engineering change", "ECO", "product lifecycle", "BOM audit"],
    "forecast-to-plan": ["forecast", "S&OP", "demand planning", "business strategy"],
    "hire-to-retire": ["workforce", "HR", "headcount", "onboarding", "employee"],
    "inventory-to-deliver": ["warehouse", "inventory", "freight", "shipping", "on-hand"],
    "order-to-cash": ["sales order", "AR", "accounts receivable", "credit", "collections", "invoice customer"],
    "plan-to-produce": ["production order", "BOM completeness", "production planning", "MRP"],
    "project-to-profit": ["project", "project margin", "project budget", "project actuals"],
    "prospect-to-quote": ["sales quote", "lead", "opportunity", "quote conversion"],
    "record-to-report": ["trial balance", "general ledger", "GL", "period close", "month-end", "journal entry", "FX revaluation"],
    "service-to-deliver": ["service work order", "field service", "technician", "service utilization"],
    "source-to-pay": ["vendor", "purchase order", "AP", "accounts payable", "supplier", "procurement"],
}

L1_ICONS = {
    "acquire-to-dispose": "Building",
    "administer-to-operate": "Settings",
    "case-to-resolution": "Headset",
    "concept-to-market": "Lightbulb",
    "design-to-retire": "Wrench",
    "forecast-to-plan": "ChartMultiple",
    "hire-to-retire": "PeopleTeam",
    "inventory-to-deliver": "BoxMultiple",
    "order-to-cash": "Money",
    "plan-to-produce": "BuildingFactory",
    "project-to-profit": "Tasks",
    "prospect-to-quote": "Target",
    "record-to-report": "DocumentBulletList",
    "service-to-deliver": "WrenchScrewdriver",
    "source-to-pay": "Cart",
}


def detect_l1(slug: str) -> str:
    s = slug
    if s.startswith("d365-"):
        s = s[len("d365-"):]
    for l1 in L1_TITLES:
        if s == l1 or s.startswith(l1 + "-"):
            return l1
    raise ValueError(f"Couldn't map slug '{slug}' to an L1 domain")


def is_l1_skill(slug: str) -> bool:
    return slug[len("d365-"):] in L1_TITLES


def build_skill_md(slug: str) -> str:
    l1 = detect_l1(slug)
    l1_title = L1_TITLES[l1]
    is_l1 = is_l1_skill(slug)
    triggers = L1_TRIGGERS[l1]
    icon = L1_ICONS[l1]

    if is_l1:
        scope_desc = f"the **{l1_title}** end-to-end business process"
        l2_or_l3 = "covering every area in this domain"
    else:
        l2_slug = slug[len("d365-") + len(l1) + 1:]
        l2_title = l2_slug.replace("-", " ").capitalize()
        scope_desc = f"the **{l2_title}** area within **{l1_title}**"
        l2_or_l3 = f"focused specifically on the {l2_title} L2 area"

    trigger_quoted = ", ".join(f'"{t}"' for t in triggers[:5])
    description = (
        f"Dynamics 365 Finance & Supply Chain Management expert scoped to "
        f"{l1_title.lower()}. Use when user mentions {trigger_quoted}, or any "
        f"USMF tenant question that lands in this domain."
    )

    body = f"""# {slug}

## When to Use

Activate this skill whenever the user's request touches {scope_desc}, {l2_or_l3}. Specific trigger phrases include:

{chr(10).join(f"- {t}" for t in triggers)}

Also activate when the user names any Dynamics 365 F&SCM entity that belongs to this domain (vendor, purchase order, sales order, trial balance, BOM, fixed asset, project, work order, etc.) and the request is about D365 ERP rather than CRM (Sales / Customer Service).

## Workflow

1. **Always lead the D365 prompt** with `"Using the Dynamics 365 ERP plugin against legal entity USMF, ..."`. The explicit legal-entity scope is the single biggest reliability lever - never omit it.

2. **Pick the right MCP tool**. The D365 ERP plugin exposes 22 generic tools across three categories. For this domain, prefer:
   - **Read-only analytics** (~80% of requests): `data_find_entity_type` then `data_find_entities_sql`.
   - **Bulk writes** (with explicit user approval): `data_create_entities` / `data_update_entities` / `data_delete_entities`. Always produce a dry-run preview workbook first.
   - **Form-based entry**: `form_open_menu_item` + `form_find_controls` + `form_set_control_values` + `form_save_form`.
   - **Action / business operation**: `api_find_actions` + `api_invoke_action`.

3. **Be explicit about entities, time window, threshold, and output artifact** (e.g. `'<rid>-<YYYY-MM-DD>.xlsx'`). Don't leave the agent to guess any of these.

4. **End every read prompt with the honesty escape**: `"If the tenant has no <X>, honestly report that and stop."` This engages the honest-degrade path - the constraint table the agent returns when data isn't available is itself a useful deliverable.

5. **Document data-availability findings** in a "Notes" or "Methodology" sheet of any workbook output, so the next person knows what was reachable and what wasn't.

6. **For write actions**: produce a validation / dry-run workbook FIRST. Pause and ask for approval. Only after the user confirms, apply the changes and emit a confirmation workbook with before/after values.

## USMF tenant conventions (memorize)

- General Ledger / period close: FY 2017 (Dec 2017 is the canonical "most recent" period)
- Customer AR transactions: through 2023-11-29 (newer than other subledgers)
- Production orders: 2016-11 to 2016-12
- Service work orders: through 2016-12-30
- Workers: 97 active (92 employees + 5 contractors; no Intern enum)
- Released products: 206
- Vendor invoices: **zero** records in USMF `VendorInvoiceHeader` (data lives in USSI / USRT siblings)
- Sales quotes: **one quote** in entire tenant history (Quote 000007, 2012-10-03)

## Known unreachable entities (return a constraint table, never fabricate)

- `ProdCalcTrans` (production cost variance)
- `VendInvoiceJour` (posted vendor-invoice journal)
- `SecurityUserRoles` + `SecurityRoles` (access-restricted at the entity layer)
- Last-sign-in date (lives in Entra / Azure AD audit logs, not D365)
- Per-technician work calendars (USMF has Service Management, not Field Service)
- Aisle / rack / shelf / bin metadata (frequently NULL even when location ID exists)

## When NOT to Use

- The user is asking about Dynamics 365 Sales or Customer Service CRM scenarios (use the appropriate CRM skill instead).
- The request is about Microsoft Graph, Entra, or other M365 surfaces that aren't in the D365 ERP plugin.
- A specific recipe from the Cowork Cookbook already covers the exact ask - use that recipe directly rather than re-deriving it.
- The user wants raw Power Query / DAX / Power BI work against D365 - this skill is about the live MCP plugin, not BI export pipelines.
"""

    fm = f"""---
name: {slug}
description: {description}
cowork:
  category: dynamics-365
  icon: {icon}
---

"""
    return fm + body


def update_readme(rid: str, area: str) -> None:
    readme_path = RECIPES / area / rid / "README.md"
    if not readme_path.exists():
        return
    text = readme_path.read_text(encoding="utf-8")
    # Replace the install path
    text = text.replace(
        "/Documents/Cowork/skills/",
        "/Cowork/.claude/skills/",
    ).replace(
        "Documents/Cowork/skills/",
        "Cowork/.claude/skills/",
    )
    readme_path.write_text(text, encoding="utf-8")


def main() -> int:
    skill_recipe_yamls = sorted(RECIPES.rglob("d365-*/recipe.yaml"))
    print(f"Found {len(skill_recipe_yamls)} skill recipes")
    fixed = 0
    for ry in skill_recipe_yamls:
        rid = ry.parent.name
        area = ry.parent.parent.name
        skill_md = ry.parent / "skill" / "SKILL.md"
        if not skill_md.exists():
            print(f"  SKIP {rid} (no skill/SKILL.md)")
            continue
        new_content = build_skill_md(rid)
        skill_md.write_text(new_content, encoding="utf-8")
        update_readme(rid, area)
        fixed += 1
    print(f"Rewrote {fixed} SKILL.md files + updated README install paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
