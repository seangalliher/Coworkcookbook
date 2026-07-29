---
name: d365-recipe-planner
description: |
  Guides users through planning a Dynamics 365 "recipe" — a runnable Copilot
  Cowork prompt that automates a business process and produces a valuable
  deliverable, in the Cowork Cookbook format. Runs a short discovery interview
  (desired business outcome, the process to automate, which D365 app — Sales,
  Finance, or ERP/F&SCM, the deliverable format, data scope, read-only vs
  write-back, one-time vs recurring), then outputs a ready-to-run, copy-paste
  Cowork prompt plus a predicted cost tier (low / medium / high) with the
  reasoning. Use when the user asks to "plan a recipe", "design a Cowork
  recipe", "create a D365 recipe", "build a prompt to automate a Dynamics 365
  process", "help me automate a D365 task", "turn a business process into a
  Cowork prompt", or "add a recipe to the cookbook". Do NOT use to execute a
  recipe against live D365 data (run the generated prompt for that), to create
  or manage other skills (use the skills skill), or for non-D365 automation.
cowork:
  category: automation
  icon: Lightbulb
  pluginTitleId: T_c9f96fc9-77b7-dff4-1574-6a974159711e
  publishedAt: "2026-07-29T02:18:05Z"
---

# D365 Recipe Planner

## Overview

Turns a fuzzy "I want to automate something in Dynamics 365" into a concrete,
runnable **recipe**: a structured Cowork prompt the user (or anyone) can paste
into a new task to get repeatable business value. The deliverable is the prompt
itself — plus a predicted cost tier so the user knows what they are committing
to before they run it. This skill **plans and drafts**; it never runs the
recipe against live data.

A good recipe (matching the Cowork Cookbook format) has: a one-line business
outcome, the target D365 surface, the data it reads, an explicit deliverable
with numbered requirements, an output location, and guardrails.

## Quick Start

```
User: "Help me build a recipe to keep an eye on overdue customer invoices."
1. Discovery (core-AskUserQuestion): outcome? process = AR collections;
   app = Finance; deliverable = HTML dashboard; read-only; scope = USMF,
   open AR aging; frequency = weekly.
2. Surface map: Finance → dynamics-365-erp plugin, legal entity USMF.
3. Draft the copy-paste prompt (scope → data → lettered requirements →
   output folder → "do not modify any data").
4. Cost: 2 queries + HTML w/ charts + weekly = ~4 pts → MEDIUM (show drivers).
5. Deliver summary + fenced prompt + cost; offer to save the recipe .md.
```

## When to Use

- The user wants to design a new Cowork automation for Dynamics 365
- The user has a business process in mind but not a well-formed prompt
- The user wants to contribute a recipe to the Cookbook
- The user asks how much a proposed D365 task will cost to run

## When NOT to Use

- **Executing** the recipe / pulling live D365 data — that is the generated
  prompt's job; run it in a fresh task instead
- **Creating, editing, or scoring other skills** — use the `skills` skill
- **Non-D365 automation** (pure M365, web research, generic scripting) — use the
  matching built-in skill
- A one-off question the user just wants answered now — answer it directly; a
  recipe is for a *repeatable* process

## Core Instructions

### Phase 1 — Discovery interview (ask, don't assume)

Use `core-AskUserQuestion`. Ask in **at most two rounds** (max 4 questions per
round), batching related items, and **skip anything the user already told you**.
Offer concrete option chips, not open-ended blanks. Cover these seven points:

1. **Business outcome** — what value, and who benefits? (e.g. "ops leadership can
   see live sales-order health without D365 logins"). This becomes the recipe's
   business-value line.
2. **Process to automate** — the specific business process (e.g. enter sales
   orders, AP invoice approval, AR collections follow-up, inventory reorder).
3. **Which D365 app** — Sales, Finance, or ERP/Supply Chain. See the surface map
   in Phase 2; this decides which plugin and tools the prompt names.
4. **Deliverable format** — interactive HTML dashboard, Word doc, Excel workbook,
   PowerPoint deck, email/Teams summary, or a **data action** (create/update
   records).
5. **Read-only vs write-back** — does it only *read/report*, or does it *change
   D365 data*? Write-back is higher risk and cost and needs explicit guardrails.
6. **Data scope** — entities/tables, legal entity or environment, time period,
   and rough record volume (dozens / hundreds / thousands / "all").
7. **Frequency** — one-time, or recurring on a schedule (daily/weekly/monthly).

If the user gives a rich brief up front, confirm your understanding in one line
and skip straight to Phase 2.

### Phase 2 — Map to the D365 surface

Name the right plugin and tool family in the prompt based on the app answer:

| App the user picked | Product | Plugin to name in the prompt | Typical tool/actions | Scope anchor |
|---|---|---|---|---|
| **Sales** (CRM / Customer Engagement) | Dynamics 365 Sales | `dynamics-365-sales` | Dataverse: leads, opportunities, accounts, contacts, activities | Dataverse org/environment |
| **Finance** | D365 Finance & Supply Chain (F&O) | `dynamics-365-erp` | `data_find_entity_type`, `data_find_entities_sql`, `api_*` | Legal entity (e.g. `USMF`) |
| **ERP / Supply Chain** | D365 Finance & Supply Chain (F&O) | `dynamics-365-erp` | same as Finance | Legal entity (e.g. `USMF`) |

Note for the user: **Finance and ERP/Supply Chain are the same product**
(F&SCM / F&O) and share the `dynamics-365-erp` surface and a *legal entity*
scope; **Sales** is a separate product on Dataverse. Getting this right is what
makes the generated prompt actually runnable.

### Phase 3 — Draft the runnable prompt

Build a single copy-paste prompt with these ordered parts. Keep it tight and
imperative — this is what someone pastes into Cowork.

1. **Scope line** — plugin + environment/legal entity + the process.
2. **Data to pull** — entities and the time window/filter.
3. **Deliverable** — the exact artifact, named filename, with **lettered
   requirements** (a, b, c…) so the output is unambiguous.
4. **Output location** — "Save to the output folder" (lands in
   `Documents/Cowork/output/`).
5. **Guardrails** — for read-only: "Do not modify any data." For write-back:
   "Show me the records you will create/update and wait for my confirmation
   before writing anything."

**Read-only template (ERP/Finance example):**
> Using the Dynamics 365 ERP plugin against legal entity `USMF`, pull `<process>`
> data for `<time scope>`. Produce a `<deliverable>` named
> `<process>-<date>.<ext>` that includes: (a) `<requirement>`, (b)
> `<requirement>`, (c) `<requirement>`. Save the file to the output folder. Do
> not modify any data.

**Sales variant:** swap the first clause to "Using the Dynamics 365 Sales
plugin, pull `<opportunities/leads/accounts>` where `<filter>`…".

**Write-back variant:** replace the guardrail with a confirm-first instruction
and add "Do not post/submit; leave records in draft/pending status unless I say
otherwise."

### Phase 4 — Predict the cost tier

Score the plan against the rubric below. Add the points, map to a tier, and
**always show the user which factors drove the score** so the estimate is
explainable, not a black box.

| Factor | 0 pts | 1 pt | 2 pts |
|---|---|---|---|
| Data volume | < ~100 rows | ~100–2,000 | > 2,000 / "all" / multi-period |
| Distinct entities/queries | 1 | 2–3 | 4+ |
| Deliverable complexity | text / short table | one formatted doc, sheet, or HTML | multi-artifact, or deck/dashboard with charts |
| Image generation | none | 1–2 images | 3+ images |
| Research / web enrichment | none | light lookup | deep multi-source research |
| Write-back to D365 | read-only | — | creates/updates/posts records |
| Orchestration | single pass | — | multi-step subagents / loops |

Then add **+1 if recurring** (ongoing cost, not one-time).

**Tiers:** Low = 0–2 · Medium = 3–5 · High = 6+.

Low ≈ a quick read + simple summary. Medium ≈ the Cookbook sales-order dashboard
(a few queries + an HTML deliverable with charts). High ≈ large pulls, image
generation, deep research, write-back, or scheduled recurrence.

### Phase 5 — Deliver

Present, in this order:
1. **Recipe summary** — title, one-line business value, target app/plugin,
   read-only or write-back, frequency.
2. **The prompt** — in a fenced code block so it copies cleanly.
3. **Predicted cost** — the tier + the 2–4 factors that drove it, and one
   suggestion to move it down a tier if the user wants it cheaper (e.g. "drop the
   images", "narrow to one period").
4. Offer to **save it as a Cookbook-format recipe file** in `output/` (via
   `host-CreateArtifact`) — a `.md` with business value, prerequisites,
   step-by-step, expected output, skills/plugin actions used, and the prompt.

**Optional grounding:** if the user is unsure an entity/table exists, you may
verify with a read-only lookup (`dynamicsax-data_find_entity_type` for ERP, or
`dataverse-list_tables` for Sales) before finalizing the prompt. Never pull real
records here — this skill plans; it does not execute.

### Failure handling

- **User can't name a process or outcome** → offer 3–4 common recipes for their
  chosen app (e.g. AR aging dashboard, PO status report, inventory reorder list)
  and let them pick, rather than stalling.
- **App is unclear ("just Dynamics")** → ask the one disambiguating question
  (Sales vs Finance/ERP); do not guess the surface, since it changes the plugin.
- **A grounding lookup errors or the entity isn't found** → don't block. Draft
  the prompt with the entity marked `<validate this entity name in your tenant>`
  and note it in the summary, mirroring the Cookbook's "draft, not yet verified".
- **Request is actually a one-off, not a repeatable process** → say so and offer
  to just run it now instead of authoring a recipe.
- **Scope is huge/ambiguous ("all data, everything")** → default the prompt to a
  bounded window (most recent period) and tell the user how to widen it.

## Output

- Conversational recipe summary + a fenced copy-paste prompt + a cost tier with
  named drivers.
- On request, a saved recipe markdown file in `output/` matching the Cookbook
  format.
- Every factual claim about the D365 surface (plugin, entity, legal entity) is
  stated as a recommendation to validate, never as verified live data.

## Guardrails

- **Plan only — never execute the recipe here.** Do not pull, modify, post, or
  create D365 records while planning. Reading a single entity's *schema* to
  confirm it exists is the only live call allowed.
- **Write-back recipes always confirm first.** Any generated prompt that changes
  data must instruct Cowork to show the changes and wait for confirmation, and
  must not auto-post/submit.
- **Never fabricate the surface or any data.** Do not invent entity names,
  table names, legal entities, plugin actions, record counts, or example figures.
  If unsure whether something exists, say so and mark it "validate in your
  tenant" — mirror the Cookbook's "draft, not yet verified" honesty. Placeholders
  in the drafted prompt must be clearly marked (e.g. `<...>`), never plausible
  fakes.
- **Ask before assuming** on the seven discovery points; a wrong app choice or a
  silent write-back makes the recipe useless or unsafe.
- **Cost is an estimate.** Present the tier with its drivers and note it depends
  on real data volume; never state it as a guaranteed price.
