#!/usr/bin/env python3
"""Claude Code Stop hook -- send task-completion alerts via ntfy.sh.

This module is designed to be run as:
    python3 -m claude_alert.hooks.stop

It reads JSON from stdin (Claude Code hook contract), formats a
stop notification, and sends it to ntfy.sh.  It **always** exits 0
so it never blocks Claude Code.
"""

from __future__ import annotations

import json
import sys

from claude_alert.config import load_config
from claude_alert.formatter import format_stop_event
from claude_alert.ntfy import NtfyMessage, send_notification


def main() -> None:
    """Entry point for the Stop hook."""
    try:
        payload = json.load(sys.stdin)
        config = load_config()
        if config is None:
            sys.exit(0)

        cwd: str = payload.get("cwd", "")
        # Claude Code's Stop hook exposes the final assistant text as
        # `last_assistant_message` (there is no `stop_reason` field).
        last_message: str = payload.get("last_assistant_message", "")

        title, body, priority, tags = format_stop_event(cwd, last_message)
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
