from cli_tool.templates.code_review import build_code_review_prompt
from cli_tool.templates.email import build_email_prompt
from cli_tool.templates.meeting import build_meeting_prompt


def test_email_prompt_contains_notes():
    prompt = build_email_prompt("Tell John I finished the report.")
    assert "Tell John I finished the report." in prompt
    assert "professional email" in prompt


def test_code_review_prompt_contains_code_and_filename():
    prompt = build_code_review_prompt("print('hello')", "app.py")
    assert "print('hello')" in prompt
    assert "app.py" in prompt
    assert prompt.count("```") == 2


def test_meeting_prompt_contains_notes():
    prompt = build_meeting_prompt("We decided to ship Friday.")
    assert "We decided to ship Friday." in prompt
    assert "Action items" in prompt
    assert prompt.startswith("You are an executive assistant.")
