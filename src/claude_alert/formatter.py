"""Format Claude Code hook events into notification messages."""

from __future__ import annotations

import os

# Notification types that should be silently skipped.
_SKIP_TYPES = frozenset({"idle_prompt", "auth_success"})


def extract_project_name(cwd: str) -> str:
    """Extract a human-readable project name from a working directory path."""
    name = os.path.basename(cwd) if cwd else ""
    return name or "unknown"


def format_notification_event(
    cwd: str,
    message: str,
    notification_type: str,
) -> tuple[str, str, int, tuple[str, ...]] | None:
    """Format a Notification hook event for ntfy.sh.

    Returns a (title, body, priority, tags) tuple, or None if the
    notification type should be silently skipped.
    """
    if notification_type in _SKIP_TYPES:
        return None

    project = extract_project_name(cwd)

    if notification_type == "permission_prompt":
        return (
            f"[{project}] Permission Required",
            message,
            4,
            ("warning",),
        )

    if notification_type == "elicitation_dialog":
        return (
            f"[{project}] Selection Required",
            message,
            4,
            ("question",),
        )

    # Unknown or empty type: use a sensible default.
    return (
        f"[{project}] Notification",
        message,
        3,
        ("bell",),
    )


def format_stop_event(
    cwd: str,
    last_message: str,
) -> tuple[str, str, int, tuple[str, ...]]:
    """Format a Stop hook event for ntfy.sh.

    `last_message` is the final assistant message text (the Stop hook's
    `last_assistant_message` field). Always returns a
    (title, body, priority, tags) tuple.
    """
    project = extract_project_name(cwd)
    body = (
        last_message
        if last_message
        else "Claude Code has finished and is ready for input."
    )
    return (
        f"[{project}] Task Complete",
        body,
        3,
        ("white_check_mark",),
    )
