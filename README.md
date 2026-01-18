<div align="center">

# 📊 ccpulse

<p>
  <img src="https://img.shields.io/pypi/v/ccpulse?color=E07A5F&style=flat-square" alt="PyPI version">
  <img src="https://img.shields.io/pypi/pyversions/ccpulse?color=81B29A&style=flat-square" alt="Python versions">
  <img src="https://img.shields.io/pypi/l/ccpulse?color=F2CC8F&style=flat-square" alt="License">
  <img src="https://img.shields.io/pypi/dm/ccpulse?color=F4A261&style=flat-square" alt="Downloads">
</p>

**Track quality metrics for custom Skills and Subagents in Claude Code**

*Find broken tools fast. Focus on quality, not quantity.*

[Installation](#-installation) • [Usage](#-usage) • [Features](#-features) • [Examples](#-example-output)

</div>

---

## 🎯 What it does

ccpulse analyzes your Claude Code session data to identify **failing** Skills and Subagents:

- **🎨 Skills** - Track success rates for custom slash commands
- **🤖 Custom Subagents** - Monitor custom subagent reliability
- **⚠️ Quality Focus** - Shows only tools with issues (< 80% success rate by default)
- **📁 Multi-Project Support** - Track quality across all projects or filter by current project

## 💡 Why ccpulse?

**The Core Insight:** Using a skill 100 times means nothing if it fails 90 times.

Version 1.0.0 represents a **complete pivot** from counting usage to tracking quality:

### What Changed
- ❌ **Removed:** Usage counts and frequency tracking
- ✅ **Added:** Success rates, failure tracking, and error detection
- 🎯 **Philosophy:** Do one thing well - find broken tools fast

### Why Quality Matters
- **Catch issues early** - Know when skills or subagents start failing
- **Focus on reliability** - Success rate matters more than call count
- **Actionable insights** - See exactly which tools need attention
- **Zero noise** - Only shows problematic tools (≥80% success rate = hidden)

## 📦 Installation

```bash
pip install ccpulse
```

## 🚀 Quick Start

```bash
# Check quality across all projects (today)
ccpulse

# Check current project only
ccpulse --here

# Check last 7 days
ccpulse 7d

# Adjust threshold (show tools below 90% success rate)
ccpulse --threshold 90
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
# Show only current project
ccpulse --here

# Combine with time periods
ccpulse 7d --here

# Combine with filters
ccpulse --here --skills
ccpulse 1m --here --subagents
```

### Quality Thresholds

```bash
# Default: show tools with <80% success rate
ccpulse

# Stricter: show tools with <90% success rate
ccpulse --threshold 90

# More lenient: show tools with <50% success rate
ccpulse --threshold 50

# Show all tools (even 0% success rate)
ccpulse --threshold 100
```

### Display Filters

```bash
# Show only skills with issues
ccpulse -s

# Show only subagents with issues
ccpulse -a

# Combine filters
ccpulse 7d --skills --threshold 90
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
| `--threshold` | `-t` | Success rate threshold (0-100, default: 80) |
| `--here` | `-h` | Show only current project |

### Other

| Option | Short | Description |
|--------|-------|-------------|
| `--version` | `-v` | Show version and exit |
| `--help` | | Show help message |

## 📊 Example Output

### Problematic Tools Found

```
╭──────────────── ccpulse ────────────────╮
│  Period: Last 7 days                    │
│  Project: ccpulse                       │
│  Status: 2 problematic tools found      │
╰─────────────────────────────────────────╯

⚠️  SKILLS WITH ISSUES
────────────────────────────────────────
deploy          45%  █████      9/20  (1 incomplete)
test-report     62%  ██████     5/8
```

**Color Coding:**
- 🔴 **Red** (< 50%): Critical - needs immediate attention
- 🟡 **Yellow** (50-69%): Warning - investigate soon
- ⚪ **Normal** (70-79%): Below threshold but not critical

### All Tools Working Well

```
╭──────────────── ccpulse ────────────────╮
│  Period: Last 7 days                    │
│  Status: All tools working well!        │
╰─────────────────────────────────────────╯

✅ No problematic skills or subagents detected.

   All executions have ≥80% success rate.
```

### Multi-Project View

```
╭──────────────── ccpulse ────────────────╮
│  Period: Last 30 days                   │
│  Status: 3 problematic tools found      │
╰─────────────────────────────────────────╯

⚠️  SKILLS WITH ISSUES
────────────────────────────────────────
[ccpulse] deploy         45%  █████      9/20
[binpack] test-runner    58%  ██████    11/19  (2 incomplete)

⚠️  SUBAGENTS WITH ISSUES
────────────────────────────────────────
[boxhub] analyzer        72%  ███████   18/25
```

## ✨ Features

- 🎯 **Quality Over Quantity** - Focus on success rates, not call counts
- 🚨 **Smart Filtering** - Only shows problematic tools (< 80% by default)
- 🎨 **Color-Coded Output** - Instantly see severity (red/yellow/normal)
- 📊 **Actionable Metrics** - Success rate %, success/failure counts, incomplete tracking
- 📁 **Multi-Project Support** - Track quality across all projects or focus on one
- 🔒 **Privacy First** - All data stays on your machine
- 🚀 **Fast & Lightweight** - Two-pass JSONL parsing for accurate results
- ⚙️ **Configurable Threshold** - Adjust sensitivity with `--threshold`

## 🔄 Migration from 0.x

**Breaking Changes in 1.0.0:**

ccpulse has completely pivoted from usage tracking to quality tracking.

### What's Removed
- ❌ Usage counts and frequency metrics
- ❌ Top-N display (`--full` option)
- ❌ "Total calls" statistics

### What's New
- ✅ Success rate percentage (primary metric)
- ✅ Success/failure counts (e.g., "18/20")
- ✅ Incomplete execution tracking
- ✅ `--threshold` option to adjust sensitivity
- ✅ Color-coded severity indicators

### What Stays the Same
- ✅ Time period filtering (`7d`, `2w`, `1m`)
- ✅ Project filtering (`--here`)
- ✅ Display filters (`--skills`, `--subagents`)
- ✅ All data stays local

### Upgrade Guide

```bash
# Update to 1.0.0
pip install --upgrade ccpulse

# Old usage (0.x) - showed top 5 most used skills
ccpulse 7d --skills

# New usage (1.0.0) - shows skills with <80% success rate
ccpulse 7d --skills

# Adjust threshold if needed
ccpulse 7d --skills --threshold 90
```

**No backward compatibility** - This is a complete pivot. If you need usage counting, stay on version 0.3.1.

## 🔒 Data Source

Reads from `~/.claude/projects/` where Claude Code stores local session data.

**How It Works:**
1. **Pass 1:** Extract all tool executions with their IDs
2. **Pass 2:** Match tool results to determine success/failure
3. **Analysis:** Calculate success rates and filter by threshold

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
