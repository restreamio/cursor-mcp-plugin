# Connect Restream in Grok Bot and grok.com

Read when: the user is in Grok Bot, or in Grok on grok.com or the Grok mobile apps, and no Restream tools are callable.

Checked 2026-10-07 against cursor.com and docs.x.ai. Review by 2027-01-05. The grok.com path is documented but has not been tried with Restream.

## Grok Bot (Restream plugin from the Cursor Marketplace)
Grok Bot comes with paid Cursor plans, or with a linked SuperGrok subscription.
1. In Grok Bot, open **Settings > Plugins** (or the Marketplace) and find **Restream**, published by Restream.
2. Install it, then click **Connect** and sign in to Restream with the workspace you want active. The sign-in is kept for your account, so every bot of yours can use it.
3. If the plugin shows "Disabled by team admin", ask the team admin to allow it. There is no workaround.
4. Ask the bot: "check my Restream connection".

Notes:
- Installing the plugin is not the same as signing in. If the plugin is installed but the bot sees no Restream tools, open the plugin and click Connect again.
- Grok Bot asks before actions that change things (approval cards, "Ask first" rules).
- Whether Restream skills bundled in the plugin load in Grok Bot is unverified. The connector works either way.

## grok.com and the Grok apps (unverified with Restream)
1. Go to **grok.com/connectors > New Connector > Custom**.
2. URL: `https://mcp.restream.io/mcp`. Authentication: OAuth. Save, then sign in to Restream with the right workspace active.
3. On Grok Business and Enterprise, an admin adds connectors for the team first.
4. Start a new conversation and say "check my Restream connection".

- Whether write tools work through grok.com custom connectors is unverified. If reads work and changes are refused, give Restream dashboard steps for the change instead.
- Never paste or build an authorization link; the sign-in window comes from Grok.
