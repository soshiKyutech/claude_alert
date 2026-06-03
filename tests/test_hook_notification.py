"""Tests for claude_alert.hooks.notification."""

from __future__ import annotations

import io
import json
from unittest.mock import MagicMock, patch

from claude_alert.hooks.notification import main


class TestNotificationHook:
    """Tests for the Notification hook main()."""

    @patch("claude_alert.hooks.notification.send_notification", return_value=True)
    @patch("claude_alert.hooks.notification.load_config")
    def test_permission_prompt_sends_notification(
        self,
        mock_config: MagicMock,
        mock_send: MagicMock,
        ntfy_config: object,
        monkeypatch: object,
    ) -> None:
        """A permission_prompt event should trigger a notification."""
        import pytest

        mp = pytest.MonkeyPatch()

        # Arrange
        from claude_alert.config import NtfyConfig

        config = NtfyConfig(topic="test", server="https://ntfy.sh", token=None)
        mock_config.return_value = config

        payload = {
            "cwd": "/tmp/myproject",
            "message": "Allow read?",
            "notification_type": "permission_prompt",
        }
        mp.setattr("sys.stdin", io.StringIO(json.dumps(payload)))

        # Act
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Assert
        assert exc_info.value.code == 0
        mock_send.assert_called_once()
        msg = mock_send.call_args[0][1]
        assert msg.title == "[myproject] Permission Required"
        mp.undo()

    @patch("claude_alert.hooks.notification.send_notification", return_value=True)
    @patch("claude_alert.hooks.notification.load_config")
    def test_idle_prompt_skips_notification(
        self,
        mock_config: MagicMock,
        mock_send: MagicMock,
        ntfy_config: object,
        monkeypatch: object,
    ) -> None:
        """An idle_prompt event should be silently skipped."""
        import pytest

        mp = pytest.MonkeyPatch()

        from claude_alert.config import NtfyConfig

        config = NtfyConfig(topic="test", server="https://ntfy.sh", token=None)
        mock_config.return_value = config

        payload = {
            "cwd": "/tmp/proj",
            "message": "idle",
            "notification_type": "idle_prompt",
        }
        mp.setattr("sys.stdin", io.StringIO(json.dumps(payload)))

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mock_send.assert_not_called()
        mp.undo()

    @patch("claude_alert.hooks.notification.send_notification")
    @patch("claude_alert.hooks.notification.load_config", return_value=None)
    def test_no_config_exits_zero(
        self,
        mock_config: MagicMock,
        mock_send: MagicMock,
        monkeypatch: object,
    ) -> None:
        """When config is None (topic not set), exit 0 without sending."""
        import pytest

        mp = pytest.MonkeyPatch()

        payload = {
            "cwd": "/tmp/proj",
            "message": "hi",
            "notification_type": "permission_prompt",
        }
        mp.setattr("sys.stdin", io.StringIO(json.dumps(payload)))

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mock_send.assert_not_called()
        mp.undo()

    def test_invalid_json_exits_zero(self, monkeypatch: object) -> None:
        """Malformed stdin should not crash; exit 0."""
        import pytest

        mp = pytest.MonkeyPatch()
        mp.setattr("sys.stdin", io.StringIO("NOT JSON"))

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mp.undo()
