from typing import Any

from openai import OpenAI

from cli_tool.core.config import get_openai_api_key, get_openai_model
from cli_tool.core.models import ModelTask, choose_openai_model


def ask_model(
    instructions: str,
    input_text: str,
    model: str | None = None,
    task: ModelTask = ModelTask.FAST,
) -> str:
    client = OpenAI(api_key=get_openai_api_key())

    response = client.responses.create(
        model=choose_openai_model(task, model),
        instructions=instructions,
        input=input_text,
    )

    return response.output_text


def count_input_tokens(
    model: str,
    instructions: str | None = None,
    input_text: str | None = None,
    tools: Any = None,
) -> int:
    client = OpenAI(api_key=get_openai_api_key())

    response = client.responses.input_tokens.count(
        model=model,
        instructions=instructions,
        input=input_text,
        tools=tools,
    )

    return response.input_tokens


def run_openai_web_research(query: str, model: str | None = None) -> str:
    client = OpenAI(api_key=get_openai_api_key())

    instructions = """
You are a research assistant with access to live web search.
Use web search to verify current information.
Return valid JSON only with:
query, used_live_web, summary, key_findings, sources, follow_up_queries, limitations.
Set used_live_web to true only if web search was used.
Include source URLs for web-backed claims.
""".strip()

    response = client.responses.create(
        model=model or get_openai_model(),
        instructions=instructions,
        input=f"<query>{query}</query>",
        tools=[{"type": "web_search_preview"}],
    )

    return response.output_text


def run_openai(prompt: str, model: str | None = None) -> str:
    client = OpenAI(api_key=get_openai_api_key())

    response = client.responses.create(
        model=model or get_openai_model(),
        input=prompt,
    )

    return response.output_text
