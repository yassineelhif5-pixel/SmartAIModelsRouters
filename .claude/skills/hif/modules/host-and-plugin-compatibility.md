# HIF module: host, Skill and Plugin compatibility

HIF has three separate layers:
- **Portable Agent Skill:** instructions and references loaded by a host.
- **MCP server:** structured tools for evaluation, orchestration, status and controlled actions.
- **Host Plugin/App package:** installable manifest that bundles one or more Skills and optionally maps an MCP server.

Do not imply that installing a Skill starts the runtime or connects other models. Do not imply a plugin marketplace listing is already published.

## Supported integration strategy
- Agent Skills-compatible hosts: provide the canonical `skills/hif/SKILL.md` and supporting module references.
- Claude Code, Gemini CLI, Cursor, Kimi Code CLI, Qwen Code, Codex and GitHub Copilot: use their documented native skill locations and MCP configuration.
- ChatGPT/Codex Plugin: use the portable Agent Plugins `plugin.json` manifest, `skills/` directory and optional `mcp.json`; plugin install is separate from remote MCP server deployment and authentication.
- Other agent frameworks: integrate through MCP where supported, or adapt the Skill instructions to their native agent/workflow mechanism.

Treat host compatibility as a tested matrix with version/date, Skill discovery, MCP transport, auth, approvals, file access and sub-agent support. Never infer support from a product name alone.
