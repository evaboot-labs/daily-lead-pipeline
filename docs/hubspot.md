# HubSpot

HubSpot is our example CRM. Any CRM with an MCP server works: change the step 3 of the task.

## Connect HubSpot

In Claude: *Settings > Connectors > Browse connectors*, search **HubSpot**, click **Connect** and sign in to your portal. Claude Code uses the same connectors when you sign in with the same Claude account.

## The "Lead source" property

The daily task writes "Lead source" on every contact, so you can filter the contacts the pipeline brings. HubSpot has no such property by default. Create it once:

1. *Settings > Data Management > Properties > Create property*.
2. Object: Contact. Group: Contact information. Label: `Lead source`. Field type: Single-line text.

Or ask your AI Agent to create it with the HubSpot connector.

## What the task writes

| HubSpot property | From the Evaboot lead |
|---|---|
| Email | Email |
| First name, Last name | First Name, Last Name |
| Company name | Company Name |
| Job title | Current Job |
| LinkedIn URL | Linkedin URL Public |
| Lead source | the text in the task settings |

Contacts are matched on email, so a second run updates them and never makes a copy.

Back to the [README](../README.md).
