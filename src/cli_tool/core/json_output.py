import json
from typing import Any

from cli_tool.core.errors import CliToolError


def load_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise CliToolError("Model did not return valid JSON.") from error

    if not isinstance(data, dict):
        raise CliToolError("Expected a JSON object.")

    return data


def require_keys(data: dict[str, Any], required_keys: set[str]) -> dict[str, Any]:
    missing = sorted(required_keys - data.keys())
    if missing:
        raise CliToolError(f"JSON output is missing required keys: {', '.join(missing)}")

    return data
