---
name: daily-lead-pipeline
description: Set up a daily lead pipeline from LinkedIn Sales Navigator to a cold email campaign - build a Sales Navigator search from a sentence, turn it into a daily Evaboot recurring export, create a lemlist campaign whose first email is written by AI, write the email brief, run the pipeline once by hand (HubSpot contacts, one email per lead, leads added to lemlist), then schedule it as a daily Claude task. Use when the user asks to automate prospecting every day, send new Sales Navigator leads to their CRM and outreach tool automatically, or set up intent-based automated outreach (IBAO).
---

# Daily lead pipeline

This skill runs inside a clone of https://github.com/evaboot-labs/daily-lead-pipeline: it uses the repo's `TASK.md`, `BRIEF.md` and `docs/`. If `TASK.md` is not in the working directory, clone the repo and work from there.

The pipeline is one scheduled Claude task that uses three connectors: Evaboot (`https://mcp.evaboot.com/mcp`), HubSpot and lemlist (`https://app.lemlist.com/mcp`). HubSpot and lemlist are examples: any CRM and any outreach tool with an MCP server works the same way. You set it up with the user here, run it once by hand, then the user schedules it.

## Rules

- Confirm with the user before every call that spends credits or writes somewhere: `export_sn_search_or_list`, `create_recurring_export`, the lemlist campaign, the HubSpot property, and the first run. Show the count and the cost (1 Evaboot credit per lead), then wait for a yes.
- Never start a lemlist campaign. The user reads the first batch, then starts it.
- Write each email only from that lead's Evaboot data and `BRIEF.md`. Never invent a customer, a number or a result.
- Never ask for or paste an API key. The user writes them into `.env`, or connects each tool in Claude's settings.
- Print every Sales Navigator URL as a Markdown link with the URL in angle brackets: `[Open in Sales Navigator](<url>)`.

## Step 0: check the connectors

1. Evaboot: call `get_daily_export_quota`. If the tool is missing, follow `docs/connect-your-agent.md`. If `has_valid_salesnav` is false, ask the user to sign in to Evaboot in Chrome, open any Sales Navigator search, click **Export with Evaboot**, then call it again.
2. lemlist: call `get_team_info`. If the tool is missing, follow `docs/connect-your-agent.md`.
3. HubSpot: look for the HubSpot connector tools. If they are missing, ask the user to connect HubSpot in Claude (*Settings > Connectors*), then restart.

## Step 1: the search

Ask who they want to reach and how many leads a day they can handle.

1. Call `build_sn_search_from_prompt` with **people only** (job titles, seniority, geography, a signal such as "changed jobs in the past 90 days") and `max_results`. Never put an industry or a company size in this request: that starts a company-first search, whose temporary company lists a recurring export rejects.
2. Poll `get_search_build`. Add the industry and company size filters to the people-search URL yourself (`INDUSTRY`, `COMPANY_HEADCOUNT`), then show it as a link and ask the user to check the people in Sales Navigator.

## Step 2: the daily recurring export

1. On a yes, call `export_sn_search_or_list` with the URL, a short `name` (it names the recurring export too) and `max_results` (start with 10 to 25). Poll `get_export` until `EXECUTED`. This first export is the batch for the first run.
2. Call `create_recurring_export` with its `extraction_id` and `frequency: "daily"`. Do not attach a destination: Claude pushes the leads. Tell the user `next_execution_at`: the first automatic run is one day later, and each run brings only people new to the search.

## Step 3: the lemlist campaign

Follow `docs/lemlist.md` with the user. With the lemlist connector, `create_campaign_with_sequence` with subject `{{aiSubject}}` and body `{{aiEmail}}` makes it in one call. The campaign stays a draft until the user adds a mailbox and starts it.

## Step 4: the brief

Read `BRIEF.md`. If it says `Status: EXAMPLE`, ask what they sell, to whom, what proof they may use, and what they ask for. Rewrite the brief and set `Status: yours`.

## Step 5: HubSpot

Follow `docs/hubspot.md`: the contacts get a "Lead source" property. Create it if it does not exist, on a yes.

## Step 6: the first run, by hand

Fill the settings of `TASK.md` with the names from steps 2 and 3, and the brief from step 4. Then run its six steps now, on the export from step 2. Show the summary and 3 sample emails, and ask the user to read the leads in lemlist and the contacts in HubSpot. Fix the brief until the emails are right.

## Step 7: schedule it

Give the user the filled task and the time to run it: a few hours after `next_execution_at`. They paste it in the Claude desktop app (*Scheduled > New task*, daily), or you create a Claude Code routine with `/schedule`. Then they add a sending mailbox in lemlist and start the campaign when the first batch looks right.

To change the search later, edit the saved search in Sales Navigator. To pause, call `update_recurring_export` with `paused: true`. To stop, `delete_recurring_export`, and delete the scheduled task.
