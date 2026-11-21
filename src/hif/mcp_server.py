"""Local stdio MCP server and factory for authenticated remote MCP transports."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from mcp.server.fastmcp import FastMCP

from hif.config import Settings
from hif.engine import HIFEngine
from hif.storage import HIFStore


@lru_cache(maxsize=1)
def _engine() -> HIFEngine:
    # One engine per process shares SQLite, provider semaphores and usage routing.
    return HIFEngine()


def create_mcp_server(
    *,
    auth: Any | None = None,
    token_verifier: Any | None = None,
    host: str = "127.0.0.1",
    transport_security: Any | None = None,
) -> FastMCP:
    """Create an MCP server with optional OAuth resource-server authentication."""
    server = FastMCP(
        "HIF Smart AI Models Router",
        auth=auth,
        token_verifier=token_verifier,
        host=host,
        transport_security=transport_security,
    )

    @server.tool()
    async def hif_run(goal: str, context: str = "", session_id: str | None = None) -> str:
        """Plan a goal and route its tasks through configured models sequentially.

        Use for normal HIF orchestration when parallel specialist execution is not requested.
        This tool accepts text context only; it does not edit files or execute shell commands.
        """
        result = await _engine().run(
            goal=goal, context=context, session_id=session_id, parallel=False
        )
        return result.model_dump_json(indent=2)

    @server.tool()
    async def hifnode_run(goal: str, context: str = "", session_id: str | None = None) -> str:
        """Run a complex goal as parallel specialist nodes sharing one HIF session memory."""
        result = await _engine().run(
            goal=goal, context=context, session_id=session_id, parallel=True
        )
        return result.model_dump_json(indent=2)

    @server.tool()
    def hif_session_status(session_id: str) -> str:
        """Return persisted HIF node statuses for a session."""
        return json.dumps(_engine().status(session_id), ensure_ascii=False, indent=2)

    @server.tool()
    def hif_models() -> str:
        """Return the configured primary model, fallback chain and credential readiness."""
        return json.dumps(_engine().model_configuration(), ensure_ascii=False, indent=2)

    @server.tool()
    def hif_usage() -> str:
        """Return HIF-measured token usage, not official provider subscription quotas."""
        settings = Settings.from_env()
        store = HIFStore(settings.database_path)
        return json.dumps(
            {
                "window_hours": settings.usage_window_hours,
                "source": "hif_measured_tokens",
                "models": store.usage_summary(settings.usage_window_hours),
            },
            ensure_ascii=False,
            indent=2,
        )

    return server


# The local stdio server remains compatible with existing host registrations.
mcp = create_mcp_server()


def main() -> None:
    """Run the local stdio MCP transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
