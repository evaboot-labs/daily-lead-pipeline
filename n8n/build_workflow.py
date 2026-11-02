"""Builds n8n/daily-lead-pipeline.json. Run: python3 n8n/build_workflow.py

Every day: find the newest run of your Evaboot recurring export, keep the leads that match your filters with a
safe email, save them as HubSpot contacts, let Claude write one email per lead from your brief, and add each
lead with its email to your lemlist campaign. Nothing is sent: you start the campaign in lemlist.
"""
import json
import uuid
from pathlib import Path

EVABOOT_MCP = "https://mcp.evaboot.com/mcp"
LEMLIST_MCP = "https://app.lemlist.com/mcp"
EVABOOT_CRED = {"httpBearerAuth": {"id": "", "name": "Evaboot MCP (Bearer)"}}
LEMLIST_CRED = {"httpBearerAuth": {"id": "", "name": "lemlist MCP (Bearer)"}}
ANTHROPIC_CRED = {"anthropicApi": {"id": "", "name": "Anthropic"}}
HUBSPOT_CRED = {"hubspotAppToken": {"id": "", "name": "HubSpot app token"}}
MODEL = "claude-sonnet-5-5"

nodes, connections = [], {}


def node(name, type_, version, params, pos, creds=None, **extra):
    n = {"parameters": params, "id": str(uuid.uuid4()), "name": name, "type": type_,
         "typeVersion": version, "position": pos, **extra}
    if creds:
        n["credentials"] = creds
    nodes.append(n)


def link(a, b, kind="main", out=0):
    connections.setdefault(a, {}).setdefault(kind, [])
    while len(connections[a][kind]) <= out:
        connections[a][kind].append([])
    connections[a][kind][out].append({"node": b, "type": kind, "index": 0})


def mcp_call(name, url, cred, tool, json_expr, pos):
    node(name, "@n8n/n8n-nodes-langchain.mcpClient", 1.1, {
        "endpointUrl": url, "authentication": "bearerAuth",
        "tool": {"__rl": True, "mode": "list", "value": tool, "cachedResultName": tool},
        "inputMode": "json", "jsonInput": json_expr, "options": {"timeout": 120000},
    }, pos, cred)


def code(name, js, pos, **extra):
    node(name, "n8n-nodes-base.code", 2, {"jsCode": js}, pos, **extra)


S = "$('Your settings').first().json"

PICK_JS = r"""
// The newest export whose name starts with the recurring export name: today's run.
const s = $('Your settings').first().json;
const list = $json.structuredContent?.result || [];
const run = list.find(e => String(e.search_name || '').startsWith(s.recurring_export_name));
if (!run) throw new Error(`No export named "${s.recurring_export_name}" yet.`);
if (run.status !== 'EXECUTED') throw new Error(`The newest run is ${run.status}, not finished yet.`);
const ageH = (Date.now() - new Date(run.search_date_created.replace(' ', 'T'))) / 36e5;
if (ageH > 24) return [];  // no new run today: stop quietly
return [{ json: { extraction_id: run.search_id, name: run.search_name } }];
"""

KEEP_JS = r"""
// Leads that match your filters with a safe email, with the facts Claude may use.
const num = v => { const n = parseFloat(String(v ?? '').replace(/,/g, '')); return isNaN(n) ? null : n; };
const words = s => String(s || '').split(/\s+/).join(' ').trim();
const all = $json.structuredContent?.result?.prospects || [];
const kept = all.filter(p => p['Matches Filters'] === 'YES' && p['Email Status'] === 'safe');
if (!kept.length) return [];
return kept.map(p => ({ json: {
  id: p['Email'], email: p['Email'], first_name: p['First Name'] || '', last_name: p['Last Name'] || '',
  title: String(p['Current Job'] || '').trim(), company: p['Company Name'] || '', company_domain: p['Company Domain'] || '',
  linkedin_url: p['Linkedin URL Public'] || '',
  time_in_role: [[num(p['Years in Position']), 'year'], [num(p['Months in Position']), 'month']]
    .filter(([n]) => n).map(([n, u]) => `${n} ${u}${n > 1 ? 's' : ''}`).join(' ') || 'under a month',
  new_position: String(p['Has New Position']).toLowerCase() === 'yes',
  headline: words(p['Profile Headline']), summary: words(p['Profile Summary']).slice(0, 600),
  job_description: words(p['Job Description']).slice(0, 400),
  company_description: words(p['Company Description']).slice(0, 400),
  company_headcount: num(p['Company Employee Exact Count']),
  company_growth_6m_pct: num(p['Company Employee Growth 6 Months (%)']),
  company_growth_1y_pct: num(p['Company Employee Growth 1 Year (%)']),
  company_growth_2y_pct: num(p['Company Employee Growth 2 Years (%)']),
  revenue_musd: [p['Company Revenue Min (Millions USD)'], p['Company Revenue Max (Millions USD)']].filter(Boolean).join(' to ') || null,
  sales_team: num(p['Sales Team Size']),
} }));
"""

LEADS_JS = r"""
// One lemlist lead per written email; leads Claude skipped are left out.
const leads = $('Leads to email').all().map(i => i.json);
const out = Object.fromEntries(($json.output?.emails || []).map(e => [e.id, e]));
const rows = leads.filter(l => out[l.id] && !out[l.id].skip && out[l.id].subject && out[l.id].body).map(l => ({
  email: l.email, firstName: l.first_name, lastName: l.last_name, companyName: l.company,
  companyDomain: l.company_domain, jobTitle: l.title, linkedinUrl: l.linkedin_url,
  customVariables: { aiSubject: out[l.id].subject, aiEmail: out[l.id].body },
}));
if (!rows.length) return [];
return [{ json: { leads: rows } }];
"""

WRITE_SYSTEM = """You write the first cold email to each lead in the JSON you are given, following the brief below. Use only the facts in the JSON and the brief: never invent a customer, a number or a result.
For each lead return {id, subject, body}, or {id, skip: true, reason} when nothing in the data fits the brief. Separate paragraphs with a blank line.

Brief:
"""

node("Every day", "n8n-nodes-base.scheduleTrigger", 1.2, {
    "rule": {"interval": [{"field": "days", "triggerAtHour": 18}]}}, [0, 0])
node("Your settings", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [
    {"id": str(uuid.uuid4()), "name": "recurring_export_name", "type": "string", "value": "VP Sales France SaaS"},
    {"id": str(uuid.uuid4()), "name": "lemlist_campaign_id", "type": "string", "value": "PASTE_YOUR_CAMPAIGN_ID"},
    {"id": str(uuid.uuid4()), "name": "lead_source", "type": "string", "value": "Evaboot recurring export"},
    {"id": str(uuid.uuid4()), "name": "brief", "type": "string",
     "value": "PASTE YOUR BRIEF (see BRIEF.md): what you sell, to whom, the proof you may use, the rules for each email."},
]}, "options": {}}, [220, 0])
mcp_call("Latest exports", EVABOOT_MCP, EVABOOT_CRED, "get_export_list", '={{ JSON.stringify({ limit: 25 }) }}', [440, 0])
code("Today's run", PICK_JS, [660, 0])
mcp_call("Get the leads", EVABOOT_MCP, EVABOOT_CRED, "get_export",
         "={{ JSON.stringify({ extraction_id: $json.extraction_id }) }}", [880, 0])
code("Leads to email", KEEP_JS, [1100, 0])
node("Save in HubSpot", "n8n-nodes-base.hubspot", 2.1, {
    "authentication": "appToken", "resource": "contact", "operation": "upsert", "email": "={{ $json.email }}",
    "additionalFields": {
        "firstName": "={{ $json.first_name }}", "lastName": "={{ $json.last_name }}",
        "companyName": "={{ $json.company }}", "jobTitle": "={{ $json.title }}",
        "customPropertiesUi": {"customPropertiesValues": [
            {"property": "hs_linkedin_url", "value": "={{ $json.linkedin_url }}"},
            {"property": "lead_source", "value": "={{ " + S + ".lead_source }}"},
        ]},
    },
    "options": {},
}, [1320, -120], HUBSPOT_CRED)
node("All leads", "n8n-nodes-base.aggregate", 1, {
    "aggregate": "aggregateAllItemData", "destinationFieldName": "leads", "options": {}}, [1320, 120])
node("Write the emails", "@n8n/n8n-nodes-langchain.agent", 2.2, {
    "promptType": "define", "text": "={{ JSON.stringify($json.leads) }}", "hasOutputParser": True,
    "options": {"systemMessage": "=" + WRITE_SYSTEM + "{{ " + S + ".brief }}", "maxIterations": 3},
}, [1540, 120], retryOnFail=True, maxTries=3, waitBetweenTries=2000)
node("Claude", "@n8n/n8n-nodes-langchain.lmChatAnthropic", 1.3, {
    "model": {"__rl": True, "mode": "list", "value": MODEL, "cachedResultName": MODEL},
    "options": {"maxTokensToSample": 12000},
}, [1500, 340], ANTHROPIC_CRED)
node("Emails", "@n8n/n8n-nodes-langchain.outputParserStructured", 1.3, {
    "schemaType": "manual",
    "inputSchema": json.dumps({"type": "object", "required": ["emails"], "properties": {"emails": {
        "type": "array", "items": {"type": "object", "required": ["id"], "properties": {
            "id": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"},
            "skip": {"type": "boolean"}, "reason": {"type": "string"}}}}}}, indent=2),
}, [1660, 340])
code("lemlist leads", LEADS_JS, [1760, 120])
mcp_call("Add to lemlist", LEMLIST_MCP, LEMLIST_CRED, "add_leads_to_campaign",
         "={{ JSON.stringify({ campaignId: " + S + ".lemlist_campaign_id, deduplicate: true, leads: $json.leads }) }}",
         [1980, 120])

for a, b in [("Every day", "Your settings"), ("Your settings", "Latest exports"), ("Latest exports", "Today's run"),
             ("Today's run", "Get the leads"), ("Get the leads", "Leads to email"),
             ("Leads to email", "Save in HubSpot"), ("Leads to email", "All leads"),
             ("All leads", "Write the emails"), ("Write the emails", "lemlist leads"),
             ("lemlist leads", "Add to lemlist")]:
    link(a, b)
link("Claude", "Write the emails", "ai_languageModel")
link("Emails", "Write the emails", "ai_outputParser")

workflow = {"name": "Daily lead pipeline (Evaboot + HubSpot + Claude + lemlist)", "nodes": nodes,
            "connections": connections, "settings": {"executionOrder": "v1"}, "pinData": {}}
out = Path(__file__).with_name("daily-lead-pipeline.json")
out.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + "\n")
print(out, len(nodes), "nodes")
