import json

from typer.testing import CliRunner

from cli_tool import main, providers
from cli_tool.commands import ask_file as ask_file_command
from cli_tool.commands import meeting as meeting_command
from cli_tool.commands import research as research_command
from cli_tool.commands import review as review_command
from cli_tool.commands import tokens as tokens_command
from cli_tool.commands import tokens_chat as tokens_chat_command
from cli_tool.core.token_policy import TokenPolicyResult, TokenRiskLevel
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
    assert "tokens" in result.output
    assert "tokens-chat" in result.output


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
    monkeypatch.setattr(meeting_command, "count_prompt_tokens", fake_safe_token_count)

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
    monkeypatch.setattr(meeting_command, "count_prompt_tokens", fake_safe_token_count)

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
    monkeypatch.setattr(review_command, "count_prompt_tokens", fake_safe_token_count)

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
    monkeypatch.setattr(ask_file_command, "count_prompt_tokens", fake_safe_token_count)

    result = runner.invoke(main.app, ["ask-file", str(source), "What setup is documented?"])

    assert result.exit_code == 0
    assert "It documents uv sync." in result.output
    assert f'<file path="{source}">' in prompts[0].input
    assert "<question>" in prompts[0].input
    assert "What setup is documented?" in prompts[0].input


def test_ask_file_json_includes_token_check(monkeypatch, tmp_path):
    source = tmp_path / "README.md"
    source.write_text("hello", encoding="utf-8")
    monkeypatch.setattr(providers, "generate_text", lambda _prompt, _provider, model=None: "answer")
    monkeypatch.setattr(ask_file_command, "count_prompt_tokens", fake_safe_token_count)

    result = runner.invoke(main.app, ["ask-file", str(source), "What?", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["answer"] == "answer"
    assert payload["token_check"]["input_tokens"] == 42
    assert payload["source"]["truncated"] is False


def test_ask_file_json_token_block_is_json_only(monkeypatch, tmp_path):
    source = tmp_path / "README.md"
    source.write_text("hello", encoding="utf-8")
    monkeypatch.setattr(
        ask_file_command,
        "count_prompt_tokens",
        lambda _prompt, model=None: TokenPolicyResult(
            model="test-model",
            input_tokens=100_000,
            risk_level=TokenRiskLevel.LARGE,
            should_send=False,
            recommendation="Use a preview.",
        ),
    )

    result = runner.invoke(main.app, ["ask-file", str(source), "What?", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["error"] == "Token risk is too large to send safely."
    assert payload["token_check"]["risk_level"] == "large"


def test_ask_file_large_file_uses_retrieved_chunks(monkeypatch, tmp_path):
    prompts = []
    source = tmp_path / "notes.txt"
    source.write_text(
        ("alpha setup details\n" * 3000)
        + ("billing integration important answer\n" * 50)
        + ("unrelated footer\n" * 3000),
        encoding="utf-8",
    )

    def fake_generate_text(prompt, _provider, model=None):
        prompts.append(prompt)
        return "answer"

    monkeypatch.setattr(providers, "generate_text", fake_generate_text)
    monkeypatch.setattr(ask_file_command, "count_prompt_tokens", fake_safe_token_count)

    result = runner.invoke(main.app, ["ask-file", str(source), "billing integration"])

    assert result.exit_code == 0
    assert "<chunk " in prompts[0].input
    assert "billing integration important answer" in prompts[0].input
    assert "Using retrieved chunks" in result.output


def test_research_json_uses_live_web_when_available(monkeypatch):
    monkeypatch.setattr(
        research_command,
        "run_openai_web_research",
        lambda query, model=None: json.dumps(research_payload(query, used_live_web=True)),
    )

    result = runner.invoke(main.app, ["research", "python packaging", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["used_live_web"] is True
    assert payload["sources"][0]["url"] == "https://example.com"


def test_research_json_falls_back_when_web_unavailable(monkeypatch):
    def fail_web(_query, model=None):
        raise RuntimeError("web unavailable")

    monkeypatch.setattr(research_command, "run_openai_web_research", fail_web)
    monkeypatch.setattr(
        providers,
        "generate_text",
        lambda _prompt, _provider, model=None: json.dumps(
            research_payload("python packaging", used_live_web=False)
        ),
    )
    monkeypatch.setattr(research_command, "count_prompt_tokens", fake_safe_token_count)

    result = runner.invoke(main.app, ["research", "python packaging", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["used_live_web"] is False
    assert "Live web search failed" in payload["limitations"][0]


def test_tokens_file_json_outputs_policy(monkeypatch, tmp_path):
    source = tmp_path / "README.md"
    source.write_text("hello", encoding="utf-8")
    monkeypatch.setattr(tokens_command, "count_prompt_tokens", fake_safe_token_count)

    result = runner.invoke(main.app, ["tokens", str(source), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["input_tokens"] == 42
    assert payload["risk_level"] == "safe"
    assert payload["source"] == {"type": "file", "path": str(source)}


def test_tokens_file_rejects_env_files(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=secret", encoding="utf-8")

    result = runner.invoke(main.app, ["tokens", str(env_file)])

    assert result.exit_code == 1
    assert "Refusing to token-count .env" in result.output


def test_tokens_chat_json_outputs_policy(monkeypatch, tmp_path):
    session_file = tmp_path / "session.json"
    session_file.write_text(
        json.dumps({"messages": [{"role": "user", "content": "hello"}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(tokens_chat_command, "count_prompt_tokens", fake_safe_token_count)

    result = runner.invoke(main.app, ["tokens-chat", "--session", str(session_file), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["input_tokens"] == 42
    assert payload["source"] == {"type": "chat", "path": str(session_file)}


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


def fake_safe_token_count(_prompt, model: str | None = None) -> TokenPolicyResult:
    return TokenPolicyResult(
        model=model or "test-model",
        input_tokens=42,
        risk_level=TokenRiskLevel.SAFE,
        should_send=True,
        recommendation="Okay to send.",
    )


def research_payload(query: str, used_live_web: bool) -> dict:
    return {
        "query": query,
        "used_live_web": used_live_web,
        "summary": "Summary.",
        "key_findings": [
            {
                "claim": "A verified claim.",
                "source_title": "Example",
                "source_url": "https://example.com",
                "source_date": None,
                "confidence": "high",
            }
        ],
        "sources": [
            {
                "title": "Example",
                "url": "https://example.com",
                "publisher": "Example",
                "date": None,
            }
        ],
        "follow_up_queries": ["next query"],
        "limitations": [],
    }
