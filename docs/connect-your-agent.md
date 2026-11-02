# Connect your AI Agent

The pipeline needs three MCP servers: Evaboot, your CRM (HubSpot here) and your outreach tool (lemlist here).

## 1. Accounts

- An [Evaboot account](https://dash.evaboot.com/accounts/signup/?last_click_origin=daily-lead-pipeline-repo) with credits, and a Sales Navigator seat connected to it.
- A HubSpot portal and a lemlist team, or the CRM and outreach tool you use instead.

## 2. Get the repo

```bash
git clone https://github.com/evaboot-labs/daily-lead-pipeline
cd daily-lead-pipeline
cp .env.example .env
```

## 3. Connect the MCP servers

**Claude (web and desktop app)**, where the daily task runs:

1. *Settings > Connectors > Add custom connector*: name `Evaboot`, URL `https://mcp.evaboot.com/mcp`. Sign in to Evaboot and approve.
2. *Browse connectors*: search **HubSpot**, click **Connect**, sign in.
3. *Browse connectors*: search **lemlist**, click **Connect**, authorize your team.

**Claude Code:** sign in with the same Claude account and the connectors above are there. Or use the repo's `.mcp.json`: write `EVABOOT_API_KEY` ([dash.evaboot.com/dash/api/](https://dash.evaboot.com/dash/api/)) and `LEMLIST_API_KEY` (lemlist: *Settings > Integrations > API & Webhooks*) into `.env`, then start Claude Code from this folder.

**Codex, Cursor:** add `https://mcp.evaboot.com/mcp` and `https://app.lemlist.com/mcp` as HTTP MCP servers with the header `Authorization: Bearer <key>`, and the HubSpot MCP server your client supports.

## 4. Check

Ask your AI Agent: "Check my Evaboot quota and whether my Sales Navigator is connected, then show my lemlist team." Both answers mean you are ready.

Back to the [README](../README.md).
