from pathlib import Path
from typing import Annotated

import typer

from cli_tool.core.errors import CliToolError, exit_with_error
from cli_tool.core.files import read_text_file
from cli_tool.core.json_output import model_to_json_dict, validate_json_model
from cli_tool.core.output import print_json, print_panel
from cli_tool.core.token_counter import count_prompt_tokens, token_report_with_source
from cli_tool.core.token_policy import format_token_policy
from cli_tool.prompts.workflows import build_ask_file_prompt
from cli_tool.schemas.tokens import TokenReportOutput


def tokens(
    file: Annotated[str, typer.Argument(help="File to count before sending to AI.")],
    model: Annotated[
        str | None, typer.Option("--model", help="Override the OpenAI model used for counting.")
    ] = None,
    json_output: Annotated[
        bool, typer.Option("--json", help="Return valid machine-readable JSON only.")
    ] = False,
) -> None:
    """Count OpenAI input tokens for a local file prompt."""
    try:
        ensure_safe_token_source(file)
        content = read_text_file(file)
        prompt = build_ask_file_prompt(
            file,
            content,
            "Count this file before sending it to an AI command.",
            truncated=False,
        )
        result = count_prompt_tokens(prompt, model=model)
        if json_output:
            validated = validate_json_model(
                token_report_with_source(result, "file", file), TokenReportOutput
            )
            print_json(model_to_json_dict(validated))
            return
        print_panel(format_token_policy(result), title="Token Count")
    except (OSError, RuntimeError, ValueError) as error:
        exit_with_error(error)


def ensure_safe_token_source(path: str) -> None:
    file_path = Path(path)
    if file_path.name == ".env" or ".env" in file_path.parts:
        raise CliToolError("Refusing to token-count .env files or secret environment files.")
