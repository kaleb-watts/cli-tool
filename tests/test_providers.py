from types import SimpleNamespace

from cli_tool.core.models import ModelTask
from cli_tool.providers import anthropic_client, openai_client


def test_run_openai_uses_responses_api_and_returns_output_text(monkeypatch):
    calls = []

    class FakeResponses:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(output_text="openai output")

    class FakeOpenAI:
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.responses = FakeResponses()

    clients = []

    def fake_openai(api_key: str) -> FakeOpenAI:
        client = FakeOpenAI(api_key)
        clients.append(client)
        return client

    monkeypatch.setattr(openai_client, "OpenAI", fake_openai)
    monkeypatch.setattr(openai_client, "get_openai_api_key", lambda: "test-openai-key")
    monkeypatch.setattr(openai_client, "get_openai_model", lambda: "test-openai-model")

    result = openai_client.run_openai("Prompt text")

    assert result == "openai output"
    assert clients[0].api_key == "test-openai-key"
    assert calls == [
        {
            "model": "test-openai-model",
            "input": "Prompt text",
        }
    ]


def test_ask_model_separates_instructions_and_input(monkeypatch):
    calls = []

    class FakeResponses:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(output_text="separated output")

    class FakeOpenAI:
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.responses = FakeResponses()

    monkeypatch.setattr(openai_client, "OpenAI", FakeOpenAI)
    monkeypatch.setattr(openai_client, "get_openai_api_key", lambda: "test-openai-key")

    result = openai_client.ask_model(
        instructions="Follow these rules.",
        input_text="<file>content</file>",
        model="custom-model",
        task=ModelTask.STRONG,
    )

    assert result == "separated output"
    assert calls == [
        {
            "model": "custom-model",
            "instructions": "Follow these rules.",
            "input": "<file>content</file>",
        }
    ]


def test_run_anthropic_uses_messages_api_and_joins_text_blocks(monkeypatch):
    calls = []

    class FakeMessages:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(
                content=[
                    SimpleNamespace(type="text", text="first"),
                    SimpleNamespace(type="image", text="ignored"),
                    SimpleNamespace(type="text", text="second"),
                ]
            )

    class FakeAnthropic:
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.messages = FakeMessages()

    clients = []

    def fake_anthropic(api_key: str) -> FakeAnthropic:
        client = FakeAnthropic(api_key)
        clients.append(client)
        return client

    monkeypatch.setattr(anthropic_client, "Anthropic", fake_anthropic)
    monkeypatch.setattr(anthropic_client, "get_anthropic_api_key", lambda: "test-anthropic-key")
    monkeypatch.setattr(anthropic_client, "get_anthropic_model", lambda: "test-anthropic-model")

    result = anthropic_client.run_anthropic("Prompt text")

    assert result == "first\nsecond"
    assert clients[0].api_key == "test-anthropic-key"
    assert calls == [
        {
            "model": "test-anthropic-model",
            "max_tokens": 1200,
            "messages": [
                {
                    "role": "user",
                    "content": "Prompt text",
                }
            ],
        }
    ]
