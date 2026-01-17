# ccpulse

Claude Code usage statistics analyzer - visualize your local Claude Code session data in the terminal.

## Installation

```bash
pip install ccpulse
```

## Usage

```bash
# Show project costs (default)
ccpulse

# Show all statistics
ccpulse all

# Individual views
ccpulse languages    # Language breakdown
ccpulse tools        # Tool usage stats
ccpulse subagents    # Subagent usage
ccpulse hours        # Hourly activity
ccpulse projects     # Project details

# Filter by time
ccpulse --days 7     # Last 7 days only
```

## Features

- **Project costs** - See estimated costs per project
- **Language stats** - Which languages you work with most
- **Tool usage** - Read, Edit, Bash, etc. breakdown
- **Hourly activity** - When you code most
- **Subagent tracking** - Explore, Plan agent usage

## Data Source

Reads from `~/.claude/projects/` directory where Claude Code stores session data.

## License

MIT
