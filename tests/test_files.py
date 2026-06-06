from pathlib import Path

import pytest

from cli_tool.core.files import read_text_file, save_text_file


def test_save_text_file_creates_parent_directories(tmp_path):
    target = tmp_path / "reports" / "summary.txt"

    save_text_file(target, "done")

    assert target.read_text(encoding="utf-8") == "done"


def test_read_text_file_rejects_directory(tmp_path):
    with pytest.raises(ValueError, match="Path is not a file"):
        read_text_file(tmp_path)


def test_read_text_file_accepts_path_objects(tmp_path):
    target = Path(tmp_path / "notes.txt")
    target.write_text("hello", encoding="utf-8")

    assert read_text_file(target) == "hello"
