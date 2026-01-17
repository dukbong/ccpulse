"""Terminal display using rich library."""

import sys

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

BAR_CHAR = "="


def make_bar(value: int, max_value: int, width: int = 15) -> str:
    """Create a bar for the given value."""
    if max_value == 0:
        return ""
    filled = int((value / max_value) * width)
    return BAR_CHAR * filled


def display(stats: Stats, days: int | None = None):
    """Display skills and subagents usage."""
    # Header
    subtitle = f"Last {days} days" if days else "All time"
    panel = Panel(
        f"[{COLOR_MUTED}]{subtitle}[/]",
        title=f"[bold {COLOR_PRIMARY}]ccpulse[/]",
        box=box.ROUNDED,
        border_style=COLOR_PRIMARY,
        padding=(0, 2),
    )
    console.print()
    console.print(panel, justify="center")

    # Check if any data
    if stats.total_skills == 0 and stats.total_subagents == 0:
        console.print()
        console.print(f"[{COLOR_MUTED}]No custom skills or subagents used yet.[/]")
        console.print()
        console.print(f"[{COLOR_MUTED}]Register skills in .claude/settings.json[/]")
        console.print(f"[{COLOR_MUTED}]or create custom subagents to see stats here.[/]")
        return

    # Skills
    if stats.skills:
        console.print()
        console.print(f"[bold {COLOR_PRIMARY}]Skills[/]")
        console.print(f"[{COLOR_MUTED}]{'─' * 40}[/]")

        table = Table(
            show_header=True,
            header_style=f"bold {COLOR_TEXT}",
            box=box.ROUNDED,
            border_style=COLOR_MUTED,
            padding=(0, 1),
        )
        table.add_column("Skill", style=COLOR_TEXT)
        table.add_column("Uses", justify="right", style=COLOR_SECONDARY)
        table.add_column("", width=17)

        max_count = max(stats.skills.values()) if stats.skills else 0
        for skill, count in stats.skills.items():
            bar = make_bar(count, max_count)
            table.add_row(skill, str(count), f"[{COLOR_PRIMARY}]{bar}[/]")

        console.print(table)
        console.print(f"[{COLOR_MUTED}]{stats.total_skills} total calls[/]")

    # Subagents
    if stats.subagents:
        console.print()
        console.print(f"[bold {COLOR_PRIMARY}]Custom Subagents[/]")
        console.print(f"[{COLOR_MUTED}]{'─' * 40}[/]")

        table = Table(
            show_header=True,
            header_style=f"bold {COLOR_TEXT}",
            box=box.ROUNDED,
            border_style=COLOR_MUTED,
            padding=(0, 1),
        )
        table.add_column("Subagent", style=COLOR_TEXT)
        table.add_column("Uses", justify="right", style=COLOR_SECONDARY)
        table.add_column("", width=17)

        max_count = max(stats.subagents.values()) if stats.subagents else 0
        for subagent, count in stats.subagents.items():
            bar = make_bar(count, max_count)
            table.add_row(subagent, str(count), f"[{COLOR_PRIMARY}]{bar}[/]")

        console.print(table)
        console.print(f"[{COLOR_MUTED}]{stats.total_subagents} total calls[/]")

    console.print()
