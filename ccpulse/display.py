"""Terminal display using rich library."""

import sys
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from .analyzer import QualityStats, ToolQuality

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

console = Console(force_terminal=True)

# Colors
COLOR_PRIMARY = "#E07A5F"
COLOR_SECONDARY = "#81B29A"
COLOR_MUTED = "#6B7280"
COLOR_TEXT = "#F4F3EE"
COLOR_CRITICAL = "#EF4444"    # Red for <50%
COLOR_WARNING = "#F59E0B"     # Yellow for 50-69%
COLOR_SUCCESS = "#10B981"     # Green for >=80%

BAR_CHAR = "█"
BAR_WIDTH = 10      # Width of the bar chart for success rates
NAME_MIN_WIDTH = 15 # Minimum width for name column


def get_rate_color(success_rate: float) -> str:
    """Get color based on success rate."""
    if success_rate < 0.50:
        return COLOR_CRITICAL  # Red
    elif success_rate < 0.70:
        return COLOR_WARNING   # Yellow
    else:
        return COLOR_TEXT      # Normal (70-79%)


def make_success_bar(success_rate: float, width: int = 10) -> str:
    """Create a bar representing success rate percentage."""
    filled = int(success_rate * width)
    return BAR_CHAR * filled


def display_quality_list(
    tools: list[ToolQuality],
    name_width: int,
    bar_width: int,
):
    """Display quality metrics as plain text with bars and colors."""
    for tool in tools:
        # Format rate percentage
        rate_pct = f"{int(tool.success_rate * 100)}%"

        # Create bar based on success rate
        bar = make_success_bar(tool.success_rate, bar_width)

        # Format success/total ratio
        completed = tool.success_count + tool.failure_count
        ratio = f"{tool.success_count}/{completed}"

        # Add incomplete note if any
        incomplete_note = f"  ({tool.incomplete_count} incomplete)" if tool.incomplete_count > 0 else ""

        # Get color based on rate
        color = get_rate_color(tool.success_rate)

        # Format line
        line = f"{tool.name:<{name_width}} {rate_pct:>4}  {bar:<{bar_width}} {ratio:>6}{incomplete_note}"
        console.print(f"[{color}]{line}[/]")


def display_quality(
    stats: QualityStats,
    threshold: float = 0.80,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    date_label: str | None = None,
    show_skills: bool = False,
    show_subagents: bool = False,
    project_name: str | None = None,
):
    """Display quality metrics for skills and subagents.

    Args:
        stats: Quality statistics to display
        threshold: Success rate threshold (0.80 = 80%)
        start_date: Start date for the period
        end_date: End date for the period
        date_label: Label for the date range
        show_skills: If True, show only skills
        show_subagents: If True, show only subagents
        project_name: Name of the project being analyzed
    """
    # Determine what to show
    display_skills = not show_subagents  # Show skills unless --subagents is specified
    display_subagents = not show_skills  # Show subagents unless --skills is specified

    # Get problematic tools
    problematic_skills, problematic_subagents = stats.get_problematic(threshold)

    # Filter based on display flags
    if not display_skills:
        problematic_skills = []
    if not display_subagents:
        problematic_subagents = []

    total_problematic = len(problematic_skills) + len(problematic_subagents)

    # Parse date label for display
    if date_label:
        import re
        if re.match(r'^\d+[dwm]$', date_label.lower()):
            value = int(date_label[:-1])
            unit = date_label[-1].lower()
            unit_map = {'d': 'day', 'w': 'week', 'm': 'month'}
            unit_name = unit_map[unit]
            if value > 1:
                unit_name += 's'
            subtitle = f"Last {value} {unit_name}"
        else:
            try:
                from_date = datetime.strptime(date_label, "%Y%m%d")
                subtitle = f"From {from_date.strftime('%Y-%m-%d')}"
            except ValueError:
                subtitle = "Today"
    else:
        subtitle = "Today"

    # Check if any data exists
    has_any_data = len(stats.skills) > 0 or len(stats.subagents) > 0

    if not has_any_data:
        # No data case
        panel_content = f"[{COLOR_MUTED}]Period: {subtitle}[/]"
        if project_name:
            panel_content += f"\n[{COLOR_MUTED}]Project: {project_name}[/]"
        panel_content += f"\n[{COLOR_MUTED}]Status: No data available[/]"

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
        console.print()
        console.print(f"[{COLOR_MUTED}]No custom skills or subagents used in this period.[/]")
        console.print()
        return

    # Build panel content
    panel_content = f"[{COLOR_MUTED}]Period: {subtitle}[/]"
    if project_name:
        panel_content += f"\n[{COLOR_MUTED}]Project: {project_name}[/]"

    if total_problematic == 0:
        # All good case
        panel_content += f"\n[{COLOR_SUCCESS}]Status: All tools working well![/]"
    else:
        # Problematic tools found
        tool_word = "tool" if total_problematic == 1 else "tools"
        panel_content += f"\n[{COLOR_WARNING}]Status: {total_problematic} problematic {tool_word} found[/]"

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

    if total_problematic == 0:
        # All good message
        console.print()
        console.print(f"[{COLOR_SUCCESS}]✅ No problematic skills or subagents detected.[/]")
        console.print()
        console.print(f"[{COLOR_MUTED}]   All executions have ≥{int(threshold * 100)}% success rate.[/]")
        console.print()
        return

    # Display problematic skills
    if display_skills and problematic_skills:
        console.print()
        console.print(f"[bold {COLOR_WARNING}]⚠️  SKILLS WITH ISSUES[/]")
        console.print(f"[{COLOR_MUTED}]{'─' * 60}[/]")

        # Calculate dynamic name width
        name_width = max(max(len(tool.name) for tool in problematic_skills), NAME_MIN_WIDTH)

        display_quality_list(problematic_skills, name_width, BAR_WIDTH)

    # Display problematic subagents
    if display_subagents and problematic_subagents:
        console.print()
        console.print(f"[bold {COLOR_WARNING}]⚠️  SUBAGENTS WITH ISSUES[/]")
        console.print(f"[{COLOR_MUTED}]{'─' * 60}[/]")

        # Calculate dynamic name width
        name_width = max(max(len(tool.name) for tool in problematic_subagents), NAME_MIN_WIDTH)

        display_quality_list(problematic_subagents, name_width, BAR_WIDTH)

    console.print()
