"""Statistics analyzer for Claude Code session data."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone

from .loader import SessionMessage


# File extension to language mapping
EXTENSION_TO_LANGUAGE = {
    # Python
    '.py': 'Python',
    '.pyi': 'Python',
    '.pyw': 'Python',

    # JavaScript/TypeScript
    '.js': 'JavaScript',
    '.jsx': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    '.mjs': 'JavaScript',
    '.cjs': 'JavaScript',

    # Java/JVM
    '.java': 'Java',
    '.kt': 'Kotlin',
    '.kts': 'Kotlin',
    '.scala': 'Scala',
    '.groovy': 'Groovy',
    '.gradle': 'Gradle',

    # Web
    '.html': 'HTML',
    '.htm': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.sass': 'Sass',
    '.less': 'Less',
    '.vue': 'Vue',
    '.svelte': 'Svelte',

    # Systems
    '.c': 'C',
    '.h': 'C',
    '.cpp': 'C++',
    '.cc': 'C++',
    '.cxx': 'C++',
    '.hpp': 'C++',
    '.rs': 'Rust',
    '.go': 'Go',

    # Shell/Scripts
    '.sh': 'Shell',
    '.bash': 'Shell',
    '.zsh': 'Shell',
    '.fish': 'Shell',
    '.ps1': 'PowerShell',
    '.bat': 'Batch',
    '.cmd': 'Batch',

    # Data/Config
    '.json': 'JSON',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.toml': 'TOML',
    '.xml': 'XML',
    '.ini': 'INI',
    '.env': 'Env',

    # Documentation
    '.md': 'Markdown',
    '.mdx': 'MDX',
    '.rst': 'reStructuredText',
    '.txt': 'Text',

    # Other languages
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.swift': 'Swift',
    '.m': 'Objective-C',
    '.cs': 'C#',
    '.fs': 'F#',
    '.vb': 'Visual Basic',
    '.r': 'R',
    '.jl': 'Julia',
    '.lua': 'Lua',
    '.pl': 'Perl',
    '.ex': 'Elixir',
    '.exs': 'Elixir',
    '.erl': 'Erlang',
    '.hs': 'Haskell',
    '.clj': 'Clojure',
    '.sql': 'SQL',
    '.graphql': 'GraphQL',
    '.proto': 'Protocol Buffers',

    # Build/Config files
    '.dockerfile': 'Dockerfile',
    '.makefile': 'Makefile',
}


@dataclass
class LanguageStats:
    """Statistics about language usage."""
    language_counts: dict[str, int]  # language -> file count
    total_files: int


@dataclass
class HourlyStats:
    """Statistics about hourly activity."""
    hour_counts: dict[int, int]  # hour (0-23) -> message count
    weekday_counts: dict[int, int]  # weekday (0=Mon, 6=Sun) -> message count
    total_messages: int


@dataclass
class CostInfo:
    """Cost information for a project or total."""
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    total_cost_usd: float = 0.0


@dataclass
class ProjectStats:
    """Statistics about project usage."""
    project_sessions: dict[str, set[str]]  # project -> set of session IDs
    project_messages: dict[str, int]  # project -> message count
    project_costs: dict[str, CostInfo]  # project -> cost info
    total_projects: int
    total_sessions: int
    total_cost: CostInfo


@dataclass
class ToolStats:
    """Statistics about tool usage."""
    tool_counts: dict[str, int]  # tool name -> usage count
    subagent_counts: dict[str, int]  # subagent type -> usage count
    total_calls: int


# Claude pricing (per 1M tokens) - Sonnet 4 pricing as default
# Note: Actual pricing may vary by model
PRICING = {
    'input': 3.0,           # $3 per 1M input tokens
    'output': 15.0,         # $15 per 1M output tokens
    'cache_read': 0.30,     # $0.30 per 1M cache read tokens (90% discount)
    'cache_creation': 3.75, # $3.75 per 1M cache creation tokens (25% premium)
}


def calculate_cost(cost_info: CostInfo) -> float:
    """Calculate total cost in USD from token counts."""
    cost = 0.0
    cost += (cost_info.input_tokens / 1_000_000) * PRICING['input']
    cost += (cost_info.output_tokens / 1_000_000) * PRICING['output']
    cost += (cost_info.cache_read_tokens / 1_000_000) * PRICING['cache_read']
    cost += (cost_info.cache_creation_tokens / 1_000_000) * PRICING['cache_creation']
    return cost


def extract_file_paths(msg: SessionMessage) -> list[str]:
    """Extract file paths from tool_use blocks in a message."""
    file_paths = []

    for tool_use in msg.tool_uses:
        tool_input = tool_use.get('input', {})

        # Read, Write, Edit tools have 'file_path'
        if 'file_path' in tool_input:
            file_paths.append(tool_input['file_path'])

        # Glob tool has 'pattern' (not a real file, skip)
        # Grep tool has 'path' (directory, skip)

    return file_paths


def get_language_from_path(file_path: str) -> str | None:
    """Determine language from file path."""
    # Handle special files
    file_lower = file_path.lower()
    basename = file_path.split('/')[-1].split('\\')[-1].lower()

    # Special file names
    if basename == 'dockerfile':
        return 'Dockerfile'
    if basename == 'makefile':
        return 'Makefile'
    if basename.startswith('.') and not '.' in basename[1:]:
        return 'Config'  # Dotfiles like .gitignore

    # Extract extension
    if '.' in basename:
        ext = '.' + basename.rsplit('.', 1)[-1]
        return EXTENSION_TO_LANGUAGE.get(ext)

    return None


def analyze_languages(messages: list[SessionMessage]) -> LanguageStats:
    """Analyze language usage from session messages."""
    file_set = set()  # Track unique files
    language_counts = Counter()

    for msg in messages:
        if msg.message_type != 'assistant':
            continue

        for file_path in extract_file_paths(msg):
            if file_path in file_set:
                continue

            file_set.add(file_path)
            language = get_language_from_path(file_path)
            if language:
                language_counts[language] += 1

    return LanguageStats(
        language_counts=dict(language_counts.most_common()),
        total_files=len(file_set),
    )


def analyze_hours(messages: list[SessionMessage]) -> HourlyStats:
    """Analyze hourly activity patterns."""
    hour_counts = Counter()
    weekday_counts = Counter()

    for msg in messages:
        # Convert UTC to local time
        local_time = msg.timestamp.astimezone()
        hour_counts[local_time.hour] += 1
        weekday_counts[local_time.weekday()] += 1

    return HourlyStats(
        hour_counts=dict(hour_counts),
        weekday_counts=dict(weekday_counts),
        total_messages=len(messages),
    )


def analyze_projects(messages: list[SessionMessage]) -> ProjectStats:
    """Analyze project usage."""
    project_sessions: dict[str, set[str]] = defaultdict(set)
    project_messages: dict[str, int] = Counter()
    project_costs: dict[str, CostInfo] = defaultdict(CostInfo)

    # Total cost tracking
    total_cost = CostInfo()

    for msg in messages:
        if msg.cwd:
            project_sessions[msg.cwd].add(msg.session_id)
            project_messages[msg.cwd] += 1

            # Accumulate token usage for assistant messages
            if msg.message_type == 'assistant':
                usage = msg.usage
                # Get or create CostInfo for this project
                if msg.cwd not in project_costs:
                    project_costs[msg.cwd] = CostInfo()

                cost_info = project_costs[msg.cwd]
                cost_info.input_tokens += usage.input_tokens
                cost_info.output_tokens += usage.output_tokens
                cost_info.cache_read_tokens += usage.cache_read_tokens
                cost_info.cache_creation_tokens += usage.cache_creation_tokens

                # Also accumulate total
                total_cost.input_tokens += usage.input_tokens
                total_cost.output_tokens += usage.output_tokens
                total_cost.cache_read_tokens += usage.cache_read_tokens
                total_cost.cache_creation_tokens += usage.cache_creation_tokens

    # Calculate costs for each project
    for project, cost_info in project_costs.items():
        cost_info.total_cost_usd = calculate_cost(cost_info)

    # Calculate total cost
    total_cost.total_cost_usd = calculate_cost(total_cost)

    # Convert defaultdict to regular dict
    project_sessions_dict = {k: v for k, v in project_sessions.items()}

    # Count unique sessions across all projects
    all_sessions = set()
    for sessions in project_sessions.values():
        all_sessions.update(sessions)

    return ProjectStats(
        project_sessions=project_sessions_dict,
        project_messages=dict(project_messages),
        project_costs=dict(project_costs),
        total_projects=len(project_sessions),
        total_sessions=len(all_sessions),
        total_cost=total_cost,
    )


def analyze_tools(messages: list[SessionMessage]) -> ToolStats:
    """Analyze tool usage from session messages."""
    tool_counts = Counter()
    subagent_counts = Counter()

    for msg in messages:
        if msg.message_type != 'assistant':
            continue

        for tool_use in msg.tool_uses:
            tool_name = tool_use.get('name', 'Unknown')
            tool_counts[tool_name] += 1

            # Extract subagent type for Task tool
            if tool_name == 'Task':
                tool_input = tool_use.get('input', {})
                subagent_type = tool_input.get('subagent_type', 'unknown')
                subagent_counts[subagent_type] += 1

    return ToolStats(
        tool_counts=dict(tool_counts.most_common()),
        subagent_counts=dict(subagent_counts.most_common()),
        total_calls=sum(tool_counts.values()),
    )


@dataclass
class OverallStats:
    """Overall usage statistics."""
    total_messages: int
    total_sessions: int
    total_projects: int
    date_range: tuple[datetime, datetime] | None
    languages: LanguageStats
    hours: HourlyStats
    projects: ProjectStats
    tools: ToolStats


def analyze_all(messages: list[SessionMessage]) -> OverallStats:
    """Compute all statistics from messages."""
    if not messages:
        return OverallStats(
            total_messages=0,
            total_sessions=0,
            total_projects=0,
            date_range=None,
            languages=LanguageStats({}, 0),
            hours=HourlyStats({}, {}, 0),
            projects=ProjectStats({}, {}, {}, 0, 0, CostInfo()),
            tools=ToolStats({}, {}, 0),
        )

    languages = analyze_languages(messages)
    hours = analyze_hours(messages)
    projects = analyze_projects(messages)
    tools = analyze_tools(messages)

    # Get date range
    first_ts = messages[0].timestamp
    last_ts = messages[-1].timestamp

    return OverallStats(
        total_messages=len(messages),
        total_sessions=projects.total_sessions,
        total_projects=projects.total_projects,
        date_range=(first_ts, last_ts),
        languages=languages,
        hours=hours,
        projects=projects,
        tools=tools,
    )
