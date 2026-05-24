Using the Dynamics 365 ERP plugin, query the trial balance for the most recent posted period AND the prior period for the same chart of accounts in legal entity USMF. For each posting account: compute the variance amount and the variance percent. Mark any account where |variance| >= $10,000 OR |variance %| >= 10% as 'material'.

Use the Excel skill to produce a workbook 'TB-variance-<YYYY-MM>.xlsx' with two sheets: 'Material' (variances that crossed the threshold, sorted by absolute variance amount descending) and 'All' (every account).

Then draft an email to the controller summarizing the count of material variances and the top 5 by amount. Do not modify any data.

(Tenant note: the USMF demo tenant's posted GL activity is mostly FY2017 — if you want guaranteed data, ask Cowork to use March 2017 vs February 2017 explicitly. Cowork will derive the comparison from posted ledger journal lines if no trial-balance snapshot exists.)
