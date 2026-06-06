from typing import Any

from cli_tool.core.errors import CliToolError
from cli_tool.core.models import ModelTask, choose_openai_model
from cli_tool.core.token_policy import TokenPolicyResult, evaluate_token_policy
from cli_tool.prompts.types import Prompt
from cli_tool.providers.openai_client import count_input_tokens


def count_prompt_tokens(prompt: str | Prompt, model: str | None = None) -> TokenPolicyResult:
    if isinstance(prompt, Prompt):
        resolved_model = choose_openai_model(prompt.task, model)
        input_tokens = count_input_tokens(
            model=resolved_model,
            instructions=prompt.instructions,
            input_text=prompt.input,
        )
        return evaluate_token_policy(resolved_model, input_tokens)

    resolved_model = choose_openai_model(ModelTask.FAST, model)
    input_tokens = count_input_tokens(model=resolved_model, input_text=prompt)
    return evaluate_token_policy(resolved_model, input_tokens)


def token_report_with_source(
    result: TokenPolicyResult, source_type: str, path: str | None = None
) -> dict[str, Any]:
    data = result.to_dict()
    data["source"] = {"type": source_type, "path": path}
    return data


def require_sendable(result: TokenPolicyResult) -> None:
    if not result.should_send:
        raise CliToolError(f"Token risk is {result.risk_level.value}: {result.recommendation}")
