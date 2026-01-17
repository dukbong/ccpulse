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


def load_tool_calls(days: int | None = None) -> list[ToolCall]:
    """Load all tool calls from Claude projects directory."""
    projects_dir = get_claude_projects_dir()
    if not projects_dir.exists():
        return []

    cutoff = None
    if days is not None:
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

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
                            if cutoff and timestamp < cutoff:
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
