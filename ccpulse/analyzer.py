"""Analyzer for Skills and Subagents quality metrics."""

from collections import defaultdict
from dataclasses import dataclass

from .loader import ToolExecution


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
class ToolQuality:
    """Quality metrics for a single tool (skill or subagent)."""
    name: str
    success_count: int
    failure_count: int
    incomplete_count: int
    total_count: int
    success_rate: float  # 0.0 to 1.0


@dataclass
class QualityStats:
    """Quality statistics for skills and subagents."""
    skills: list[ToolQuality]
    subagents: list[ToolQuality]

    def get_problematic(self, threshold: float) -> tuple[list[ToolQuality], list[ToolQuality]]:
        """Get tools with success rate below threshold.

        Args:
            threshold: Success rate threshold (e.g., 0.80 for 80%)

        Returns:
            Tuple of (problematic_skills, problematic_subagents)
        """
        problematic_skills = [s for s in self.skills if s.success_rate < threshold]
        problematic_subagents = [s for s in self.subagents if s.success_rate < threshold]
        return problematic_skills, problematic_subagents


def analyze_quality(
    executions: list[ToolExecution],
    include_project_prefix: bool = True
) -> QualityStats:
    """Analyze tool executions for quality metrics.

    Args:
        executions: List of tool executions to analyze.
        include_project_prefix: If True, prepend [project] to names.

    Returns:
        QualityStats with success rates and counts for each tool.
    """
    # Track counts by tool name
    skills_data = defaultdict(lambda: {'success': 0, 'failure': 0, 'incomplete': 0})
    subagents_data = defaultdict(lambda: {'success': 0, 'failure': 0, 'incomplete': 0})

    for execution in executions:
        if execution.tool_name == 'Skill':
            skill_name = execution.tool_input.get('skill', 'unknown')
            if include_project_prefix:
                display_name = f"[{execution.project}] {skill_name}"
            else:
                display_name = skill_name

            if not execution.has_result:
                skills_data[display_name]['incomplete'] += 1
            elif execution.is_error:
                skills_data[display_name]['failure'] += 1
            else:
                skills_data[display_name]['success'] += 1

        elif execution.tool_name == 'Task':
            subagent_type = execution.tool_input.get('subagent_type', '')
            # Only count custom subagents (not built-in)
            if subagent_type and subagent_type not in BUILTIN_SUBAGENTS:
                if include_project_prefix:
                    display_name = f"[{execution.project}] {subagent_type}"
                else:
                    display_name = subagent_type

                if not execution.has_result:
                    subagents_data[display_name]['incomplete'] += 1
                elif execution.is_error:
                    subagents_data[display_name]['failure'] += 1
                else:
                    subagents_data[display_name]['success'] += 1

    # Convert to ToolQuality objects
    def build_tool_quality(name: str, data: dict) -> ToolQuality:
        success = data['success']
        failure = data['failure']
        incomplete = data['incomplete']
        total = success + failure + incomplete

        # Calculate success rate (only from completed executions)
        completed = success + failure
        if completed > 0:
            success_rate = success / completed
        else:
            success_rate = 0.0

        return ToolQuality(
            name=name,
            success_count=success,
            failure_count=failure,
            incomplete_count=incomplete,
            total_count=total,
            success_rate=success_rate,
        )

    # Build sorted lists (worst first)
    skills = [build_tool_quality(name, data) for name, data in skills_data.items()]
    skills.sort(key=lambda x: x.success_rate)

    subagents = [build_tool_quality(name, data) for name, data in subagents_data.items()]
    subagents.sort(key=lambda x: x.success_rate)

    return QualityStats(skills=skills, subagents=subagents)
