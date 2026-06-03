#!/bin/sh
# Claude Code Notification hook wrapper.
# Sources user config and delegates to the Python hook module.

CONFIG_FILE="${HOME}/.config/claude_alert/config"

if [ -f "${CONFIG_FILE}" ]; then
    # shellcheck disable=SC1090
    . "${CONFIG_FILE}"
fi

export CLAUDE_ALERT_NTFY_TOPIC="${CLAUDE_ALERT_NTFY_TOPIC:-}"
export CLAUDE_ALERT_NTFY_SERVER="${CLAUDE_ALERT_NTFY_SERVER:-}"
export CLAUDE_ALERT_NTFY_TOKEN="${CLAUDE_ALERT_NTFY_TOKEN:-}"

export PYTHONPATH="/mnt/m2ssd/workspace/claude_ws/git/claude_alert/src"

exec python3 -m claude_alert.hooks.notification
