"""JSONL file loader for Claude Code session data."""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


@dataclass
class ToolCall:
    """Represents a tool call from a session."""
    timestamp: datetime
    tool_name: str
    tool_input: dict


def get_claude_projects_dir() -> Path:
    """Get the Claude projects directory path."""
    return Path.home() / ".claude" / "projects"


def parse_timestamp(ts_str: str) -> datetime:
    """Parse ISO-8601 timestamp to datetime."""
    if ts_str.endswith('Z'):
        ts_str = ts_str[:-1] + '+00:00'
    return datetime.fromisoformat(ts_str)


def load_tool_calls(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[ToolCall]:
    """Load tool calls from Claude projects directory within date range.

    Args:
        start_date: Start date (inclusive). If None, defaults to today at 00:00:00.
        end_date: End date (inclusive). If None, defaults to today at 23:59:59.
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

    tool_calls = []

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        for jsonl_file in project_dir.glob('*.jsonl'):
            try:
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
                                        tool_calls.append(ToolCall(
                                            timestamp=timestamp,
                                            tool_name=item.get('name', ''),
                                            tool_input=item.get('input', {}),
                                        ))
                        except (json.JSONDecodeError, ValueError):
                            continue
            except (IOError, OSError):
                continue

    tool_calls.sort(key=lambda x: x.timestamp)
    return tool_calls
