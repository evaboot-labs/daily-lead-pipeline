# Agent instructions

This repo sets up a daily lead pipeline. Every day, an Evaboot recurring export brings the people new to a Sales Navigator search, with verified emails. A scheduled Claude task saves them in the CRM (HubSpot here), writes one cold email per lead from their real data, and adds each lead with its email to an outreach campaign (lemlist here). It never sends: the user starts the campaign.

1. Follow the skill in `skills/daily-lead-pipeline/SKILL.md` step by step.
2. The daily task is `TASK.md`. You fill in its settings and the brief, run it once with the user, then they schedule it.
3. The email brief is `BRIEF.md`. If it says `Status: EXAMPLE`, ask the user for their offer and rewrite it.
4. If a connector is missing, follow `docs/connect-your-agent.md`. For the campaign, `docs/lemlist.md`. For the CRM, `docs/hubspot.md`.
5. If the user wants n8n instead of a Claude task, follow `docs/n8n.md` with them one step at a time.

Confirm with the user before every call that spends credits (1 Evaboot credit per lead), saves, sends or changes anything. Never start a campaign and never send an email. Never ask for or handle another tool's API key: the user writes keys into `.env` or connects each tool in Claude's settings. Never commit `.env` or `data/`: they hold real people's data and secrets.
