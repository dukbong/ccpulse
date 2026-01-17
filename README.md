# ccpulse

<p align="center">
  <img src="https://img.shields.io/pypi/v/ccpulse?color=E07A5F&style=flat-square" alt="PyPI version">
  <img src="https://img.shields.io/pypi/pyversions/ccpulse?color=81B29A&style=flat-square" alt="Python versions">
  <img src="https://img.shields.io/pypi/l/ccpulse?color=F2CC8F&style=flat-square" alt="License">
</p>

<p align="center">
  <b>Track your custom Skills and Subagents usage in Claude Code</b>
</p>

---

## What it does

ccpulse analyzes your local Claude Code session data and shows:

- **Skills** - Your registered slash commands (like /commit, /review-pr)
- **Custom Subagents** - Your registered subagent types

## Installation

```bash
pip install ccpulse
```

## Usage

```bash
# Today (default)
ccpulse

# Last 7 days
ccpulse 7d

# Last 2 weeks
ccpulse 2w

# Last 1 month
ccpulse 1m

# From specific date (YYYYMMDD)
ccpulse 20260101

# Show only skills (top 5)
ccpulse 7d -s

# Show only subagents (top 5)
ccpulse 1m -a

# Show all skills (no limit)
ccpulse -s -f

# Combine options
ccpulse 2w -a -f
```

## Options

### Date Period (positional argument)
- (none) - Today only (default)
- `7d` - Last 7 days
- `2w` - Last 2 weeks
- `1m` - Last 1 month
- `20260101` - From specific date to today (YYYYMMDD format)

### Filtering
- `--skills` / `-s` - Show only custom skills
- `--subagents` / `-a` - Show only custom subagents
- `--full` / `-f` - Show all results (default: top 5). Requires `--skills` or `--subagents`

### Other
- `--version` / `-v` - Show version and exit
- `--help` - Show help message

## Example Output

```
┌─ ccpulse ───────────────────────────────┐
│  Today                                  │
└─────────────────────────────────────────┘

Custom Subagents
────────────────────────────────────────
┌─────────────┬──────┬───────────────────┐
│ Subagent    │ Uses │                   │
├─────────────┼──────┼───────────────────┤
│ test-runner │   15 │ ===============   │
│ linter      │    8 │ ========          │
│ validator   │    5 │ =====             │
└─────────────┴──────┴───────────────────┘
Showing top 5: 28 calls

Skills
────────────────────────────────────────
┌─────────────┬──────┬───────────────────┐
│ Skill       │ Uses │                   │
├─────────────┼──────┼───────────────────┤
│ commit      │   42 │ ===============   │
│ review-pr   │   18 │ ======            │
│ test        │    7 │ ==                │
│ deploy      │    5 │ =                 │
│ rollback    │    3 │ =                 │
└─────────────┴──────┴───────────────────┘
Showing top 5: 75 calls
```

## Data Source

Reads from `~/.claude/projects/` where Claude Code stores local session data. No data is sent anywhere - everything stays on your machine.

## Requirements

- Python 3.10+
- Claude Code CLI installed

## License

MIT

---

<p align="center">
  Made for the Claude Code community
</p>
