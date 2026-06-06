from typing import Annotated

import typer

from cli_tool import providers
from cli_tool.core.errors import exit_with_error
from cli_tool.core.files import save_text_file
from cli_tool.core.output import print_panel, print_saved
from cli_tool.templates.email import build_email_prompt


def email(
    notes: Annotated[str, typer.Argument(help="Rough notes for the email.")],
    provider: Annotated[
        providers.Provider, typer.Option("--provider", "-p", help="AI provider to use.")
    ] = providers.Provider.OPENAI,
    model: Annotated[
        str | None, typer.Option("--model", help="Override the provider model for this run.")
    ] = None,
    save: Annotated[str | None, typer.Option("--save", "-s", help="Save output to a file.")] = None,
) -> None:
    """Turn rough notes into a clean email draft."""
    try:
        result = providers.generate_text(build_email_prompt(notes), provider, model=model)
        print_panel(result)
        if save:
            save_text_file(save, result)
            print_saved(save)
    except (OSError, RuntimeError, ValueError) as error:
        exit_with_error(error)
