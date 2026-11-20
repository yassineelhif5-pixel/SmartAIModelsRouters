"""Initial HIF command-line interface."""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(
    name="hif",
    help="HIF — Hybrid Intelligent Flow, your multi-provider AI task orchestrator.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def version() -> None:
    """Display the installed HIF version."""
    from hif import __version__

    console.print(f"HIF {__version__}")


@app.command()
def status() -> None:
    """Show the local orchestration service status (MVP placeholder)."""
    console.print("[yellow]HIF core is under development.[/yellow]")
    console.print("The CLI foundation is installed; provider execution is not implemented yet.")


@app.command()
def plan(goal: str) -> None:
    """Create a task plan for GOAL (planner implementation is forthcoming)."""
    if not goal.strip():
        raise typer.BadParameter("Goal must not be empty.")
    console.print("[bold]HIF[/bold] received goal:")
    console.print(goal)
    console.print("[yellow]Planner is not implemented in this foundation commit.[/yellow]")


if __name__ == "__main__":
    app()
