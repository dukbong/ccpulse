"""JSONL file loader for Claude Code session data."""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


@dataclass
class TokenUsage:
    """Token usage for a message."""
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0


@dataclass
class SessionMessage:
    """Represents a single message from a Claude Code session."""
    timestamp: datetime
    session_id: str
    message_type: str  # 'user' or 'assistant'
    cwd: str | None
    git_branch: str | None
    content: list | str | None
    tool_uses: list[dict]  # Extracted tool_use blocks
    usage: TokenUsage = field(default_factory=TokenUsage)
    model: str | None = None


def get_claude_projects_dir() -> Path:
    """Get the Claude projects directory path."""
    home = Path.home()
    return home / ".claude" / "projects"


def parse_timestamp(ts_str: str) -> datetime:
    """Parse ISO-8601 timestamp to datetime."""
    # Handle format: 2026-01-17T03:17:37.304Z
    if ts_str.endswith('Z'):
        ts_str = ts_str[:-1] + '+00:00'
    return datetime.fromisoformat(ts_str)


def extract_tool_uses(content: list | str | None) -> list[dict]:
    """Extract tool_use blocks from message content."""
    tool_uses = []
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'tool_use':
                tool_uses.append(item)
    return tool_uses


def extract_usage(message: dict) -> TokenUsage:
    """Extract token usage from message."""
    usage_data = message.get('usage', {})
    return TokenUsage(
        input_tokens=usage_data.get('input_tokens', 0),
        output_tokens=usage_data.get('output_tokens', 0),
        cache_read_tokens=usage_data.get('cache_read_input_tokens', 0),
        cache_creation_tokens=usage_data.get('cache_creation_input_tokens', 0),
    )


def parse_jsonl_line(line: str) -> SessionMessage | None:
    """Parse a single JSONL line into a SessionMessage."""
    try:
        data = json.loads(line.strip())

        # Extract timestamp
        ts_str = data.get('timestamp')
        if not ts_str:
            return None
        timestamp = parse_timestamp(ts_str)

        # Extract other fields
        session_id = data.get('sessionId', '')
        message_type = data.get('type', '')
        cwd = data.get('cwd')
        git_branch = data.get('gitBranch')

        # Extract content and usage from message
        message = data.get('message', {})
        content = message.get('content') if isinstance(message, dict) else None
        model = message.get('model') if isinstance(message, dict) else None

        # Extract tool uses
        tool_uses = extract_tool_uses(content)

        # Extract token usage (for assistant messages)
        usage = extract_usage(message) if isinstance(message, dict) else TokenUsage()

        return SessionMessage(
            timestamp=timestamp,
            session_id=session_id,
            message_type=message_type,
            cwd=cwd,
            git_branch=git_branch,
            content=content,
            tool_uses=tool_uses,
            usage=usage,
            model=model,
        )
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


def load_session_file(file_path: Path) -> Iterator[SessionMessage]:
    """Load messages from a single JSONL session file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    msg = parse_jsonl_line(line)
                    if msg:
                        yield msg
    except (IOError, OSError):
        pass


def load_all_sessions(days: int | None = None) -> list[SessionMessage]:
    """Load all session messages from Claude projects directory.

    Args:
        days: If provided, only load messages from the last N days.

    Returns:
        List of all session messages, sorted by timestamp.
    """
    projects_dir = get_claude_projects_dir()
    if not projects_dir.exists():
        return []

    # Calculate cutoff time if days is specified
    cutoff = None
    if days is not None:
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    messages = []

    # Iterate through all project directories
    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue

        # Load all .jsonl files in the project directory
        for jsonl_file in project_dir.glob('*.jsonl'):
            for msg in load_session_file(jsonl_file):
                if cutoff is None or msg.timestamp >= cutoff:
                    messages.append(msg)

    # Sort by timestamp
    messages.sort(key=lambda m: m.timestamp)
    return messages


def decode_project_name(encoded_name: str) -> str:
    """Decode project directory name to original path.

    Example: 'C--binpack' -> 'C:\\binpack'
    """
    # Replace single dash with path separator, but handle double-dash
    # The encoding replaces path separators with '-'
    if os.name == 'nt':
        # Windows: C--binpack -> C:\binpack
        if len(encoded_name) >= 2 and encoded_name[1] == '-':
            # Looks like a Windows drive letter
            return encoded_name[0] + ':' + encoded_name[2:].replace('-', '\\')
    return encoded_name.replace('-', '/')
