from typing import Annotated

import typer

from cli_tool import providers
from cli_tool.core.errors import exit_with_error
from cli_tool.core.files import read_text_preview, save_text_file
from cli_tool.core.output import console, print_panel, print_saved
from cli_tool.prompts.workflows import build_ask_file_prompt


def ask_file(
    file: Annotated[str, typer.Argument(help="Path to the file to inspect.")],
    question: Annotated[str, typer.Argument(help="Question to ask about the file.")],
    provider: Annotated[
        providers.Provider, typer.Option("--provider", "-p", help="AI provider to use.")
    ] = providers.Provider.OPENAI,
    model: Annotated[
        str | None, typer.Option("--model", help="Override the provider model for this run.")
    ] = None,
    save: Annotated[str | None, typer.Option("--save", "-s", help="Save output to a file.")] = None,
) -> None:
    """Ask a grounded question about a local file."""
    try:
        contents, truncated = read_text_preview(file)
        if truncated:
            console.print("[yellow]Warning:[/yellow] File was truncated to a safe preview.")
        prompt = build_ask_file_prompt(file, contents, question, truncated)
        result = providers.generate_text(prompt, provider, model=model)
        print_panel(result, title="Ask File")
        if save:
            save_text_file(save, result)
            print_saved(save)
    except (OSError, RuntimeError, ValueError) as error:
        exit_with_error(error)
