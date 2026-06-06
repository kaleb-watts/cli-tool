import json
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ValidationError

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


def validate_json_model[T: BaseModel](data: dict[str, Any], schema: type[T]) -> T:
    try:
        return schema.model_validate(data)
    except ValidationError as error:
        raise CliToolError(f"JSON output failed schema validation: {error}") from error


def load_json_model[T: BaseModel](text: str, schema: type[T]) -> T:
    return validate_json_model(load_json_object(text), schema)


def load_json_model_with_repair[T: BaseModel](
    text: str,
    schema: type[T],
    repair: Callable[[str], str],
) -> T:
    try:
        return load_json_model(text, schema)
    except CliToolError as first_error:
        repaired = repair(str(first_error))
        try:
            return load_json_model(repaired, schema)
        except CliToolError as second_error:
            raise CliToolError(
                f"JSON output failed schema validation after one repair attempt: {second_error}"
            ) from second_error


def model_to_json_dict(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json")
