# Connect Restream in Codex (CLI, IDE extension, Codex in the ChatGPT desktop app)

Read when: the user is in Codex and no Restream tools are callable.

Checked 2026-10-07 against OpenAI's Codex docs. Review by 2027-01-05. Command flags change between Codex versions: if a command below is rejected, run `codex mcp --help` and use the matching flag.

## Add it
1. In a terminal:
   ```
   codex mcp add restream --url https://mcp.restream.io/mcp
   ```
   Or add it to `~/.codex/config.toml`:
   ```toml
   [mcp_servers.restream]
   url = "https://mcp.restream.io/mcp"
   ```
2. Sign in:
   ```
   codex mcp login restream
   ```
   A browser window opens to sign in to Restream. Make sure the workspace you want is active in Restream before you approve.
3. `codex mcp list` should show restream. Start a new Codex session and say "check my Restream connection".

## Notes
- The CLI, the IDE extension and Codex in the ChatGPT desktop app read the same Codex config, so one setup likely covers all three.
- Codex asks before tool calls according to its approval mode (auto, prompt, writes, approve). Restream skills also ask before every change.
- Codex's sandbox has no network by default. Opening a Restream download link from a shell command needs the user's network approval; MCP tool calls themselves don't.
- Never put a Restream password, stream key or token into the config or a command. Sign-in happens in the browser.
- Restream plugin: where it is published for Codex, installing it adds the skills and the server config. It still needs `codex mcp login restream`.
