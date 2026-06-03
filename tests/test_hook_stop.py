"""Tests for claude_alert.hooks.stop."""

from __future__ import annotations

import io
import json
from unittest.mock import MagicMock, patch

from claude_alert.hooks.stop import main


class TestStopHook:
    """Tests for the Stop hook main()."""

    @patch("claude_alert.hooks.stop.send_notification", return_value=True)
    @patch("claude_alert.hooks.stop.load_config")
    def test_stop_event_sends_notification(
        self,
        mock_config: MagicMock,
        mock_send: MagicMock,
        monkeypatch: object,
    ) -> None:
        """A stop event should trigger a task-complete notification."""
        import pytest

        mp = pytest.MonkeyPatch()

        from claude_alert.config import NtfyConfig

        config = NtfyConfig(topic="test", server="https://ntfy.sh", token=None)
        mock_config.return_value = config

        payload = {
            "cwd": "/tmp/myproject",
            "last_assistant_message": "task_complete",
        }
        mp.setattr("sys.stdin", io.StringIO(json.dumps(payload)))

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mock_send.assert_called_once()
        msg = mock_send.call_args[0][1]
        assert msg.title == "[myproject] Task Complete"
        assert msg.body == "task_complete"
        mp.undo()

    @patch("claude_alert.hooks.stop.send_notification", return_value=True)
    @patch("claude_alert.hooks.stop.load_config")
    def test_empty_stop_reason_uses_default(
        self,
        mock_config: MagicMock,
        mock_send: MagicMock,
        monkeypatch: object,
    ) -> None:
        """An empty stop_reason should produce a default body."""
        import pytest

        mp = pytest.MonkeyPatch()

        from claude_alert.config import NtfyConfig

        config = NtfyConfig(topic="test", server="https://ntfy.sh", token=None)
        mock_config.return_value = config

        payload = {"cwd": "/tmp/proj", "last_assistant_message": ""}
        mp.setattr("sys.stdin", io.StringIO(json.dumps(payload)))

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        msg = mock_send.call_args[0][1]
        assert msg.body == "Claude Code has finished and is ready for input."
        mp.undo()

    @patch("claude_alert.hooks.stop.send_notification")
    @patch("claude_alert.hooks.stop.load_config", return_value=None)
    def test_no_config_exits_zero(
        self,
        mock_config: MagicMock,
        mock_send: MagicMock,
        monkeypatch: object,
    ) -> None:
        """When config is None, exit 0 without sending."""
        import pytest

        mp = pytest.MonkeyPatch()

        payload = {"cwd": "/tmp/proj", "last_assistant_message": "done"}
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
        mp.setattr("sys.stdin", io.StringIO("{broken"))

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0
        mp.undo()
