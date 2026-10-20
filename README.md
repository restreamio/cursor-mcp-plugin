# Restream for AI assistants

Run your Restream live streams from your AI assistant, then turn finished streams into reports, transcripts, captions, show notes, posts, clips and cards. This plugin is published by Restream, Inc. It connects to Restream's official MCP server and adds 16 skills that teach the assistant how to do each job safely. You need a Restream account; the plugin works on every Restream plan, and paid features stay subject to your plan.

This package targets Claude (claude.ai, Cowork, Claude Code), Codex, Cursor and Grok Bot, VS Code with GitHub Copilot, and other apps that read Agent Skills. Directory users receive the skills after the updated listing is reviewed. ChatGPT skills are deferred to a separate submission after the current approval.

## Skills

| Skill | What it does |
|---|---|
| `restream-get-started` | Checks the connection, shows your workspace, explains what the plugin can and can't do |
| `restream-schedule-stream` | Creates streams, weekly series, record-only sessions, replays and loops |
| `restream-manage-stream` | Moves, renames, cancels or deletes a stream; turns channels on or off, also while live |
| `restream-preflight-stream` | Read-only GO / NO-GO check before you go live |
| `restream-check-account-health` | Finds channels to reconnect, sign-ins about to expire and recordings about to be deleted |
| `restream-fix-my-stream` | Diagnoses dropped frames, missing audio, platforms that didn't go live and stuck uploads |
| `restream-assist-live-stream` (beta) | Catches you up on chat and questions while you're live |
| `restream-report-performance` | Viewers and chat by platform for one stream or a trend |
| `restream-export-files` | Recording links, full transcript, SRT/VTT captions, chat log |
| `restream-write-show-notes` | Recap, YouTube chapters, show notes, blog and newsletter drafts |
| `restream-analyze-chat` | Which viewer questions were answered, in chat or on air; FAQ and next-show ideas |
| `restream-extract-highlights` | Quotes, takeaways and on-air Q&A with timestamps |
| `restream-draft-social-posts` | Drafts for X, LinkedIn, Threads and Bluesky |
| `restream-curate-clips` | Ranks the clips Restream Clips already made and gets download links |
| `restream-render-cards` | Turns a highlights list into image cards and a LinkedIn carousel PDF |
| `restream-log-stream` | Keeps a stream log in Notion, Google Sheets, Airtable or Docs |

Not sure where to start? Ask: "What can I do with Restream?"

## Install

- **Claude (claude.ai, Cowork):** Customize → Plugins → find **Restream**, then open its Connectors tab and sign in to Restream. Team and Enterprise owners can make it available or required for the whole organization.
- **Claude Code:** `/plugin marketplace add restreamio/cursor-mcp-plugin`, then `/plugin install restream@restream`. To get updates automatically, turn on auto-update in `/plugin` → Marketplaces.
- **Codex CLI:** `codex plugin marketplace add restreamio/cursor-mcp-plugin`, then install **Restream** from `/plugins`.
- **ChatGPT:** coming soon to the ChatGPT plugin directory.
- **Cursor and Grok Bot:** install **Restream** from the Cursor Marketplace.
- **Grok Build (xAI CLI):** Grok reads Claude Code plugins, so add this repo as a plugin marketplace with `grok plugin marketplace add`, then install **Restream** from `/plugins`.
- **VS Code / GitHub Copilot CLI:** `copilot plugin marketplace add restreamio/cursor-mcp-plugin`, then `copilot plugin install restream@restream`.

The first time a Restream tool runs, your browser opens so you can sign in to Restream and approve access (OAuth 2.1). No API key or stream key is needed, and the skills never ask for one.

## Data and network

- All Restream access goes through Restream's MCP server at `https://mcp.restream.io/mcp`, using the Restream account you signed in with. It reads your channels, events, analytics, chat, transcripts, recordings and clips.
- Only `restream-schedule-stream` and `restream-manage-stream` change anything in Restream. Each change is shown to you first and needs your yes; "cancel" unschedules a stream, and deleting one needs its exact title and date. Starting a paid transcription always asks first.
- When you ask for a file, the assistant may download the temporary link Restream returns into a temporary folder and delete it afterwards. Links are never stored.
- Only when you ask, the skills can draft into apps you connected yourself (for example Notion, Google Docs or Sheets, Slack, Buffer). They never post or send anything without your confirmation.
- Scheduled or unattended runs never change anything in Restream. The plugin itself collects no analytics or telemetry.
- Chat, transcripts and logs are treated as data, never as instructions.

## Local scripts

A few skills include small Python scripts that run on your own computer, offline, using only the standard library (caption files, title length checks, transcript preparation). Rendering card PNGs needs Playwright and Chromium on your computer; if they aren't installed, you get an HTML page of the cards instead, and the skill shows the one command to install them yourself.

## Privacy, terms and support

- Privacy policy: https://restream.io/privacy-policy
- Terms of service: https://restream.io/terms-of-service
- Help center: https://support.restream.io
- MCP server documentation: https://developers.restream.io/mcp-server
- Contact: developers@restream.io

## License

Code and skill text: [MIT](LICENSE). The Restream name and logo are trademarks of Restream, Inc. and aren't licensed under MIT; see [NOTICE](NOTICE).

## Development checks

Run the offline packaging and helper smoke tests with Python 3:

```sh
python3 -m unittest discover -s tests -v
```

Validate the Claude plugin and marketplace with Claude Code:

```sh
claude plugin validate .claude-plugin/plugin.json
claude plugin validate .claude-plugin/marketplace.json
```
