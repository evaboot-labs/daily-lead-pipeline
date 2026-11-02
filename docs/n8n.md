# Run it in n8n

[`n8n/daily-lead-pipeline.json`](../n8n/daily-lead-pipeline.json) is the same pipeline for n8n, when you prefer n8n to a scheduled Claude task. It runs every day at 18:00.

## What runs

1. **Your settings** (Set): the recurring export name, the lemlist campaign id, the lead source and your brief.
2. **Latest exports** and **Today's run** (Evaboot MCP + Code): the newest export with that name. It stops if the run is not finished, or quietly if there is no run in the past 24 hours.
3. **Get the leads** and **Leads to email** (Evaboot MCP + Code): keeps leads where Matches Filters is YES and the email is safe.
4. **Save in HubSpot** (HubSpot node): creates or updates each contact, matched on email, with the Lead source.
5. **Write the emails** (AI Agent with Claude): one subject and body per lead from your brief, or a skip with a reason.
6. **Add to lemlist** (lemlist MCP): adds each lead with `aiSubject` and `aiEmail`, and skips leads already in the campaign.

## Set it up

1. **Create the recurring export** in Evaboot and the **lemlist campaign** ([lemlist.md](lemlist.md)). Copy the campaign id (`cam_...`) from its URL.
2. **Create the HubSpot property** "Lead source" ([hubspot.md](hubspot.md)).
3. **Import** the JSON: *Workflows > Import from file*.
4. **Add four credentials:**
   - **Bearer Auth** named `Evaboot MCP (Bearer)`: your key from [dash.evaboot.com/dash/api/](https://dash.evaboot.com/dash/api/). Select it on **Latest exports** and **Get the leads**.
   - **Bearer Auth** named `lemlist MCP (Bearer)`: your lemlist API key. Select it on **Add to lemlist**.
   - **Anthropic** on the **Claude** node.
   - **HubSpot App Token** (a HubSpot private app with the contacts read and write scopes) on **Save in HubSpot**.
5. **Fill in Your settings**, with your brief from [BRIEF.md](../BRIEF.md).
6. **Test:** click *Execute workflow* the day after the recurring export was created, read the leads in lemlist, then turn the workflow on.

## Good to know

- Running it twice the same day is safe: HubSpot matches on email and lemlist skips leads already in the campaign.
- Nothing is sent. You start the campaign in lemlist.

Back to the [README](../README.md).
