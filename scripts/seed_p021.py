"""
P-021 seed script — generates 20 starter recipes for the Cowork Cookbook.

Each recipe spec produces:
  recipes/<area>/<id>/recipe.yaml
  recipes/<area>/<id>/prompt.md
  recipes/<area>/<id>/README.md
  recipes/<area>/<id>/screenshots/01-placeholder.svg

Re-runnable: removes the target folder before writing so the spec is the source of truth.
"""
from __future__ import annotations
import shutil
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

REPO = Path(__file__).resolve().parents[1]
TODAY = "2026-05-23"


@dataclass
class Recipe:
    rid: str
    area: str  # e.g., "record-to-report"
    title: str
    summary: str
    business_value: str
    process_tags: List[str]
    ootb: List[str]
    plugin_actions: List[Tuple[str, str]]  # (plugin, action) — use real MCP tool names from the D365 ERP MCP server
    mutates_data: bool
    prompt: str
    what: str
    prerequisites: List[str]
    steps: str
    expected: str
    custom: List[str] = field(default_factory=list)
    # Verification state — when verified=True the recipe is published as `status: verified`
    # with no draft banner, and the real screenshot replaces the placeholder.
    verified: bool = False
    verified_screenshot: str = ""  # filename under scripts/seed_assets/<rid>/ to copy as 01-cowork-output.png
    verified_against_cowork_build: str = ""
    tenant_caveat: str = ""


def yaml_list(items: List[str], indent: str = "    ") -> str:
    if not items:
        return " []"
    return "\n" + "\n".join(f"{indent}- {x}" for x in items)


def plugin_yaml(items: List[Tuple[str, str]], indent: str = "    ") -> str:
    if not items:
        return " []"
    return "\n" + "\n".join(
        f"{indent}- plugin: {p}\n{indent}  action: {a}" for p, a in items
    )


def custom_yaml(items: List[str], indent: str = "    ") -> str:
    if not items:
        return " []"
    return "\n" + "\n".join(f"{indent}- {x}" for x in items)


def write_recipe(r: Recipe) -> None:
    folder = REPO / "recipes" / r.area / r.rid
    # Selectively remove generated files so real captured screenshots are preserved.
    for relpath in ("recipe.yaml", "prompt.md", "README.md", "screenshots/01-placeholder.svg"):
        p = folder / relpath
        if p.exists():
            p.unlink()
    (folder / "screenshots").mkdir(parents=True, exist_ok=True)

    status_block = (
        f"status: verified\n"
        f"last_verified_on: \"{TODAY}\"\n"
        f"verified_against_cowork_build: \"{r.verified_against_cowork_build or 'live-tenant-' + TODAY}\"\n"
        if r.verified
        else "status: draft\n"
    )
    recipe_yaml = (
        f"id: {r.rid}\n"
        f"title: {r.title}\n"
        f"summary: >-\n"
        f"  {r.summary}\n"
        f"business_value: >-\n"
        f"  {r.business_value}\n"
        f"plugin: dynamics-365-erp\n"
        f"process_tags:\n"
        + "".join(f"  - {t}\n" for t in r.process_tags)
        + f"recipe_type: prompt\n"
        f"difficulty: intermediate\n"
        f"mutates_data: {str(r.mutates_data).lower()}\n"
        f"min_plugin_version: \"1.0.0\"\n"
        f"generated_by: copilot\n"
        f"reviewed_by: seangalliher\n"
        + status_block
        + f"deprecated: false\n"
        f"license: CC-BY-4.0\n"
        f"uses_skills:\n"
        f"  ootb:{yaml_list(r.ootb)}\n"
        f"  plugin:{plugin_yaml(r.plugin_actions)}\n"
        f"  custom:{custom_yaml(r.custom)}\n"
        f"prerequisites:\n"
        + "".join(f"  - {p}\n" for p in r.prerequisites)
        + f"youtube: []\n"
        f"authors:\n"
        f"  - github: seangalliher\n"
        f"    name: Sean Galliher\n"
        f"created: \"{TODAY}\"\n"
        f"version: \"1.0.0\"\n"
    )
    (folder / "recipe.yaml").write_text(recipe_yaml, encoding="utf-8")
    (folder / "prompt.md").write_text(r.prompt.strip() + "\n", encoding="utf-8")

    sandbox_warning = ""
    if r.mutates_data:
        sandbox_warning = (
            "\n> ⚠ **This recipe modifies Dynamics 365 data.** Run it in a sandbox tenant first "
            "and review the proposed changes before approving any write action.\n"
        )
    draft_warning = (
        ""
        if r.verified
        else (
            "\n> ⚠ **Draft recipe — not yet verified.** The prompt, OOTB skill list, and plugin "
            "actions named below are starter content. No one has run this against a live Cowork tenant "
            "with the Dynamics 365 ERP plugin yet. Validate before relying on it.\n"
        )
    )
    tenant_caveat_block = (
        f"\n> ℹ **Tenant data caveat.** {r.tenant_caveat}\n" if r.tenant_caveat else ""
    )
    if r.verified and r.verified_screenshot:
        screenshot_md = (
            f"![Cowork output for {r.title}](screenshots/01-cowork-output.png "
            f"\"Captured against a live Cowork tenant on {TODAY}.\")"
        )
    else:
        screenshot_md = (
            f"![Placeholder screenshot for {r.title}](screenshots/01-placeholder.svg "
            f"\"Placeholder — replace with a real screenshot captured against your tenant.\")"
        )
    readme = (
        f"# {r.title}\n\n"
        f"{r.summary}\n"
        f"{draft_warning}"
        f"{tenant_caveat_block}"
        f"{sandbox_warning}\n"
        f"## Business value\n\n{r.business_value}\n\n"
        f"## What it does\n\n{r.what}\n\n"
        f"## Prerequisites\n\n" + "\n".join(f"- {p}" for p in r.prerequisites) + "\n\n"
        f"## Step-by-step\n\n{r.steps}\n\n"
        f"## Expected output\n\n{r.expected}\n\n"
        f"{screenshot_md}\n\n"
        f"## Skills used\n\n"
        f"OOTB: {', '.join(r.ootb) if r.ootb else '—'}\n"
        f"Plugin actions: {', '.join(f'{p}/{a}' for p, a in r.plugin_actions) if r.plugin_actions else '—'}\n\n"
        f"## License\n\nCC-BY-4.0 — see repo `LICENSE`.\n"
    )
    (folder / "README.md").write_text(readme, encoding="utf-8")

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img" '
        f'aria-label="Placeholder screenshot for {r.title}">\n'
        f'  <rect width="800" height="450" fill="#f3f4f6"/>\n'
        f'  <rect x="20" y="20" width="760" height="40" fill="#1f2937"/>\n'
        f'  <text x="40" y="48" fill="#f9fafb" font-family="system-ui, sans-serif" font-size="18" font-weight="600">{r.title}</text>\n'
        f'  <text x="400" y="240" text-anchor="middle" fill="#6b7280" font-family="system-ui, sans-serif" font-size="16">'
        f'Placeholder — captured screenshot will replace this image.</text>\n'
        f'</svg>\n'
    )
    if not (r.verified and r.verified_screenshot):
        (folder / "screenshots" / "01-placeholder.svg").write_text(svg, encoding="utf-8")
    # Copy a verified screenshot from scripts/seed_assets if specified.
    if r.verified and r.verified_screenshot:
        src = REPO / "scripts" / "seed_assets" / r.rid / r.verified_screenshot
        dst = folder / "screenshots" / "01-cowork-output.png"
        if src.exists():
            shutil.copyfile(src, dst)
        elif not dst.exists():
            print(f"  WARN: verified screenshot {src} not found and no existing {dst}")
    print(f"wrote {r.area}/{r.rid}")


RECIPES: List[Recipe] = [
    # ===== Record to Report =====
    Recipe(
        rid="gl-trial-balance-variance",
        area="record-to-report",
        title="GL Trial Balance Variance Report",
        summary="Compares the current-period trial balance to the prior period and highlights GL accounts with material variances.",
        business_value=(
            "Cuts month-end review time by focusing the controller on the GL accounts with material variances instead of every line in the trial balance."
        ),
        process_tags=["record-to-report/record-financial-transactions"],
        ootb=["Excel", "Email"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        verified=True,
        verified_screenshot="01-cowork-output.png",
        verified_against_cowork_build="m365.cloud.microsoft 2026-05-23",
        tenant_caveat=(
            "Validated end-to-end against a live Cowork tenant on 2026-05-23 with USMF demo data. Cowork executed the full "
            "5-step plan (find trial balance entity → query March/February 2017 → compute variances → build workbook → draft "
            "email), produced 'TB-variance-2017-03.xlsx' with 8 material accounts and an 'All' sheet of 9 posting accounts, "
            "and saved a controller email draft summarizing the top 5 by absolute variance. Because USMF has no saved trial-"
            "balance snapshots for 2017, Cowork honestly derived the comparison from posted LedgerJournalLines activity rather "
            "than running balances — see the screenshot for the agent's note on this. For a tenant with running trial-balance "
            "snapshots you'll get period-end positions instead of period activity; both shapes are useful for variance review."
        ),
        prompt=(
            "Using the Dynamics 365 ERP plugin, query the trial balance for the most recent posted period AND the prior period "
            "for the same chart of accounts in legal entity USMF. For each posting account: compute the variance amount and the "
            "variance percent. Mark any account where |variance| >= $10,000 OR |variance %| >= 10% as 'material'.\n\n"
            "Use the Excel skill to produce a workbook 'TB-variance-<YYYY-MM>.xlsx' with two sheets: 'Material' (variances that "
            "crossed the threshold, sorted by absolute variance amount descending) and 'All' (every account).\n\n"
            "Then draft an email to the controller summarizing the count of material variances and the top 5 by amount. "
            "Do not modify any data.\n\n"
            "(Tenant note: the USMF demo tenant's posted GL activity is mostly FY2017 — if you want guaranteed data, ask Cowork "
            "to use March 2017 vs February 2017 explicitly. Cowork will derive the comparison from posted ledger journal lines "
            "if no trial-balance snapshot exists.)"
        ),
        what="Pulls the trial balance for two consecutive periods, computes variance, flags material lines, and produces a workbook + email draft.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the General ledger user role",
            "Cowork D365 ERP plugin enabled",
        ],
        steps=(
            "1. Open Cowork and paste the prompt.\n"
            "2. Approve the read-only data access when prompted.\n"
            "3. Review the produced workbook in the side panel.\n"
            "4. Edit the email draft recipients before sending."
        ),
        expected="An Excel workbook with Material/All sheets and a draft email summarizing the top variances.",
    ),
    Recipe(
        rid="journal-entry-validation",
        area="record-to-report",
        title="Journal Entry Pre-Posting Validation",
        summary="Validates open journal entries against a configurable rule set before posting and produces an exception report.",
        business_value=(
            "Catches posting errors before they hit the ledger, eliminating the reverse-and-repost cycles that delay close."
        ),
        process_tags=["record-to-report/record-financial-transactions"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "List all open (unposted) general journal entries in the current period. For each line, validate: account is active, "
            "dimensions are valid for the account, debits = credits at the header level, and the description is non-empty. "
            "Produce an Excel workbook 'Journal-exceptions-<YYYY-MM-DD>.xlsx' with one row per failing line, indicating which rule was violated. "
            "Do not post anything."
        ),
        what="Reads open journals and runs validation rules. Output is a workbook of exceptions for the GL team to triage.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the General ledger user role",
            "Cowork D365 ERP plugin enabled",
        ],
        steps=(
            "1. Open Cowork and paste the prompt.\n"
            "2. Approve the read-only data access.\n"
            "3. Review the exceptions sheet; resolve in D365 before posting."
        ),
        expected="One workbook with one row per failing journal line and the rule that failed.",
    ),
    Recipe(
        rid="period-close-checklist",
        area="record-to-report",
        title="Period Close Checklist Generator",
        summary="Generates a tailored period-close checklist with item owners and ETA estimates based on the active legal entity's configuration.",
        business_value=(
            "Standardizes the close calendar so nothing slips, and gives the controller a single-page view to chase owners across legal entities."
        ),
        process_tags=["record-to-report/close-financial-periods"],
        ootb=["Word", "Email", "Communications"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "Generate a period-close checklist for the active legal entity for the current month. Include: AR aging review, "
            "AP aging review, FX revaluation status, sub-ledger reconciliations (AR/AP/Inventory), accrual reversals, "
            "period-end journal posting, and the period-close switch. For each item include suggested owner role and an ETA "
            "in business days. Output as a Word document and as a chat-ready Communications draft summarizing the list."
        ),
        what="Produces a tailored period-close checklist as both a Word document and a Communications-ready summary.",
        prerequisites=[
            "Dynamics 365 F&SCM read access",
            "Cowork D365 ERP plugin enabled",
        ],
        steps=(
            "1. Open Cowork and paste the prompt.\n"
            "2. Review the produced checklist and customize for your team."
        ),
        expected="One Word document and one Communications summary.",
    ),
    Recipe(
        rid="fx-revaluation-health-check",
        area="record-to-report",
        title="FX Revaluation Health Check",
        summary="Reviews FX revaluation configuration and last-run status, and flags any monetary accounts that look misconfigured.",
        business_value=(
            "Prevents misstated currency exposure by catching unflagged monetary accounts and skipped revaluations before they hit the financials."
        ),
        process_tags=["record-to-report/close-financial-periods"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "Audit the FX revaluation setup for the active legal entity. For each monetary main account: confirm it is flagged "
            "for revaluation, the appropriate gain/loss accounts are configured, and there has been a revaluation run in the "
            "current period. Build an Excel report 'FX-health-<YYYY-MM-DD>.xlsx' listing any account that is misconfigured or "
            "appears to have been skipped, with the suggested fix in a 'Recommendation' column. Do not post or change anything."
        ),
        what="Detects misconfigured monetary accounts and missed FX revaluation runs.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the General ledger user role",
        ],
        steps=(
            "1. Open Cowork and paste the prompt.\n"
            "2. Review the workbook with the GL team before changing any setup."
        ),
        expected="Workbook listing misconfigured accounts and missed runs.",
    ),
    Recipe(
        rid="month-end-close-status-dashboard",
        area="record-to-report",
        title="Month-End Close Status Dashboard",
        summary="Builds a one-page status dashboard summarizing where each close task stands as of today.",
        business_value=(
            "Replaces 'where are we on close?' standup chatter with a glanceable RAG dashboard the finance lead can post to Teams."
        ),
        process_tags=["record-to-report/close-financial-periods"],
        ootb=["Excel", "Adaptive Cards"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "Build a one-page month-end close status dashboard for the current period. Include: AR sub-ledger reconciliation "
            "status, AP sub-ledger reconciliation status, journal posting completeness, FX revaluation completion, period-close "
            "switch state, and a RAG (Red/Amber/Green) overall indicator. Produce both an Excel workbook with the data and an "
            "Adaptive Card summary that can be posted to a Teams channel. Do not post the card on my behalf."
        ),
        what="Builds an at-a-glance close status workbook and an Adaptive Card summary ready to be posted.",
        prerequisites=[
            "Dynamics 365 F&SCM read access",
        ],
        steps=(
            "1. Open Cowork and paste the prompt.\n"
            "2. Review the Adaptive Card before sharing in Teams."
        ),
        expected="One workbook and one Adaptive Card draft.",
    ),

    # ===== Source to Pay =====
    Recipe(
        rid="vendor-master-cleanup",
        area="source-to-pay",
        title="Vendor Master Cleanup Report",
        summary="Identifies duplicate, incomplete, or inactive vendors in the master record and proposes a cleanup plan.",
        business_value=(
            "Reduces duplicate payments and tax-reporting errors by tightening the vendor master before bad data propagates into invoicing and 1099s."
        ),
        process_tags=["source-to-pay/manage-supplier-relationships"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "Read the vendor master. For each vendor: flag missing tax id, missing payment terms, missing default bank account, "
            "inactive vendors with open POs, and likely duplicates (fuzzy match on name + tax id + bank). Output an Excel workbook "
            "'Vendor-cleanup-<YYYY-MM-DD>.xlsx' with one sheet per finding category. Do not delete or merge anything."
        ),
        what="Finds dirty vendor records and suggests a triage list.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Accounts payable role",
        ],
        steps=(
            "1. Paste the prompt in Cowork.\n"
            "2. Review the workbook; merge or update vendors directly in D365 as needed."
        ),
        expected="Workbook with categorized vendor-master issues.",
    ),
    Recipe(
        rid="vendor-invoice-validation",
        area="source-to-pay",
        title="Vendor Invoice Pre-Posting Validation",
        summary="Validates open vendor invoices against posting rules and emails the AP team a fix-list.",
        business_value=(
            "Avoids the back-and-forth of failed postings by surfacing posting blockers (inactive vendor, missing tax, PO mismatch) before AP releases the batch."
        ),
        process_tags=["source-to-pay/manage-accounts-payable"],
        ootb=["Excel", "Email"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "List open vendor invoices not yet posted. For each: confirm vendor is active, posting profile is configured, "
            "currency matches the vendor, tax lines balance, and (when applicable) a PO match exists. Build an Excel workbook "
            "of exceptions and draft an email (do not send) to the AP team summarizing counts by exception type."
        ),
        what="Catches posting-blocker issues on vendor invoices before they get to the GL.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Accounts payable role",
        ],
        steps=(
            "1. Paste the prompt in Cowork.\n"
            "2. Review the email draft and recipients before sending."
        ),
        expected="Workbook of invoices that would fail to post, and an email draft to the AP team.",
    ),
    Recipe(
        rid="payment-proposal-review",
        area="source-to-pay",
        title="Payment Proposal Review",
        summary="Reviews the current payment proposal for accuracy and flags lines that need attention before release.",
        business_value=(
            "Stops payment-run mistakes - duplicates, blocked vendors, missed discounts - at the review stage instead of after the wire clears."
        ),
        process_tags=["source-to-pay/manage-accounts-payable"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "Read the current payment proposal lines. Flag: vendors on hold, invoices with discount expiring within 2 days that "
            "are NOT in the proposal, duplicate invoices, payments below a $50 threshold, and vendors missing bank details. "
            "Output an Excel workbook 'Payment-proposal-review-<YYYY-MM-DD>.xlsx'. Do not release the proposal."
        ),
        what="Sanity-checks a payment proposal before release.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Accounts payable role",
        ],
        steps=(
            "1. Paste the prompt.\n"
            "2. Review the workbook with the AP manager before releasing the proposal in D365."
        ),
        expected="Workbook with flagged proposal lines by category.",
    ),

    # ===== Order to Cash =====
    Recipe(
        rid="customer-credit-limit-review",
        area="order-to-cash",
        title="Customer Credit Limit Review",
        summary="Builds a review report of customers whose credit limit or exposure looks out of policy.",
        business_value=(
            "Protects DSO and reduces bad-debt write-offs by flagging customers who have drifted out of credit policy before the next big order ships."
        ),
        process_tags=["order-to-cash/manage-credit-and-collections"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "Build a credit-management review: list customers whose current AR exposure is greater than 80% of their credit limit, "
            "customers with no credit limit set but with AR balance > $10,000, and customers with credit limit > $0 but no activity "
            "in 12 months. Output an Excel workbook with one sheet per category, sorted by exposure descending. Do not change limits."
        ),
        what="Highlights credit-policy issues so the credit team can act.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Credit/collections role",
        ],
        steps=(
            "1. Paste the prompt.\n"
            "2. Review the report; update limits via D365 with the credit committee."
        ),
        expected="Workbook with categorized customer credit issues.",
    ),
    Recipe(
        rid="ar-aging-collection-email",
        area="order-to-cash",
        title="AR Aging Collection Email Draft",
        summary="Drafts polite-but-firm collection emails to customers with overdue invoices, grouped by severity bucket.",
        business_value=(
            "Multiplies the collections team - every overdue customer gets a personalized, tone-appropriate nudge without anyone hand-writing emails."
        ),
        process_tags=["order-to-cash/manage-credit-and-collections"],
        ootb=["Email", "Communications"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "For each customer with invoices overdue >30 days, draft a collection email referencing the specific invoice numbers, "
            "due dates, and amounts. Vary tone by aging bucket (30/60/90+). Save drafts to the Cowork output folder; do not send."
        ),
        what="Generates per-customer collection emails as drafts, varying tone by aging bucket.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Credit/collections role",
        ],
        steps=(
            "1. Paste the prompt.\n"
            "2. Open each draft, review tone, and personalize before sending."
        ),
        expected="One email draft per overdue customer.",
    ),
    Recipe(
        rid="sales-order-validation",
        area="order-to-cash",
        title="Sales Order Compliance Check",
        summary="Validates open sales orders against policy: pricing, credit, customer status, delivery terms.",
        business_value=(
            "Prevents shipped-but-uninvoiceable orders by catching pricing, credit, and tax issues at order entry instead of at invoicing."
        ),
        process_tags=["order-to-cash/manage-sales-orders"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "Review all open sales orders. Flag: orders with item prices that deviate >10% from the active price list, customers on "
            "credit hold, missing delivery terms, and missing tax group. Output a workbook with one sheet per finding. Do not modify orders."
        ),
        what="Pre-shipment policy check on the sales-order book.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Sales role",
        ],
        steps=(
            "1. Paste the prompt.\n"
            "2. Resolve flagged orders in D365 before shipping."
        ),
        expected="Workbook of out-of-policy sales orders by category.",
    ),
    Recipe(
        rid="customer-revenue-globe",
        area="order-to-cash",
        title="Customer Revenue 3D Globe Visualization",
        summary="Builds an interactive 3D globe HTML visualization plotting customer locations sized by trailing-12-month revenue.",
        business_value=(
            "Turns the customer master and revenue tape into an exec-ready visual that makes geographic concentration risk and growth pockets immediately obvious."
        ),
        process_tags=["order-to-cash/analyze-sales-performance"],
        ootb=["PDF"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "Read the customer master and trailing-12-month sales by customer. For each customer with a country and city, geocode the "
            "city to lat/lon. Produce a standalone HTML file that renders a 3D globe (using a web library like globe.gl) with a marker "
            "per customer, sized by revenue and colored by region. Include a side legend. Save the HTML to the output folder."
        ),
        what="Visualizes customer revenue on a 3D globe as a standalone HTML file.",
        prerequisites=[
            "Dynamics 365 F&SCM read access",
        ],
        steps=(
            "1. Paste the prompt.\n"
            "2. Open the saved HTML file in your browser to explore."
        ),
        expected="One standalone interactive HTML file.",
    ),

    # ===== Plan to Produce =====
    Recipe(
        rid="bom-completeness-audit",
        area="plan-to-produce",
        title="BOM Completeness Audit",
        summary="Audits active BOMs for missing components, expired versions, and items that are obsolete.",
        business_value=(
            "Prevents MRP planning failures and production stoppages by catching obsolete components and version gaps before they cause a line-down event."
        ),
        process_tags=["plan-to-produce/develop-production-strategies"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "Audit every active BOM. Flag: BOMs whose effective-from date has passed but effective-to is null AND there is no successor "
            "version; BOM lines that reference inactive items; BOM lines with zero quantity; missing UoM. Output an Excel workbook."
        ),
        what="Detects BOM hygiene issues that cause planning errors.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Production role",
        ],
        steps="1. Paste the prompt.\n2. Triage findings with the BOM owner.",
        expected="Workbook of BOM hygiene issues by category.",
    ),
    Recipe(
        rid="planned-order-summary",
        area="plan-to-produce",
        title="Planned Order Summary by Resource",
        summary="Summarizes planned production orders by resource for the next four weeks, including load vs capacity.",
        business_value=(
            "Gives production planning a one-page view of where capacity is overcommitted, so the team can rebalance before missed promise dates pile up."
        ),
        process_tags=["plan-to-produce/plan-production-operations"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "List planned production orders for the next 4 weeks. Aggregate by primary resource and by week. Include the planned "
            "load in hours vs the configured capacity. Highlight any week where load > 90% of capacity. Produce an Excel workbook "
            "with a pivot-ready data sheet and a summary sheet."
        ),
        what="Capacity-and-load view of the planned production schedule.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Production role",
        ],
        steps="1. Paste the prompt.\n2. Use the workbook in production planning meetings.",
        expected="Workbook with data + summary sheet.",
    ),
    Recipe(
        rid="production-variance-report",
        area="plan-to-produce",
        title="Production Cost Variance Report",
        summary="Compares standard cost to actual cost on completed production orders and highlights material variances.",
        business_value=(
            "Identifies where standards are drifting from reality so engineering and cost accounting can fix the root cause, not just absorb the variance."
        ),
        process_tags=["plan-to-produce/run-production-operations"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "For production orders completed in the last 30 days, compute the variance between standard cost and actual cost by "
            "category (material, routing, overhead). Flag orders where the absolute variance is greater than 5% of standard. "
            "Output an Excel workbook with a 'Material variances' sheet and an 'All' sheet."
        ),
        what="Quantifies and flags production cost variance for completed orders.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Production role",
        ],
        steps="1. Paste the prompt.\n2. Review with the production controller.",
        expected="Workbook with variances by category.",
    ),

    # ===== Acquire to Dispose =====
    Recipe(
        rid="fixed-asset-register-audit",
        area="acquire-to-dispose",
        title="Fixed Asset Register Audit",
        summary="Audits the fixed asset register for missing fields, inconsistent depreciation profiles, and assets due for retirement.",
        business_value=(
            "Cleans up the asset register so depreciation, insurance, and property-tax reporting are all based on accurate data - not stale records."
        ),
        process_tags=["acquire-to-dispose/manage-active-assets"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "Audit the fixed-asset register. Flag: assets missing service-life or depreciation profile, assets fully depreciated but not "
            "retired, assets with mismatched depreciation profile vs asset group, and assets with no location assigned. Output a workbook."
        ),
        what="Surfaces fixed-asset data quality issues.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Fixed assets role",
        ],
        steps="1. Paste the prompt.\n2. Update flagged records in D365 with the asset owner.",
        expected="Workbook of fixed-asset register findings.",
    ),
    Recipe(
        rid="depreciation-forecast",
        area="acquire-to-dispose",
        title="Depreciation Forecast (12 months)",
        summary="Forecasts the next 12 months of depreciation expense by asset group and by GL account.",
        business_value=(
            "Gives FP&A a defensible, asset-by-asset depreciation forecast for the budget instead of the historical-average shortcut."
        ),
        process_tags=["acquire-to-dispose/analyze-assets"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "For every active fixed asset, calculate the depreciation expense expected over the next 12 months under the current depreciation "
            "profile. Aggregate by asset group and by GL account. Produce an Excel workbook with a 'By group', 'By account', and 'Detail' sheet."
        ),
        what="A 12-month forward look at depreciation expense.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Fixed assets role",
        ],
        steps="1. Paste the prompt.\n2. Share the workbook with FP&A.",
        expected="Workbook with three sheets.",
    ),

    # ===== Hire to Retire =====
    Recipe(
        rid="workforce-headcount-report",
        area="hire-to-retire",
        title="Workforce Headcount Report",
        summary="Builds a headcount report by department, location, and worker type for the current period.",
        business_value=(
            "Gives HR and finance a unified headcount source-of-truth that reconciles to payroll without spreadsheet stitching."
        ),
        process_tags=["hire-to-retire/analyze-hr-programs"],
        ootb=["Excel"],
        plugin_actions=[],
        mutates_data=False,
        prompt=(
            "Build a workforce headcount report as of today. Aggregate by department, by location, and by worker type (employee, "
            "contractor, intern). Include trend vs same date last year if data is available. Output as an Excel workbook."
        ),
        what="HR snapshot of current headcount with year-over-year trend.",
        prerequisites=[
            "Read access to the configured HR data source via Cowork",
        ],
        steps="1. Paste the prompt.\n2. Validate the trend figures with HR.",
        expected="Workbook with headcount by dimension and YoY trend.",
    ),
    Recipe(
        rid="onboarding-checklist-generator",
        area="hire-to-retire",
        title="Onboarding Checklist Generator",
        summary="Generates a role-tailored onboarding checklist as a Word document for a named new hire.",
        business_value=(
            "Cuts hours of HR busywork per new hire and makes sure no role-specific access, equipment, or compliance step gets missed."
        ),
        process_tags=["hire-to-retire/recruit-and-onboard-talent"],
        ootb=["Word", "Email"],
        plugin_actions=[],
        mutates_data=False,
        prompt=(
            "I'll provide a new hire name, role, start date, and manager. Produce a Word onboarding checklist tailored to the role "
            "covering: IT access, mandatory training, intro meetings, week-1/week-2/week-4 milestones. Also draft a welcome email "
            "(do not send) from the manager to the new hire."
        ),
        what="Produces a tailored onboarding plan and a welcome-email draft.",
        prerequisites=[
            "No D365 dependency",
        ],
        steps="1. Paste the prompt and provide the new-hire details when asked.\n2. Review and personalize before sending.",
        expected="One Word document and one email draft.",
    ),

    # ===== Administer to Operate =====
    Recipe(
        rid="user-access-review-audit",
        area="administer-to-operate",
        title="User Access Review & SoD Audit",
        summary="Audits Dynamics 365 user accounts for segregation-of-duties conflicts, inactive accounts with active role assignments, and roles granted without recent login.",
        business_value=(
            "Reduces audit findings and insider-risk exposure by surfacing access drift (over-privileged accounts, "
            "ghost users, SoD conflicts) before the IT auditors do."
        ),
        process_tags=["administer-to-operate/manage-system-access-and-security"],
        ootb=["Excel", "Email"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "Using the Dynamics 365 ERP plugin, list every user in the active legal entity with their assigned security roles "
            "and the date they last signed in. Flag: (a) users with both AP-vendor-maintenance AND AP-payment-release roles "
            "(SoD conflict), (b) users with no sign-in in the last 90 days who still have privileged roles, (c) users disabled "
            "in the directory but still holding D365 roles. Output an Excel workbook 'Access-review-<YYYY-MM-DD>.xlsx' with a "
            "sheet per finding category, and draft an email to the IT security lead summarizing the counts. Do not change any "
            "role assignments. (Tenant note: in the USMF demo tenant, demo accounts may have stale sign-in data — focus on the "
            "SoD conflict signal.) This recipe is a strong candidate for a Cowork scheduled task: run weekly and email the report."
        ),
        what="Identifies user access risks (SoD conflicts, stale accounts, orphaned roles) and produces an auditor-ready workbook.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the System administrator or Security administrator role",
            "Cowork D365 ERP plugin enabled",
        ],
        steps=(
            "1. Paste the prompt in Cowork.\n"
            "2. Review the workbook with the IT security lead before remediating in D365.\n"
            "3. (Optional) Schedule this task in Cowork to run weekly."
        ),
        expected="Workbook with categorized access findings and a draft summary email.",
    ),

    # ===== Case to Resolution =====
    Recipe(
        rid="case-heatmap-html",
        area="case-to-resolution",
        title="Customer Service Case Heatmap (HTML)",
        summary="Builds an interactive HTML heatmap of customer service cases by product category × priority × age bucket, with drill-through tooltips.",
        business_value=(
            "Gives service-ops leadership a one-click view of where backlog is concentrated so staffing and SLA effort can "
            "be retargeted on the products that are actually causing pain."
        ),
        process_tags=["case-to-resolution/analyze-case-performance"],
        ootb=["PDF"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "Read open customer service cases. For each case capture: product category, priority, days-open bucket "
            "(0-3, 4-7, 8-14, 15-30, 30+), and current owner. Produce a standalone HTML file 'Case-heatmap-<YYYY-MM-DD>.html' "
            "that renders an interactive heatmap (use a vanilla SVG grid or a small d3 script embedded inline) with: product "
            "category on the Y axis, priority × age bucket on the X axis, cells colored by case count, and a tooltip on hover "
            "showing the top 5 case titles in that cell. Include a header with the total open case count and a 'data refreshed "
            "at' timestamp. Save the HTML to the output folder. (Tenant note: USMF demo data is largely 2017 — adjust the date "
            "window if your tenant has older cases.)"
        ),
        what="Builds a self-contained HTML heatmap of open cases — opens in any browser, no D365 access needed by the viewer.",
        prerequisites=[
            "Dynamics 365 access with read on Customer Service cases",
            "Cowork D365 ERP plugin enabled",
        ],
        steps=(
            "1. Paste the prompt in Cowork.\n"
            "2. Open the saved HTML in your browser and share via Teams or email."
        ),
        expected="One standalone interactive HTML heatmap file.",
    ),

    # ===== Concept to Market =====
    Recipe(
        rid="product-launch-readiness-scorecard",
        area="concept-to-market",
        title="Released Product Launch Readiness Scorecard",
        summary="Scores released products on launch readiness based on setup completeness (dimensions, pricing, BOM, tax, default order settings) and produces a scorecard.",
        business_value=(
            "Prevents launch-day surprises by catching the setup gaps that block sales orders, MRP runs, or warehouse picking "
            "while there is still time to fix them."
        ),
        process_tags=["concept-to-market/manage-service-offerings"],
        ootb=["Excel", "Adaptive Cards"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "List released products released in the last 6 months (for the USMF demo tenant, broaden to FY2017). For each "
            "product, score launch readiness on a 0-100 scale based on: dimension groups set, default order settings present, "
            "active sales price configured, BOM exists for manufactured items, sales tax group assigned, and item is approved. "
            "Produce an Excel workbook with one row per product and a column per check (1/0), a total score, and a RAG indicator "
            "(<60 Red, 60-85 Amber, 85+ Green). Also produce an Adaptive Card summarizing counts in each RAG bucket, ready to "
            "post in Teams. Do not modify any product setup."
        ),
        what="Scores newly released products on readiness for launch and surfaces the specific setup gaps blocking each one.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Product designer or Item maintainer role",
            "Cowork D365 ERP plugin enabled",
        ],
        steps=(
            "1. Paste the prompt in Cowork.\n"
            "2. Review the workbook; assign owners to fix the Red and Amber items.\n"
            "3. Post the Adaptive Card to the product-launch Teams channel."
        ),
        expected="Workbook with per-product readiness score and an Adaptive Card summary.",
    ),

    # ===== Design to Retire =====
    Recipe(
        rid="eco-impact-analysis",
        area="design-to-retire",
        title="Engineering Change Order Impact Analysis",
        summary="For a proposed item change, finds every BOM, sales order, and inventory location affected and quantifies downstream impact.",
        business_value=(
            "Eliminates the 'didn't realize that part is in 14 other BOMs' surprise by surfacing the full blast radius of a "
            "proposed engineering change before it is approved."
        ),
        process_tags=["design-to-retire/manage-active-products"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "Given an item number (ask the user which one if not specified), produce an impact analysis: (a) every active BOM "
            "where the item is a component, with the parent item and the quantity per; (b) every open sales order line for the "
            "item with quantity and expected ship date; (c) on-hand inventory by warehouse; (d) any open purchase order lines "
            "for the item with expected receipt date. Output an Excel workbook 'ECO-impact-<item>-<YYYY-MM-DD>.xlsx' with one "
            "sheet per category and a summary sheet. Do not change anything."
        ),
        what="Builds a complete pre-change impact report (BOM usage, open orders, inventory, inbound POs) for a single item.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Production or Item maintainer role",
            "Cowork D365 ERP plugin enabled",
        ],
        steps=(
            "1. Paste the prompt and provide the item number when asked.\n"
            "2. Review the workbook with the engineering change board."
        ),
        expected="Workbook with BOM/SO/PO/inventory impact sheets and a summary.",
    ),

    # ===== Forecast to Plan =====
    Recipe(
        rid="forecast-vs-actuals",
        area="forecast-to-plan",
        title="Demand Forecast vs Actuals Variance",
        summary="Compares demand forecast lines to actual sales orders for the same period and items, computes forecast accuracy, and flags poor performers.",
        business_value=(
            "Surfaces which items and which planners are consistently over- or under-forecasting so demand planning can be "
            "improved where it matters most — and inventory dollars stop pooling on the wrong SKUs."
        ),
        process_tags=["forecast-to-plan/conduct-sales-and-operations-planning"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "For each item with a demand forecast in the previous 3 months (for the USMF demo tenant, use FY2017 — Jan-Mar 2017), "
            "compare forecasted quantity vs the sum of actual sales-order quantities for the same period. Compute the absolute "
            "forecast accuracy as 1 - |forecast - actual| / max(forecast, actual). Flag items with accuracy < 70%. Output an "
            "Excel workbook 'Forecast-accuracy-<YYYY-MM-DD>.xlsx' with: a 'Poor' sheet (accuracy < 70%, sorted ascending), an "
            "'All' sheet, and a 'By planner' summary. Do not modify any forecast lines."
        ),
        what="Quantifies forecast accuracy at the item level and routes poor-performing items to the right planner.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Demand planner role",
            "Cowork D365 ERP plugin enabled",
        ],
        steps=(
            "1. Paste the prompt.\n"
            "2. Review with the demand planning team and adjust forecast models on the worst items."
        ),
        expected="Workbook with poor/all/by-planner accuracy sheets.",
    ),

    # ===== Inventory to Deliver =====
    Recipe(
        rid="3d-warehouse-heatmap",
        area="inventory-to-deliver",
        title="3D Warehouse Inventory Heatmap (HTML)",
        summary="Generates a self-contained 3D HTML visualization of warehouse bins colored by fill percentage or inventory value, navigable in any browser.",
        business_value=(
            "Turns the warehouse on-hand snapshot into a spatial picture so ops can see at a glance where slow-movers are "
            "blocking prime pick locations and where capacity is genuinely full vs just disorganized."
        ),
        process_tags=["inventory-to-deliver/manage-warehouse-operations"],
        ootb=["PDF"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "Read on-hand inventory by warehouse location for a single warehouse (ask the user which one, default to the "
            "primary USMF warehouse e.g. 24 if unspecified). For each location, capture aisle, rack, shelf, bin, item count, "
            "on-hand quantity, and on-hand value. Produce a standalone HTML file 'Warehouse-3D-<warehouse>-<YYYY-MM-DD>.html' "
            "that renders a 3D grid (use three.js via CDN) where each bin is a colored cube — color by fill percentage (green "
            "= empty, red = at capacity) and label by item count on hover. Include orbit controls, a legend, and a header with "
            "the warehouse name and snapshot time. Save the HTML to the output folder."
        ),
        what="Renders an interactive 3D warehouse view in a single HTML file — opens in any browser, no D365 access needed by the viewer.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Warehouse manager role",
            "Cowork D365 ERP plugin enabled",
        ],
        steps=(
            "1. Paste the prompt and confirm the warehouse when asked.\n"
            "2. Open the HTML in your browser and orbit/pan to inspect bins.\n"
            "3. Share via Teams to the warehouse leads."
        ),
        expected="One standalone interactive 3D HTML file.",
    ),

    # ===== Project to Profit =====
    Recipe(
        rid="project-margin-health",
        area="project-to-profit",
        title="Project Margin Health Report",
        summary="Compares project budget to actuals by cost category, flags projects with margin erosion, and drafts emails to the project managers of red projects.",
        business_value=(
            "Catches project margin erosion mid-flight (instead of at close-out), so project managers can act on overruns "
            "while there is still time to negotiate a change order or replan."
        ),
        process_tags=["project-to-profit/analyze-project-performance"],
        ootb=["Excel", "Email"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "For every active project, compute: total budget, actuals to date by category (hours, expenses, items), and "
            "current expected margin vs the original quote. Flag projects with current margin < 80% of original margin as "
            "'Red'. Output an Excel workbook 'Project-margin-<YYYY-MM-DD>.xlsx' with a 'Red' sheet, an 'All' sheet, and a "
            "'By PM' summary. For each Red project, draft an email (do not send) to the assigned project manager naming the "
            "specific cost categories that have overrun and the dollar impact. (Tenant note: USMF demo has FY2017 project data — "
            "adjust 'active' filter if needed.)"
        ),
        what="Identifies projects with margin erosion and routes specific overrun information to the responsible PM.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Project manager role",
            "Cowork D365 ERP plugin enabled",
        ],
        steps=(
            "1. Paste the prompt.\n"
            "2. Review the workbook; release the email drafts after personalizing tone."
        ),
        expected="Workbook with red/all/by-PM project margin sheets and one email draft per Red project.",
    ),

    # ===== Prospect to Quote =====
    Recipe(
        rid="quote-conversion-funnel",
        area="prospect-to-quote",
        title="Quote Conversion Funnel Analysis (HTML)",
        summary="Analyzes won/lost/expired sales quotes by salesperson, product family, and reason; produces a funnel chart HTML and a workbook.",
        business_value=(
            "Highlights where deals are leaking from the quote pipeline (which salesperson, which product, which lost-reason) "
            "so sales coaching and product positioning effort can be targeted with evidence."
        ),
        process_tags=["prospect-to-quote/analyze-sales"],
        ootb=["Excel", "PDF"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "Read all sales quotes for the last fiscal year (for the USMF demo tenant use FY2017). For each quote: capture "
            "salesperson, customer, product family, quote total, status (Sent / Won / Lost / Expired), and lost-reason if "
            "available. Compute the conversion funnel: sent → won. Produce: (a) an Excel workbook 'Quote-funnel-<YYYY>.xlsx' "
            "with detail and pivoted summaries by salesperson and product family; and (b) a standalone HTML 'Quote-funnel-<YYYY>.html' "
            "with a horizontal funnel chart (inline SVG) and a small breakdown table beneath. Save both to the output folder."
        ),
        what="Surfaces quote-pipeline leakage with both a workbook for analysis and an HTML funnel for sales leadership review.",
        prerequisites=[
            "Dynamics 365 F&SCM access with the Sales manager role",
            "Cowork D365 ERP plugin enabled",
        ],
        steps=(
            "1. Paste the prompt.\n"
            "2. Review with the sales leadership team.\n"
            "3. Use the lost-reason breakdown to drive a coaching agenda."
        ),
        expected="One Excel workbook and one HTML funnel chart.",
    ),

    # ===== Service to Deliver =====
    Recipe(
        rid="field-service-daily-utilization",
        area="service-to-deliver",
        title="Field Service Resource Utilization Daily Email",
        summary="Drafts a morning email to service operations summarizing technician utilization for today and the coming week, including overbooked and underbooked resources.",
        business_value=(
            "Replaces a daily manual spreadsheet stitch with an automatic morning brief so dispatchers walk into standup "
            "already knowing who is overbooked, who has slack, and which jobs are at risk."
        ),
        process_tags=["service-to-deliver/manage-service-work"],
        ootb=["Email", "Communications"],
        plugin_actions=[("dynamics-365-erp", "data_find_entity_type"), ("dynamics-365-erp", "data_find_entities_sql")],
        mutates_data=False,
        prompt=(
            "For each field-service technician, read scheduled work orders for today and the next 7 days. Compute: scheduled "
            "hours per day, configured working hours per day, and utilization percent. Identify: (a) technicians with utilization "
            ">100% on any day (overbooked), (b) technicians with utilization <50% on any day (slack), (c) work orders without an "
            "assigned technician. Draft an email to the service operations manager with three sections matching (a)/(b)/(c). "
            "Save the draft; do not send. Also produce a Communications-ready summary suitable for a Teams channel post. "
            "This recipe is a strong Cowork scheduled-task candidate — schedule for 6am each weekday."
        ),
        what="Builds a daily dispatch-ready utilization brief covering overbookings, slack, and unassigned work.",
        prerequisites=[
            "Dynamics 365 Field Service or F&SCM Service module access",
            "Cowork D365 ERP plugin enabled",
        ],
        steps=(
            "1. Paste the prompt in Cowork.\n"
            "2. Review the email draft and Teams summary.\n"
            "3. (Optional) Schedule the task in Cowork to run at 6am weekdays."
        ),
        expected="One email draft and one Communications summary covering technician utilization for the coming week.",
    ),
]


def main() -> int:
    for r in RECIPES:
        write_recipe(r)
    print(f"\n{len(RECIPES)} recipes written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
