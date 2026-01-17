"""Analyzer for Skills and Subagents usage."""

from collections import Counter
from dataclasses import dataclass

from .loader import ToolCall


# Built-in subagent types (not custom)
BUILTIN_SUBAGENTS = {
    'Explore',
    'Plan',
    'Bash',
    'general-purpose',
    'statusline-setup',
    'claude-code-guide',
}


@dataclass
class Stats:
    """Usage statistics for skills and subagents."""
    skills: dict[str, int]  # skill name -> count
    subagents: dict[str, int]  # subagent type -> count
    total_skills: int
    total_subagents: int


def analyze(tool_calls: list[ToolCall], include_project_prefix: bool = True) -> Stats:
    """Analyze tool calls for skills and subagents usage.

    Args:
        tool_calls: List of tool calls to analyze.
        include_project_prefix: If True, prepend [project] to names.
    """
    skills = Counter()
    subagents = Counter()

    for call in tool_calls:
        if call.tool_name == 'Skill':
            skill_name = call.tool_input.get('skill', 'unknown')
            if include_project_prefix:
                display_name = f"[{call.project}] {skill_name}"
            else:
                display_name = skill_name
            skills[display_name] += 1

        elif call.tool_name == 'Task':
            subagent_type = call.tool_input.get('subagent_type', '')
            # Only count custom subagents (not built-in)
            if subagent_type and subagent_type not in BUILTIN_SUBAGENTS:
                if include_project_prefix:
                    display_name = f"[{call.project}] {subagent_type}"
                else:
                    display_name = subagent_type
                subagents[display_name] += 1

    return Stats(
        skills=dict(skills.most_common()),
        subagents=dict(subagents.most_common()),
        total_skills=sum(skills.values()),
        total_subagents=sum(subagents.values()),
    )
