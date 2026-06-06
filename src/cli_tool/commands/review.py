import json
from typing import Annotated

import typer

from cli_tool import providers
from cli_tool.core.errors import exit_with_error
from cli_tool.core.files import read_text_file, save_text_file
from cli_tool.core.json_output import load_json_object, require_keys
from cli_tool.core.output import print_json, print_panel, print_saved
from cli_tool.prompts.workflows import build_code_review_json_prompt
from cli_tool.templates.code_review import build_code_review_prompt


def review(
    file: Annotated[str, typer.Argument(help="Path to code file.")],
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
    """Review a code file."""
    try:
        code = read_text_file(file)
        prompt = (
            build_code_review_json_prompt(code, file)
            if json_output
            else build_code_review_prompt(code, file)
        )
        result = providers.generate_text(prompt, provider, model=model)

        if json_output:
            data = require_keys(load_json_object(result), {"issues"})
            print_json(data)
            if save:
                save_text_file(save, json.dumps(data, indent=2))
            return

        print_panel(result)
        if save:
            save_text_file(save, result)
            print_saved(save)
    except (OSError, RuntimeError, ValueError) as error:
        exit_with_error(error)
