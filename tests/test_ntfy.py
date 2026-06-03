"""Tests for claude_alert.ntfy."""

from __future__ import annotations

import urllib.error
from unittest.mock import MagicMock, patch

from claude_alert.ntfy import NtfyMessage, send_notification


class TestNtfyMessage:
    """Tests for the NtfyMessage dataclass."""

    def test_defaults(self) -> None:
        msg = NtfyMessage(title="Hello", body="World")
        assert msg.priority == 3
        assert msg.tags == ()
        assert msg.click_url is None


class TestSendNotification:
    """Tests for send_notification()."""

    @patch("claude_alert.ntfy.urllib.request.urlopen")
    def test_success_returns_true(self, mock_urlopen: MagicMock) -> None:
        # Arrange
        mock_urlopen.return_value = MagicMock()
        message = NtfyMessage(title="T", body="B")

        # Act
        result = send_notification("https://ntfy.sh/topic", message)

        # Assert
        assert result is True
        mock_urlopen.assert_called_once()

    @patch("claude_alert.ntfy.urllib.request.urlopen")
    def test_timeout_returns_false(self, mock_urlopen: MagicMock) -> None:
        # Arrange
        mock_urlopen.side_effect = TimeoutError("timed out")
        message = NtfyMessage(title="T", body="B")

        # Act
        result = send_notification("https://ntfy.sh/topic", message)

        # Assert
        assert result is False

    @patch("claude_alert.ntfy.urllib.request.urlopen")
    def test_url_error_returns_false(self, mock_urlopen: MagicMock) -> None:
        # Arrange
        mock_urlopen.side_effect = urllib.error.URLError("fail")
        message = NtfyMessage(title="T", body="B")

        # Act
        result = send_notification("https://ntfy.sh/topic", message)

        # Assert
        assert result is False

    @patch("claude_alert.ntfy.urllib.request.urlopen")
    def test_sends_authorization_header(self, mock_urlopen: MagicMock) -> None:
        # Arrange
        mock_urlopen.return_value = MagicMock()
        message = NtfyMessage(title="T", body="B")

        # Act
        send_notification("https://ntfy.sh/topic", message, token="tk_abc")

        # Assert
        request = mock_urlopen.call_args[0][0]
        assert request.get_header("Authorization") == "Bearer tk_abc"

    @patch("claude_alert.ntfy.urllib.request.urlopen")
    def test_sends_tags_as_comma_separated(self, mock_urlopen: MagicMock) -> None:
        # Arrange
        mock_urlopen.return_value = MagicMock()
        message = NtfyMessage(title="T", body="B", tags=("warning", "skull"))

        # Act
        send_notification("https://ntfy.sh/topic", message)

        # Assert
        request = mock_urlopen.call_args[0][0]
        assert request.get_header("Tags") == "warning,skull"

    @patch("claude_alert.ntfy.urllib.request.urlopen")
    def test_sends_click_url(self, mock_urlopen: MagicMock) -> None:
        # Arrange
        mock_urlopen.return_value = MagicMock()
        message = NtfyMessage(title="T", body="B", click_url="https://example.com")

        # Act
        send_notification("https://ntfy.sh/topic", message)

        # Assert
        request = mock_urlopen.call_args[0][0]
        assert request.get_header("Click") == "https://example.com"

    @patch("claude_alert.ntfy.urllib.request.urlopen")
    def test_os_error_returns_false(self, mock_urlopen: MagicMock) -> None:
        # Arrange
        mock_urlopen.side_effect = OSError("connection refused")
        message = NtfyMessage(title="T", body="B")

        # Act
        result = send_notification("https://ntfy.sh/topic", message)

        # Assert
        assert result is False
