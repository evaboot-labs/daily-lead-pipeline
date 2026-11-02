# The lemlist campaign

lemlist is our example. Any outreach tool works the same way if its MCP server can add a lead with custom variables.

## Connect lemlist to your AI Agent

- **Claude (web and desktop):** *Settings > Connectors > Browse connectors*, search **lemlist**, click **Connect** and authorize your team.
- **Claude Code:** the repo's `.mcp.json` connects `https://app.lemlist.com/mcp` with `LEMLIST_API_KEY` from `.env`. Create the key in lemlist: *Settings > Integrations > API & Webhooks > Generate key*.
- **Codex, Cursor:** add the server by hand, as in [connect-your-agent.md](connect-your-agent.md).

## Create the campaign

Ask your AI Agent:

```text
In lemlist, create a campaign named "VP Sales France SaaS". Its first email has the subject {{aiSubject}} and the body {{aiEmail}}.
```

Or create it by hand: a new campaign, step 1 an email with `{{aiSubject}}` as the subject and `{{aiEmail}}` as the whole body. Both are custom variables: the daily task fills them for each lead. The lemlist editor lists them as `Contact > aiSubject` and `Contact > aiEmail` once a lead with them is in your team, so asking your AI Agent is the easier path.

Then add your follow-up steps as normal lemlist templates.

## Before you start the campaign

1. Connect a sending mailbox in lemlist and warm it up.
2. Read the first batch: open a few leads and check the email preview.
3. Start the campaign. From then on, each lead the daily task adds gets its own email.

The daily task never starts a campaign and never sends an email.

Back to the [README](../README.md).
