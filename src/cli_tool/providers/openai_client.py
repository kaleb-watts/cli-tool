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


def run_openai(prompt: str, model: str | None = None) -> str:
    client = OpenAI(api_key=get_openai_api_key())

    response = client.responses.create(
        model=model or get_openai_model(),
        input=prompt,
    )

    return response.output_text
