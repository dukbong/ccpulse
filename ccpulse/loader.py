"""JSONL file loader for Claude Code session data."""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator
import os


@dataclass
class ToolExecution:
    """Represents a tool execution with its result status."""
    timestamp: datetime
    tool_name: str
    tool_input: dict
    project: str  # e.g., "ccpulse", "binpack"
    tool_use_id: str
    is_error: bool | None  # None if no result available
    has_result: bool


def get_claude_projects_dir() -> Path:
    """Get the Claude projects directory path."""
    return Path.home() / ".claude" / "projects"


def parse_timestamp(ts_str: str) -> datetime:
    """Parse ISO-8601 timestamp to datetime."""
    if ts_str.endswith('Z'):
        ts_str = ts_str[:-1] + '+00:00'
    return datetime.fromisoformat(ts_str)


def extract_project_name(project_dir_name: str) -> str:
    """Extract clean project name from directory name.

    Examples:
        C--ccpulse -> ccpulse
        C--Users-jkmo2 -> Users-jkmo2
    """
    import re
    match = re.match(r'^[A-Z]--(.+)$', project_dir_name)
    if match:
        return match.group(1)
    return project_dir_name


def get_current_project_dir() -> str | None:
    """Get project directory name for current working directory."""
    cwd = Path.cwd()
    projects_dir = get_claude_projects_dir()

    if not projects_dir.exists():
        return None

    # Match cwd basename against project names
    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        project_name = extract_project_name(project_dir.name)
        if cwd.name.lower() == project_name.lower():
            return project_dir.name
        if project_name.lower() in str(cwd).lower():
            return project_dir.name

    return None


def load_tool_executions(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    project_filter: str | None = None,
) -> list[ToolExecution]:
    """Load tool executions from Claude projects directory within date range.

    Uses two-pass parsing to correlate tool_use with tool_result entries.

    Args:
        start_date: Start date (inclusive). If None, defaults to today at 00:00:00.
        end_date: End date (inclusive). If None, defaults to today at 23:59:59.
        project_filter: Project directory name to filter by (e.g., "C--ccpulse"). If None, all projects.
    """
    projects_dir = get_claude_projects_dir()
    if not projects_dir.exists():
        return []

    # Default to today if no dates provided
    if start_date is None and end_date is None:
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = today
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif start_date is None:
        # If only end_date provided, no start limit
        start_date = datetime.min.replace(tzinfo=timezone.utc)
    elif end_date is None:
        # If only start_date provided, set end to today
        end_date = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        # Both dates provided, normalize them to include full days
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)

    # Two-pass parsing: Pass 1 - Build dict of executions from tool_use
    executions_dict: dict[str, ToolExecution] = {}

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        # Apply project filter
        if project_filter and project_dir.name != project_filter:
            continue

        # Extract project name
        project_name = extract_project_name(project_dir.name)

        for jsonl_file in project_dir.glob('*.jsonl'):
            try:
                # Quick filter: skip files modified before start_date
                file_mtime = datetime.fromtimestamp(os.path.getmtime(jsonl_file), tz=timezone.utc)
                if file_mtime < start_date:
                    continue

                # Pass 1: Extract tool_use entries
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                            ts_str = data.get('timestamp')
                            if not ts_str:
                                continue

                            timestamp = parse_timestamp(ts_str)

                            # Filter by date range
                            if timestamp < start_date or timestamp > end_date:
                                continue

                            # Only process assistant messages
                            if data.get('type') != 'assistant':
                                continue

                            message = data.get('message', {})
                            content = message.get('content', [])

                            if isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and item.get('type') == 'tool_use':
                                        tool_use_id = item.get('id', '')
                                        if tool_use_id:
                                            executions_dict[tool_use_id] = ToolExecution(
                                                timestamp=timestamp,
                                                tool_name=item.get('name', ''),
                                                tool_input=item.get('input', {}),
                                                project=project_name,
                                                tool_use_id=tool_use_id,
                                                is_error=None,
                                                has_result=False,
                                            )
                        except (json.JSONDecodeError, ValueError):
                            continue

                # Pass 2: Update with tool_result entries
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)

                            # Only process user messages
                            if data.get('type') != 'user':
                                continue

                            message = data.get('message', {})
                            content = message.get('content', [])

                            if isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and item.get('type') == 'tool_result':
                                        tool_use_id = item.get('tool_use_id', '')
                                        if tool_use_id and tool_use_id in executions_dict:
                                            execution = executions_dict[tool_use_id]
                                            execution.has_result = True
                                            # Default to False if is_error field missing
                                            execution.is_error = item.get('is_error', False)
                        except (json.JSONDecodeError, ValueError):
                            continue

            except (IOError, OSError):
                continue

    # Convert dict to sorted list
    executions = list(executions_dict.values())
    executions.sort(key=lambda x: x.timestamp)
    return executions
