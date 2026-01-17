<div align="center">

# 📊 ccpulse

<p>
  <img src="https://img.shields.io/pypi/v/ccpulse?color=E07A5F&style=flat-square" alt="PyPI version">
  <img src="https://img.shields.io/pypi/pyversions/ccpulse?color=81B29A&style=flat-square" alt="Python versions">
  <img src="https://img.shields.io/pypi/l/ccpulse?color=F2CC8F&style=flat-square" alt="License">
  <img src="https://img.shields.io/pypi/dm/ccpulse?color=F4A261&style=flat-square" alt="Downloads">
</p>

**Track your custom Skills and Subagents usage in Claude Code**

*Analyze. Measure. Optimize your AI workflow.*

[Installation](#-installation) • [Usage](#-usage) • [Features](#-features) • [Examples](#-example-output)

</div>

---

## 🎯 What it does

ccpulse analyzes your local Claude Code session data and provides insights into:

- **🎨 Skills** - Your custom slash commands (like `/commit`, `/review-pr`)
- **🤖 Custom Subagents** - Your registered subagent types
- **📁 Multi-Project Support** - Track usage across all your projects or filter by current project

## 📦 Installation

```bash
pip install ccpulse
```

## 🚀 Quick Start

```bash
# View today's stats across all projects
ccpulse

# Filter to current project only
ccpulse --here

# View last 7 days
ccpulse 7d

# Current project, last month
ccpulse 1m --here
```

## 💡 Usage

### Basic Commands

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
```

### Project Filtering

```bash
# Show only current project (no [project] prefix)
ccpulse --here

# Combine with time periods
ccpulse 7d --here

# Combine with filters
ccpulse --here --skills
ccpulse 1m --here --subagents
```

### Display Options

```bash
# Show only skills (top 5)
ccpulse 7d -s

# Show only subagents (top 5)
ccpulse 1m -a

# Show all skills (no limit)
ccpulse -s -f

# Combine options
ccpulse 2w -a -f
```

## ⚙️ Options

### Date Period (positional argument)

| Argument | Description |
|----------|-------------|
| *(none)* | Today only (default) |
| `7d` | Last 7 days |
| `2w` | Last 2 weeks |
| `1m` | Last 1 month |
| `20260101` | From specific date to today (YYYYMMDD format) |

### Filtering

| Option | Short | Description |
|--------|-------|-------------|
| `--skills` | `-s` | Show only custom skills |
| `--subagents` | `-a` | Show only custom subagents |
| `--full` | `-f` | Show all results (default: top 5) |
| `--here` | `-h` | Show only current project (removes `[project]` prefix) |

### Other

| Option | Short | Description |
|--------|-------|-------------|
| `--version` | `-v` | Show version and exit |
| `--help` | | Show help message |

## 📊 Example Output

### Multi-Project View (Default)

```
╭────────────────────────────────── ccpulse ──────────────────────────────────╮
│  Period: Last 7 days                                                        │
│  Total Skill Calls: 95                                                      │
│  Total Subagent Calls: 69                                                   │
╰─────────────────────────────────────────────────────────────────────────────╯

SKILL USAGE
────────────────────────────────────────────────────────────
[ccpulse] commit         ███████████████████████████  42
[binpack] optimize       ████████████████████          28
[ccpulse] review-pr      ██████████████                18
[boxhub] deploy          ████████                      12

CUSTOM SUBAGENT USAGE
────────────────────────────────────────────────────────────
[ccpulse] test-runner    ██████████████████████████████  20
[binpack] analyzer       ██████████████████████          15
[ccpulse] debugger       ████████████████                11
```

### Single Project View (`--here`)

```
╭────────────────────────────────── ccpulse ──────────────────────────────────╮
│  Period: Last 7 days                                                        │
│  Project: ccpulse                                                           │
│  Total Skill Calls: 60                                                      │
│  Total Subagent Calls: 31                                                   │
╰─────────────────────────────────────────────────────────────────────────────╯

SKILL USAGE
────────────────────────────────────────────────────────────
commit          ███████████████████████████████  42
review-pr       ██████████████                   18

CUSTOM SUBAGENT USAGE
────────────────────────────────────────────────────────────
test-runner     ██████████████████████████████  20
debugger        ████████████████                11
```

## ✨ Features

- 🎯 **Zero Configuration** - Works out of the box with Claude Code
- 📁 **Multi-Project Support** - Track usage across all projects or focus on one
- 🎨 **Beautiful Output** - Rich terminal UI with progress bars
- 🚀 **Fast & Lightweight** - Analyzes thousands of sessions instantly
- 🔒 **Privacy First** - All data stays on your machine
- 📊 **Flexible Filtering** - Filter by time, project, skills, or subagents

## 🔒 Data Source

Reads from `~/.claude/projects/` where Claude Code stores local session data.

**Privacy Note:** No data is sent anywhere - everything stays on your machine.

## 📋 Requirements

- Python 3.10+
- Claude Code CLI installed

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests

Visit the [GitHub repository](https://github.com/dukbong/ccpulse) to get started.

## 📄 License

MIT License - see LICENSE file for details

---

<div align="center">

**Made with ❤️ for the Claude Code community**

[⭐ Star on GitHub](https://github.com/dukbong/ccpulse) • [🐛 Report Bug](https://github.com/dukbong/ccpulse/issues) • [💡 Request Feature](https://github.com/dukbong/ccpulse/issues)

</div>
