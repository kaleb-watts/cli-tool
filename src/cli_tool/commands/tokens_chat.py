from pathlib import Path
from typing import Annotated

import typer

from cli_tool.core.errors import exit_with_error
from cli_tool.core.json_output import model_to_json_dict, validate_json_model
from cli_tool.core.output import print_json, print_panel
from cli_tool.core.sessions import DEFAULT_SESSION_PATH, load_session
from cli_tool.core.token_counter import count_prompt_tokens, token_report_with_source
from cli_tool.core.token_policy import format_token_policy
from cli_tool.prompts.workflows import build_chat_prompt
from cli_tool.schemas.tokens import TokenReport


def tokens_chat(
    session: Annotated[
        str, typer.Option("--session", help="Session name or JSON path.")
    ] = "default",
    model: Annotated[
        str | None, typer.Option("--model", help="Override the OpenAI model used for counting.")
    ] = None,
    json_output: Annotated[
        bool, typer.Option("--json", help="Return valid machine-readable JSON only.")
    ] = False,
) -> None:
    """Count OpenAI input tokens for the saved chat session."""
    try:
        session_path = resolve_session_path(session)
        chat_session = load_session(session_path)
        prompt = build_chat_prompt(chat_session.messages, "Count this saved chat session.")
        result = count_prompt_tokens(prompt, model=model)
        if json_output:
            validated = validate_json_model(
                token_report_with_source(result, "chat", str(session_path)), TokenReport
            )
            print_json(model_to_json_dict(validated))
            return
        print_panel(format_token_policy(result), title="Chat Token Count")
    except (OSError, RuntimeError, ValueError) as error:
        exit_with_error(error)


def resolve_session_path(session: str) -> Path:
    if session == "default":
        return DEFAULT_SESSION_PATH

    path = Path(session)
    if path.suffix == ".json":
        return path

    return Path(".cli_tool/sessions") / f"{session}.json"
