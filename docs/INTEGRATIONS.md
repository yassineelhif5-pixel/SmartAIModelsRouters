# Multi-host integrations

HIF has one provider-neutral orchestration engine and host-specific adapters. The same portable Agent Skill instructions can be reused where the host supports the Agent Skills format, but command discovery, extension packaging, MCP transport and permissions vary by product.

## Integration matrix

| Host | Native integration | How HIF is exposed | Important limitations |
|---|---|---|---|
| Claude Code | Claude Code plugin and Agent Skill | User-invoked /hif and /hifnode skills plus MCP tools | Claude plugin files are not portable to other hosts. |
| ChatGPT | Custom MCP app/plugin | Remote authenticated HTTPS MCP server | Full custom MCP support is plan/workspace dependent. ChatGPT consumer plans do not all expose the same MCP capabilities. |
| Gemini CLI | Gemini CLI extension and Agent Skills | Extension commands /hif and /hifnode, plus MCP tools | This targets Gemini CLI, not the Gemini web app/Gems interface. |
| GitHub Copilot | Agent Skills and MCP | Skills in .github/skills or personal Copilot skills directory; MCP server | Skill availability depends on the Copilot host/harness and version. |
| Other MCP clients | MCP | Connect to HIF MCP endpoint | Only clients that support the configured MCP transport can connect. |

## Claude Code

The repository provides a Claude Code plugin package under plugins/hif and portable personal skills under skills/. To install the short user-level skills, copy skills/hif and skills/hifnode into:

- Windows: %USERPROFILE%\.claude\skills\
- macOS/Linux: ~/.claude/skills/

The skill commands appear as /hif and /hifnode in Claude Code. The plugin install path can be used where marketplace/plugin installation is preferred.

## ChatGPT

ChatGPT does not install a local Claude-style SKILL.md into a conversation. The supported integration model is a custom MCP app/plugin connecting to a remote HIF MCP endpoint over HTTPS (or an approved secure tunnel where available).

1. Deploy the HIF MCP gateway to a protected HTTPS endpoint.
2. Require authentication and restrict allowed tools.
3. In ChatGPT, open the custom MCP app/plugin connection flow available to the account/workspace.
4. Add the HTTPS endpoint, authenticate, review the exposed tools and grant the requested permissions.
5. Invoke HIF tools in a conversation and ask ChatGPT to use the HIF orchestrator.

Availability is controlled by ChatGPT plan and workspace policy. Current OpenAI documentation describes full custom MCP connections for Business and Enterprise/Edu workspaces; Pro support is more limited (read/fetch only). Do not assume this integration is available on Free or Go. Check the current plan's Apps/MCP settings before deployment.

ChatGPT integration is a remote MCP connection, not a promise that ChatGPT's built-in model, hidden chat context or native session is silently replaced. The user must explicitly provide relevant context or authorize the app to access it.

Official documentation:
- https://developers.openai.com/chatgpt
- https://developers.openai.com/api/docs/guides/custom-mcp-server
- https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt

## Gemini CLI

The repository includes a Gemini extension manifest and custom commands. Install it from the GitHub repository using Gemini CLI's extension manager, then restart the CLI and list extensions. The extension commands provide /hif and /hifnode. The Gemini CLI also supports Agent Skills in .gemini/skills and shared .agents/skills locations.

This adapter targets Gemini CLI, which supports extensions, custom commands, MCP servers and Agent Skills. It does not claim to install a skill into the consumer Gemini web app or Gems.

Official documentation:
- https://geminicli.com/docs/extensions/
- https://geminicli.com/docs/extensions/writing-extensions/
- https://geminicli.com/docs/cli/creating-skills/

## GitHub Copilot

For repository-level availability in supported Copilot agent harnesses, place skills under:

- Project: .github/skills/hif/SKILL.md and .github/skills/hifnode/SKILL.md
- Personal: ~/.copilot/skills/hif/SKILL.md and ~/.copilot/skills/hifnode/SKILL.md

Copilot can also connect to an MCP server. Skill locations and available features depend on the specific host (VS Code, Copilot CLI, GitHub.com, Visual Studio, etc.) and agent harness. In VS Code, start a new agent session after installing or changing skills.

Official documentation:
- https://code.visualstudio.com/docs/agent-customization/agent-skills
- https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills
- https://docs.github.com/en/copilot/reference/customization-cheat-sheet

## Cross-host session and memory behavior

All integrations connect to the same HIF backend. A host invocation creates or resumes an HIF session. Tasks dispatched by that invocation share the same HIF session ID, role registry, approved memory and artifact index. HIF returns a synthesis to the invoking host.

This does not merge native histories between Claude, ChatGPT, Gemini and Copilot. Each host has its own account, permission model, session history and product-level context. Cross-host continuity exists only for information explicitly stored in HIF and permitted by the user.

## Deployment status

Host packaging and skill instructions are being prepared, but a usable integration requires the corresponding HIF MCP/HTTP service, authentication, provider adapters and platform-specific tests. Do not treat a skill file alone as a functioning router.
