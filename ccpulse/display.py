"""Terminal display using rich library."""

import sys
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from .analyzer import Stats

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

console = Console(force_terminal=True)

# Colors
COLOR_PRIMARY = "#E07A5F"
COLOR_SECONDARY = "#81B29A"
COLOR_MUTED = "#6B7280"
COLOR_TEXT = "#F4F3EE"

BAR_CHAR = "█"
BAR_WIDTH = 30      # Width of the bar chart
NAME_MIN_WIDTH = 15 # Minimum width for name column


def make_bar(value: int, max_value: int, width: int = 30) -> str:
    """Create a bar for the given value."""
    if max_value == 0:
        return ""
    filled = int((value / max_value) * width)
    return BAR_CHAR * filled


def display_usage_list(
    items: list[tuple[str, int]],
    max_count: int,
    name_width: int,
    bar_width: int,
):
    """Display usage as plain text with bars."""
    for name, count in items:
        bar = make_bar(count, max_count, bar_width)
        line = f"{name:<{name_width}} {bar:<{bar_width}} {count:>3}"
        console.print(f"[{COLOR_TEXT}]{line}[/]")


def display(
    stats: Stats,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    date_label: str | None = None,
    show_skills: bool = False,
    show_subagents: bool = False,
    show_full: bool = False,
):
    """Display skills and subagents usage."""
    # Determine what to show
    display_skills = not show_subagents  # Show skills unless --subagents is specified
    display_subagents = not show_skills  # Show subagents unless --skills is specified

    # Header
    if date_label:
        # Check if it's a --last format (e.g., "7d", "2w", "1m")
        import re
        if re.match(r'^\d+[dwm]$', date_label.lower()):
            # Parse the label for display
            value = int(date_label[:-1])
            unit = date_label[-1].lower()
            unit_map = {'d': 'day', 'w': 'week', 'm': 'month'}
            unit_name = unit_map[unit]
            # Add 's' for plural
            if value > 1:
                unit_name += 's'
            subtitle = f"Last {value} {unit_name}"
        else:
            # It's a --from date (YYYYMMDD)
            try:
                from_date = datetime.strptime(date_label, "%Y%m%d")
                subtitle = f"From {from_date.strftime('%Y-%m-%d')}"
            except ValueError:
                subtitle = "Today"
    else:
        # Default: today
        subtitle = "Today"

    # Build panel content with period and totals
    panel_content = f"[{COLOR_MUTED}]Period: {subtitle}[/]"

    # Add total counts based on display flags
    if display_skills and display_subagents:
        panel_content += f"\n[{COLOR_MUTED}]Total Skill Calls: {stats.total_skills}[/]"
        panel_content += f"\n[{COLOR_MUTED}]Total Subagent Calls: {stats.total_subagents}[/]"
    elif display_skills:
        panel_content += f"\n[{COLOR_MUTED}]Total Skill Calls: {stats.total_skills}[/]"
    else:
        panel_content += f"\n[{COLOR_MUTED}]Total Subagent Calls: {stats.total_subagents}[/]"

    panel = Panel(
        panel_content,
        title=f"[bold {COLOR_PRIMARY}]ccpulse[/]",
        title_align="left",
        box=box.HEAVY,
        border_style=COLOR_PRIMARY,
        padding=(0, 2),
    )
    console.print()
    console.print(panel)

    # Limit to top 5 unless --full is specified
    limit = None if show_full else 5

    # Check if any data
    if stats.total_skills == 0 and stats.total_subagents == 0:
        console.print()
        console.print(f"[{COLOR_MUTED}]No custom skills or subagents used yet.[/]")
        console.print()
        console.print(f"[{COLOR_MUTED}]Register skills in .claude/settings.json[/]")
        console.print(f"[{COLOR_MUTED}]or create custom subagents to see stats here.[/]")
        return

    # Custom Subagents (show first)
    if display_subagents and stats.subagents:
        console.print()
        console.print(f"[bold {COLOR_PRIMARY}]CUSTOM SUBAGENT USAGE[/]")
        console.print(f"[{COLOR_MUTED}]{'─' * 60}[/]")

        # Sort by count (descending) and apply limit
        sorted_subagents = sorted(stats.subagents.items(), key=lambda x: x[1], reverse=True)
        if limit:
            sorted_subagents = sorted_subagents[:limit]

        max_count = max(item[1] for item in sorted_subagents) if sorted_subagents else 0

        # Calculate dynamic name width
        name_width = max(max(len(name) for name, _ in sorted_subagents), NAME_MIN_WIDTH)

        display_usage_list(sorted_subagents, max_count, name_width, BAR_WIDTH)

    # Skills (show second)
    if display_skills and stats.skills:
        console.print()
        console.print(f"[bold {COLOR_PRIMARY}]SKILL USAGE[/]")
        console.print(f"[{COLOR_MUTED}]{'─' * 60}[/]")

        # Sort by count (descending) and apply limit
        sorted_skills = sorted(stats.skills.items(), key=lambda x: x[1], reverse=True)
        if limit:
            sorted_skills = sorted_skills[:limit]

        max_count = max(item[1] for item in sorted_skills) if sorted_skills else 0

        # Calculate dynamic name width
        name_width = max(max(len(name) for name, _ in sorted_skills), NAME_MIN_WIDTH)

        display_usage_list(sorted_skills, max_count, name_width, BAR_WIDTH)

    console.print()
