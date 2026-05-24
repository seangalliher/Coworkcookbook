"""
generate_full_catalog.py — bulk-generate draft recipes covering every BPC process node.

Outputs to recipes/<area>/<rid>/ directly (does NOT use seed_p021.py - that script
remains the source of truth for the 28 hand-curated + validated recipes).

Each L3 (process) node gets 2 draft recipes using a deterministic template rotation.
All recipes are status: draft with placeholder screenshots and real MCP plugin action ids.

Run: python scripts/generate_full_catalog.py
"""
from __future__ import annotations
import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parents[1]
TAX_PATH = Path(r"d:/Dev/Cowork Cookbook/web/public/data/taxonomy.json")
TODAY = "2026-05-24"
PROTECTED = {  # Hand-curated rids — never overwrite these
    "gl-trial-balance-variance", "journal-entry-validation", "period-close-checklist",
    "fx-revaluation-health-check", "month-end-close-status-dashboard",
    "vendor-master-cleanup", "vendor-invoice-validation", "payment-proposal-review",
    "customer-credit-limit-review", "ar-aging-collection-email", "sales-order-validation",
    "customer-revenue-globe", "bom-completeness-audit", "planned-order-summary",
    "production-variance-report", "fixed-asset-register-audit", "depreciation-forecast",
    "workforce-headcount-report", "onboarding-checklist-generator",
    "user-access-review-audit", "case-heatmap-html", "product-launch-readiness-scorecard",
    "eco-impact-analysis", "forecast-vs-actuals", "3d-warehouse-heatmap",
    "project-margin-health", "quote-conversion-funnel", "field-service-daily-utilization",
    "vendor-invoice-three-way-match-status",
}

# Sanitize a title fragment into a slug-safe stem.
def slugify(s: str) -> str:
    s = s.lower().replace("&", "and")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

# Truncate to a safe id length, preserving leading verb.
def cap_id(s: str, maxlen: int = 78) -> str:
    s = s.strip("-")
    if len(s) <= maxlen:
        return s
    return s[:maxlen].rstrip("-")

def titlecase(s: str) -> str:
    # Convert "manage-active-products" -> "Manage Active Products"
    return " ".join(w.capitalize() for w in s.replace("_", "-").split("-"))


# 10 template verbs. Each produces a complete Recipe shell.
# Fields: verb_slug, title_suffix, mutates, ootb, plugin_actions, recipe_type,
# prompt_template, summary_template, business_value_template, what_template.
TEMPLATES: List[Dict] = [
    {  # 0
        "verb": "audit",
        "title": "{Process} Completeness Audit",
        "mutates": False,
        "ootb": ["Excel"],
        "plugin_actions": [("dynamics-365-erp", "data_find_entity_type"),
                           ("dynamics-365-erp", "data_find_entities_sql")],
        "summary": "Audits {process_lower} records for completeness and policy compliance against rule-based checks.",
        "business_value": "Reduces audit findings and prevents downstream errors by surfacing missing fields, stale records, and out-of-policy entries while there is still time to fix them at the source.",
        "what": "Reads {process_lower} records, runs a rule-based completeness audit, and emits an exceptions workbook.",
        "prompt": (
            "Using the Dynamics 365 ERP plugin against legal entity USMF, audit {process_lower} records for completeness. "
            "For each record, flag: missing required fields, stale dates, blank descriptions, references to inactive entities, "
            "and any policy violations specific to {process_lower}. Output an Excel workbook "
            "'{rid}-{date}.xlsx' with one sheet per finding category, plus a Summary sheet with counts. "
            "Do not modify any data. If the tenant has no {process_lower} data, honestly report that and stop. "
            "(Tenant note: USMF demo data is mostly FY2017 - adjust your date window accordingly.)"
        ),
    },
    {  # 1
        "verb": "report",
        "title": "{Process} Summary Report",
        "mutates": False,
        "ootb": ["Excel"],
        "plugin_actions": [("dynamics-365-erp", "data_find_entity_type"),
                           ("dynamics-365-erp", "data_find_entities_sql")],
        "summary": "Builds a structured summary report of {process_lower} activity with totals, trends, and breakdowns.",
        "business_value": "Gives leadership a fast, repeatable view of where {process_lower} stands so decisions are made on facts rather than spreadsheet stitches.",
        "what": "Reads {process_lower} records, computes summary statistics and groupings, and emits an Excel report.",
        "prompt": (
            "Using the Dynamics 365 ERP plugin against legal entity USMF, build a summary report of {process_lower} for "
            "the most recent posted period available in the tenant (USMF demo data is mostly FY2017). Include totals, "
            "by-dimension breakdowns (by department / category / responsible owner where applicable), and a 'Top 10 by value' "
            "section. Output an Excel workbook '{rid}-{date}.xlsx' with Summary, Detail, and Top10 sheets. Do not modify any data."
        ),
    },
    {  # 2
        "verb": "dashboard",
        "title": "{Process} Interactive HTML Dashboard",
        "mutates": False,
        "ootb": ["PDF"],
        "plugin_actions": [("dynamics-365-erp", "data_find_entity_type"),
                           ("dynamics-365-erp", "data_find_entities_sql")],
        "summary": "Produces a self-contained interactive HTML dashboard for {process_lower} - opens in any browser, no D365 access needed by the viewer.",
        "business_value": "Lets ops leadership share a live-looking view of {process_lower} with executives and customers without granting D365 logins.",
        "what": "Builds a single-file HTML dashboard with inline SVG/d3 charts visualizing {process_lower}.",
        "prompt": (
            "Using the Dynamics 365 ERP plugin against legal entity USMF, pull {process_lower} data for the most recent "
            "fiscal period available. Produce a standalone HTML file '{rid}-{date}.html' that renders an interactive "
            "dashboard with: (a) a header with totals and 'data refreshed at' timestamp, (b) at least two inline SVG charts "
            "(bar, donut, or trend), (c) a sortable detail table beneath, (d) a colour-coded RAG indicator. Save the HTML to "
            "the output folder. Do not modify any data."
        ),
    },
    {  # 3
        "verb": "scheduled-brief",
        "title": "{Process} Scheduled Email Brief",
        "mutates": False,
        "ootb": ["Email", "Communications"],
        "plugin_actions": [("dynamics-365-erp", "data_find_entity_type"),
                           ("dynamics-365-erp", "data_find_entities_sql")],
        "summary": "Schedulable morning-brief email summarizing {process_lower} for the responsible owner; designed to run daily or weekly.",
        "business_value": "Replaces a daily manual spreadsheet stitch with an automatic brief so owners walk into standup already knowing where {process_lower} stands.",
        "what": "Reads {process_lower}, computes a short brief, drafts an email, and is a strong candidate for a Cowork scheduled task.",
        "prompt": (
            "Using the Dynamics 365 ERP plugin against legal entity USMF, build a short morning brief on {process_lower} for "
            "the responsible owner. Include: (a) top 5 items by impact today, (b) any anomalies vs the 7-day rolling average, "
            "(c) recommended next actions. Draft an email to the owner (save to drafts, do not send). Also produce a "
            "Communications-ready summary suitable for a Teams channel post. This recipe is a strong candidate for a Cowork "
            "scheduled task - schedule for weekday mornings at 7am."
        ),
    },
    {  # 4
        "verb": "demo-data",
        "title": "{Process} Demo Data Generator",
        "mutates": True,
        "ootb": ["Excel"],
        "plugin_actions": [("dynamics-365-erp", "data_create_entities")],
        "summary": "Generates and creates realistic demo records for {process_lower} in a sandbox tenant for training and pilot scenarios.",
        "business_value": "Eliminates the 'no data to demo with' blocker for trainers, implementation partners, and pilot programs by populating realistic but synthetic {process_lower} data in minutes.",
        "what": "Generates a configurable number of realistic {process_lower} records and creates them via the D365 ERP plugin.",
        "prompt": (
            "Using the Dynamics 365 ERP plugin against a SANDBOX legal entity (default USMF), generate 25 realistic demo "
            "records for {process_lower}. Use plausible values for every required field, vary the data so it looks organic, "
            "and stage them in an Excel workbook '{rid}-{date}.xlsx' BEFORE creating. Then create the records in D365. After "
            "creation, output a confirmation list with each new record's primary key. WARNING: this recipe creates data - run "
            "in sandbox only, and never against a production legal entity."
        ),
    },
    {  # 5
        "verb": "configure",
        "title": "{Process} Configuration Bulk Setup",
        "mutates": True,
        "ootb": ["Excel"],
        "plugin_actions": [("dynamics-365-erp", "data_find_entity_type"),
                           ("dynamics-365-erp", "data_update_entities"),
                           ("dynamics-365-erp", "form_open_menu_item"),
                           ("dynamics-365-erp", "form_set_control_values"),
                           ("dynamics-365-erp", "form_save_form")],
        "summary": "Applies a bulk configuration change to {process_lower} from an input Excel file, with validation and rollback support.",
        "business_value": "Eliminates the click-by-click burden of bulk configuration changes for {process_lower}, cutting setup time from days to minutes while preserving auditability.",
        "what": "Reads a configuration Excel file, validates each row, then applies updates via the D365 ERP plugin.",
        "prompt": (
            "Using the Dynamics 365 ERP plugin against legal entity USMF (sandbox first!), read an attached configuration "
            "Excel file containing one row per {process_lower} target with the new field values. Validate every row before "
            "applying anything (required fields present, valid references, no duplicates). Produce a 'validation' workbook "
            "showing which rows would succeed vs fail and why. Pause and ask me to approve before applying any changes. After "
            "approval, apply the validated changes and emit a confirmation workbook with before/after values. WARNING: this "
            "recipe modifies data - sandbox first."
        ),
    },
    {  # 6
        "verb": "ppt-exec",
        "title": "{Process} Executive PowerPoint Deck",
        "mutates": False,
        "ootb": ["PowerPoint", "Excel"],
        "plugin_actions": [("dynamics-365-erp", "data_find_entity_type"),
                           ("dynamics-365-erp", "data_find_entities_sql")],
        "summary": "Generates an executive-ready PowerPoint deck on {process_lower} status, complete with charts and talking-point notes.",
        "business_value": "Cuts deck prep time from hours to minutes for {process_lower} reviews while ensuring the numbers in the slides match D365 to the cent.",
        "what": "Reads {process_lower} data and produces a 6-8 slide PowerPoint suitable for an executive review.",
        "prompt": (
            "Using the Dynamics 365 ERP plugin against legal entity USMF, build an executive PowerPoint deck on {process_lower} "
            "for a 15-minute monthly review. Produce '{rid}-{date}.pptx' with: (1) title slide, (2) headline KPIs, "
            "(3) trend chart vs prior period, (4) top issues / red flags, (5) recommended actions, (6) appendix - data sources "
            "and methodology. Include speaker-notes on each slide with talking points. Do not modify any data."
        ),
    },
    {  # 7
        "verb": "teams-update",
        "title": "{Process} Teams Channel Update",
        "mutates": False,
        "ootb": ["Communications", "Adaptive Cards"],
        "plugin_actions": [("dynamics-365-erp", "data_find_entity_type"),
                           ("dynamics-365-erp", "data_find_entities_sql")],
        "summary": "Drafts a Teams channel post on {process_lower} status with an interactive Adaptive Card for quick triage.",
        "business_value": "Replaces 'check the spreadsheet' Teams pings with a glanceable card the team can act on directly - reducing back-and-forth and decision latency.",
        "what": "Reads {process_lower}, produces a Communications-ready Teams post + an Adaptive Card with quick-action buttons.",
        "prompt": (
            "Using the Dynamics 365 ERP plugin against legal entity USMF, summarize the current state of {process_lower}. "
            "Produce: (a) a Communications-ready Teams channel post (markdown) with a 2-sentence summary and 3 bullet "
            "highlights; (b) an Adaptive Card JSON '{rid}-{date}-card.json' showing KPIs, status indicators, and quick-action "
            "buttons (e.g., 'View detail', 'Open in D365'). Do not post the card on my behalf - save the artifacts for me to review."
        ),
    },
    {  # 8
        "verb": "adaptive-card",
        "title": "{Process} Status Adaptive Card",
        "mutates": False,
        "ootb": ["Adaptive Cards"],
        "plugin_actions": [("dynamics-365-erp", "data_find_entity_type"),
                           ("dynamics-365-erp", "data_find_entities_sql")],
        "summary": "Produces a reusable Adaptive Card JSON snapshot of {process_lower} status for embedding in dashboards, emails, or Teams.",
        "business_value": "Gives any consuming app (Teams, Outlook, custom dashboard) a single canonical {process_lower} status card so different surfaces always show the same numbers.",
        "what": "Generates an Adaptive Card JSON file with current {process_lower} KPIs and RAG indicators.",
        "prompt": (
            "Using the Dynamics 365 ERP plugin against legal entity USMF, produce an Adaptive Card JSON file "
            "'{rid}-{date}-card.json' that visualizes the current state of {process_lower}. Include: header with title and "
            "timestamp, 3-5 KPI tiles with current value + trend arrow, a RAG indicator row, and 2-3 action buttons. The card "
            "should render correctly in Teams, Outlook Adaptive Card preview, and the Adaptive Cards designer. Do not modify any data."
        ),
    },
    {  # 9
        "verb": "bulk-update",
        "title": "{Process} Bulk Field Update",
        "mutates": True,
        "ootb": ["Excel"],
        "plugin_actions": [("dynamics-365-erp", "data_find_entity_type"),
                           ("dynamics-365-erp", "data_update_entities")],
        "summary": "Applies a bulk field update across {process_lower} records from an input list, with dry-run preview before commit.",
        "business_value": "Avoids the click-by-click drudgery (and risk of inconsistency) when {process_lower} records need a coordinated change - and the dry-run preview catches mistakes before they hit the system.",
        "what": "Reads target record IDs + desired field values, previews changes, then applies them after explicit approval.",
        "prompt": (
            "Using the Dynamics 365 ERP plugin against legal entity USMF (sandbox first!), apply a bulk field update to "
            "{process_lower} records. Input format: I'll provide a list of record IDs and the new value(s). Produce a dry-run "
            "preview workbook showing every proposed change (before / after / status). Pause and ask for approval. After I "
            "approve, apply the changes and emit a confirmation workbook. WARNING: this recipe modifies data - sandbox only, "
            "and have a rollback plan."
        ),
    },
]


def first_para(s: str, maxlen: int = 280) -> str:
    s = s.strip().split("\n")[0]
    return s[:maxlen]


def main() -> int:
    nodes = json.loads(TAX_PATH.read_text(encoding="utf-8"))["nodes"]
    # Index by id
    by_id: Dict[str, dict] = {n["id"]: n for n in nodes}
    # L3 process nodes
    l3 = [n for n in nodes if n["level"] == "process"]
    # Build counter for verb assignment per L2 area
    l2_to_l3s: Dict[str, List[dict]] = {}
    for n in l3:
        l2_to_l3s.setdefault(n["parent"], []).append(n)

    seen_rids = set(PROTECTED)
    written = 0
    skipped_protected = 0
    domains_l1 = sorted({n["id"] for n in nodes if n["level"] == "end-to-end"})

    for l2_id, l3_list in l2_to_l3s.items():
        for l3_idx, l3_node in enumerate(l3_list):
            # Two verb indices per L3 - one read (0-3 or 6-8) and one mutate (4,5,9)
            # Rotate to ensure mix
            base = (l3_idx + sum(ord(c) for c in l2_id)) % 10
            v1 = base
            # Pair with complementary verb (read with write or vice versa)
            v2 = (base + 4) % 10
            # Ensure v1 != v2 mod doesn't collapse
            if v1 == v2:
                v2 = (v1 + 1) % 10
            for verb_idx in (v1, v2):
                tmpl = TEMPLATES[verb_idx]
                l3_slug = l3_node["id"].split("/")[-1]
                rid_raw = f"{tmpl['verb']}-{l3_slug}"
                rid = cap_id(rid_raw, 78)
                # Ensure uniqueness
                base_rid = rid
                disambig = 2
                while rid in seen_rids:
                    suffix = f"-{disambig}"
                    rid = cap_id(base_rid, 78 - len(suffix)) + suffix
                    disambig += 1
                seen_rids.add(rid)
                # Build content
                process_title = l3_node["title"]
                process_lower = process_title[0].lower() + process_title[1:] if process_title else "this process"
                area_l1 = l3_node["id"].split("/")[0]
                vars_ = {
                    "process": process_title,
                    "Process": process_title,
                    "process_lower": process_lower,
                    "rid": rid,
                    "date": TODAY,
                }
                title = tmpl["title"].format(**vars_)
                summary = first_para(tmpl["summary"].format(**vars_), 280)
                bv = first_para(tmpl["business_value"].format(**vars_), 500)
                what = tmpl["what"].format(**vars_)
                prompt_body = tmpl["prompt"].format(**vars_)
                # Write files
                folder = REPO / "recipes" / area_l1 / rid
                if folder.exists() and rid in PROTECTED:
                    skipped_protected += 1
                    continue
                # Don't blast existing folders unless they're ours to overwrite
                folder.mkdir(parents=True, exist_ok=True)
                (folder / "screenshots").mkdir(exist_ok=True)
                # Build recipe.yaml
                ootb_yaml = "\n".join(f"    - {x}" for x in tmpl["ootb"]) if tmpl["ootb"] else "    []"
                if tmpl["plugin_actions"]:
                    plugin_yaml_str = "\n".join(
                        f"    - plugin: {p}\n      action: {a}" for p, a in tmpl["plugin_actions"]
                    )
                else:
                    plugin_yaml_str = " []"
                if ootb_yaml.strip() == "[]":
                    ootb_block = "  ootb: []"
                else:
                    ootb_block = "  ootb:\n" + ootb_yaml
                if plugin_yaml_str.strip() == "[]":
                    plugin_block = "  plugin: []"
                else:
                    plugin_block = "  plugin:\n" + plugin_yaml_str
                # process_tags: use the full L3 path
                pt_block = f"  - {l3_node['id']}"
                # Build YAML body
                yaml_body = f"""id: {rid}
title: {title}
summary: >-
  {summary}
business_value: >-
  {bv}
plugin: dynamics-365-erp
process_tags:
{pt_block}
recipe_type: prompt
difficulty: intermediate
mutates_data: {"true" if tmpl["mutates"] else "false"}
min_plugin_version: "1.0.0"
generated_by: copilot
reviewed_by: seangalliher
status: draft
deprecated: false
license: CC-BY-4.0
uses_skills:
{ootb_block}
{plugin_block}
  custom: []
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
                (folder / "recipe.yaml").write_text(yaml_body, encoding="utf-8")
                (folder / "prompt.md").write_text(prompt_body.strip() + "\n", encoding="utf-8")
                # README
                draft_warning = (
                    "\n> ⚠ **Draft recipe — not yet verified.** Generated by the bulk catalog generator to ensure every "
                    "Business Process Catalog process has at least one recipe. The prompt below uses the real D365 ERP MCP "
                    "tool surface and the USMF tenant data conventions, but no one has run this against a live Cowork tenant "
                    "yet. Validate before relying on it.\n"
                )
                sandbox_warning = ""
                if tmpl["mutates"]:
                    sandbox_warning = (
                        "\n> ⚠ **This recipe modifies Dynamics 365 data.** Run it in a sandbox tenant first and review the "
                        "proposed changes before approving any write action.\n"
                    )
                # SVG placeholder
                svg = (
                    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img" '
                    f'aria-label="Placeholder screenshot for {title}">\n'
                    f'  <rect width="800" height="450" fill="#f3f4f6"/>\n'
                    f'  <rect x="20" y="20" width="760" height="40" fill="#1f2937"/>\n'
                    f'  <text x="40" y="48" fill="#f9fafb" font-family="system-ui, sans-serif" font-size="18" font-weight="600">{title[:80]}</text>\n'
                    f'  <text x="400" y="240" text-anchor="middle" fill="#6b7280" font-family="system-ui, sans-serif" font-size="16">'
                    f'Placeholder - replace with a real screenshot once captured against your tenant.</text>\n'
                    f'</svg>\n'
                )
                (folder / "screenshots" / "01-placeholder.svg").write_text(svg, encoding="utf-8")
                readme = (
                    f"# {title}\n\n"
                    f"{summary}\n"
                    f"{draft_warning}"
                    f"{sandbox_warning}\n"
                    f"## Business value\n\n{bv}\n\n"
                    f"## What it does\n\n{what}\n\n"
                    f"## Prerequisites\n\n- Dynamics 365 F&SCM access with the appropriate role\n- Cowork D365 ERP plugin enabled\n\n"
                    f"## Step-by-step\n\n"
                    f"1. Open Cowork and confirm the Dynamics 365 ERP plugin is toggled on for your session.\n"
                    f"2. Paste the prompt from `prompt.md` into a new task.\n"
                    f"3. Review the generated output and adjust scope as needed.\n"
                    f"{'4. **Before approving any write action, review the dry-run preview.**' + chr(10) if tmpl['mutates'] else ''}\n"
                    f"## Expected output\n\n"
                    f"See the prompt for the specific deliverable(s). All generated files land in `Documents/Cowork/output/` in OneDrive.\n\n"
                    f"![Placeholder screenshot for {title}](screenshots/01-placeholder.svg \"Placeholder - replace with a real screenshot captured against your tenant.\")\n\n"
                    f"## Skills used\n\n"
                    f"OOTB: {', '.join(tmpl['ootb']) if tmpl['ootb'] else '—'}\n"
                    f"Plugin actions: {', '.join(f'{p}/{a}' for p, a in tmpl['plugin_actions']) if tmpl['plugin_actions'] else '—'}\n\n"
                    f"## License\n\nCC-BY-4.0 — see repo `LICENSE`.\n"
                )
                (folder / "README.md").write_text(readme, encoding="utf-8")
                written += 1

    # --- Build the 15 L1-domain skills + ~15 L2 area skills (total <= 30 of 50) ---
    skills_root = REPO / "skills"
    skills_root.mkdir(exist_ok=True)
    skills_written = 0
    # 15 L1 domain skills
    for l1_id in domains_l1:
        l1_node = by_id[l1_id]
        skill_slug = f"d365-{l1_id}"
        sd = skills_root / skill_slug
        sd.mkdir(exist_ok=True)
        # Find all L2/L3 under this L1
        l2s = sorted({n["title"] for n in nodes if n.get("parent") == l1_id})
        l3s_under = sorted({n["title"] for n in nodes if n["level"] == "process" and n["id"].startswith(l1_id + "/")})
        body = f"""---
name: D365 {l1_node['title']} Expert
description: A Dynamics 365 Finance & Supply Chain Management expert scoped to the {l1_node['title']} end-to-end process - covers {len(l2s)} L2 areas and {len(l3s_under)} L3 processes from the Microsoft Business Process Catalog.
---

You are a Dynamics 365 Finance & Supply Chain Management subject-matter expert focused exclusively on the **{l1_node['title']}** end-to-end process.

## Scope

{l1_node.get('description', '')}

You cover the following areas within this domain:

{chr(10).join(f"- **{x}**" for x in l2s)}

## Plugin you rely on

Use the **Dynamics 365 ERP** plugin (dynamic MCP server) for all data access. The plugin exposes 22 generic tools across three categories:

- **Data tools**: `data_find_entity_type`, `data_get_entity_metadata`, `data_find_entities`, `data_find_entities_sql`, `data_create_entities`, `data_update_entities`, `data_delete_entities`
- **Form tools**: `form_find_menu_item`, `form_open_menu_item`, `form_find_controls`, `form_set_control_values`, `form_open_lookup`, `form_click_control`, `form_filter_form`, `form_filter_grid`, `form_sort_grid_column`, `form_select_grid_row`, `form_open_or_close_tab`, `form_save_form`, `form_close_form`
- **Action tools**: `api_find_actions`, `api_invoke_action`

For read-only analytics use `data_find_entity_type` + `data_find_entities_sql`. For writes use `data_create_entities` / `data_update_entities` (with explicit user approval).

## Always do

1. Lead with `"Using the Dynamics 365 ERP plugin against legal entity USMF, ..."` (or substitute the user's legal entity).
2. Be explicit about entities, time window, threshold, and output artifact name.
3. End with: `"If the tenant has no <X>, honestly report that and stop."` to enable honest-degrade.
4. For write actions: always produce a dry-run preview workbook and pause for approval.
5. Document any data-availability findings in a Notes/Methodology sheet of the workbook.

## USMF demo tenant conventions

- General Ledger / period close: FY 2017 (Dec 2017 is "most recent")
- AR transactions: through 2023-11-29
- Production orders: 2016-11 to 2016-12
- Service work orders: through 2016-12-30
- Workers: 97 active (92 employees + 5 contractors)
- Released products: 206
- Vendor invoices: zero in USMF (USSI/USRT have data)

## Known entity limitations

These entities are NOT queryable via the plugin's OData surface - if asked for them, return a constraint table and offer alternatives:

- `ProdCalcTrans` (production cost variance)
- `VendInvoiceJour` (posted vendor-invoice journal)
- `SecurityUserRoles` + `SecurityRoles` (access-restricted)
- Last-sign-in date (lives in Entra/Azure AD)
- Per-technician work calendars (Service Mgmt module only)
- Aisle/rack/shelf/bin metadata (frequently NULL)
"""
        (sd / "SKILL.md").write_text(body, encoding="utf-8")
        skills_written += 1

    # 15 L2 skills: pick a representative L2 per L1
    for l1_id in domains_l1:
        l2_under = [n for n in nodes if n.get("parent") == l1_id and n["level"] == "area"]
        if not l2_under:
            continue
        # Pick the L2 with the most L3 children
        l2_with_counts = [
            (n, sum(1 for x in nodes if x["level"] == "process" and x["id"].startswith(n["id"] + "/")))
            for n in l2_under
        ]
        l2_with_counts.sort(key=lambda t: -t[1])
        l2_node = l2_with_counts[0][0]
        l3s_under_l2 = [n["title"] for n in nodes if n["level"] == "process" and n["id"].startswith(l2_node["id"] + "/")]
        skill_slug = f"d365-{l2_node['id'].replace('/', '-')}"
        skill_slug = cap_id(skill_slug, 78)
        sd = skills_root / skill_slug
        sd.mkdir(exist_ok=True)
        body = f"""---
name: D365 {l2_node['title']} Expert
description: A Dynamics 365 F&SCM expert scoped to the {l2_node['title']} area (a level-2 subdomain of {by_id[l1_id]['title']}) - covers {len(l3s_under_l2)} L3 processes.
---

You are a Dynamics 365 F&SCM subject-matter expert focused on the **{l2_node['title']}** area within {by_id[l1_id]['title']}.

## Scope

{l2_node.get('description', '')}

You cover the following processes:

{chr(10).join(f"- {x}" for x in l3s_under_l2)}

## Plugin you rely on

Use the Dynamics 365 ERP plugin. For reads: `data_find_entity_type` + `data_find_entities_sql`. For writes: `data_create_entities` / `data_update_entities` with explicit user approval and a dry-run preview workbook first.

## Always do

1. Lead with `"Using the Dynamics 365 ERP plugin against legal entity USMF, ..."`
2. End reads with `"If the tenant has no <X>, honestly report that and stop."`
3. For writes: dry-run preview + explicit approval before commit.
4. Document any data-availability findings in a Methodology sheet.

## USMF demo tenant data eras

GL=2017, AR=through 2023-11, Production=2016-11/12, Service=through 2016-12-30, Workers=97, Released products=206, Vendor invoices=zero in USMF.
"""
        (sd / "SKILL.md").write_text(body, encoding="utf-8")
        skills_written += 1

    print(f"Wrote {written} draft recipes")
    print(f"Skipped {skipped_protected} protected (hand-curated) recipes")
    print(f"Wrote {skills_written} domain-scoped Cowork skills under skills/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
