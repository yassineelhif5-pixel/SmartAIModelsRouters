# Multi-host integrations

HIF has one provider-neutral engine and host-specific entry points. The portable SKILL.md workflow is reused across products where they support Agent Skills, but installation, invocation, tool access and permissions differ.

## Compatibility matrix

| Host | How to install the skill | How the skill is invoked | Can it call the HIF engine? |
|---|---|---|---|
| Claude web/Desktop | Upload ZIP in Customize > Skills | Select or ask Claude to use HIF | Only when the skill's required tools/service are available |
| Claude Code | Copy to ~/.claude/skills or use project .claude/skills | /hif, /hifnode | Via local/remote MCP once the HIF MCP server is implemented and configured |
| ChatGPT | Import ZIP under Plugins > Skills (eligible plans) | Select/ask for HIF skill | Via a custom MCP app/plugin when remote HIF MCP gateway is deployed |
| Gemini web app | Upload the skill in Gemini Skills | Select or ask Gemini to use HIF | Skill instructions alone do not connect to HIF; a supported tool integration is also required |
| Gemini CLI | User-level Agent Skills or Gemini extension | Skill activation or extension command | Via MCP once the HIF MCP server is implemented |
| GitHub Copilot | Agent Skills in supported Copilot harnesses | Skill picker / slash menu depending on host | Via MCP once HIF MCP server is implemented |
| Microsoft 365 Copilot | Copilot Studio agent with custom engine/MCP tool | Agent conversation in Microsoft 365 Copilot | Via remote HIF MCP after gateway/authentication is implemented |
| Microsoft Copilot consumer app | No generic HIF skill installer is documented here | Not currently supported as a direct installation target | Not without a supported agent/connector extension path |
| OpenAI Codex | ~/.agents/skills (user) or project .agents/skills | Skill activation in Codex | Via MCP once the HIF MCP server is implemented |

A skill is the **instruction layer**. The HIF API/MCP service is the **execution layer**. Importing the first does not automatically install, host or authenticate the second.

## 1. Claude web app and Claude Desktop

Custom skills are available on Claude Free, Pro, Max, Ultra, Team and Enterprise plans when code execution and file creation are enabled, subject to organization policy.

1. Run python scripts/package-skills.py from the repository root.
2. Open Claude and go to Customize > Skills.
3. Choose Create skill > Upload a skill.
4. Upload dist/hif.zip, then repeat with dist/hifnode.zip.
5. Enable both skills.

Team/Enterprise administrators can provision skills for an organization. Skills uploaded in Claude can sync to Claude Code for users signed in with the same Claude account, on a compatible Claude Code version.

Official documentation:
- https://support.claude.com/fr/articles/12512180-utiliser-les-competences-dans-claude
- https://support.claude.com/fr/articles/12512198-comment-creer-des-competences-personnalisees

## 2. Claude Code

For global user-level access, run:

    .\scripts\install-hif-skills.ps1 -Hosts Claude

On Linux/macOS:

    bash scripts/install-hif-skills.sh --hosts claude

The skill directories are installed under ~/.claude/skills/hif and ~/.claude/skills/hifnode. Start a new Claude Code session and run /hif or /hifnode.

This repository currently distributes skill instructions. The production HIF MCP server/plugin still needs to be implemented before those skills can perform real provider dispatch.

## 3. ChatGPT

ChatGPT supports importable Skills for eligible Business, Enterprise, Healthcare and Edu accounts, subject to workspace settings and feature availability. These plans are the ones currently listed in the OpenAI Help Center; the feature is not documented there as generally available on ChatGPT Go.

1. Run python scripts/package-skills.py.
2. In ChatGPT, open Plugins > Skills.
3. Select Create > Upload from your computer.
4. Upload dist/hif.zip and dist/hifnode.zip.
5. Use the HIF skill from the Skills area or ask ChatGPT to apply it to a task.

For actual multi-provider tool execution, HIF also needs a custom MCP app/plugin connected to a remote HTTPS MCP endpoint. A local stdio process on a developer PC is not reachable by ChatGPT web. The remote gateway, authentication and MCP tools are not production-ready in this repository yet.

Official documentation:
- https://help.openai.com/fr-fr/articles/20001066-skills-in-chatgpt
- https://developers.openai.com/plugins/concepts/skills
- https://developers.openai.com/api/docs/guides/custom-mcp-server

## 4. Gemini web app

Gemini Apps support custom Skills imported from SKILL.md on supported web and macOS surfaces; feature availability may vary by account, region and rollout.

1. Open Gemini Apps and go to Skills.
2. Select the create/import option.
3. Upload the HIF skill file from skills/hif/SKILL.md.
4. Repeat for skills/hifnode/SKILL.md.
5. Ask Gemini to use the HIF skill for a task.

This makes workflow instructions available in Gemini. It does not by itself connect Gemini web to a HIF backend or authorize cross-provider API calls.

Official documentation:
- https://support.google.com/gemini/answer/17094296
- https://support.google.com/gemini/answer/18560919

## 5. Gemini CLI

Install user-level skills using the provided script:

    .\scripts\install-hif-skills.ps1 -Hosts GeminiCLI
    gemini skills list

    bash scripts/install-hif-skills.sh --hosts gemini
    gemini skills list

Gemini CLI also supports installing skills from Git repositories and packaging skills in extensions. Extension installation is a separate option from portable skill directories.

Official documentation:
- https://geminicli.com/docs/cli/skills/
- https://geminicli.com/docs/cli/using-agent-skills/
- https://geminicli.com/docs/extensions/

## 6. GitHub Copilot

For user-level skill availability, install to ~/.copilot/skills. For a single repository, use the checked-in .github/skills folders.

    .\scripts\install-hif-skills.ps1 -Hosts Copilot

Start a new Copilot agent session after installing. Feature availability and supported skill paths depend on the Copilot host/harness (for example VS Code, Copilot CLI or GitHub.com) and organization policy.

Official documentation:
- https://code.visualstudio.com/docs/agent-customization/agent-skills
- https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills

## 7. Microsoft 365 Copilot

For Microsoft 365 Copilot, the target integration is a Copilot Studio agent that connects to the HIF remote MCP endpoint as a tool. This is not the same mechanism as installing a GitHub Copilot Agent Skill.

High-level steps after the HIF remote MCP service is released:
1. Create or open the Copilot Studio agent in the appropriate environment.
2. Open Tools > Add a tool > Model Context Protocol.
3. Add the HIF HTTPS MCP endpoint and configure its required authentication.
4. Review the exposed tools and restrict the set to the minimum required.
5. Test in Preview, then publish under the organization's governance and data policies.

The Microsoft Copilot consumer app does not currently have a generic direct install path for these local skill files documented by this project. The Microsoft 365 Copilot path uses Copilot Studio, tenant policies and governance.

Official documentation:
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-components-to-agent
- https://learn.microsoft.com/en-us/microsoft-copilot-studio/agents-experience/tools-add-mcp-server
- https://learn.microsoft.com/microsoft-365/copilot/extensibility/overview-custom-engine-agent

## 8. OpenAI Codex

Codex uses the Agent Skills standard and discovers user-level skills from ~/.agents/skills and project skills from .agents/skills.

    .\scripts\install-hif-skills.ps1 -Hosts Codex

Start a new Codex session and ask it to use HIF. MCP tools can be added separately after the HIF MCP service is available.

## 9. Shared session memory and multi-provider execution

A connected HIF backend is intended to create or resume one HIF session. All specialist nodes in a /hifnode run share the same session ID, role registry, approved memory and artifact index. The backend returns a consolidated result to the invoking host.

This does not merge native chat histories across Claude, ChatGPT, Gemini and Copilot. Cross-host continuity exists only for information explicitly stored in HIF and permitted by the user.

## Current implementation status

- Portable hif and hifnode skill instructions are in the repository.
- Host-specific skill locations are included for Claude Code, Gemini CLI, GitHub Copilot and Codex.
- ZIP packaging and user-level copy installers are provided as source scripts.
- ChatGPT and Gemini web have upload instructions in this guide.
- Microsoft 365 Copilot has a documented Copilot Studio/MCP integration target.
- Production HIF provider execution, shared session memory, remote authenticated MCP gateway and fully tested host-specific adapters remain implementation work.
