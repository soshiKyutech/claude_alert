#!/usr/bin/env python3
"""Claude Code Notification hook -- send push alerts via ntfy.sh.

This module is designed to be run as:
    python3 -m claude_alert.hooks.notification

It reads JSON from stdin (Claude Code hook contract), formats a
notification, and sends it to ntfy.sh.  It **always** exits 0 so
it never blocks Claude Code.
"""

from __future__ import annotations

import json
import sys

from claude_alert.config import load_config
from claude_alert.formatter import format_notification_event
from claude_alert.ntfy import NtfyMessage, send_notification


def main() -> None:
    """Entry point for the Notification hook."""
    try:
        payload = json.load(sys.stdin)
        config = load_config()
        if config is None:
            sys.exit(0)

        cwd: str = payload.get("cwd", "")
        message: str = payload.get("message", "")
        notification_type: str = payload.get("notification_type", "")

        result = format_notification_event(cwd, message, notification_type)
        if result is None:
            sys.exit(0)

        title, body, priority, tags = result
        ntfy_message = NtfyMessage(
            title=title,
            body=body,
            priority=priority,
            tags=tags,
        )
        send_notification(config.url, ntfy_message, config.token)
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
