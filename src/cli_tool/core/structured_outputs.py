from typing import Any

from pydantic import BaseModel

from cli_tool.core.errors import CliToolError
from cli_tool.core.models import ModelTask, choose_openai_model
from cli_tool.providers.openai_client import parse_structured_response


def parse_structured_prompt[T: BaseModel](
    instructions: str,
    input_text: str,
    schema: type[T],
    model: str | None = None,
    task: ModelTask = ModelTask.FAST,
    tools: Any = None,
) -> T:
    resolved_model = choose_openai_model(task, model)
    parsed = parse_structured_response(
        model=resolved_model,
        instructions=instructions,
        input_text=input_text,
        schema=schema,
        tools=tools,
    )
    if parsed is None:
        raise CliToolError("Structured output was empty.")
    return parsed
