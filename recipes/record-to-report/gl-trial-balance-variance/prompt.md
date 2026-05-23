Using the Dynamics 365 ERP plugin, query the trial balance for the current period AND the prior period for the same chart of accounts. For each posting account: compute the variance amount and the variance percent. Mark any account where |variance| ≥ $10,000 OR |variance %| ≥ 10% as 'material'.

Use the Excel skill to produce a workbook 'TB-variance-<YYYY-MM-DD>.xlsx' with two sheets: 'Material' (variances that crossed the threshold, sorted by absolute variance amount descending) and 'All' (every account).

Then draft an email to the controller summarizing the count of material variances and the top 5 by amount. Do not modify any data.
