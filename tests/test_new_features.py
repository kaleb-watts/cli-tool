import json

import pytest

from cli_tool.core.analysis import analyze_path
from cli_tool.core.json_output import load_json_object, require_keys
from cli_tool.core.repo_review import run_safe_command
from cli_tool.core.sessions import ChatSession, append_message, load_session, save_session
from cli_tool.prompts.workflows import build_ask_file_prompt


def test_load_json_object_accepts_plain_json():
    assert load_json_object('{"summary": "done"}') == {"summary": "done"}


def test_require_keys_rejects_missing_key():
    with pytest.raises(Exception, match="missing required keys"):
        require_keys({"summary": "done"}, {"summary", "decisions"})


def test_ask_file_prompt_uses_xml_style_tags():
    prompt = build_ask_file_prompt("README.md", "Setup notes", "What is missing?", truncated=False)

    assert "using only the provided file content" in prompt.instructions
    assert '<file path="README.md">' in prompt.input
    assert "Setup notes" in prompt.input
    assert "<question>" in prompt.input
    assert "What is missing?" in prompt.input


def test_analyze_log_detects_errors_and_warnings(tmp_path):
    log = tmp_path / "app.log"
    log.write_text("WARN slow request\nERROR failed\nERROR failed\n", encoding="utf-8")

    result = analyze_path(log)

    assert result["type"] == "log"
    assert result["error_count"] == 2
    assert result["warning_count"] == 1
    assert result["repeated_lines"] == [{"line": "ERROR failed", "count": 2}]


def test_repo_review_rejects_unsafe_commands():
    with pytest.raises(Exception, match="Unsafe command"):
        run_safe_command("rm -rf .")


def test_chat_session_history_is_written_and_loaded(tmp_path):
    session_path = tmp_path / ".cli_tool" / "sessions" / "default.json"
    session = ChatSession()
    append_message(session, "user", "hello")
    append_message(session, "assistant", "hi")

    save_session(session, session_path)
    loaded = load_session(session_path)

    assert loaded.messages == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]
    assert json.loads(session_path.read_text(encoding="utf-8"))["updated_at"]
