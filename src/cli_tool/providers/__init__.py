"""AI provider clients for cli_tool."""

from enum import StrEnum

from cli_tool.prompts.types import Prompt
from cli_tool.providers.anthropic_client import ask_anthropic, run_anthropic
from cli_tool.providers.openai_client import ask_model, run_openai


class Provider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


def generate_text(
    prompt: str | Prompt,
    provider: Provider = Provider.OPENAI,
    model: str | None = None,
) -> str:
    if provider == Provider.OPENAI:
        if isinstance(prompt, Prompt):
            return ask_model(prompt.instructions, prompt.input, model=model, task=prompt.task)
        return run_openai(prompt, model=model)
    if provider == Provider.ANTHROPIC:
        if isinstance(prompt, Prompt):
            return ask_anthropic(prompt.instructions, prompt.input, model=model)
        return run_anthropic(prompt, model=model)

    raise ValueError(f"Unsupported provider: {provider}")
