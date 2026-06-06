from typing import Any

from openai import OpenAI
from pydantic import BaseModel

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


def parse_structured_response[T: BaseModel](
    model: str,
    instructions: str,
    input_text: str,
    schema: type[T],
    tools: Any = None,
) -> T | None:
    client = OpenAI(api_key=get_openai_api_key())

    response = client.responses.parse(
        model=model,
        instructions=instructions,
        input=input_text,
        text_format=schema,
        tools=tools,
    )

    refusal = extract_refusal(response)
    if refusal:
        raise RuntimeError(f"Model refused structured output: {refusal}")

    parsed = getattr(response, "output_parsed", None)
    if parsed is None:
        return None

    return schema.model_validate(parsed)


def extract_refusal(response: Any) -> str | None:
    refusal = getattr(response, "refusal", None)
    if refusal:
        return str(refusal)

    for output_item in getattr(response, "output", []) or []:
        for content_item in getattr(output_item, "content", []) or []:
            refusal = getattr(content_item, "refusal", None)
            if refusal:
                return str(refusal)
            if getattr(content_item, "type", None) == "refusal":
                return str(getattr(content_item, "text", "Model refused the request."))

    return None


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
