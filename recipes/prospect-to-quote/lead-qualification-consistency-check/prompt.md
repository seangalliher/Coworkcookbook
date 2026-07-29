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
