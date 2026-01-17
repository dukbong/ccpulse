"""CLI entry point for ccpulse."""

from typing import Optional

import typer
from rich.console import Console

from . import __version__
from .analyzer import analyze_all, analyze_languages, analyze_hours, analyze_projects, analyze_tools
from .display import (
    console,
    display_all,
    display_header,
    display_languages,
    display_hours,
    display_weekdays,
    display_projects,
    display_tools,
    display_subagents,
    display_no_data,
)
from .loader import load_all_sessions

app = typer.Typer(
    name="ccpulse",
    help="Claude Code usage statistics analyzer",
    add_completion=False,
)


def version_callback(value: bool):
    if value:
        console.print(f"ccpulse version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """Claude Code usage statistics analyzer."""
    pass


@app.command()
def show(
    days: Optional[int] = typer.Option(
        None,
        "--days",
        "-d",
        help="Only show data from the last N days",
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        help="Number of projects to show",
    ),
):
    """Show project costs (default command)."""
    messages = load_all_sessions(days=days)

    if not messages:
        display_no_data()
        raise typer.Exit(1)

    display_header(days)
    stats = analyze_projects(messages)
    display_projects(stats, limit=limit)


@app.command(name="all")
def show_all(
    days: Optional[int] = typer.Option(
        None,
        "--days",
        "-d",
        help="Only show data from the last N days",
    ),
):
    """Show all statistics."""
    messages = load_all_sessions(days=days)

    if not messages:
        display_no_data()
        raise typer.Exit(1)

    stats = analyze_all(messages)
    display_all(stats, days=days)


@app.command()
def languages(
    days: Optional[int] = typer.Option(
        None,
        "--days",
        "-d",
        help="Only show data from the last N days",
    ),
    limit: int = typer.Option(
        15,
        "--limit",
        "-n",
        help="Number of languages to show",
    ),
):
    """Show language statistics."""
    messages = load_all_sessions(days=days)

    if not messages:
        display_no_data()
        raise typer.Exit(1)

    display_header(days)
    stats = analyze_languages(messages)
    display_languages(stats, limit=limit)


@app.command()
def hours(
    days: Optional[int] = typer.Option(
        None,
        "--days",
        "-d",
        help="Only show data from the last N days",
    ),
):
    """Show hourly activity patterns."""
    messages = load_all_sessions(days=days)

    if not messages:
        display_no_data()
        raise typer.Exit(1)

    display_header(days)
    stats = analyze_hours(messages)
    display_hours(stats)
    display_weekdays(stats)


@app.command()
def projects(
    days: Optional[int] = typer.Option(
        None,
        "--days",
        "-d",
        help="Only show data from the last N days",
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        help="Number of projects to show",
    ),
):
    """Show project usage statistics."""
    messages = load_all_sessions(days=days)

    if not messages:
        display_no_data()
        raise typer.Exit(1)

    display_header(days)
    stats = analyze_projects(messages)
    display_projects(stats, limit=limit)


@app.command()
def tools(
    days: Optional[int] = typer.Option(
        None,
        "--days",
        "-d",
        help="Only show data from the last N days",
    ),
    limit: int = typer.Option(
        15,
        "--limit",
        "-n",
        help="Number of tools to show",
    ),
):
    """Show tool usage statistics."""
    messages = load_all_sessions(days=days)

    if not messages:
        display_no_data()
        raise typer.Exit(1)

    display_header(days)
    stats = analyze_tools(messages)
    display_tools(stats, limit=limit, show_subagents=False)


@app.command()
def subagents(
    days: Optional[int] = typer.Option(
        None,
        "--days",
        "-d",
        help="Only show data from the last N days",
    ),
):
    """Show subagent usage statistics."""
    messages = load_all_sessions(days=days)

    if not messages:
        display_no_data()
        raise typer.Exit(1)

    display_header(days)
    stats = analyze_tools(messages)
    display_subagents(stats)


# Make 'show' the default command when running without subcommand
def cli():
    """Entry point that defaults to 'show' command."""
    import sys

    # If no command is provided, default to 'show'
    if len(sys.argv) == 1:
        sys.argv.append('show')
    elif len(sys.argv) >= 2 and sys.argv[1].startswith('-') and sys.argv[1] not in ('-v', '--version', '--help', '-h'):
        # If first arg is an option (like --days), insert 'show' command
        sys.argv.insert(1, 'show')

    app()


if __name__ == "__main__":
    cli()
