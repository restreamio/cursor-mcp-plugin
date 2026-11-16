# Restream for AI assistants

Run your Restream live streams from your AI assistant, then turn finished streams into reports, transcripts, captions, show notes, posts, clips and cards. This plugin is published by Restream, Inc. It connects to Restream's official MCP server without bundled skills. You need a Restream account; the plugin works on every Restream plan, and paid features stay subject to your plan.

This package targets Claude (claude.ai, Cowork, Claude Code), Codex, Cursor and Grok Bot, VS Code with GitHub Copilot, and other apps that read Agent Skills. Directory users receive updates after the updated listing is reviewed. ChatGPT skills are deferred to a separate submission after the current approval.

## Install

- **Claude (claude.ai, Cowork):** Customize → Plugins → find **Restream**, then open its Connectors tab and sign in to Restream. Team and Enterprise owners can make it available or required for the whole organization.
- **Claude Code:** `/plugin marketplace add restreamio/cursor-mcp-plugin`, then `/plugin install restream@restream`. To get updates automatically, turn on auto-update in `/plugin` → Marketplaces.
- **Codex CLI:** `codex plugin marketplace add restreamio/cursor-mcp-plugin`, then install **Restream** from `/plugins`.
- **ChatGPT:** coming soon to the ChatGPT plugin directory.
- **Cursor and Grok Bot:** install **Restream** from the Cursor Marketplace.
- **Grok Build (xAI CLI):** Grok reads Claude Code plugins, so add this repo as a plugin marketplace with `grok plugin marketplace add`, then install **Restream** from `/plugins`.
- **VS Code / GitHub Copilot CLI:** `copilot plugin marketplace add restreamio/cursor-mcp-plugin`, then `copilot plugin install restream@restream`.

The first time a Restream tool runs, your browser opens so you can sign in to Restream and approve access (OAuth 2.1). No API key or stream key is needed.

## Data and network

Restream access goes through `https://mcp.restream.io/mcp`, using the account you authorize. Keep human confirmation enabled and review write actions before approving them. This package contains no bundled skills or helper scripts.

## Privacy, terms and support

- Privacy policy: https://restream.io/privacy-policy
- Terms of service: https://restream.io/terms-of-service
- Help center: https://support.restream.io
- MCP server documentation: https://developers.restream.io/mcp-server
- Contact: developers@restream.io

## License

Code: [MIT](LICENSE). The Restream name and logo are trademarks of Restream, Inc. and aren't licensed under MIT; see [NOTICE](NOTICE).

## Development checks

Run the offline packaging checks with Python 3:

```sh
python3 -m unittest discover -s tests -v
```

Validate the Claude plugin and marketplace with Claude Code:

```sh
claude plugin validate .claude-plugin/plugin.json
claude plugin validate .claude-plugin/marketplace.json
```

### Test a branch locally in Cursor

Cursor's **Add → From Local Repository** imports a marketplace source; it does not by itself confirm that the plugin is installed. For a local smoke test, copy the committed branch into Cursor's [local plugin directory](https://cursor.com/docs/plugins#test-plugins-locally). From this repository's root:

```sh
mkdir -p "$HOME/.cursor/plugins/local"
# Deliberately fails if an existing Restream installation would be overwritten.
mkdir "$HOME/.cursor/plugins/local/restream" &&
  git archive HEAD | tar -x -C "$HOME/.cursor/plugins/local/restream"
```

Open **Customize → Plugins → Restream** and verify **MCPs 1** and no bundled skills. Sign in to Restream if prompted. If the plugin has not appeared, run **Developer: Reload Window**. Local plugin imports must be allowed by your organization, and an installed marketplace plugin with the same name takes precedence. Do not symlink this directory to a checkout elsewhere; Cursor skips symlinks whose targets are outside the local plugin directory.

This installs a snapshot of the committed branch; later checkout edits do not update the installed copy.
