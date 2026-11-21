# Multi-host integrations

HIF has one provider-neutral engine and host-specific entry points. The portable SKILL.md workflow is reused across products where they support Agent Skills, but installation, invocation, tool access and permissions differ.

## Compatibility matrix

| Host | How to install the skill | How the skill is invoked | Can it call the HIF engine? |
|---|---|---|---|
| Claude web/Desktop | Upload ZIP in Customize > Skills | Select or ask Claude to use HIF | Only when the skill's required tools/service are available |
| Claude Code | Copy to ~/.claude/skills or use project .claude/skills | /hif, /hifnode | Yes — local stdio MCP is implemented; register the venv hif-mcp executable with user scope |
| ChatGPT | Import ZIP under Plugins > Skills (eligible plans) | Select/ask for HIF skill | Via a custom MCP app connected to a deployed HIF HTTPS MCP endpoint; plan/workspace permissions apply |
| Gemini web app | Upload the skill in Gemini Skills | Select or ask Gemini to use HIF | Skill instructions alone do not connect to HIF; a supported tool integration is also required |
| Gemini CLI | User-level Agent Skills or Gemini extension | Skill activation or extension command | Yes — add the local hif-mcp executable as a user-scope stdio MCP server |
| GitHub Copilot | Agent Skills in supported Copilot harnesses | Skill picker / slash menu depending on host | Yes — configure local stdio MCP in the supported Copilot host (for VS Code, user MCP config or .vscode/mcp.json) |
| Microsoft 365 Copilot | Copilot Studio agent with custom engine/MCP tool | Agent conversation in Microsoft 365 Copilot | Via deployed HIF HTTPS MCP endpoint and tenant-approved authentication |
| Microsoft Copilot consumer app | No generic HIF skill installer is documented here | Not currently supported as a direct installation target | Not without a supported agent/connector extension path |
| OpenAI Codex | ~/.agents/skills (user) or project .agents/skills | Skill activation in Codex | Yes — add the local hif-mcp executable with codex mcp add |

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

The local HIF stdio MCP server and the HIF 0.3 authenticated HTTP + Streamable HTTP MCP gateway are implemented. After installing the runtime, Claude Code can use stdio locally; remote clients can use a deployed HTTPS gateway. Both paths currently dispatch text-only tasks.

## 3. ChatGPT

ChatGPT supports importable Skills for eligible Business, Enterprise, Healthcare and Edu accounts, subject to workspace settings and feature availability. These plans are the ones currently listed in the OpenAI Help Center; the feature is not documented there as generally available on ChatGPT Go.

1. Run python scripts/package-skills.py.
2. In ChatGPT, open Plugins > Skills.
3. Select Create > Upload from your computer.
4. Upload dist/hif.zip and dist/hifnode.zip.
5. Use the HIF skill from the Skills area or ask ChatGPT to apply it to a task.

For actual multi-provider tool execution, HIF needs a custom MCP app/plugin connected to a deployed HTTPS MCP endpoint. HIF 0.3.0 now includes the authenticated REST + Streamable HTTP MCP gateway; it can run as a single-tenant private pilot behind a trusted TLS reverse proxy. A local stdio process on a developer PC is not reachable by ChatGPT web. The gateway can validate OAuth 2.1 access tokens from an external OIDC provider (including an Entra ID setup); the provider must perform authorization-code + PKCE and issue the JWT. Tenant isolation and production SaaS hardening are still future work.

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

This makes workflow instructions available in Gemini. To connect Gemini web to the HIF runtime, configure a supported remote MCP integration pointing to a deployed HTTPS /mcp endpoint and authorize its bearer token. Skill import alone does not grant that access.

Official documentation:
- https://support.google.com/gemini/answer/17094296
- https://support.google.com/gemini/answer/18560919

## 5. Gemini CLI

Install user-level skills using the provided script:

    .\scripts\install-hif-skills.ps1 -Hosts GeminiCLI
    gemini skills list

    bash scripts/install-hif-skills.sh --hosts gemini
    gemini skills list

Gemini CLI also supports installing skills from Git repositories and packaging skills in extensions. To connect the local HIF backend at user scope:

Windows PowerShell:

    gemini mcp add --scope user hif "C:\path\to\SmartAIModelsRouters\.venv\Scripts\hif-mcp.exe"
    gemini mcp list

Linux/macOS:

    gemini mcp add --scope user hif "$HOME/path/to/SmartAIModelsRouters/.venv/bin/hif-mcp"
    gemini mcp list

This stdio registration is local to the machine/user. Gemini web needs the remote gateway deployed on a reachable HTTPS address; see docs/GATEWAY.md.

Official documentation:
- https://geminicli.com/docs/cli/skills/
- https://geminicli.com/docs/cli/using-agent-skills/
- https://geminicli.com/docs/extensions/

## 6. GitHub Copilot

For user-level skill availability, install to ~/.copilot/skills. For a single repository, use the checked-in .github/skills folders.

    .\scripts\install-hif-skills.ps1 -Hosts Copilot

Start a new Copilot agent session after installing. For GitHub Copilot in VS Code, add the local stdio server to the workspace file .vscode/mcp.json, or use the VS Code command palette action MCP: Open User Configuration for user-wide registration.

Example .vscode/mcp.json (replace the executable path):

    {
      "servers": {
        "hif": {
          "type": "stdio",
          "command": "C:\\full\\path\\SmartAIModelsRouters\\.venv\\Scripts\\hif-mcp.exe",
          "args": []
        }
      }
    }

On Linux/macOS, set command to the repository venv executable .venv/bin/hif-mcp. VS Code and Copilot require the local runtime to be installed in the same execution environment as the agent. Feature availability depends on the Copilot host/harness and organization policy.

Official documentation:
- https://code.visualstudio.com/docs/agent-customization/agent-skills
- https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills

## 7. Microsoft 365 Copilot

For Microsoft 365 Copilot, the target integration is a Copilot Studio agent that connects to the HIF remote MCP endpoint as a tool. This is not the same mechanism as installing a GitHub Copilot Agent Skill.

High-level steps after the HIF remote MCP service has been deployed behind HTTPS:
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

Start a new Codex session and register the local MCP service:

Windows:

    codex mcp add hif -- "C:\path\to\SmartAIModelsRouters\.venv\Scripts\hif-mcp.exe"
    codex mcp list

Linux/macOS:

    codex mcp add hif -- "$HOME/path/to/SmartAIModelsRouters/.venv/bin/hif-mcp"
    codex mcp list

Codex user and project MCP settings are distinct; use the user-level config for a machine-wide setup.

## 9. Shared session memory and multi-provider execution

A connected HIF backend is intended to create or resume one HIF session. All specialist nodes in a /hifnode run share the same session ID, role registry, approved memory and artifact index. The backend returns a consolidated result to the invoking host.

This does not merge native chat histories across Claude, ChatGPT, Gemini and Copilot. Cross-host continuity exists only for information explicitly stored in HIF and permitted by the user.

## Current implementation status

- Portable hif and hifnode skill instructions are in the repository.
- Host-specific skill locations are included for Claude Code, Gemini CLI, GitHub Copilot and Codex.
- ZIP packaging and user-level copy installers are provided as source scripts.
- ChatGPT and Gemini web have upload instructions in this guide.
- Microsoft 365 Copilot has a documented Copilot Studio/MCP integration target.
- Local text-only provider execution, shared SQLite session memory, DAG node parallelism, HIF-measured 80% fallback, local stdio MCP and authenticated remote HTTP MCP tools are implemented.
- HIF 0.3.0 includes an authenticated REST + Streamable HTTP MCP gateway for a single-tenant private pilot; deploy it behind HTTPS before connecting remote clients.
- File editing, shell execution, browsing, deployment and fully tested cross-host tool workflows remain out of scope for the local MVP.


# ChatGPT support and plan requirements

The current OpenAI Help Center describes importable ChatGPT Skills for eligible Business, Enterprise, Healthcare and Edu accounts. It does not list ChatGPT Go among the eligible plans for imported Skills.

Custom remote MCP access has separate plan limits:
- Business: workspace admins/owners create and publish custom MCP apps.
- Enterprise/Edu: admins/owners and members explicitly authorized by RBAC can create/test; admins/owners publish.
- Pro: custom MCP server access is read/fetch-only; full MCP write/modify support is not available.
- Go: not listed among the plans supported by the current custom MCP server connection documentation.

Therefore, a ChatGPT Go user should not assume the native ChatGPT Skill or custom MCP integration can be installed. The HIF skill package can still be used in other supported clients, and ChatGPT integration can be enabled later if the account/workspace has the required plan and controls.

Official plan and permission details:
- https://help.openai.com/fr-fr/articles/20001066-skills-in-chatgpt
- https://help.openai.com/fr-fr/articles/12584461-connecting-custom-mcp-servers-in-chatgpt


## HIF remote gateway

HIF 0.3.0 provides a Streamable HTTP MCP endpoint at /mcp and REST endpoints for runs, status and measured usage. See docs/GATEWAY.md for authentication, request limits, TLS termination, client configuration examples and the current single-tenant security boundary. A remote gateway must be deployed on an HTTPS-reachable host; this repository does not provision cloud infrastructure automatically.
