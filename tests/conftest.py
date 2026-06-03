"""Shared fixtures for claude_alert tests."""

from __future__ import annotations

import pytest

from claude_alert.config import NtfyConfig


@pytest.fixture()
def ntfy_config() -> NtfyConfig:
    """Return a sample NtfyConfig for testing."""
    return NtfyConfig(
        topic="test-topic",
        server="https://ntfy.sh",
        token=None,
    )


@pytest.fixture()
def ntfy_config_with_token() -> NtfyConfig:
    """Return a NtfyConfig with an auth token."""
    return NtfyConfig(
        topic="test-topic",
        server="https://ntfy.sh",
        token="tk_test_secret",
    )
