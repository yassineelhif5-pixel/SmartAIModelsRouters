"""Local stdio MCP server exposing HIF orchestration tools."""

from __future__ import annotations

import json
from functools import lru_cache

from mcp.server.fastmcp import FastMCP

from hif.config import Settings
from hif.engine import HIFEngine
from hif.storage import HIFStore

mcp = FastMCP("HIF Smart AI Models Router")


@lru_cache(maxsize=1)
def _engine() -> HIFEngine:
    # Keep one router, SQLite store and provider semaphore set per MCP process.
    return HIFEngine()


@mcp.tool()
async def hif_run(goal: str, context: str = "", session_id: str | None = None) -> str:
    """Plan a goal and route its tasks through configured models sequentially.

    Use for normal HIF orchestration when parallel specialist execution is not requested.
    This tool accepts text context only; it does not edit files or execute shell commands.
    """
    result = await _engine().run(
        goal=goal, context=context, session_id=session_id, parallel=False
    )
    return result.model_dump_json(indent=2)


@mcp.tool()
async def hifnode_run(goal: str, context: str = "", session_id: str | None = None) -> str:
    """Run a complex goal as parallel specialist nodes sharing one HIF session memory."""
    result = await _engine().run(
        goal=goal, context=context, session_id=session_id, parallel=True
    )
    return result.model_dump_json(indent=2)


@mcp.tool()
def hif_session_status(session_id: str) -> str:
    """Return persisted HIF node statuses for a session."""
    return json.dumps(_engine().status(session_id), ensure_ascii=False, indent=2)


@mcp.tool()
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


def main() -> None:
    """Run the local MCP stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
