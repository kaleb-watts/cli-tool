from anthropic import Anthropic

from cli_tool.core.config import get_anthropic_api_key, get_anthropic_model


def run_anthropic(prompt: str) -> str:
    client = Anthropic(api_key=get_anthropic_api_key())

    response = client.messages.create(
        model=get_anthropic_model(),
        max_tokens=1200,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    text_parts = []

    for block in response.content:
        if getattr(block, "type", None) == "text":
            text_parts.append(block.text)

    return "\n".join(text_parts)
