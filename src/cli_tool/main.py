from enum import StrEnum
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from cli_tool.core.files import read_text_file, save_text_file
from cli_tool.providers.anthropic_client import run_anthropic
from cli_tool.providers.openai_client import run_openai
from cli_tool.templates.code_review import build_code_review_prompt
from cli_tool.templates.email import build_email_prompt
from cli_tool.templates.meeting import build_meeting_prompt

app = typer.Typer(help="CLI Tool: simple AI CLI for emails, code reviews, and meeting summaries.")
console = Console()


class Provider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


def run_prompt(prompt: str, provider: Provider, save: str | None = None) -> None:
    if provider == Provider.OPENAI:
        result = run_openai(prompt)
    elif provider == Provider.ANTHROPIC:
        result = run_anthropic(prompt)

    console.print(Panel(result, title="CLI Tool Output", border_style="green"))

    if save:
        save_text_file(save, result)
        console.print(f"[bold green]Saved to:[/bold green] {save}")


@app.command()
def email(
    notes: Annotated[str, typer.Argument(help="Rough notes for the email.")],
    provider: Annotated[
        Provider, typer.Option("--provider", "-p", help="AI provider to use.")
    ] = Provider.OPENAI,
    save: Annotated[str | None, typer.Option("--save", "-s", help="Save output to a file.")] = None,
) -> None:
    """Turn rough notes into a clean email draft."""
    prompt = build_email_prompt(notes)
    run_prompt(prompt, provider, save)


@app.command()
def review(
    file: Annotated[str, typer.Argument(help="Path to code file.")],
    provider: Annotated[
        Provider, typer.Option("--provider", "-p", help="AI provider to use.")
    ] = Provider.OPENAI,
    save: Annotated[str | None, typer.Option("--save", "-s", help="Save output to a file.")] = None,
) -> None:
    """Review a code file."""
    code = read_text_file(file)
    prompt = build_code_review_prompt(code, file)
    run_prompt(prompt, provider, save)


@app.command()
def meeting(
    file: Annotated[str, typer.Argument(help="Path to meeting transcript or notes.")],
    provider: Annotated[
        Provider, typer.Option("--provider", "-p", help="AI provider to use.")
    ] = Provider.OPENAI,
    save: Annotated[str | None, typer.Option("--save", "-s", help="Save output to a file.")] = None,
) -> None:
    """Summarize a meeting transcript or notes."""
    notes = read_text_file(file)
    prompt = build_meeting_prompt(notes)
    run_prompt(prompt, provider, save)


if __name__ == "__main__":
    app()
