"""HIF command-line interface."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from hif import __version__
from hif.config import Settings
from hif.engine import HIFEngine
from hif.storage import HIFStore

app = typer.Typer(
    name="hif",
    help="HIF — Hybrid Intelligent Flow, multi-provider AI task orchestration.",
    no_args_is_help=True,
)
console = Console()
security_app = typer.Typer(help="Fast, read-only security checks for application source code.")
app.add_typer(security_app, name="security")



@security_app.command("scan")
def security_scan(
    project_path: Path = typer.Argument(Path("."), help="Project directory to scan."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    """Run a lightweight, read-only security pre-audit. Project code is never executed."""
    engine = HIFEngine()
    try:
        report = asyncio.run(engine.security_scan(str(project_path)))
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    finally:
        engine.close()

    data = report.to_dict()
    if json_output:
        typer.echo(json.dumps(data, indent=2))
        return

    summary = data["summary"]
    console.print(
        f"[bold]Security pre-audit[/bold] — {report.scanned_files} files, "
        f"{report.elapsed_ms} ms"
    )
    console.print(
        f"Critical: {summary['critical']} | High: {summary['high']} | "
        f"Medium: {summary['medium']}"
    )
    table = Table("Severity", "Rule", "File:line", "Finding")
    for finding in report.findings:
        table.add_row(
            finding.severity.upper(), finding.rule_id,
            f"{finding.path}:{finding.line}", finding.title,
        )
    console.print(table)
    console.print("[bold]Recommended action plan[/bold]")
    for index, item in enumerate(data["action_plan"], 1):
        console.print(
            f"{index}. [{item['priority']}] {item['step']} "
            f"({item.get('location', 'project-wide')})"
        )
        console.print(f"   Owner: {item.get('owner_role', 'security_reviewer')}")
        console.print(f"   {item['action']}")
        console.print(f"   Verify: {item['verification']}")
    console.print("[dim]Heuristic pre-audit only. Review findings; no code was executed.[/dim]")


@app.command()
def version() -> None:
    """Display the installed HIF version."""
    console.print(f"HIF {__version__}")


@app.command()
def run(
    goal: str = typer.Argument(..., help="The outcome HIF should deliver."),
    context_file: Optional[Path] = typer.Option(None, "--context-file", "-c"),
    session_id: Optional[str] = typer.Option(None, "--session-id"),
    parallel: bool = typer.Option(False, "--parallel/--sequential"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Plan and dispatch a task. Use --parallel for independent specialist nodes."""
    if context_file and not context_file.is_file():
        raise typer.BadParameter(f"Context file not found: {context_file}")
    context = context_file.read_text(encoding="utf-8") if context_file else ""
    try:
        result = asyncio.run(
            HIFEngine().run(goal, context=context, session_id=session_id, parallel=parallel)
        )
    except Exception as exc:
        console.print(f"[red]HIF failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if json_output:
        typer.echo(result.model_dump_json(indent=2))
        return

    console.print(f"[bold green]HIF session:[/bold green] {result.session_id}")
    console.print(f"Completed nodes: {len(result.nodes)} | Elapsed: {result.elapsed_ms} ms")
    console.print(
        f"Tokens reported: {result.total_input_tokens} input / "
        f"{result.total_output_tokens} output"
    )
    table = Table("Node", "Role", "Model", "Duration", "Fallbacks")
    for node in result.nodes:
        table.add_row(
            node.title, node.role, node.model, f"{node.duration_ms} ms",
            str(node.fallback_count),
        )
    console.print(table)
    console.print("\n[bold]Result[/bold]\n" + result.synthesis)


@app.command()
def node(
    goal: str = typer.Argument(..., help="Complex goal for parallel HIF nodes."),
    context_file: Optional[Path] = typer.Option(None, "--context-file", "-c"),
    session_id: Optional[str] = typer.Option(None, "--session-id"),
) -> None:
    """Run the goal through the parallel specialist-node scheduler."""
    if context_file and not context_file.is_file():
        raise typer.BadParameter(f"Context file not found: {context_file}")
    context = context_file.read_text(encoding="utf-8") if context_file else ""
    try:
        result = asyncio.run(
            HIFEngine().run(goal, context=context, session_id=session_id, parallel=True)
        )
    except Exception as exc:
        console.print(f"[red]HIF Node failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    typer.echo(result.model_dump_json(indent=2))


@app.command()
def status(session_id: str = typer.Argument(..., help="HIF session identifier.")) -> None:
    """Show node execution state for a session."""
    rows = HIFEngine().status(session_id)["nodes"]
    if not rows:
        console.print("[yellow]No nodes found for that session.[/yellow]")
        return
    table = Table("Node ID", "Role", "Status", "Model")
    for row in rows:
        table.add_row(row["node_id"], row["role"], row["status"], row["model"] or "-")
    console.print(table)


@app.command()
def usage() -> None:
    """Display HIF-measured usage, not provider subscription quota data."""
    settings = Settings.from_env()
    rows = HIFStore(settings.database_path).usage_summary(settings.usage_window_hours)
    if not rows:
        console.print("[yellow]No HIF usage recorded yet.[/yellow]")
        return
    table = Table("Model", "Input tokens", "Output tokens", "Estimated cost USD")
    for row in rows:
        cost = row["cost_usd"]
        table.add_row(
            row["model"], str(row["input_tokens"]), str(row["output_tokens"]),
            f"{cost:.6f}" if cost is not None else "unknown",
        )
    console.print(table)
    console.print(
        f"[dim]Window: {settings.usage_window_hours} hours. "
        "This is HIF-measured usage, not an official provider quota percentage.[/dim]"
    )




@app.command()
def models() -> None:
    """Display the configured primary AI model and ordered fallback chain."""
    import json
    from hif.model_manager import AIModelManager

    status = AIModelManager(Settings.from_env()).status()
    console.print_json(json.dumps(status, ensure_ascii=False))


@app.command()
def providers(
    configured_only: bool = typer.Option(False, "--configured", help="Only configured ones."),
) -> None:
    """List every AI provider HIF can reach and whether it is configured here."""
    from hif.provider_catalog import PROVIDERS

    table = Table("Prefix", "Provider", "Protocol", "Region", "Configured", "Credentials")
    for spec in PROVIDERS:
        ready = spec.is_configured()
        if configured_only and not ready:
            continue
        creds = ", ".join(spec.env_keys) if spec.env_keys else spec.base_url_env
        table.add_row(spec.id, spec.name, spec.kind, spec.region,
                      "[green]yes[/green]" if ready else "no", creds)
    console.print(table)
    console.print("[dim]Model ids are written <prefix>/<model>, e.g. mistral/mistral-small-latest. "
                  "Override any endpoint with HIF_<PREFIX>_BASE_URL.[/dim]")


@app.command()
def bench(
    baseline: str = typer.Option(..., "--baseline", help="Single model to compare against, "
                                 "e.g. openai/gpt-6.2-sol."),
    tasks: Path = typer.Option(Path("bench/tasks.jsonl"), "--tasks", help="JSONL task file."),
    out: Path = typer.Option(Path("bench-results"), "--out", help="Output directory."),
    limit: int = typer.Option(0, "--limit", help="Run only the first N tasks (0 = all)."),
    allow_code_exec: bool = typer.Option(
        False, "--allow-code-exec",
        help="Run model-written Python for coding tasks in an isolated interpreter."),
) -> None:
    """Benchmark HIF against a single model on deterministic tasks."""
    from hif.bench import load_tasks, main_sync, write_report
    from hif.native_providers import AutoProvider

    task_list = load_tasks(tasks)
    if limit:
        task_list = task_list[:limit]
    settings = Settings.from_env()
    report = main_sync(
        tasks=task_list, baseline_model=baseline, provider=AutoProvider(),
        engine_factory=lambda: HIFEngine(settings=settings),
        allow_code_exec=allow_code_exec, hif_models=list(settings.get_models()),
    )
    json_path, md_path = write_report(report, out)
    summary = report.summary()
    table = Table("", "Single model", "HIF")
    for key, label in (("passed", "Passed"), ("input_tokens", "Input tokens"),
                       ("output_tokens", "Output tokens"), ("cost_usd", "Reported cost USD")):
        table.add_row(label, str(summary["baseline"][key]), str(summary["hif"][key]))
    console.print(table)
    console.print(f"[dim]Report: {md_path} · raw data: {json_path}[/dim]")


@app.command()
def gateway() -> None:
    """Start the authenticated HTTP REST + Streamable HTTP MCP gateway."""
    from hif.gateway import main as gateway_main

    gateway_main()


@app.command()
def mcp() -> None:
    """Start the local stdio MCP server."""
    from hif.mcp_server import main as mcp_main

    mcp_main()


if __name__ == "__main__":
    app()
