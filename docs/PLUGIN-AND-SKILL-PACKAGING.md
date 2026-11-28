# HIF portable Skill and Plugin distribution

## Three layers, three responsibilities

1. **Agent Skill:** portable workflow instructions and references, using the Agent Skills `SKILL.md` convention.
2. **Plugin package:** stable identity plus one or more Skills, optional MCP configuration and optional assets.
3. **HIF runtime:** Python engine and MCP tools. It must be installed/deployed and authenticated separately.

HIF ships a portable Agent Plugin manifest in `plugins/hif-universal/` and a repository marketplace in `.agents/plugins/marketplace.json`. The plugin currently bundles Skills only. It intentionally does not point at a fake remote MCP URL; configure the real local or remote HIF MCP server separately.

## Confirmed and target hosts

| Host / surface | Integration approach | Status |
|---|---|---|
| Claude Code | Native `.claude/skills` and MCP configuration | Repository mirror + installer |
| OpenAI Codex | `.agents/skills`, portable Agent Plugin and marketplace | Repository mirror + plugin manifest |
| ChatGPT | Portable plugin / custom MCP server connection where account/workspace allows | Plugin package prepared; MCP deployment and workspace connection remain operator steps |
| Gemini CLI | Native Agent Skills and MCP | Repository mirror + installer |
| GitHub Copilot in VS Code | `.github/skills`, Agent Skills discovery and optional extension contribution | Repository mirror; VS Code extension package not included |
| Cursor | Native `.cursor/skills` and MCP | Repository mirror + installer |
| Kimi Code CLI | Native Kimi skill directory and MCP | Repository mirror + installer; verify CLI version-specific discovery |
| Qwen Code | Native `.qwen/skills` and MCP | Repository mirror + installer |
| VS Code extensions | `contributes.chatSkills` can expose the Skill directory | Adapter opportunity; no VS Code extension package in this release |
| Windsurf, Cline, Roo Code, Continue, OpenHands and other MCP clients | Evaluate native Agent Skills discovery first; otherwise connect via MCP and provide host-specific instructions | Adapter-ready, not certified by this repository |

Agent Skills is an open format, but supported directories, slash-command behavior, scripts, sub-agents and permissions vary by host/version. HIF tests repository mirrors and installers; it does not claim end-to-end certification for every host.

## ChatGPT / Codex plugin

The portable manifest follows the Agent Plugins schema and packages Skills from `plugins/hif-universal/skills/`. The repo marketplace makes the plugin discoverable in supported local plugin workflows. Public distribution requires a separate submission/review process. A plugin manifest does not deploy a server.

For a connected ChatGPT experience, use a real HTTPS MCP endpoint or a supported secure tunnel, configure authentication, review tool permissions, and refresh the connection when tool schemas change. Workspace plan/admin policy applies. Read-only and write tools should have distinct approval policies.

## Installation notes

- Portable Skill: copy the full `skills/hif/` directory, not just `SKILL.md`, because module references are relative.
- Repository plugin: use `.agents/plugins/marketplace.json` and install `hif-universal` through a supported plugin host.
- Connected runtime: install `.[providers]`, configure provider credentials and host MCP transport, then verify available tools.
- Browser-only Skill: use sequential/compact workflow; no local process, shell, file system, persistent session or resource telemetry is assumed.

## References

- Agent Plugins package structure: https://developers.openai.com/plugins/build/plugins
- ChatGPT custom MCP connections: https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt
- VS Code Agent Skills: https://code.visualstudio.com/docs/agent-customization/agent-skills
- VS Code Skills extension contribution: https://code.visualstudio.com/docs/agent-customization/agent-skills#_contribute-skills-from-extensions
- HIF integration matrix: [INTEGRATIONS.md](INTEGRATIONS.md)
