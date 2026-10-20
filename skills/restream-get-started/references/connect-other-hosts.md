# Connect Restream in Cursor, VS Code and Gemini CLI

Read when: the user is in Cursor, VS Code (GitHub Copilot agent mode), Gemini CLI or another MCP app, and no Restream tools are callable.

Checked 2026-10-07 against each vendor's MCP docs. Review by 2027-01-05. Gemini CLI has not been tried with Restream.

| App | Add the server | Sign in |
|---|---|---|
| Cursor | Install **Restream** from the Cursor Marketplace, or add to `.cursor/mcp.json` (one project) or `~/.cursor/mcp.json` (all projects): `{"mcpServers": {"restream": {"url": "https://mcp.restream.io/mcp"}}}` | Cursor Settings > MCP: click Connect (or Login) next to restream, then approve in the browser |
| VS Code (Copilot agent mode) | Command Palette > **MCP: Add Server** > HTTP, or add to `.vscode/mcp.json`: `{"servers": {"restream": {"type": "http", "url": "https://mcp.restream.io/mcp"}}}` | Start the server from `mcp.json`, sign in when VS Code asks, then enable its tools in agent mode |
| Gemini CLI (unverified) | Add to `~/.gemini/settings.json`: `{"mcpServers": {"restream": {"httpUrl": "https://mcp.restream.io/mcp"}}}` | Run `/mcp auth restream`, then `/mcp` to see it listed |
| Any other MCP app | Add `https://mcp.restream.io/mcp` as a remote (HTTP) server with OAuth | Sign in through the app's own browser window |

For every app:
- Make sure the Restream workspace you want is active before approving the sign-in. One connection sees one workspace.
- Never put a Restream password, stream key or token into a config file. Sign-in happens in the browser.
- After signing in, start a new chat or session and say "check my Restream connection".
- Restream's own guide: [Restream MCP server docs](https://developers.restream.io/mcp-server); the Restream help center also has a "Connect Restream MCP server to your AI assistant" article.
