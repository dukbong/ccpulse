"""CLI entry point for ccpulse."""

from typing import Optional

import typer

from . import __version__
from .analyzer import analyze
from .display import console, display
from .loader import load_tool_calls

app = typer.Typer(
    name="ccpulse",
    help="Track your custom Skills and Subagents usage in Claude Code",
    add_completion=False,
)


def version_callback(value: bool):
    if value:
        console.print(f"ccpulse version {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    days: Optional[int] = typer.Option(
        None,
        "--days",
        "-d",
        help="Only show data from the last N days",
    ),
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """Track your custom Skills and Subagents usage in Claude Code."""
    if ctx.invoked_subcommand is None:
        tool_calls = load_tool_calls(days=days)
        stats = analyze(tool_calls)
        display(stats, days=days)


def cli():
    """Entry point."""
    app()


if __name__ == "__main__":
    cli()
