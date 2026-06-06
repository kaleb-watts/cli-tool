from enum import StrEnum

from cli_tool.core.config import get_openai_model


class ModelTask(StrEnum):
    FAST = "fast"
    STRONG = "strong"


DEFAULT_FAST_MODEL = "gpt-4.1-mini"
DEFAULT_STRONG_MODEL = "gpt-4.1"


def choose_openai_model(task: ModelTask = ModelTask.FAST, override: str | None = None) -> str:
    if override:
        return override

    if task == ModelTask.STRONG:
        return DEFAULT_STRONG_MODEL

    return get_openai_model() or DEFAULT_FAST_MODEL
