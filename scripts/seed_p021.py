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
    process_tags: List[str]
    ootb: List[str]
    plugin_actions: List[Tuple[str, str]]  # (plugin, action)
    mutates_data: bool
    prompt: str
    what: str
    prerequisites: List[str]
    steps: str
    expected: str
    custom: List[str] = field(default_factory=list)


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
    if folder.exists():
        shutil.rmtree(folder)
    (folder / "screenshots").mkdir(parents=True, exist_ok=True)

    recipe_yaml = (
        f"id: {r.rid}\n"
        f"title: {r.title}\n"
        f"summary: >-\n"
        f"  {r.summary}\n"
        f"plugin: dynamics-365-erp\n"
        f"process_tags:\n"
        + "".join(f"  - {t}\n" for t in r.process_tags)
        + f"recipe_type: prompt\n"
        f"difficulty: intermediate\n"
        f"mutates_data: {str(r.mutates_data).lower()}\n"
        f"min_plugin_version: \"1.0.0\"\n"
        f"generated_by: copilot\n"
        f"reviewed_by: seangalliher\n"
        f"status: draft\n"
        f"deprecated: false\n"
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
        "\n> ⚠ **Draft recipe — not yet verified.** The prompt, OOTB skill list, and plugin "
        "actions named below are starter content. No one has run this against a live Cowork tenant "
        "with the Dynamics 365 ERP plugin yet. Plugin action ids may not match Microsoft's actual "
        "published surface. Validate before relying on it.\n"
    )
    readme = (
        f"# {r.title}\n\n"
        f"{r.summary}\n"
        f"{draft_warning}"
        f"{sandbox_warning}\n"
        f"## What it does\n\n{r.what}\n\n"
        f"## Prerequisites\n\n" + "\n".join(f"- {p}" for p in r.prerequisites) + "\n\n"
        f"## Step-by-step\n\n{r.steps}\n\n"
        f"## Expected output\n\n{r.expected}\n\n"
        f"![Placeholder screenshot for {r.title}](screenshots/01-placeholder.svg \"Placeholder — replace with a real screenshot captured against your tenant.\")\n\n"
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
    (folder / "screenshots" / "01-placeholder.svg").write_text(svg, encoding="utf-8")
    print(f"wrote {r.area}/{r.rid}")


RECIPES: List[Recipe] = [
    # ===== Record to Report =====
    Recipe(
        rid="gl-trial-balance-variance",
        area="record-to-report",
        title="GL Trial Balance Variance Report",
        summary="Compares the current-period trial balance to the prior period and highlights GL accounts with material variances.",
        process_tags=["record-to-report/record-financial-transactions"],
        ootb=["Excel", "Email"],
        plugin_actions=[("dynamics-365-erp", "trial-balance-query")],
        mutates_data=False,
        prompt=(
            "Using the Dynamics 365 ERP plugin, query the trial balance for the current period AND the prior period for "
            "the same chart of accounts. For each posting account: compute the variance amount and the variance percent. "
            "Mark any account where |variance| ≥ $10,000 OR |variance %| ≥ 10% as 'material'.\n\n"
            "Use the Excel skill to produce a workbook 'TB-variance-<YYYY-MM-DD>.xlsx' with two sheets: 'Material' (variances "
            "that crossed the threshold, sorted by absolute variance amount descending) and 'All' (every account).\n\n"
            "Then draft an email to the controller summarizing the count of material variances and the top 5 by amount. "
            "Do not modify any data."
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
        process_tags=["record-to-report/record-financial-transactions"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "trial-balance-query")],
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
        process_tags=["record-to-report/close-financial-periods"],
        ootb=["Word", "Email", "Communications"],
        plugin_actions=[("dynamics-365-erp", "trial-balance-query")],
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
        process_tags=["record-to-report/close-financial-periods"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "trial-balance-query")],
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
        process_tags=["record-to-report/close-financial-periods"],
        ootb=["Excel", "Adaptive Cards"],
        plugin_actions=[("dynamics-365-erp", "trial-balance-query")],
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
        process_tags=["source-to-pay/manage-supplier-relationships"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "vendor-master-query")],
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
        process_tags=["source-to-pay/manage-accounts-payable"],
        ootb=["Excel", "Email"],
        plugin_actions=[("dynamics-365-erp", "vendor-invoice-query")],
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
        process_tags=["source-to-pay/manage-accounts-payable"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "payment-proposal-query")],
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
        process_tags=["order-to-cash/manage-credit-and-collections"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "ar-aging-query")],
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
        process_tags=["order-to-cash/manage-credit-and-collections"],
        ootb=["Email", "Communications"],
        plugin_actions=[("dynamics-365-erp", "ar-aging-query")],
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
        process_tags=["order-to-cash/manage-sales-orders"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "sales-order-query")],
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
        process_tags=["order-to-cash/analyze-sales-performance"],
        ootb=["PDF"],
        plugin_actions=[("dynamics-365-erp", "sales-order-query")],
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
        process_tags=["plan-to-produce/develop-production-strategies"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "bom-query")],
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
        process_tags=["plan-to-produce/plan-production-operations"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "bom-query")],
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
        process_tags=["plan-to-produce/run-production-operations"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "bom-query")],
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
        process_tags=["acquire-to-dispose/manage-active-assets"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "fixed-asset-query")],
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
        process_tags=["acquire-to-dispose/analyze-assets"],
        ootb=["Excel"],
        plugin_actions=[("dynamics-365-erp", "fixed-asset-query")],
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
]


def main() -> int:
    for r in RECIPES:
        write_recipe(r)
    print(f"\n{len(RECIPES)} recipes written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
