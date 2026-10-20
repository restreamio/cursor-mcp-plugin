# Connect Restream in Claude (claude.ai web, Claude desktop, Claude mobile, Cowork)

Read when: the user is in claude.ai, the Claude desktop or mobile app, or Cowork, and no Restream tools are callable.

Checked 2026-10-07 against Claude's help pages. Review by 2027-01-05, or sooner if Claude renames its settings. Menu labels can shift; when they differ, follow the labels on the user's screen and keep the same order of steps.

## Steps (Free, Pro, Max)
1. Open **Settings > Connectors** (on the web: click your name at the bottom left, then Settings).
2. Click **Add custom connector**.
3. Name: `Restream`. URL: `https://mcp.restream.io/mcp`. Leave the advanced fields empty. Click **Add**.
4. Click **Connect** next to Restream. A Restream sign-in window opens.
5. Before you approve, check that the workspace you want is the active one in Restream. The connection stays tied to the workspace that was active when you approved.
6. Approve. Back in Claude, start a new chat, open the tools menu (the "+" or sliders icon under the message box) and make sure Restream is switched on.
7. Say "check my Restream connection".

Say it in this shape, numbered, one action per line. Never paste or build an authorization link: the Connect button opens the real Restream sign-in.

## Plan and team notes
- **Free plan** (as of October 2026): one custom connector. If another custom connector is already added, the user has to remove it first or use a paid Claude plan.
- **Team and Enterprise:** an Owner adds Restream once for the organization (organization settings > Connectors). Each member then clicks Connect and signs in with their own Restream account.
- **Desktop and mobile:** they use the same account. A connector added on the web shows up there; restart the app once if it doesn't.
- **Permissions:** Claude lets each tool be set to Always allow, Needs approval or Blocked. If Restream's write tools are Blocked, reading still works. Restream skills ask before every change anyway.
- **Plugin vs connector:** installing the Restream plugin (Customize > Plugins) adds the skills. Its connector still appears on the plugin's Connectors tab and needs its own Connect and sign-in. "Plugin installed" does not mean "connector signed in".
- **Skills without the plugin (optional):** Customize > Skills > Create skill > Upload a skill takes a ZIP whose top folder is the skill. Skills need code execution turned on in Settings (as of October 2026).
- If Restream is already listed, don't add it a second time. Click Connect (or Disconnect, then Connect) on the existing entry.

## When it doesn't work
- **Sign-in window closes or loops:** Disconnect Restream in Settings > Connectors. In the browser, sign in to Restream and switch to the right workspace. Then click Connect again.
- **Connected, but no Restream tools in the chat:** start a new chat and check the tools menu. In the desktop app, quit and reopen it once.
- **Wrong workspace:** Disconnect, switch the workspace in Restream, Connect again. One connection sees one workspace.
- **Restream's own guide:** [Restream MCP server docs](https://developers.restream.io/mcp-server); the Restream help center also has a "Connect Restream MCP server to your AI assistant" article.
