import json
from typing import Annotated

import typer

from cli_tool import providers
from cli_tool.core.chunking import format_chunks_xml
from cli_tool.core.errors import exit_with_error
from cli_tool.core.files import MAX_FILE_CHARS, read_text_file, save_text_file
from cli_tool.core.json_output import model_to_json_dict, validate_json_model
from cli_tool.core.output import console, print_json, print_panel, print_saved
from cli_tool.core.retrieval import select_relevant_chunks
from cli_tool.core.token_counter import count_prompt_tokens, require_sendable
from cli_tool.core.token_policy import TokenRiskLevel
from cli_tool.prompts.workflows import build_ask_file_prompt
from cli_tool.schemas.ask_file import AskFileJson


def ask_file(
    file: Annotated[str, typer.Argument(help="Path to the file to inspect.")],
    question: Annotated[str, typer.Argument(help="Question to ask about the file.")],
    provider: Annotated[
        providers.Provider, typer.Option("--provider", "-p", help="AI provider to use.")
    ] = providers.Provider.OPENAI,
    model: Annotated[
        str | None, typer.Option("--model", help="Override the provider model for this run.")
    ] = None,
    full: Annotated[
        bool, typer.Option("--full", help="Send the full file instead of the safe preview.")
    ] = False,
    verbose_tokens: Annotated[
        bool, typer.Option("--verbose-tokens", help="Print token risk before sending.")
    ] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Return valid machine-readable JSON only.")
    ] = False,
    save: Annotated[str | None, typer.Option("--save", "-s", help="Save output to a file.")] = None,
) -> None:
    """Ask a grounded question about a local file."""
    try:
        if full:
            contents = read_text_file(file)
            truncated = False
        else:
            raw_contents = read_text_file(file)
            if len(raw_contents) > MAX_FILE_CHARS:
                chunks = select_relevant_chunks(raw_contents, question)
                contents = format_chunks_xml(chunks, file)
                truncated = True
            else:
                contents = raw_contents
                truncated = False
        if truncated:
            console.print(
                "[yellow]Warning:[/yellow] Large file detected. "
                "Using retrieved chunks instead of silently truncating."
            )
        prompt = build_ask_file_prompt(file, contents, question, truncated)
        token_report = None
        if provider == providers.Provider.OPENAI:
            token_result = count_prompt_tokens(prompt, model=model)
            token_report = token_result.to_dict()
            if json_output and not token_result.should_send:
                print_json(
                    {
                        "error": "Token risk is too large to send safely.",
                        "token_check": token_report,
                        "source": {"type": "file", "path": file, "truncated": truncated},
                    }
                )
                raise typer.Exit(1)
            if not json_output and (
                verbose_tokens or token_result.risk_level != TokenRiskLevel.SAFE
            ):
                console.print(
                    "[yellow]Token check:[/yellow] "
                    f"{token_result.input_tokens:,} input tokens, "
                    f"risk={token_result.risk_level.value}. {token_result.recommendation}"
                )
            require_sendable(token_result)
        result = providers.generate_text(prompt, provider, model=model)
        if json_output:
            validated = validate_json_model(
                {
                    "answer": result,
                    "token_check": token_report,
                    "source": {"type": "file", "path": file, "truncated": truncated},
                },
                AskFileJson,
            )
            data = model_to_json_dict(validated)
            print_json(data)
            if save:
                save_text_file(save, json.dumps(data, indent=2))
            return
        print_panel(result, title="Ask File")
        if save:
            save_text_file(save, result)
            print_saved(save)
    except typer.Exit:
        raise
    except (OSError, RuntimeError, ValueError) as error:
        exit_with_error(error)
