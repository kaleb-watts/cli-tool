from openai import OpenAI

from cli_tool.core.config import get_openai_api_key, get_openai_model


def run_openai(prompt: str) -> str:
    client = OpenAI(api_key=get_openai_api_key())

    response = client.responses.create(
        model=get_openai_model(),
        input=prompt,
    )

    return response.output_text
