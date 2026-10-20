# Connect Restream in Claude Code (terminal, IDE extensions, desktop Code tab)

Read when: the user is in Claude Code and no Restream tools are callable after searching for deferred tools.

Checked 2026-10-07 against code.claude.com. Review by 2027-01-05.

## First, check it isn't already there
- Claude Code loads MCP tools on demand. Search for deferred tools (for example "restream list_channels") before deciding Restream is missing.
- Run `/mcp`. If a Restream server is listed (it may also arrive from claude.ai connectors on the same account, under another name), authenticate that one instead of adding a second copy.

## Add it
1. In a terminal:
   ```
   claude mcp add --transport http restream https://mcp.restream.io/mcp
   ```
   Add `--scope user` to make it available in every project, not just this folder.
2. Start Claude Code (or restart the session) and run `/mcp`.
3. Pick **restream > Authenticate**. A browser window opens to sign in to Restream. Make sure the workspace you want is active in Restream before you approve; the connection stays tied to it.
4. `/mcp` now shows restream as connected. Say "check my Restream connection".

## With the Restream plugin
- `/plugin` installs the Restream plugin, which brings the server config with it. It still needs step 3: installing the plugin does not sign you in.

## Notes
- Remote HTTP with OAuth is the only supported setup. Never put a Restream password, stream key or token into a config file or command.
- Cloud sessions and routines can call connector tools without asking. Restream skills stay read-only in any scheduled or unattended run.
- Wrong workspace: in `/mcp`, clear the authentication for restream, switch the workspace in Restream, then Authenticate again.
- Restream's own guide: [Restream MCP server docs](https://developers.restream.io/mcp-server); the Restream help center also has a "Connect Restream MCP server to your AI assistant" article.
