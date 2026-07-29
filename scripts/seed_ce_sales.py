"""
seed_ce_sales.py — test batch of 10 Dynamics 365 Sales recipes for Copilot Cowork.

Sibling of seed_p021.py (the ERP manifest). Differences that matter:

  * plugin: dynamics-365-sales, backed by the Dataverse MCP server
  * plugin actions are the REAL Dataverse tool ids (search / describe / read_query),
    not the F&SCM data_* / form_* / api_* tools
  * prompts are TENANT-GENERIC: no environment name, no company name, no legal
    entity, no hardcoded data era. Scope is caller-anchored ("owned by me"),
    schema is discovered at runtime, and the date window is discovered from the
    data rather than asserted.

Every recipe ships status: draft. None has been run against a live Cowork tenant.

Each recipe spec produces:
  recipes/prospect-to-quote/<rid>/recipe.yaml
  recipes/prospect-to-quote/<rid>/prompt.md
  recipes/prospect-to-quote/<rid>/README.md
  recipes/prospect-to-quote/<rid>/screenshots/01-placeholder.svg

Re-runnable: regenerates the four files above so this manifest stays the source
of truth. Real captured screenshots are preserved.

Run: python scripts/seed_ce_sales.py
"""
from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

REPO = Path(__file__).resolve().parents[1]
TODAY = "2026-07-28"
AREA = "prospect-to-quote"
PLUGIN = "dynamics-365-sales"

# The Dataverse MCP read trio. These are the real, current tool names.
# NOTE: describe_table / list_tables / fetch were removed and folded into
# `describe`; the old data-search `search` was renamed `search_data` and the
# current `search` searches metadata. Do not use the pre-rename names.
READ_TOOLS: List[Tuple[str, str]] = [
    (PLUGIN, "search"),
    (PLUGIN, "describe"),
    (PLUGIN, "read_query"),
]

PREREQS = [
    "A Dynamics 365 Sales licence and access to a Dynamics 365 Sales environment",
    "The Dynamics 365 Sales plugin enabled in your Cowork session (+ > Customize > Dynamics 365 Sales)",
    "The plugin bound to the environment you want to analyze (gear icon on the plugin tile)",
]


@dataclass
class Recipe:
    rid: str
    title: str
    summary: str
    business_value: str
    process_tags: List[str]
    ootb: List[str]
    prompt: str
    what: str
    steps: str
    expected: str
    plugin_actions: List[Tuple[str, str]] = field(default_factory=lambda: list(READ_TOOLS))
    mutates_data: bool = False
    difficulty: str = "intermediate"


def yaml_list(items: List[str], indent: str = "    ") -> str:
    if not items:
        return " []"
    return "\n" + "\n".join(f"{indent}- {x}" for x in items)


def plugin_yaml(items: List[Tuple[str, str]], indent: str = "    ") -> str:
    if not items:
        return " []"
    return "\n" + "\n".join(f"{indent}- plugin: {p}\n{indent}  action: {a}" for p, a in items)


def one_line(s: str) -> str:
    """Collapse to a single line for a YAML folded scalar."""
    return " ".join(s.split())


def write_recipe(r: Recipe) -> None:
    folder = REPO / "recipes" / AREA / r.rid
    for relpath in ("recipe.yaml", "prompt.md", "README.md", "screenshots/01-placeholder.svg"):
        p = folder / relpath
        if p.exists():
            p.unlink()
    (folder / "screenshots").mkdir(parents=True, exist_ok=True)

    recipe_yaml = (
        f"id: {r.rid}\n"
        f"title: {r.title}\n"
        f"summary: >-\n"
        f"  {one_line(r.summary)}\n"
        f"business_value: >-\n"
        f"  {one_line(r.business_value)}\n"
        f"plugin: {PLUGIN}\n"
        f"process_tags:\n"
        + "".join(f"  - {t}\n" for t in r.process_tags)
        + f"recipe_type: prompt\n"
        f"difficulty: {r.difficulty}\n"
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
        f"  custom: []\n"
        f"prerequisites:\n"
        + "".join(f"  - {p}\n" for p in PREREQS)
        + f"youtube: []\n"
        f"authors:\n"
        f"  - github: seangalliher\n"
        f"    name: Sean Galliher\n"
        f"created: \"{TODAY}\"\n"
        f"version: \"1.0.0\"\n"
    )
    (folder / "recipe.yaml").write_text(recipe_yaml, encoding="utf-8")
    (folder / "prompt.md").write_text(textwrap.dedent(r.prompt).strip() + "\n", encoding="utf-8")

    draft_warning = (
        "\n> \u26a0 **Draft recipe \u2014 not yet verified.** No one has run this against a live Cowork "
        "tenant, and the Dataverse table and column names it relies on are taken from Microsoft "
        "documentation rather than confirmed against a live environment. The prompt tells Cowork to "
        "confirm the schema at runtime before querying, so a mismatch should surface as a correction "
        "rather than a wrong answer \u2014 but validate before relying on it.\n"
    )
    sandbox_warning = ""
    if r.mutates_data:
        sandbox_warning = (
            "\n> \u26a0 **This recipe modifies Dynamics 365 data.** Run it against a sandbox "
            "environment first and review the Cowork checkpoint before approving any write.\n"
        )

    readme = (
        f"# {r.title}\n\n"
        f"{one_line(r.summary)}\n"
        f"{draft_warning}"
        f"{sandbox_warning}\n"
        f"## Business value\n\n{one_line(r.business_value)}\n\n"
        f"## What it does\n\n{textwrap.dedent(r.what).strip()}\n\n"
        f"## Prerequisites\n\n" + "\n".join(f"- {p}" for p in PREREQS) + "\n\n"
        f"## Step-by-step\n\n{textwrap.dedent(r.steps).strip()}\n\n"
        f"## Expected output\n\n{textwrap.dedent(r.expected).strip()}\n\n"
        f"![Placeholder screenshot for {r.title}](screenshots/01-placeholder.svg "
        f"\"Placeholder \u2014 replace with a real screenshot captured against your environment.\")\n\n"
        f"## Portability\n\n"
        f"This recipe names no company, environment, or date range. It scopes to the records you own, "
        f"discovers the Dataverse schema at runtime, and derives its analysis window from the data it "
        f"finds \u2014 so it behaves the same in a trial environment as in a large production org.\n\n"
        f"## Skills used\n\n"
        f"OOTB: {', '.join(r.ootb) if r.ootb else '\u2014'}\n\n"
        f"Plugin actions: {', '.join(f'{p}/{a}' for p, a in r.plugin_actions)}\n\n"
        f"## License\n\nCC-BY-4.0 \u2014 see repo `LICENSE`.\n"
    )
    (folder / "README.md").write_text(readme, encoding="utf-8")

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" role="img" '
        f'aria-label="Placeholder screenshot for {r.title}">\n'
        f'  <rect width="800" height="450" fill="#f3f4f6"/>\n'
        f'  <rect x="20" y="20" width="760" height="40" fill="#1f2937"/>\n'
        f'  <text x="40" y="48" fill="#f9fafb" font-family="system-ui, sans-serif" font-size="18" '
        f'font-weight="600">{r.title[:80]}</text>\n'
        f'  <text x="400" y="240" text-anchor="middle" fill="#6b7280" '
        f'font-family="system-ui, sans-serif" font-size="16">'
        f'Placeholder \u2014 replace with a real screenshot once captured.</text>\n'
        f'</svg>\n'
    )
    (folder / "screenshots" / "01-placeholder.svg").write_text(svg, encoding="utf-8")
    print(f"wrote {AREA}/{r.rid}")


# ---------------------------------------------------------------------------
# The 10 recipes. Coverage: all six prospect-to-quote L2 areas.
# ---------------------------------------------------------------------------

RECIPES: List[Recipe] = [
    Recipe(
        rid="opportunity-slip-risk-analysis",
        title="Opportunity Slip-Risk Analysis",
        summary=(
            "Scores your open opportunities for the risk of slipping past their estimated close date "
            "and produces a prioritized workbook of the ones that need attention."
        ),
        business_value=(
            "Turns a subjective gut-feel forecast review into an evidence-based one. Sellers see which "
            "deals are drifting while there is still time to act, and managers stop discovering slipped "
            "deals at the end of the quarter."
        ),
        process_tags=["prospect-to-quote/pursue-opportunities/manage-opportunity-process"],
        ootb=["Excel"],
        prompt="""
        Using the Dynamics 365 Sales plugin, analyze my open opportunities and identify the ones at
        risk of slipping.

        First, use search and describe to confirm the opportunity table and the columns for estimated
        close date, estimated value, sales stage, owner, status, and last modified date. Do not guess
        column names.

        Then run a read_query to find the range of estimated close dates across my open opportunities
        and report that range before you filter on it.

        Scope to opportunities where I am the owner and the status is open. For each one, compute days
        since last modified and days until estimated close. Flag an opportunity as at risk when any of
        these hold:
        - the estimated close date is already in the past
        - there has been no modification in more than 30 days
        - the estimated close is within 30 days but the sales stage is still an early one

        Produce an Excel workbook 'opportunity-slip-risk.xlsx' with:
        - a Summary sheet showing counts and total estimated value by risk reason
        - an At Risk sheet sorted by estimated value descending, one row per opportunity, with the risk
          reasons that fired
        - a Notes sheet listing which tables and columns you used and the date range you found

        Do not modify any data. If I own no open opportunities, say so plainly and stop.
        """,
        what="""
        Reads your open opportunities through the Dataverse MCP tools, derives three objective
        slip-risk signals from the record data, and writes a prioritized exceptions workbook. All
        analysis is read-only.
        """,
        steps="""
        1. Open Cowork and confirm the **Dynamics 365 Sales** plugin is toggled on for your session.
        2. Check the gear icon on the plugin tile and confirm it is bound to the environment you want
           to analyze.
        3. Paste the prompt from `prompt.md` into a new task and send it.
        4. Review the Notes sheet first \u2014 it tells you which columns Cowork actually used, which is
           where any schema customization in your org will show up.
        5. Adjust the 30-day thresholds in the prompt to match your sales cycle and re-run.
        """,
        expected="""
        An Excel workbook in your Cowork output folder with three sheets. The Summary sheet gives a
        count and value total per risk reason; the At Risk sheet is the working list, highest value
        first. If you own no open opportunities, Cowork reports that instead of inventing rows.
        """,
    ),
    Recipe(
        rid="stalled-opportunity-reengagement",
        title="Stalled Opportunity Re-Engagement List",
        summary=(
            "Finds open opportunities with no recent activity and drafts a tailored re-engagement "
            "approach for each, so dormant deals get a deliberate next step."
        ),
        business_value=(
            "Recovers pipeline that would otherwise age out silently. Instead of a generic 'check in' "
            "sweep, each dormant deal gets a next step informed by its stage, value, and what happened "
            "last."
        ),
        process_tags=[
            "prospect-to-quote/pursue-opportunities/nurture-opportunities-and-finalize-the-sale"
        ],
        ootb=["Excel", "Communications"],
        prompt="""
        Using the Dynamics 365 Sales plugin, build a re-engagement list for my stalled opportunities.

        Use search and describe first to confirm the opportunity table, the activity or task tables
        related to it, and the columns for owner, status, estimated value, sales stage, and the most
        recent activity or modification date. Do not guess table or column names.

        Before filtering by date, run a read_query to find the actual range of activity dates available,
        and report it. Then treat an opportunity as stalled when it is open, I am the owner, and there
        has been no activity for longer than 45 days \u2014 or the closest equivalent your data supports,
        which you should state.

        For each stalled opportunity, summarize: the last thing that happened, how long it has been
        dormant, the estimated value, and the current stage. Then suggest one specific re-engagement
        angle grounded in that record \u2014 not a generic follow-up.

        Produce an Excel workbook 'stalled-opportunities.xlsx' with a Summary sheet (count and value by
        dormancy band) and a Detail sheet with one row per opportunity including your suggested angle.
        Also give me a short Teams-ready paragraph summarizing the top three by value.

        Do not modify any data, and do not send anything to anyone. If nothing is stalled, say so and
        stop.
        """,
        what="""
        Correlates opportunities with their activity history to find dormancy, then produces both a
        working list and a shareable summary. Read-only; drafts nothing into your CRM.
        """,
        steps="""
        1. Confirm the **Dynamics 365 Sales** plugin is on and bound to the right environment.
        2. Paste the prompt from `prompt.md` and send it.
        3. Check the reported activity-date range \u2014 if it looks short, your activity tracking may not
           be capturing what you expect.
        4. Tune the 45-day dormancy threshold to your sales cycle.
        """,
        expected="""
        A two-sheet workbook plus a short paragraph you can paste into Teams. Each detail row carries a
        concrete re-engagement angle drawn from that opportunity's own history.
        """,
    ),
    Recipe(
        rid="lead-response-time-audit",
        title="Lead Response Time Audit",
        summary=(
            "Measures how long leads wait before someone first works them, and highlights the leads "
            "that are still sitting untouched."
        ),
        business_value=(
            "Speed to first contact is one of the strongest predictors of lead conversion. This makes "
            "response lag visible and specific rather than anecdotal, and surfaces the untouched "
            "backlog before it goes cold."
        ),
        process_tags=[
            "prospect-to-quote/identify-and-qualify-leads/manage-lead-identification-process"
        ],
        ootb=["Excel"],
        prompt="""
        Using the Dynamics 365 Sales plugin, audit how quickly leads are being worked.

        Use search and describe to confirm the lead table and the columns for created date, owner,
        status, rating, and any first-contact or first-activity indicator available. Also check for a
        related activity table that records the first touch. Do not guess column names \u2014 report what
        you find and what you could not find.

        Run a read_query to establish the range of lead creation dates present, report it, and choose an
        analysis window inside that range \u2014 prefer the most recent three months of real data rather
        than the current calendar date. State the window you chose.

        Scope to leads owned by me or by my team. For each lead in the window, compute the elapsed time
        from creation to first recorded activity. Where no activity exists, compute age since creation
        and mark it untouched.

        Produce an Excel workbook 'lead-response-audit.xlsx' with:
        - a Summary sheet: median and 90th-percentile response time, plus a count of untouched leads
        - a Response Times sheet, slowest first
        - an Untouched sheet, oldest first
        - a Notes sheet naming the tables and columns used and the window analyzed

        Do not modify any data. If no leads exist in the window, report that and stop.
        """,
        what="""
        Joins leads to their first recorded activity to derive response latency, then separates the
        genuinely slow from the never-touched. Percentiles rather than averages, so a few outliers do
        not hide the typical experience.
        """,
        steps="""
        1. Confirm the **Dynamics 365 Sales** plugin is on and bound to the right environment.
        2. Paste the prompt from `prompt.md` and send it.
        3. Read the Notes sheet to see whether your org records a usable first-contact signal \u2014 if not,
           Cowork will say so, and that gap is itself a finding worth acting on.
        """,
        expected="""
        A four-sheet workbook. The Summary sheet is the headline: median response, 90th percentile, and
        untouched count. The Untouched sheet is usually the most immediately actionable.
        """,
    ),
    Recipe(
        rid="lead-qualification-consistency-check",
        title="Lead Qualification Consistency Check",
        summary=(
            "Checks whether leads are being qualified and disqualified consistently, and surfaces "
            "disqualifications with missing or vague reasons."
        ),
        business_value=(
            "Inconsistent qualification quietly corrupts every downstream conversion metric. This shows "
            "where the qualification bar is being applied unevenly and where disqualification reasons "
            "are too thin to learn from."
        ),
        process_tags=["prospect-to-quote/identify-and-qualify-leads/qualify-and-disqualify-leads"],
        ootb=["Excel"],
        prompt="""
        Using the Dynamics 365 Sales plugin, review how consistently leads are being qualified and
        disqualified.

        Use search and describe to confirm the lead table and the columns for status, status reason,
        qualification or disqualification reason, rating, score if present, owner, and the relevant
        dates. Report any of these your environment does not have.

        Run a read_query to find the date range of lead status changes available and report it, then
        analyze the most recent complete period inside that range. State which period you chose.

        Scope to leads owned by me or by my team. Then report:
        - the distribution of disqualification reasons, including how many have a blank or generic reason
        - qualified leads that are missing fields your environment marks as required for qualification
        - any owner whose qualification or disqualification rate is a clear outlier against the group
        - leads that sat in an open qualification state longer than the typical time to decision

        Produce an Excel workbook 'lead-qualification-review.xlsx' with a Summary sheet, one sheet per
        finding above, and a Notes sheet listing the tables and columns used.

        Do not modify any data. Do not requalify or disqualify anything. If there is not enough status
        history to draw conclusions, say so plainly and stop.
        """,
        what="""
        Profiles qualification behaviour rather than lead outcomes: reason-code hygiene, missing data at
        the qualification gate, per-owner outliers, and decision latency. Read-only.
        """,
        steps="""
        1. Confirm the **Dynamics 365 Sales** plugin is on and bound to the right environment.
        2. Paste the prompt from `prompt.md` and send it.
        3. Treat the outlier section as a conversation starter, not a verdict \u2014 territory mix explains
           many apparent outliers.
        """,
        expected="""
        A multi-sheet workbook. The disqualification-reason distribution is usually the most revealing
        sheet: a large 'blank or generic' bucket means your loss reasons cannot support any real
        analysis yet.
        """,
    ),
    Recipe(
        rid="account-360-briefing",
        title="Account 360 Briefing Pack",
        summary=(
            "Assembles everything Dynamics 365 Sales knows about a named account into a single briefing "
            "document you can read before a meeting."
        ),
        business_value=(
            "Replaces fifteen minutes of clicking through related-record tabs with a single document. "
            "Sellers walk into customer conversations with the full relationship history rather than "
            "whatever they could skim on the way in."
        ),
        process_tags=[
            "prospect-to-quote/manage-customer-relationships/maintain-contacts-and-accounts"
        ],
        ootb=["Word", "Excel"],
        prompt="""
        Using the Dynamics 365 Sales plugin, build a briefing pack on the account named below.

        ACCOUNT: <type the account name here>

        Use search and describe to confirm the account, contact, opportunity, and activity tables and
        the columns you need from each. Do not guess column or relationship names.

        Then assemble, for that account:
        - the account profile: industry, size, ownership, and any relationship or account-type fields
          your environment carries
        - the contact roster, with role or job title, and a note of who has been most recently active
        - open opportunities: stage, estimated value, estimated close date, owner
        - closed opportunities: won and lost, with values and any loss reasons recorded
        - the recent activity timeline, most recent first, summarized rather than listed verbatim
        - anything that looks like a risk or an opening \u2014 dormant contacts, aging open deals,
          repeated loss reasons

        Produce a Word document 'account-briefing.docx' organized under those headings, written to be
        read in about three minutes. Lead with a short 'what you need to know' summary.

        Do not modify any data. If the account name does not match a record, list the closest matches
        and stop rather than guessing which one I meant.
        """,
        what="""
        Traverses the account's related records and composes them into a readable narrative brief. The
        no-guessing rule on account matching prevents a briefing on the wrong customer.
        """,
        steps="""
        1. Confirm the **Dynamics 365 Sales** plugin is on and bound to the right environment.
        2. Edit the `ACCOUNT:` line in the prompt to name the account you want.
        3. Paste the prompt into a new task and send it.
        4. If Cowork returns a list of close matches instead of a brief, pick one and re-run with the
           exact name.
        """,
        expected="""
        A Word document of roughly two to three pages, opening with a short summary and then the
        detailed sections. Length scales with how much history the account actually has.
        """,
    ),
    Recipe(
        rid="customer-relationship-health-check",
        title="Customer Relationship Health Check",
        summary=(
            "Scores the accounts you own for relationship health using contact coverage, engagement "
            "recency, and open-pipeline signals."
        ),
        business_value=(
            "Single-threaded and quietly dormant accounts are the ones that churn or get lost to a "
            "competitor without warning. This finds them while there is still time to build coverage."
        ),
        process_tags=[
            "prospect-to-quote/estimate-and-quote-sales/nurture-trust-relationship-regularly-with-customer"
        ],
        ootb=["Excel"],
        prompt="""
        Using the Dynamics 365 Sales plugin, assess the relationship health of the accounts I own.

        Use search and describe to confirm the account, contact, opportunity, and activity tables and
        the columns for owner, contact role or title, activity dates, and opportunity status. Report
        anything you expected but could not find.

        Run a read_query to establish the range of activity dates available and report it before using
        it. Choose a recency baseline from within that range rather than from today's date, and say what
        you chose.

        Scope to accounts where I am the owner. Score each account on:
        - contact coverage: how many active contacts, and whether more than one has recent engagement
          (a single engaged contact is a single-threading risk)
        - engagement recency: how long since any activity on the account
        - pipeline presence: whether any opportunity is currently open
        - history: won and lost opportunity counts

        Combine those into a simple red / amber / green rating, and state the rule you used so I can
        challenge it.

        Produce an Excel workbook 'account-health.xlsx' with a Summary sheet (counts by rating), a
        Detail sheet with one row per account and its component scores, and a Single-Threaded sheet
        listing accounts that depend on one contact.

        Do not modify any data. If I own no accounts, say so and stop.
        """,
        what="""
        Builds a composite health rating from four objective signals and makes the scoring rule explicit
        so it can be argued with and tuned. The single-threading view is broken out separately because
        it is the most actionable.
        """,
        steps="""
        1. Confirm the **Dynamics 365 Sales** plugin is on and bound to the right environment.
        2. Paste the prompt from `prompt.md` and send it.
        3. Read the stated scoring rule before reading the ratings, and adjust the prompt if the
           weighting does not match how your business thinks about coverage.
        """,
        expected="""
        A three-sheet workbook with an explicit scoring rule stated in the output. The Single-Threaded
        sheet is typically the one that drives immediate action.
        """,
    ),
    Recipe(
        rid="quote-aging-and-follow-up",
        title="Quote Aging and Follow-Up Tracker",
        summary=(
            "Lists your outstanding quotes by age, flags the ones past their expiry or overdue for "
            "follow-up, and totals the value sitting unanswered."
        ),
        business_value=(
            "Quotes that expire without a decision are lost revenue nobody decided to give up. This "
            "puts a number on the unanswered pipeline and orders the follow-up queue by value at risk."
        ),
        process_tags=["prospect-to-quote/estimate-and-quote-sales/define-sales-quotations"],
        ootb=["Excel"],
        prompt="""
        Using the Dynamics 365 Sales plugin, track my outstanding quotes and their follow-up status.

        Use search and describe to confirm the quote table and the columns for status, effective or
        expiry dates, total amount, owner, related account, and related opportunity. Do not guess column
        names.

        Run a read_query to find the range of quote dates present and report it. Choose your analysis
        window from inside that range and state it.

        Scope to quotes I own that are still open or active. For each, report age in days, days until
        or past expiry, total value, the account, and the related opportunity stage if there is one.

        Group them into: expired, expiring within 14 days, and comfortably open. Within each group,
        order by value descending.

        Produce an Excel workbook 'quote-aging.xlsx' with a Summary sheet showing count and total value
        per group, a Detail sheet with one row per quote, and a Notes sheet listing the tables and
        columns used.

        Do not modify any data, and do not send anything to any customer. If I have no open quotes, say
        so and stop.
        """,
        what="""
        Ages the open quote book against whatever expiry semantics your environment records, and totals
        the value in each urgency band. Read-only.
        """,
        steps="""
        1. Confirm the **Dynamics 365 Sales** plugin is on and bound to the right environment.
        2. Paste the prompt from `prompt.md` and send it.
        3. If your org does not populate quote expiry dates, Cowork will report that \u2014 the aging bands
           then fall back to quote age alone, which is still useful.
        """,
        expected="""
        A three-sheet workbook. The Summary sheet answers 'how much value is sitting in expired or
        nearly-expired quotes', which is usually the number worth escalating.
        """,
    ),
    Recipe(
        rid="sales-target-attainment-tracker",
        title="Sales Target Attainment Tracker",
        summary=(
            "Compares actual closed-won performance against recorded sales targets and reports "
            "attainment, gap to target, and the pipeline coverage available to close it."
        ),
        business_value=(
            "Answers the two questions every sales review starts with \u2014 where are we against target, "
            "and is there enough pipeline to make up the gap \u2014 without anyone rebuilding the "
            "spreadsheet each time."
        ),
        process_tags=["prospect-to-quote/define-sales-strategy-and-policies/determine-sales-targets"],
        ootb=["Excel"],
        prompt="""
        Using the Dynamics 365 Sales plugin, report attainment against sales targets.

        Use search and describe to look for how targets are represented in this environment \u2014 that may
        be a goal or quota table, a target field on the user or team record, or something custom.
        Report exactly what you found. If this environment records no targets at all, say so plainly,
        report actual performance on its own, and stop rather than inventing a target.

        Confirm the opportunity table and the columns for status, actual or estimated value, close date,
        and owner. Run a read_query to establish the range of close dates available and report it, then
        pick the most recent complete period inside that range and state your choice.

        For that period, and scoped to me and my team, report:
        - closed-won value, against target where a target exists
        - attainment percentage and absolute gap
        - open pipeline value with a close date inside the period, and the resulting coverage ratio
        - a per-owner breakdown of the same figures

        Produce an Excel workbook 'target-attainment.xlsx' with a Summary sheet, a By Owner sheet, and a
        Notes sheet naming where the target figures came from.

        Do not modify any data.
        """,
        what="""
        Locates however this environment stores targets, then reports attainment and pipeline coverage
        against them. Degrades honestly to an actuals-only report when no target data exists.
        """,
        steps="""
        1. Confirm the **Dynamics 365 Sales** plugin is on and bound to the right environment.
        2. Paste the prompt from `prompt.md` and send it.
        3. Read the Notes sheet to confirm Cowork found the target source you expected \u2014 target storage
           varies more between orgs than almost any other Sales data.
        """,
        expected="""
        A three-sheet workbook covering attainment, gap, and coverage. If your environment has no target
        data, expect an actuals-and-pipeline report plus an explicit statement that no targets were
        found.
        """,
    ),
    Recipe(
        rid="win-loss-theme-analysis",
        title="Win/Loss Theme Analysis",
        summary=(
            "Analyzes closed opportunities to surface recurring themes in why deals are won and lost, "
            "grouped by reason, competitor, value band, and stage."
        ),
        business_value=(
            "Converts loss reasons from a field nobody reads into a ranked list of what is actually "
            "costing deals, which is what makes enablement and product feedback specific enough to act "
            "on."
        ),
        process_tags=[
            "prospect-to-quote/analyze-sales/provide-insights-into-sales-strategies-and-performance"
        ],
        ootb=["Excel", "PowerPoint"],
        prompt="""
        Using the Dynamics 365 Sales plugin, analyze themes across my team's won and lost opportunities.

        Use search and describe to confirm the opportunity table and the columns for status, status
        reason, win or loss reason, competitor if tracked, estimated and actual value, sales stage at
        close, close date, and owner. Report which of these your environment does not carry.

        Run a read_query to find the range of close dates available and report it. Choose an analysis
        window inside that range \u2014 prefer the most recent twelve months of real data \u2014 and state your
        choice.

        Scope to opportunities owned by me or my team. Then report:
        - win rate by count and by value
        - the ranked distribution of loss reasons, with total value attached to each
        - the ranked distribution of win reasons where recorded
        - competitor involvement where tracked, and the win rate against each
        - the stage at which lost deals typically died
        - whether outcomes differ by deal value band

        Read any free-text loss notes available and group them into recurring themes, quoting a short
        representative example for each. Say how many records supported each theme so I can judge
        whether it is signal.

        Produce an Excel workbook 'win-loss-analysis.xlsx' with a sheet per section above, and a short
        PowerPoint deck 'win-loss-summary.pptx' of no more than six slides covering the headline
        findings.

        Do not modify any data. If there are too few closed opportunities in the window to support
        conclusions, say so and report only what the data can carry.
        """,
        what="""
        Combines structured reason-code analysis with theme extraction from free-text notes, and
        attaches record counts to every theme so weak signals are visible as weak.
        """,
        steps="""
        1. Confirm the **Dynamics 365 Sales** plugin is on and bound to the right environment.
        2. Paste the prompt from `prompt.md` and send it.
        3. Check the record count behind each theme before quoting it anywhere \u2014 a theme supported by
           three deals is a hypothesis, not a finding.
        """,
        expected="""
        A multi-sheet workbook plus a short deck. Where loss reasons are poorly populated, expect Cowork
        to say so directly rather than over-reading a thin field.
        """,
        difficulty="advanced",
    ),
    Recipe(
        rid="pipeline-health-dashboard",
        title="Pipeline Health HTML Dashboard",
        summary=(
            "Produces a self-contained interactive HTML dashboard of pipeline by stage, value, age, and "
            "owner that opens in any browser without Dynamics 365 access."
        ),
        business_value=(
            "Lets sales leadership share a current pipeline picture with people who have no CRM licence "
            "\u2014 finance, the exec team, a board pack \u2014 without exporting spreadsheets or granting "
            "access."
        ),
        process_tags=["prospect-to-quote/analyze-sales/analyze-sales-data"],
        ootb=["PDF"],
        prompt="""
        Using the Dynamics 365 Sales plugin, build an interactive pipeline dashboard.

        Use search and describe to confirm the opportunity table and the columns for sales stage,
        estimated value, estimated close date, created date, owner, and status. Do not guess column
        names.

        Run a read_query to establish the range of estimated close dates present, report it, and base
        the dashboard's time axis on that real range rather than on today's date.

        Scope to open opportunities owned by me or my team. Then produce a single self-contained HTML
        file 'pipeline-health.html' \u2014 all CSS and JavaScript inline, no external dependencies, so it
        works offline \u2014 containing:
        - a header with total open pipeline value, opportunity count, average deal size, and the data
          range the dashboard covers
        - a funnel or bar chart of value by sales stage, drawn as inline SVG
        - a distribution of opportunities by age since creation
        - a breakdown by owner
        - a sortable detail table beneath the charts
        - a colour-coded indicator highlighting stages where value is concentrated or deals are aging

        Use a readable, professional visual style. Make sure the file renders correctly when opened
        directly from disk.

        Do not modify any data. If there are no open opportunities, say so and stop.
        """,
        what="""
        Builds a shareable single-file dashboard with inline SVG charts. No external CDN dependency, so
        it renders offline and can be emailed as an attachment.
        """,
        steps="""
        1. Confirm the **Dynamics 365 Sales** plugin is on and bound to the right environment.
        2. Paste the prompt from `prompt.md` and send it.
        3. Open the generated HTML file from the Cowork output folder to check it renders standalone
           before sharing it.
        """,
        expected="""
        A single HTML file that opens in any browser with no network access, showing pipeline value by
        stage, age distribution, owner breakdown, and a sortable detail table.
        """,
        difficulty="advanced",
    ),
]


def main() -> None:
    for r in RECIPES:
        write_recipe(r)
    print(f"\n{len(RECIPES)} Dynamics 365 Sales draft recipes written to recipes/{AREA}/")


if __name__ == "__main__":
    main()
