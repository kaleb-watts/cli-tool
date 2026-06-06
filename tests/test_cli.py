import json

from typer.testing import CliRunner

from cli_tool import main, providers
from cli_tool.templates.code_review import build_code_review_prompt
from cli_tool.templates.email import build_email_prompt
from cli_tool.templates.meeting import build_meeting_prompt

runner = CliRunner()


def test_help_lists_current_commands():
    result = runner.invoke(main.app, ["--help"])

    assert result.exit_code == 0
    assert "email" in result.output
    assert "review" in result.output
    assert "meeting" in result.output
    assert "research" in result.output
    assert "ask-file" in result.output
    assert "analyze" in result.output
    assert "repo-review" in result.output
    assert "chat" in result.output


def test_email_routes_to_openai_by_default(monkeypatch):
    calls = []

    def fake_generate_text(
        prompt: str, provider: providers.Provider, model: str | None = None
    ) -> str:
        calls.append((prompt, provider))
        return "drafted email"

    monkeypatch.setattr(providers, "generate_text", fake_generate_text)

    result = runner.invoke(main.app, ["email", "Tell John I finished the report."])

    assert result.exit_code == 0
    assert "drafted email" in result.output
    assert calls == [
        (build_email_prompt("Tell John I finished the report."), providers.Provider.OPENAI),
    ]


def test_email_routes_to_anthropic_when_requested(monkeypatch):
    calls = []

    def fake_generate_text(
        prompt: str, provider: providers.Provider, model: str | None = None
    ) -> str:
        calls.append((prompt, provider))
        return "anthropic draft"

    monkeypatch.setattr(providers, "generate_text", fake_generate_text)

    result = runner.invoke(
        main.app,
        ["email", "Ask for a meeting.", "--provider", "anthropic"],
    )

    assert result.exit_code == 0
    assert "anthropic draft" in result.output
    assert calls == [(build_email_prompt("Ask for a meeting."), providers.Provider.ANTHROPIC)]


def test_save_writes_provider_output(monkeypatch, tmp_path):
    monkeypatch.setattr(
        providers, "generate_text", lambda _prompt, _provider, model=None: "saved output"
    )
    target = tmp_path / "reports" / "email.txt"

    result = runner.invoke(
        main.app,
        ["email", "Save this.", "--save", str(target)],
    )

    assert result.exit_code == 0
    assert target.read_text(encoding="utf-8") == "saved output"
    assert "Saved to:" in result.output
    assert str(target) in result.output


def test_review_reads_file_and_builds_grounded_prompt(monkeypatch, tmp_path):
    prompts = []
    source = tmp_path / "app.py"
    source.write_text("print('hello')", encoding="utf-8")

    def fake_generate_text(
        prompt: str, _provider: providers.Provider, model: str | None = None
    ) -> str:
        prompts.append(prompt)
        return "review result"

    monkeypatch.setattr(providers, "generate_text", fake_generate_text)

    result = runner.invoke(main.app, ["review", str(source)])

    assert result.exit_code == 0
    assert "review result" in result.output
    assert prompts == [build_code_review_prompt("print('hello')", str(source))]


def test_meeting_reads_file_and_builds_grounded_prompt(monkeypatch, tmp_path):
    prompts = []
    notes = tmp_path / "notes.txt"
    notes.write_text("Ship Friday.", encoding="utf-8")

    def fake_generate_text(
        prompt: str, _provider: providers.Provider, model: str | None = None
    ) -> str:
        prompts.append(prompt)
        return "meeting result"

    monkeypatch.setattr(providers, "generate_text", fake_generate_text)

    result = runner.invoke(main.app, ["meeting", str(notes)])

    assert result.exit_code == 0
    assert "meeting result" in result.output
    assert prompts == [build_meeting_prompt("Ship Friday.")]


def test_meeting_json_outputs_parseable_json(monkeypatch, tmp_path):
    notes = tmp_path / "notes.txt"
    notes.write_text("Ship Friday.", encoding="utf-8")
    monkeypatch.setattr(
        providers,
        "generate_text",
        lambda _prompt, _provider, model=None: json.dumps(
            {
                "summary": "Ship Friday.",
                "decisions": ["Ship Friday"],
                "action_items": [],
            }
        ),
    )

    result = runner.invoke(main.app, ["meeting", str(notes), "--json"])

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "summary": "Ship Friday.",
        "decisions": ["Ship Friday"],
        "action_items": [],
    }


def test_meeting_json_save_still_prints_json_only(monkeypatch, tmp_path):
    notes = tmp_path / "notes.txt"
    notes.write_text("Ship Friday.", encoding="utf-8")
    target = tmp_path / "summary.json"
    payload = {
        "summary": "Ship Friday.",
        "decisions": ["Ship Friday"],
        "action_items": [],
    }
    monkeypatch.setattr(
        providers, "generate_text", lambda _prompt, _provider, model=None: json.dumps(payload)
    )

    result = runner.invoke(main.app, ["meeting", str(notes), "--json", "--save", str(target)])

    assert result.exit_code == 0
    assert json.loads(result.output) == payload
    assert json.loads(target.read_text(encoding="utf-8")) == payload


def test_review_json_outputs_parseable_json(monkeypatch, tmp_path):
    source = tmp_path / "app.py"
    source.write_text("print('hello')", encoding="utf-8")
    monkeypatch.setattr(
        providers, "generate_text", lambda _prompt, _provider, model=None: '{"issues": []}'
    )

    result = runner.invoke(main.app, ["review", str(source), "--json"])

    assert result.exit_code == 0
    assert json.loads(result.output) == {"issues": []}


def test_ask_file_builds_grounded_prompt(monkeypatch, tmp_path):
    prompts = []
    source = tmp_path / "README.md"
    source.write_text("## Setup\nUse uv sync.", encoding="utf-8")

    def fake_generate_text(
        prompt: str, _provider: providers.Provider, model: str | None = None
    ) -> str:
        prompts.append(prompt)
        return "It documents uv sync."

    monkeypatch.setattr(providers, "generate_text", fake_generate_text)

    result = runner.invoke(main.app, ["ask-file", str(source), "What setup is documented?"])

    assert result.exit_code == 0
    assert "It documents uv sync." in result.output
    assert f'<file path="{source}">' in prompts[0].input
    assert "<question>" in prompts[0].input
    assert "What setup is documented?" in prompts[0].input


def test_analyze_csv_json_is_parseable(tmp_path):
    data = tmp_path / "data.csv"
    data.write_text("name,score\nAda,10\nLin,\n", encoding="utf-8")

    result = runner.invoke(main.app, ["analyze", str(data), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["type"] == "csv"
    assert payload["row_count"] == 2
    assert payload["missing_values"]["score"] == 1


def test_missing_file_exits_cleanly_without_traceback():
    result = runner.invoke(main.app, ["review", "does-not-exist.py"])

    assert result.exit_code == 1
    assert "Error: File not found: does-not-exist.py" in result.output
    assert "Traceback" not in result.output


def test_missing_api_key_exits_cleanly_without_traceback(monkeypatch):
    def fake_generate_text(
        _prompt: str, _provider: providers.Provider, model: str | None = None
    ) -> str:
        raise RuntimeError("Missing OPENAI_API_KEY. Add it to your .env file.")

    monkeypatch.setattr(providers, "generate_text", fake_generate_text)

    result = runner.invoke(main.app, ["email", "Tell John I finished the report."])

    assert result.exit_code == 1
    assert "Error: Missing OPENAI_API_KEY. Add it to your .env file." in result.output
    assert "Traceback" not in result.output


def test_directory_input_exits_cleanly_without_traceback(tmp_path):
    result = runner.invoke(main.app, ["meeting", str(tmp_path)])

    assert result.exit_code == 1
    assert "Error: Path is not a file:" in result.output
    assert str(tmp_path) in result.output
    assert "Traceback" not in result.output
