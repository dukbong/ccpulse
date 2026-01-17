"""Terminal display using rich library."""

import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from .analyzer import OverallStats, LanguageStats, HourlyStats, ProjectStats, ToolStats, CostInfo

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

console = Console(force_terminal=True)

# Claude-inspired color palette
COLOR_PRIMARY = "#E07A5F"      # Warm coral/orange (Claude's signature)
COLOR_SECONDARY = "#81B29A"    # Sage green
COLOR_ACCENT = "#F2CC8F"       # Warm yellow
COLOR_MUTED = "#6B7280"        # Gray
COLOR_TEXT = "#F4F3EE"         # Off-white

# Bar character
BAR_CHAR = "="


def make_bar(value: int, max_value: int, width: int = 20) -> str:
    """Create a bar for the given value."""
    if max_value == 0:
        return ""
    filled = int((value / max_value) * width)
    return BAR_CHAR * filled


def section_title(title: str, icon: str = ""):
    """Print a section title with consistent styling."""
    if icon:
        console.print(f"\n[bold {COLOR_PRIMARY}]{icon} {title}[/]")
    else:
        console.print(f"\n[bold {COLOR_PRIMARY}]{title}[/]")
    console.print(f"[{COLOR_MUTED}]{'─' * 50}[/]")


def display_header(days: int | None = None):
    """Display the header panel."""
    if days:
        subtitle = f"Last {days} days"
    else:
        subtitle = "All time statistics"

    header_text = Text()
    header_text.append("ccpulse\n", style=f"bold {COLOR_PRIMARY}")
    header_text.append(subtitle, style=COLOR_MUTED)

    panel = Panel(
        header_text,
        box=box.ROUNDED,
        border_style=COLOR_PRIMARY,
        padding=(1, 4),
    )
    console.print()
    console.print(panel, justify="center")


def display_summary(stats: OverallStats):
    """Display overall summary."""
    if stats.date_range:
        first, last = stats.date_range
        date_range_str = f"{first.strftime('%Y-%m-%d')} to {last.strftime('%Y-%m-%d')}"
    else:
        date_range_str = "N/A"

    section_title("Overview")

    table = Table(
        show_header=False,
        box=None,
        padding=(0, 3),
        collapse_padding=True,
    )
    table.add_column("Label", style=COLOR_MUTED)
    table.add_column("Value", style=f"bold {COLOR_TEXT}")

    table.add_row("Messages", f"{stats.total_messages:,}")
    table.add_row("Sessions", f"{stats.total_sessions:,}")
    table.add_row("Projects", f"{stats.total_projects:,}")
    table.add_row("Period", date_range_str)

    console.print(table)


def display_languages(stats: LanguageStats, limit: int = 10):
    """Display language statistics table."""
    section_title("Languages")

    if not stats.language_counts:
        console.print(f"[{COLOR_MUTED}]No language data found[/]")
        return

    table = Table(
        show_header=True,
        header_style=f"bold {COLOR_TEXT}",
        box=box.ROUNDED,
        border_style=COLOR_MUTED,
        padding=(0, 1),
    )
    table.add_column("Language", style=COLOR_TEXT)
    table.add_column("Files", justify="right", style=COLOR_SECONDARY)
    table.add_column("", width=22)

    max_count = max(stats.language_counts.values()) if stats.language_counts else 0

    for i, (language, count) in enumerate(stats.language_counts.items()):
        if i >= limit:
            break
        bar = make_bar(count, max_count, width=18)
        table.add_row(language, str(count), f"[{COLOR_PRIMARY}]{bar}[/]")

    console.print(table)
    console.print(f"[{COLOR_MUTED}]{stats.total_files} unique files[/]")


def display_hours(stats: HourlyStats):
    """Display hourly activity chart."""
    section_title("Hours")

    if not stats.hour_counts:
        console.print(f"[{COLOR_MUTED}]No activity data found[/]")
        return

    max_count = max(stats.hour_counts.values()) if stats.hour_counts else 0

    for hour in range(24):
        count = stats.hour_counts.get(hour, 0)
        bar = make_bar(count, max_count, width=28)
        hour_label = f"{hour:02d}"

        if count > 0:
            console.print(
                f"[{COLOR_MUTED}]{hour_label}[/] [{COLOR_PRIMARY}]{bar}[/] "
                f"[{COLOR_SECONDARY}]{count:,}[/]"
            )
        else:
            console.print(f"[{COLOR_MUTED}]{hour_label}[/]")


def display_weekdays(stats: HourlyStats):
    """Display weekday activity."""
    section_title("Weekdays")

    if not stats.weekday_counts:
        console.print(f"[{COLOR_MUTED}]No activity data found[/]")
        return

    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    max_count = max(stats.weekday_counts.values()) if stats.weekday_counts else 0

    for day in range(7):
        count = stats.weekday_counts.get(day, 0)
        bar = make_bar(count, max_count, width=28)
        day_label = weekday_names[day]

        if count > 0:
            console.print(
                f"[{COLOR_MUTED}]{day_label}[/] [{COLOR_PRIMARY}]{bar}[/] "
                f"[{COLOR_SECONDARY}]{count:,}[/]"
            )
        else:
            console.print(f"[{COLOR_MUTED}]{day_label}[/]")


def display_projects(stats: ProjectStats, limit: int = 10):
    """Display project statistics table with costs."""
    section_title("Projects")

    if not stats.project_messages:
        console.print(f"[{COLOR_MUTED}]No project data found[/]")
        return

    table = Table(
        show_header=True,
        header_style=f"bold {COLOR_TEXT}",
        box=box.ROUNDED,
        border_style=COLOR_MUTED,
        padding=(0, 1),
    )
    table.add_column("Project", style=COLOR_TEXT)
    table.add_column("Sessions", justify="right", style=COLOR_MUTED)
    table.add_column("Cost", justify="right", style=COLOR_ACCENT)
    table.add_column("", width=14)

    # Sort by cost (descending)
    sorted_projects = sorted(
        stats.project_costs.items(),
        key=lambda x: x[1].total_cost_usd,
        reverse=True
    )

    # If no cost data, fall back to sorting by messages
    if not sorted_projects:
        sorted_projects = [
            (p, CostInfo()) for p in sorted(
                stats.project_messages.keys(),
                key=lambda x: stats.project_messages[x],
                reverse=True
            )
        ]

    max_cost = max((c.total_cost_usd for _, c in sorted_projects), default=0)

    for i, (project, cost_info) in enumerate(sorted_projects):
        if i >= limit:
            break

        session_count = len(stats.project_sessions.get(project, set()))
        bar = make_bar(int(cost_info.total_cost_usd * 100), int(max_cost * 100), width=10) if max_cost > 0 else ""

        # Shorten long project paths
        display_path = project
        if len(display_path) > 30:
            display_path = "..." + display_path[-27:]

        cost_str = f"${cost_info.total_cost_usd:.2f}"

        table.add_row(
            display_path,
            str(session_count),
            cost_str,
            f"[{COLOR_PRIMARY}]{bar}[/]"
        )

    console.print(table)

    # Show total cost
    total = stats.total_cost
    console.print(
        f"[{COLOR_MUTED}]{stats.total_projects} projects[/]  "
        f"[bold {COLOR_ACCENT}]Total: ${total.total_cost_usd:.2f}[/]"
    )


def display_tools(stats: ToolStats, limit: int = 15, show_subagents: bool = True):
    """Display tool usage statistics table."""
    section_title("Tools")

    if not stats.tool_counts:
        console.print(f"[{COLOR_MUTED}]No tool usage data found[/]")
        return

    table = Table(
        show_header=True,
        header_style=f"bold {COLOR_TEXT}",
        box=box.ROUNDED,
        border_style=COLOR_MUTED,
        padding=(0, 1),
    )
    table.add_column("Tool", style=COLOR_TEXT)
    table.add_column("Calls", justify="right", style=COLOR_SECONDARY)
    table.add_column("", width=22)

    max_count = max(stats.tool_counts.values()) if stats.tool_counts else 0

    for i, (tool_name, count) in enumerate(stats.tool_counts.items()):
        if i >= limit:
            break
        bar = make_bar(count, max_count, width=18)
        table.add_row(tool_name, f"{count:,}", f"[{COLOR_PRIMARY}]{bar}[/]")

    console.print(table)
    console.print(f"[{COLOR_MUTED}]{stats.total_calls:,} total calls[/]")

    if show_subagents and stats.subagent_counts:
        console.print()
        display_subagents(stats)


def display_subagents(stats: ToolStats):
    """Display subagent usage statistics."""
    section_title("Subagents")

    if not stats.subagent_counts:
        console.print(f"[{COLOR_MUTED}]No subagent data found[/]")
        return

    table = Table(
        show_header=True,
        header_style=f"bold {COLOR_TEXT}",
        box=box.ROUNDED,
        border_style=COLOR_MUTED,
        padding=(0, 1),
    )
    table.add_column("Agent", style=COLOR_TEXT)
    table.add_column("Calls", justify="right", style=COLOR_SECONDARY)
    table.add_column("", width=22)

    max_count = max(stats.subagent_counts.values()) if stats.subagent_counts else 0

    for subagent, count in stats.subagent_counts.items():
        bar = make_bar(count, max_count, width=18)
        table.add_row(subagent, str(count), f"[{COLOR_ACCENT}]{bar}[/]")

    console.print(table)


def display_all(stats: OverallStats, days: int | None = None):
    """Display all statistics."""
    display_header(days)

    if stats.total_messages == 0:
        console.print(f"\n[{COLOR_ACCENT}]No data found.[/]")
        console.print(f"[{COLOR_MUTED}]Expected data in ~/.claude/projects/[/]")
        return

    display_summary(stats)
    display_languages(stats.languages)
    display_tools(stats.tools)
    display_hours(stats.hours)
    display_weekdays(stats.hours)
    display_projects(stats.projects)
    console.print()


def display_no_data():
    """Display message when no data is found."""
    console.print(f"\n[{COLOR_ACCENT}]No Claude Code session data found.[/]")
    console.print()
    console.print(f"[{COLOR_MUTED}]Expected location:[/]")
    console.print(f"[{COLOR_MUTED}]  ~/.claude/projects/<project>/<session>.jsonl[/]")
