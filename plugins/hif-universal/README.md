# HIF Universal Orchestrator Plugin

This portable Agent Plugin packages the HIF root Skill and its supporting modules. It is designed for plugin-aware hosts such as ChatGPT/Codex, and the same canonical Skill remains installable in Agent Skills-compatible hosts.

## Included
- `skills/hif/SKILL.md`: universal entry point and orchestration workflow.
- `skills/hif/modules/`: project evaluation, approval-gated counter-tests, adaptive profiles and host/plugin compatibility.
- Other HIF specialist Skills: domain-specific development, database, architecture and agent workflows.

## Important runtime boundary
This package contains instructions and supporting resources. It does not embed provider API keys or deploy the HIF MCP service. To call independent model providers, install/configure the HIF runtime separately and connect its MCP server using the host's supported transport. Consumer chat subscriptions are not automatically API credentials.

## Install in ChatGPT / Codex desktop
Use the repository marketplace at `.agents/plugins/marketplace.json` from a supported local plugin marketplace, or install the plugin folder through a compatible plugin workflow. Restart the host after adding a local marketplace and verify the Skill is available in a new session.

## Install as a regular Agent Skill
Copy the complete `skills/hif/` folder to a host-supported Agent Skills location. Keep the nested `modules/` references beside `SKILL.md`.

## Validate before distribution
- Confirm the host discovers `hif` and loads relative module references.
- Connect MCP separately and verify `hif_evaluate_project` appears.
- Confirm at least two distinct provider credentials/models are configured before multi-model evaluation.
- Test the approval gate in a sandbox. The counter-test tool creates a plan only; it never executes commands.
