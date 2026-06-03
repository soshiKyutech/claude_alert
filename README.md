# claude_alert

Push notifications for Claude Code via [ntfy.sh](https://ntfy.sh).

## Overview

`claude_alert` uses Claude Code's hook system to send Android/iOS push
notifications when Claude needs your attention:

- **Notification hook** -- fires when Claude is waiting for permission or
  user selection.
- **Stop hook** -- fires when Claude finishes a task.

```
Claude Code  --(hook JSON on stdin)-->  claude_alert  --(HTTP POST)-->  ntfy.sh  -->  Android/iOS
```

## Setup

### 1. Install dependencies

```bash
uv sync --all-extras
```

### 2. Configure ntfy

```bash
mkdir -p ~/.config/claude_alert
cp .env.example ~/.config/claude_alert/config
# Edit the file and set CLAUDE_ALERT_NTFY_TOPIC to a random string
```

Install the [ntfy Android app](https://play.google.com/store/apps/details?id=io.heckel.ntfy)
(or iOS app) and subscribe to the same topic.

### 3. Register hooks

```bash
python3 scripts/install_hooks.py
```

This adds entries to `~/.claude/settings.json` so Claude Code calls the
hooks automatically.

## Manual test

```bash
# Test notification hook
echo '{"cwd":"/tmp/myproject","message":"Allow read?","notification_type":"permission_prompt"}' \
  | CLAUDE_ALERT_NTFY_TOPIC=test-topic python3 -m claude_alert.hooks.notification

# Test stop hook
echo '{"cwd":"/tmp/myproject","last_assistant_message":"task_complete"}' \
  | CLAUDE_ALERT_NTFY_TOPIC=test-topic python3 -m claude_alert.hooks.stop
```

## Development

```bash
uv sync --all-extras
uv run ruff check .
uv run ruff format --check .
uv run pytest -v --cov=src --cov-report=term-missing
```
