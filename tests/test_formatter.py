"""Tests for claude_alert.formatter."""

from __future__ import annotations

from claude_alert.formatter import (
    extract_project_name,
    format_notification_event,
    format_stop_event,
)


class TestExtractProjectName:
    """Tests for extract_project_name()."""

    def test_normal_path(self) -> None:
        assert extract_project_name("/home/user/myproject") == "myproject"

    def test_empty_string_returns_unknown(self) -> None:
        assert extract_project_name("") == "unknown"

    def test_root_path_returns_unknown(self) -> None:
        # os.path.basename("/") returns ""
        assert extract_project_name("/") == "unknown"


class TestFormatNotificationEvent:
    """Tests for format_notification_event()."""

    def test_permission_prompt(self) -> None:
        result = format_notification_event(
            "/tmp/proj", "Allow file read?", "permission_prompt"
        )
        assert result is not None
        title, body, priority, tags = result
        assert title == "[proj] Permission Required"
        assert body == "Allow file read?"
        assert priority == 4
        assert tags == ("warning",)

    def test_elicitation_dialog(self) -> None:
        result = format_notification_event(
            "/tmp/proj", "Choose an option", "elicitation_dialog"
        )
        assert result is not None
        title, body, priority, tags = result
        assert title == "[proj] Selection Required"
        assert priority == 4
        assert tags == ("question",)

    def test_idle_prompt_returns_none(self) -> None:
        result = format_notification_event("/tmp/proj", "idle", "idle_prompt")
        assert result is None

    def test_auth_success_returns_none(self) -> None:
        result = format_notification_event("/tmp/proj", "ok", "auth_success")
        assert result is None

    def test_unknown_type_returns_default(self) -> None:
        result = format_notification_event(
            "/tmp/proj", "Something happened", "some_unknown_type"
        )
        assert result is not None
        title, body, priority, tags = result
        assert title == "[proj] Notification"
        assert priority == 3
        assert tags == ("bell",)

    def test_empty_type_returns_default(self) -> None:
        result = format_notification_event("/tmp/proj", "msg", "")
        assert result is not None
        assert result[0] == "[proj] Notification"


class TestFormatStopEvent:
    """Tests for format_stop_event()."""

    def test_with_reason(self) -> None:
        title, body, priority, tags = format_stop_event(
            "/home/user/myapp", "task_complete"
        )
        assert title == "[myapp] Task Complete"
        assert body == "task_complete"
        assert priority == 3
        assert tags == ("white_check_mark",)

    def test_empty_reason_uses_default_body(self) -> None:
        title, body, priority, tags = format_stop_event("/home/user/myapp", "")
        assert body == "Claude Code has finished and is ready for input."

    def test_project_name_extracted(self) -> None:
        title, _, _, _ = format_stop_event("/some/path/cool-project", "done")
        assert title == "[cool-project] Task Complete"
