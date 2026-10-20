# Assistant compatibility and distribution

Documentation checked **2026-09-07** (VS Code / Copilot and Antigravity rows: 2026-10-08). Use this reference for installation or portability questions, not as part of ordinary troubleshooting. Distinguish documented format support, a validated package, and an actual successful run in the target product. Do not describe a platform as tested based only on documentation or a simulation in another assistant.

## Shared skill, different installation paths

Keep `SKILL.md`, `references/`, `scripts/`, and `assets/` together. All runtime paths are relative to this skill. The optional `agents/openai.yaml` is host-specific UI metadata for ChatGPT and Codex; its `policy.products` may list only `CHAT` and `CODEX`, and it is not a compatibility declaration for other assistants. Keep it in every export; other hosts ignore it.

The standard export uses one top-level folder named `restream-fix-my-stream`, matching the frontmatter name. Portable archives come from the Restream skill-pack build, which also copies in the shared references this skill links. Export the complete knowledge base; copying only the entrypoint loses its references.

| Host | Documented route | What remains to verify for a release |
|---|---|---|
| ChatGPT / Codex | Use the installed personal skill and host-supported sharing/export controls. | A personal install does not establish that a public installation link works for other accounts. |
| Claude | Upload the complete skill-folder ZIP through Customize → Skills → + → Create skill → Upload a skill; enable the skill. | Confirm the target account permits skills, code execution is enabled where required, references are readable, and sample diagnoses work. |
| Grok Build | Place the skill folder under a documented skill root such as `~/.grok/skills/`; invoke its named skill when needed. | Confirm discovery, reference access, and optional helper behavior in the actual runtime. |
| Grok web / mobile | Grok documents creating skills from conversation, an uploaded file, or written instructions. | Confirm the import retains the full instruction/reference package; the public announcement does not establish that every file/archive layout imports intact. |
| VS Code / GitHub Copilot | Install the Restream plugin from its marketplace repo (VS Code `chat.plugins.marketplaces`, or Copilot CLI `copilot plugin marketplace add`), or commit the skill folder into a repo's `.github/skills/`, `.claude/skills/` or `.agents/skills/`. | Confirm the skill is discovered, its references load, and the plugin's MCP server signs in. |
| Antigravity CLI | Install the plugin with `agy plugin install <repo URL>`; it needs its own repo layout (closed `plugin.json` schema, `serverUrl` in `mcp_config.json`). | Confirm discovery and reference access; update behaviour is not documented. |
| Grok Bot | Save the workflow as a skill; manage packaged/private skills under Settings → Plugins and enable the skill for the intended Bot. | Confirm the Bot can read the full references and that it saved the actual rules rather than a short summary. |

Sources: [Claude skill installation](https://support.claude.com/en/articles/12512180-use-skills-in-claude), [Grok Build skill format](https://docs.x.ai/build/features/skills-plugins-marketplaces), [Grok skills on web and mobile](https://x.ai/news/grok-skills), [Grok Bot skills](https://docs.x.ai/grok-bot/skills-routines-and-automations).

## Capabilities to preserve across hosts

- Start with the user's named production app, or ask the neutral app question. Do not suggest other products unprompted; if the user names another tool, help them as asked. Preserve this rule in imported descriptions, starters, templates, and examples.
- Give one evidence-based next check, protect active broadcasts and unfinished recording data, and verify the result. These rules do not depend on code execution or a Restream connection.
- Read only the relevant Markdown references. Never load a catalog JSON whole; without Python, search it for one entry or use route diagnosis and platform rules instead. Node and Python helpers are optional local conveniences; use manual reading when unavailable. Do not install dependencies merely to run them.
- Use the host's actual browsing, image, file, and connector capabilities. If an attachment cannot be read, request a relevant text excerpt without pretending it was inspected. If current sources are unavailable, distinguish the dated snapshot from verified current guidance.
- Connect Restream MCP only for a relevant account question and only when that host exposes an authorized connector. A standalone diagnosis is still useful without it. Never add a connector requirement merely because the host supports connectors.

For a conversational import, instruct the destination assistant to preserve the complete rules and attached resources, including the user-first product naming rule, rather than summarizing them into a general streaming prompt. A pasted prompt without the reference files is a fallback, not the full skill.

## Release check in each actual host

Try a problem with no app name, a problem with an explicitly named app, and an unfinished-upload case. Check the initial questions, selected references, proposed action, and whether the assistant admits missing capabilities. Test a sample log only when a code runner is available; otherwise confirm a manual reading works. Use synthetic or redacted evidence and no active account changes.

Record which host and surface actually ran the checks. A successful package validation or response from another model does not certify Claude or Grok behavior. Installation and public distribution should be described as unverified until actually exercised there.
