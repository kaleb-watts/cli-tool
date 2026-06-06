from typing import Annotated

import typer

from cli_tool import providers
from cli_tool.core.errors import exit_with_error
from cli_tool.core.output import console, print_panel, print_success
from cli_tool.core.sessions import append_message, compact_session, load_session, save_session
from cli_tool.core.token_counter import count_prompt_tokens, require_sendable
from cli_tool.prompts.workflows import build_chat_prompt


def chat(
    provider: Annotated[
        providers.Provider, typer.Option("--provider", "-p", help="AI provider to use.")
    ] = providers.Provider.OPENAI,
    model: Annotated[
        str | None, typer.Option("--model", help="Override the provider model for this session.")
    ] = None,
    reset: Annotated[
        bool, typer.Option("--reset", help="Clear the saved default session.")
    ] = False,
) -> None:
    """Start an interactive assistant session."""
    try:
        session = load_session()
        if reset:
            session.messages.clear()
            save_session(session)
            print_success("Session reset.")
            return

        print_success("Chat started. Type exit or quit to leave.")
        while True:
            message = typer.prompt("cli-tool")
            if message.strip().lower() in {"exit", "quit"}:
                save_session(session)
                print_success("Session saved.")
                return

            prompt = build_chat_prompt(session.messages, message)
            if provider == providers.Provider.OPENAI:
                token_result = count_prompt_tokens(prompt, model=model)
                if not token_result.should_send and compact_session(session):
                    save_session(session)
                    console.print(
                        "[yellow]Token check:[/yellow] Chat history was compacted "
                        "before sending this turn."
                    )
                    prompt = build_chat_prompt(session.messages, message)
                    token_result = count_prompt_tokens(prompt, model=model)
                require_sendable(token_result)
            answer = providers.generate_text(prompt, provider, model=model)
            append_message(session, "user", message)
            append_message(session, "assistant", answer)
            save_session(session)
            print_panel(answer, title="Chat")
    except (OSError, RuntimeError, ValueError) as error:
        exit_with_error(error)
