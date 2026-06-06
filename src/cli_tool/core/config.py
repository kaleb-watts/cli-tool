import os
from functools import lru_cache

from dotenv import load_dotenv


@lru_cache(maxsize=1)
def load_environment() -> None:
    load_dotenv()


def get_required_env(name: str) -> str:
    load_environment()
    value = os.getenv(name, "").strip()

    if not value:
        raise RuntimeError(f"Missing {name}. Add it to your .env file.")

    return value


def get_openai_api_key() -> str:
    return get_required_env("OPENAI_API_KEY")


def get_anthropic_api_key() -> str:
    return get_required_env("ANTHROPIC_API_KEY")


def get_openai_model() -> str:
    load_environment()
    return os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"


def get_anthropic_model() -> str:
    load_environment()
    return os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest").strip() or (
        "claude-3-5-haiku-latest"
    )
