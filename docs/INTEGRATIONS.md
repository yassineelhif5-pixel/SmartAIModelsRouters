# Multi-host integrations

HIF has one provider-neutral engine and host-specific entry points. The portable \`SKILL.md\` workflow is reused across products where they support Agent Skills, but installation, invocation, tool access and permissions differ.

## Compatibility matrix

| Host | How to install the skill | How the skill is invoked | Can it call the HIF engine? |
|---|---|---|---|
| Claude web/Desktop | Upload ZIP in Customize > Skills | Select or ask Claude to use HIF | Only when the skill's required tools/service are available |
| Claude Code | Copy to \`~/.claude/skills\` or use project \`.claude/skills\` | \`/hif\`, \`/hifnode\` | Via local/remote MCP once the HIF MCP server is implemented and configured |
| ChatGPT | Import ZIP under Plugins > Skills (eligible plans) | Select/ask for HIF skill | Via a custom MCP app/plugin when remote HIF MCP gateway is deployed |
| Gemini web app | Upload skill in Gemini Skills | Select or ask Gemini to use HIF | Skill instructions alone do not provide a remote HIF tool; connect supported tools separately |
| Gemini CLI | Install/copy to \`~/.gemini/skills\` or \`~/.agents/skills\` | Skill activation in Gemini CLI | Via MCP once HIF MCP server is implemented |
| GitHub Copilot | \`.github/skills\` (workspace) or \`~/.copilot/skills\` (user) | Skill selection / slash menu in supported harnesses | Via MCP once HIF MCP server is implemented |
| OpenAI Codex | \`~/.agents/skills\` (user) or project \`.agents/skills\` | Skill activation in Codex | Via MCP once HIF MCP server is implemented |

A skill is the **instruction layer**. The HIF API/MCP service is the **execution layer**. Importing the first does not automatically install, host or authenticate the second.

## 1. Claude web app and Claude Desktop

Custom skills are available on Claude Free, Pro, Max, Ultra, Team and Enterprise plans when code execution and file creation are enabled, subject to organization policy.

1. Run \`python scripts/package-skills.py\` from the repository root.
2. Open Claude and go to **Customize > Skills**.
3. Choose **Create skill > Upload a skill**.
4. Upload \`dist/hif.zip\`, then repeat with \`dist/hifnode.zip\`.
5. Enable both skills.

Team/Enterprise administrators can provision skills for an organization. Claude skills may sync into Claude Code for users signed into the same Claude account; this requires a compatible Claude Code version and account authentication (not API-key-only mode).

Official documentation:
- https://support.claude.com/fr/articles/12512180-utiliser-les-competences-dans-claude
- https://support.claude.com/fr/articles/12512198-comment-creer-des-competences-personnalisees

## 2. Claude Code

For global user-level access, use the installer:

\`\`\`powershell
.\\scripts\\install-hif-skills.ps1 -Hosts Claude
\`\`\`

On Linux/macOS:

\`\`\`bash
bash scripts/install-hif-skills.sh --hosts claude
\`\`\`

The skill directories are installed under \`~/.claude/skills/hif\` and \`~/.claude/skills/hifnode\`. Start a new Claude Code session and run \`/hif\` or \`/hifnode\`.

A separate Claude Code plugin can later add MCP tools, hooks and plugin-managed assets. Do not assume plugin marketplace packaging alone provides a working HIF backend.

## 3. ChatGPT

ChatGPT supports importable Skills for eligible Business, Enterprise, Healthcare and Edu accounts, subject to workspace settings and feature availability.

1. Run \`python scripts/package-skills.py\`.
2. In ChatGPT, open **Plugins > Skills**.
3. Select **Create > Upload from your computer**.
4. Upload \`dist/hif.zip\` and \`dist/hifnode.zip\`.
5. Use the HIF skill from the Skills area or ask ChatGPT to apply it to a task.

For tool execution, HIF also needs a custom MCP app/plugin connected to a **remote HTTPS MCP endpoint**. A local stdio process on a developer PC is not reachable by ChatGPT web. The remote gateway, authentication and MCP tools are not production-ready in this repository yet.

Official documentation:
- https://help.openai.com/fr-fr/articles/20001066-skills-in-chatgpt
- https://developers.openai.com/plugins/concepts/skills
- https://developers.openai.com/api/docs/guides/custom-mcp-server

## 4. Gemini web app

Gemini Apps support custom Skills imported from \`SKILL.md\` on supported web/macOS surfaces. Availability may vary by account, region and staged rollout.

1. Download the repository ZIP or obtain the HIF skill package.
2. In Gemini Apps, open the Skills area and choose the option to create/import a skill.
3. Upload the HIF skill's \`SKILL.md\` or package as requested by the UI.
4. Repeat for HIF Node and ask Gemini to use the HIF skill for an appropriate task.

This makes the workflow instructions available in Gemini. It does **not** by itself connect Gemini web to a HIF backend or authorize cross-provider API calls.

Official documentation:
- https://support.google.com/gemini/answer/17094296
- https://support.google.com/gemini/answer/18560919

## 5. Gemini CLI

Install user-level skills using the provided script:

\`\`\`powershell
.\\scripts\\install-hif-skills.ps1 -Hosts GeminiCLI
gemini skills list
\`\`\`

\`\`\`bash
bash scripts/install-hif-skills.sh --hosts gemini
gemini skills list
\`\`\`

Gemini CLI also supports installing skills from Git repositories and packaging skills in extensions. Extension installation is a separate option from the portable skill directories.

Official documentation:
- https://geminicli.com/docs/cli/skills/
- https://geminicli.com/docs/cli/using-agent-skills/
- https://geminicli.com/docs/extensions/

## 6. GitHub Copilot

For user-wide skill availability, install to \`~/.copilot/skills\`. For a single repository, use the checked-in \`.github/skills\` folders.

\`\`\`powershell
.\\scripts\\install-hif-skills.ps1 -Hosts Copilot
\`\`\`

Start a new Copilot agent session after installing. Feature availability and supported skill paths depend on the Copilot host/harness (for example VS Code, Copilot CLI or GitHub.com) and organization policy.

Official documentation:
- https://code.visualstudio.com/docs/agent-customization/agent-skills
- https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills

## 7. OpenAI Codex

Codex uses the Agent Skills standard and discovers user-level skills from \`~/.agents/skills\` and project skills from \`.agents/skills\`.

\`\`\`powershell
.\\scripts\\install-hif-skills.ps1 -Hosts Codex
\`\`\`

Start a new Codex session and ask it to use HIF. MCP tools can be added separately after the HIF MCP service is available.

## 8. Shared session memory and multi-provider execution

A connected HIF backend is intended to create or resume one HIF session. All specialist nodes in a \`/hifnode\` run share the same session ID, role registry, approved memory and artifact index. The backend returns a consolidated result to the invoking host.

This does not merge native chat histories across Claude, ChatGPT, Gemini and Copilot. Cross-host continuity exists only for information explicitly stored in HIF and permitted by the user.

## Current implementation status

- Portable \`hif\` and \`hifnode\` skill instructions are in the repository.
- Host-specific skill locations are included for Claude Code, Gemini CLI, Copilot and Codex.
- ZIP packaging and user-level copy installers are provided as source scripts.
- Production HIF provider execution, shared session memory, remote authenticated MCP gateway and fully tested host-specific adapters remain implementation work.
