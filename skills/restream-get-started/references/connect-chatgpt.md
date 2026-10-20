# Connect Restream in ChatGPT

Read when: the user is in ChatGPT (web, desktop or mobile) and no Restream tools are callable, or Restream reads work but no write tools appear.

Checked 2026-10-07 against OpenAI's help and developer pages. Review by 2027-01-05, or as soon as Restream's ChatGPT plugin is published. ChatGPT renamed apps to "plugins" in July 2026; older guides may still say "apps" or "connectors".

## Path 1: the Restream plugin (use it when it is listed)
1. In ChatGPT, open **Plugins** (or the "+" menu under the message box > More) and search for "Restream".
2. Add the one published by Restream, then click **Connect** and sign in to Restream with the right workspace active.
3. In a chat, type `@Restream` or pick it from the "+" menu, then say "check my Restream connection".

Status on 2026-10-07: Restream's plugin is not confirmed in the directory yet. If the search finds nothing, use Path 2. Never add a look-alike from another publisher.

## Path 2: developer mode (custom MCP server)
1. **Settings > Security and login >** turn on **Developer mode**.
2. Go to **Plugins >** "+" **> Create custom MCP server** (some accounts show "Create MCP App").
3. Name: `Restream`. URL: `https://mcp.restream.io/mcp`. Authentication: OAuth. Click Create.
4. Sign in to Restream when asked, with the workspace you want active, and approve.
5. Start a new chat, turn Restream on from the "+" menu, and say "check my Restream connection".

## What depends on the ChatGPT plan
One rule: if **Settings > Security and login > Developer mode** isn't there, your ChatGPT plan doesn't offer custom MCP servers yet; use the Restream plugin when it's listed (Path 1). On Business, Enterprise and Edu workspaces an admin usually switches developer mode on and may also have to enable write actions (OpenAI calls writes beta).

- Reads work but every write tool is missing: this is a plan or developer-mode limit, not a broken connection. Use the "ChatGPT writes off" copy in SKILL.md and give Restream dashboard steps for the change instead.
- Developer mode is set up on ChatGPT web. Whether the connection then works in the mobile apps is unverified.
- Never paste or build an authorization link. The sign-in window comes from ChatGPT.
- Restream's own guide: [Restream MCP server docs](https://developers.restream.io/mcp-server); the Restream help center also has a "Connect Restream MCP server to your AI assistant" article.
