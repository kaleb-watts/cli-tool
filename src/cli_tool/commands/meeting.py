import json
from typing import Annotated

import typer

from cli_tool import providers
from cli_tool.core.errors import exit_with_error
from cli_tool.core.files import read_text_file, save_text_file
from cli_tool.core.json_output import load_json_model_with_repair, model_to_json_dict
from cli_tool.core.output import print_json, print_panel, print_saved
from cli_tool.core.structured_outputs import parse_structured_prompt
from cli_tool.core.token_counter import count_prompt_tokens, require_sendable
from cli_tool.prompts.workflows import build_json_repair_prompt, build_meeting_json_prompt
from cli_tool.schemas.meeting import MeetingSummaryOutput
from cli_tool.templates.meeting import build_meeting_prompt


def meeting(
    file: Annotated[str, typer.Argument(help="Path to meeting transcript or notes.")],
    provider: Annotated[
        providers.Provider, typer.Option("--provider", "-p", help="AI provider to use.")
    ] = providers.Provider.OPENAI,
    model: Annotated[
        str | None, typer.Option("--model", help="Override the provider model for this run.")
    ] = None,
    save: Annotated[str | None, typer.Option("--save", "-s", help="Save output to a file.")] = None,
    json_output: Annotated[
        bool, typer.Option("--json", help="Return valid machine-readable JSON only.")
    ] = False,
) -> None:
    """Summarize a meeting transcript or notes."""
    try:
        notes = read_text_file(file)
        if json_output:
            json_prompt = build_meeting_json_prompt(notes)
            if provider == providers.Provider.OPENAI:
                require_sendable(count_prompt_tokens(json_prompt, model=model))
            if provider == providers.Provider.OPENAI:
                validated = parse_structured_prompt(
                    json_prompt.instructions,
                    json_prompt.input,
                    MeetingSummaryOutput,
                    model=model,
                    task=json_prompt.task,
                )
            else:
                result = providers.generate_text(json_prompt, provider, model=model)
                validated = load_json_model_with_repair(
                    result,
                    MeetingSummaryOutput,
                    lambda error: providers.generate_text(
                        build_json_repair_prompt(result, error, "MeetingSummaryOutput"),
                        provider,
                        model=model,
                    ),
                )
            data = model_to_json_dict(validated)
            print_json(data)
            if save:
                save_text_file(save, json.dumps(data, indent=2))
            return

        text_prompt = build_meeting_prompt(notes)
        result = providers.generate_text(text_prompt, provider, model=model)
        print_panel(result)
        if save:
            save_text_file(save, result)
            print_saved(save)
    except (OSError, RuntimeError, ValueError) as error:
        exit_with_error(error)
