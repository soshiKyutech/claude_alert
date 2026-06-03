"""Tests for claude_alert.config."""

from __future__ import annotations

from claude_alert.config import NtfyConfig, load_config


class TestNtfyConfig:
    """Tests for the NtfyConfig dataclass."""

    def test_url_property(self) -> None:
        # Arrange
        config = NtfyConfig(topic="my-topic", server="https://ntfy.sh", token=None)

        # Act
        url = config.url

        # Assert
        assert url == "https://ntfy.sh/my-topic"

    def test_url_strips_trailing_slash(self) -> None:
        # Arrange
        config = NtfyConfig(topic="my-topic", server="https://ntfy.sh/", token=None)

        # Act / Assert
        assert config.url == "https://ntfy.sh/my-topic"


class TestLoadConfig:
    """Tests for load_config()."""

    def test_returns_none_when_topic_missing(self, monkeypatch: object) -> None:
        # Arrange
        import pytest

        mp = pytest.MonkeyPatch()
        mp.delenv("CLAUDE_ALERT_NTFY_TOPIC", raising=False)
        mp.delenv("CLAUDE_ALERT_NTFY_SERVER", raising=False)
        mp.delenv("CLAUDE_ALERT_NTFY_TOKEN", raising=False)

        # Act
        result = load_config()

        # Assert
        assert result is None
        mp.undo()

    def test_returns_none_when_topic_empty(self, monkeypatch: object) -> None:
        import pytest

        mp = pytest.MonkeyPatch()
        mp.setenv("CLAUDE_ALERT_NTFY_TOPIC", "  ")

        result = load_config()

        assert result is None
        mp.undo()

    def test_returns_config_with_defaults(self, monkeypatch: object) -> None:
        import pytest

        mp = pytest.MonkeyPatch()
        mp.setenv("CLAUDE_ALERT_NTFY_TOPIC", "my-topic")
        mp.delenv("CLAUDE_ALERT_NTFY_SERVER", raising=False)
        mp.delenv("CLAUDE_ALERT_NTFY_TOKEN", raising=False)

        result = load_config()

        assert result is not None
        assert result.topic == "my-topic"
        assert result.server == "https://ntfy.sh"
        assert result.token is None
        mp.undo()

    def test_empty_server_env_falls_back_to_default(self, monkeypatch: object) -> None:
        # The wrapper script exports CLAUDE_ALERT_NTFY_SERVER="" when the
        # user only configures a topic; an empty value must use the default.
        import pytest

        mp = pytest.MonkeyPatch()
        mp.setenv("CLAUDE_ALERT_NTFY_TOPIC", "my-topic")
        mp.setenv("CLAUDE_ALERT_NTFY_SERVER", "")
        mp.setenv("CLAUDE_ALERT_NTFY_TOKEN", "")

        result = load_config()

        assert result is not None
        assert result.server == "https://ntfy.sh"
        assert result.url == "https://ntfy.sh/my-topic"
        assert result.token is None
        mp.undo()

    def test_returns_config_with_custom_server_and_token(
        self, monkeypatch: object
    ) -> None:
        import pytest

        mp = pytest.MonkeyPatch()
        mp.setenv("CLAUDE_ALERT_NTFY_TOPIC", "my-topic")
        mp.setenv("CLAUDE_ALERT_NTFY_SERVER", "https://custom.ntfy.example.com")
        mp.setenv("CLAUDE_ALERT_NTFY_TOKEN", "tk_secret")

        result = load_config()

        assert result is not None
        assert result.server == "https://custom.ntfy.example.com"
        assert result.token == "tk_secret"
        mp.undo()
