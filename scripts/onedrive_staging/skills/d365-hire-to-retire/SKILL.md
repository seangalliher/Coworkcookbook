---
name: d365-hire-to-retire
description: Dynamics 365 Finance & Supply Chain Management expert scoped to hire to retire. Use when user mentions "workforce", "HR", "headcount", "onboarding", "employee", or any USMF tenant question that lands in this domain.
cowork:
  category: analysis
  icon: PeopleTeam
---

# d365-hire-to-retire

## When to Use

Activate this skill whenever the user's request touches the **Hire to retire** end-to-end business process, covering every area in this domain. Specific trigger phrases include:

- workforce
- HR
- headcount
- onboarding
- employee

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
