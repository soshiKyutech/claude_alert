"""Configuration management for claude_alert."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class NtfyConfig:
    """Immutable configuration for ntfy.sh notifications."""

    topic: str
    server: str
    token: str | None

    @property
    def url(self) -> str:
        """Return the full ntfy.sh endpoint URL."""
        return f"{self.server.rstrip('/')}/{self.topic}"


def load_config() -> NtfyConfig | None:
    """Load ntfy configuration from environment variables.

    Returns None if the topic is not set or empty, which signals
    that notifications are disabled.
    """
    topic = os.environ.get("CLAUDE_ALERT_NTFY_TOPIC", "").strip()
    if not topic:
        return None

    server = os.environ.get("CLAUDE_ALERT_NTFY_SERVER", "").strip() or "https://ntfy.sh"
    token = os.environ.get("CLAUDE_ALERT_NTFY_TOKEN", "").strip() or None

    return NtfyConfig(topic=topic, server=server, token=token)
