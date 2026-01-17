# ccpulse

<p align="center">
  <img src="https://img.shields.io/pypi/v/ccpulse?color=E07A5F&style=flat-square" alt="PyPI version">
  <img src="https://img.shields.io/pypi/pyversions/ccpulse?color=81B29A&style=flat-square" alt="Python versions">
  <img src="https://img.shields.io/pypi/l/ccpulse?color=F2CC8F&style=flat-square" alt="License">
  <img src="https://img.shields.io/pypi/dm/ccpulse?color=6B7280&style=flat-square" alt="Downloads">
</p>

<p align="center">
  <b>Claude Code usage statistics analyzer</b><br>
  Visualize your local Claude Code session data in the terminal
</p>

---

## Installation

```bash
pip install ccpulse
```

## Quick Start

```bash
# See your project costs (default view)
ccpulse
```

```
                    ┌───────────────────────────┐
                    │          ccpulse          │
                    │    All time statistics    │
                    └───────────────────────────┘

Projects
──────────────────────────────────────────────────
┌─────────────┬──────────┬────────┬──────────────┐
│ Project     │ Sessions │   Cost │              │
├─────────────┼──────────┼────────┼──────────────┤
│ my-app      │       12 │ $45.20 │ ==========   │
│ api-server  │        8 │ $23.15 │ =====        │
│ scripts     │        3 │  $5.40 │ =            │
└─────────────┴──────────┴────────┴──────────────┘
3 projects  Total: $73.75
```

## Commands

| Command | Description |
|---------|-------------|
| `ccpulse` | Show project costs (default) |
| `ccpulse all` | Show all statistics |
| `ccpulse languages` | Language breakdown |
| `ccpulse tools` | Tool usage (Read, Edit, Bash...) |
| `ccpulse subagents` | Subagent usage (Explore, Plan...) |
| `ccpulse hours` | Hourly activity pattern |
| `ccpulse projects` | Project details |

### Options

```bash
ccpulse --days 7      # Last 7 days only
ccpulse --days 30     # Last 30 days
ccpulse -d 1          # Today only
```

## Features

### Project Cost Tracking
See estimated costs per project based on token usage.

### Language Statistics
```
┌────────────┬───────┬────────────────────────┐
│ Language   │ Files │                        │
├────────────┼───────┼────────────────────────┤
│ Python     │    89 │ ==================     │
│ TypeScript │    45 │ =========              │
│ Java       │    23 │ ====                   │
└────────────┴───────┴────────────────────────┘
```

### Tool Usage Analytics
Track which Claude Code tools you use most: Read, Edit, Write, Bash, Glob, Grep, and more.

### Hourly Activity
Discover your coding patterns - when are you most productive?

### Subagent Tracking
See how often you use Explore and Plan agents.

## Data Source

ccpulse reads from `~/.claude/projects/` where Claude Code stores local session data. No data is sent anywhere - everything stays on your machine.

## Requirements

- Python 3.10+
- Claude Code CLI installed and used

## Contributing

Issues and PRs welcome at [GitHub](https://github.com/dukbong/ccpulse)

## License

MIT

---

<p align="center">
  Made for the Claude Code community
</p>
