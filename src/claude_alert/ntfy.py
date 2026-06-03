"""Send push notifications via ntfy.sh REST API."""

from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class NtfyMessage:
    """Immutable representation of an ntfy.sh notification message."""

    title: str
    body: str
    priority: int = 3
    tags: tuple[str, ...] = ()
    click_url: str | None = None


def send_notification(
    url: str,
    message: NtfyMessage,
    token: str | None = None,
) -> bool:
    """Send a notification to ntfy.sh.

    Returns True on success, False on any network or transport error.
    This function never raises; it is safe to call from hooks that
    must always exit 0.
    """
    try:
        data = message.body.encode("utf-8")
        headers: dict[str, str] = {
            "Title": message.title,
            "Priority": str(message.priority),
        }
        if message.tags:
            headers["Tags"] = ",".join(message.tags)
        if message.click_url:
            headers["Click"] = message.click_url
        if token:
            headers["Authorization"] = f"Bearer {token}"

        request = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method="POST",
        )
        urllib.request.urlopen(request, timeout=5)  # noqa: S310
    except (urllib.error.URLError, OSError, TimeoutError):
        return False
    else:
        return True
