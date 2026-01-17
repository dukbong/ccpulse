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
# Show all time stats
ccpulse

# Last 7 days
ccpulse --days 7

# Last 30 days
ccpulse -d 30
```

## Example Output

```
                ┌── ccpulse ──┐
                │  All time   │
                └─────────────┘

Skills
────────────────────────────────────────
┌─────────────┬──────┬───────────────────┐
│ Skill       │ Uses │                   │
├─────────────┼──────┼───────────────────┤
│ commit      │   42 │ ===============   │
│ review-pr   │   18 │ ======            │
│ test        │    7 │ ==                │
└─────────────┴──────┴───────────────────┘
67 total calls

Custom Subagents
────────────────────────────────────────
┌─────────────┬──────┬───────────────────┐
│ Subagent    │ Uses │                   │
├─────────────┼──────┼───────────────────┤
│ test-runner │   15 │ ===============   │
│ linter      │    8 │ ========          │
└─────────────┴──────┴───────────────────┘
23 total calls
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
