from dataclasses import dataclass

from cli_tool.core.models import ModelTask


@dataclass(frozen=True)
class Prompt:
    instructions: str
    input: str
    task: ModelTask = ModelTask.FAST


def as_text(prompt: Prompt) -> str:
    return f"{prompt.instructions}\n\n# Dynamic Context\n{prompt.input}".strip()
