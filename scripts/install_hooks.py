#!/usr/bin/env python3
"""Install claude_alert hooks into Claude Code settings.

Reads ~/.claude/settings.json (creates it if absent), backs it up to
~/.claude/settings.json.bak, then merges Notification and Stop hook
entries.  Existing hooks are preserved; duplicate commands are skipped.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

HOOK_ENTRIES: list[tuple[str, str]] = [
    ("Notification", str(SCRIPTS_DIR / "notify.sh")),
    ("Stop", str(SCRIPTS_DIR / "stop.sh")),
]

TIMEOUT = 10


def _ensure_hook(
    settings: dict,  # type: ignore[type-arg]
    event_name: str,
    command: str,
) -> bool:
    """Add a hook entry if not already present.  Returns True if added."""
    hooks = settings.setdefault("hooks", {})
    event_list: list[dict] = hooks.setdefault(event_name, [])  # type: ignore[type-arg]

    # Each element is an object with a "hooks" array.
    # We look for (or create) the first matcher-object and merge into it.
    if not event_list:
        event_list.append({"hooks": []})

    matcher = event_list[0]
    hook_list: list[dict] = matcher.setdefault("hooks", [])  # type: ignore[type-arg]

    # Duplicate check: skip if the same command is already registered.
    for existing in hook_list:
        if existing.get("command") == command:
            return False

    hook_list.append({"type": "command", "command": command, "timeout": TIMEOUT})
    return True


def main() -> None:
    """Entry point for the hook installer."""
    settings_path = Path.home() / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing settings or start fresh.
    if settings_path.exists():
        with open(settings_path, encoding="utf-8") as fh:
            settings: dict = json.load(fh)  # type: ignore[type-arg]
    else:
        settings = {}

    # Back up before modifying.
    if settings_path.exists():
        backup_path = settings_path.with_suffix(".json.bak")
        shutil.copy2(settings_path, backup_path)
        print(f"Backed up to {backup_path}")

    added = 0
    for event_name, command in HOOK_ENTRIES:
        if _ensure_hook(settings, event_name, command):
            print(f"Added {event_name} hook: {command}")
            added += 1
        else:
            print(f"Skipped (already present) {event_name} hook: {command}")

    with open(settings_path, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2)
        fh.write("\n")

    print(f"\nDone. {added} hook(s) added to {settings_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
