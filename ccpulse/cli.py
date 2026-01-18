"""CLI entry point for ccpulse."""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional

import typer

from . import __version__
from .analyzer import analyze_quality
from .display import console, display_quality
from .loader import load_tool_executions

app = typer.Typer(
    name="ccpulse",
    help="Track quality metrics for custom Skills and Subagents in Claude Code",
    add_completion=False,
)


def version_callback(value: bool):
    if value:
        console.print(f"ccpulse version {__version__}")
        raise typer.Exit()


def parse_period(period: str | None) -> tuple[datetime | None, datetime | None, str | None]:
    """Parse period argument and return date range.

    Args:
        period: None (today), '7d' (last 7 days), '2w' (last 2 weeks),
                '1m' (last 1 month), or '20260101' (from date)

    Returns:
        Tuple of (start_date, end_date, label) where:
        - start_date, end_date are None for today
        - label is the original period string for display
    """
    if not period:
        # Default: today only
        return None, None, None

    now = datetime.now(timezone.utc)
    end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Check for Nd/Nw/Nm format (e.g., '7d', '2w', '1m')
    match = re.match(r'^(\d+)([dwm])$', period.lower())
    if match:
        value = int(match.group(1))
        unit = match.group(2)

        if unit == 'd':
            start_date = (now - timedelta(days=value)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif unit == 'w':
            start_date = (now - timedelta(weeks=value)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif unit == 'm':
            # Approximate month as 30 days
            start_date = (now - timedelta(days=value * 30)).replace(hour=0, minute=0, second=0, microsecond=0)

        return start_date, end_date, period

    # Check for YYYYMMDD format (e.g., '20260101')
    if re.match(r'^\d{8}$', period):
        try:
            start_date = datetime.strptime(period, "%Y%m%d").replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
            )
            # Check if date is in the future
            if start_date > now:
                raise typer.BadParameter(
                    f"Date {period} is in the future. Please specify a past date."
                )
            return start_date, end_date, period
        except ValueError:
            raise typer.BadParameter(
                f"Invalid date: {period}. Expected valid YYYYMMDD format (e.g., 20260101)"
            )

    # Invalid format
    raise typer.BadParameter(
        f"Invalid format: {period}. Expected formats:\n"
        "  - 7d, 2w, 1m (last N days/weeks/months)\n"
        "  - 20260101 (from YYYYMMDD date to today)"
    )


@app.command()
def main(
    period: Optional[str] = typer.Argument(
        None,
        help="Time period: '7d' (last 7 days), '2w' (last 2 weeks), '1m' (last 1 month), '20260101' (from date), or none for today",
    ),
    skills: bool = typer.Option(
        False,
        "--skills",
        "-s",
        help="Show only custom skills",
    ),
    subagents: bool = typer.Option(
        False,
        "--subagents",
        "-a",
        help="Show only custom subagents",
    ),
    threshold: int = typer.Option(
        80,
        "--threshold",
        "-t",
        help="Success rate threshold percentage (default: 80). Show tools below this rate.",
        min=0,
        max=100,
    ),
    here: bool = typer.Option(
        False,
        "--here",
        "-h",
        help="Show only current project (no [project] prefix)",
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
    """Track quality metrics for custom Skills and Subagents in Claude Code."""
    # Parse date range
    start_date, end_date, date_label = parse_period(period)

    # Determine project filter and display mode
    project_filter = None
    include_project_prefix = True
    current_project_name = None

    if here:
        from .loader import get_current_project_dir, extract_project_name

        project_filter = get_current_project_dir()
        if project_filter is None:
            console.print("[red]Error: Could not detect current project.[/red]")
            console.print("[yellow]Make sure you're in a directory tracked by Claude Code.[/yellow]")
            raise typer.Exit(1)

        include_project_prefix = False
        current_project_name = extract_project_name(project_filter)

    executions = load_tool_executions(
        start_date=start_date,
        end_date=end_date,
        project_filter=project_filter,
    )
    stats = analyze_quality(executions, include_project_prefix=include_project_prefix)
    display_quality(
        stats,
        threshold=threshold / 100.0,  # Convert percentage to decimal
        start_date=start_date,
        end_date=end_date,
        date_label=date_label,
        show_skills=skills,
        show_subagents=subagents,
        project_name=current_project_name,
    )


def cli():
    """Entry point."""
    app()


if __name__ == "__main__":
    cli()
