# The daily task

The skill fills in the three settings and your brief, then you paste the whole block below into a scheduled task: Claude desktop app (*Scheduled > New task*) or a Claude Code routine (`/schedule`). It needs three connectors: Evaboot, HubSpot and lemlist.

```text
Run my daily lead pipeline.

Settings:
- Evaboot recurring export: VP Sales France SaaS
- lemlist campaign: VP Sales France SaaS
- HubSpot lead source: Evaboot recurring export

1. In Evaboot, call get_export_list and take the newest export whose name starts with the recurring export name. If its status is not EXECUTED, stop and tell me. If it was created more than 24 hours ago, stop and tell me there is no new run today.
2. Call get_export on it to get all its leads. Keep only leads where Matches Filters is YES and Email Status is safe. Count the others and why they were skipped.
3. In HubSpot, create or update a contact for each kept lead, matched on email: email, first name, last name, company name, job title, LinkedIn URL, and the property "Lead source" set to the HubSpot lead source above.
4. For each kept lead, write a cold email that follows my brief below. Use only facts from that lead's Evaboot data: never invent a customer, a number or a result. If nothing in the data fits the brief, skip the lead and say why.
5. In lemlist, call get_campaigns to find the campaign by name, then add_leads_to_campaign with deduplicate true. For each lead: email, firstName, lastName, companyName, companyDomain, jobTitle, linkedinUrl, and customVariables aiSubject (the subject) and aiEmail (the body). Never start the campaign.
6. Give me a summary: leads in the run, leads kept, contacts created or updated in HubSpot, leads added to lemlist, leads skipped and why, and 3 sample emails.

My brief:
[paste your brief here]
```

## Why the task works this way

- **It never sends.** It only adds leads to a lemlist campaign. You read the first batch, then start the campaign yourself.
- **Running it twice is safe.** HubSpot matches contacts on email, and lemlist skips leads already in the campaign.
- **Only Claude pushes leads.** Keep the recurring export without a destination in Evaboot, or each lead arrives twice, once without its email.
