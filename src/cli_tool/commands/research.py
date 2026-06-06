import json
from typing import Annotated

import typer

from cli_tool import providers
from cli_tool.core.errors import exit_with_error
from cli_tool.core.files import save_text_file
from cli_tool.core.json_output import load_json_model_with_repair, model_to_json_dict
from cli_tool.core.output import print_json, print_panel, print_saved
from cli_tool.core.structured_outputs import parse_structured_prompt
from cli_tool.core.token_counter import count_prompt_tokens, require_sendable
from cli_tool.prompts.workflows import (
    build_json_repair_prompt,
    build_research_json_prompt,
)
from cli_tool.schemas.research import ResearchJson, ResearchOutput


def research(
    query: Annotated[str, typer.Argument(help="Research query.")],
    provider: Annotated[
        providers.Provider, typer.Option("--provider", "-p", help="AI provider to use.")
    ] = providers.Provider.OPENAI,
    model: Annotated[
        str | None, typer.Option("--model", help="Override the provider model for this run.")
    ] = None,
    no_web: Annotated[
        bool, typer.Option("--no-web", help="Disable live web search and use model-only fallback.")
    ] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Return valid machine-readable JSON only.")
    ] = False,
    save: Annotated[str | None, typer.Option("--save", "-s", help="Save output to a file.")] = None,
) -> None:
    """Research a topic with live web search when available."""
    try:
        raw_result, used_live_web, fallback_warning = run_research(query, provider, model, no_web)
        validated = load_json_model_with_repair(
            raw_result,
            ResearchJson,
            lambda error: providers.generate_text(
                build_json_repair_prompt(raw_result, error, "ResearchJson"),
                provider,
                model=model,
            ),
        )
        data = model_to_json_dict(validated)
        if fallback_warning and fallback_warning not in data["limitations"]:
            data["limitations"].append(fallback_warning)

        if json_output:
            print_json(data)
            if save:
                save_text_file(save, json.dumps(data, indent=2))
            return

        result = format_research_output(data, data["used_live_web"], fallback_warning)
        print_panel(result, title="Research")
        if save:
            save_text_file(save, result)
            print_saved(save)
    except (OSError, RuntimeError, ValueError) as error:
        exit_with_error(error)


def run_research(
    query: str,
    provider: providers.Provider,
    model: str | None,
    no_web: bool,
) -> tuple[str, bool, str | None]:
    if provider == providers.Provider.OPENAI and not no_web:
        try:
            prompt = build_research_json_prompt(query, used_live_web=True)
            parsed = parse_structured_prompt(
                prompt.instructions,
                prompt.input,
                ResearchOutput,
                model=model,
                task=prompt.task,
                tools=[{"type": "web_search_preview"}],
            )
            return parsed.model_dump_json(), True, None
        except Exception as error:
            fallback_warning = f"Live web search failed; using model-only fallback: {error}"
            return run_model_only_research(query, provider, model), False, fallback_warning

    return (
        run_model_only_research(query, provider, model),
        False,
        (
            "Live web search disabled; using model-only fallback."
            if no_web
            else "Live web search is only available for the OpenAI provider."
        ),
    )


def run_model_only_research(
    query: str,
    provider: providers.Provider,
    model: str | None,
) -> str:
    prompt = build_research_json_prompt(query, used_live_web=False)
    if provider == providers.Provider.OPENAI:
        require_sendable(count_prompt_tokens(prompt, model=model))
    return providers.generate_text(prompt, provider, model=model)


def format_research_output(
    data: dict,
    used_live_web: bool,
    fallback_warning: str | None,
) -> str:
    lines = [
        f"Query: {data['query']}",
        f"Used live web: {str(used_live_web).lower()}",
        "",
        "Summary",
        data["summary"],
        "",
        "Key findings",
    ]
    lines.extend(
        f"- {finding['claim']} ({finding['source_title']}: {finding['source_url']})"
        for finding in data["key_findings"]
    )
    lines.append("")
    lines.append("Sources")
    lines.extend(f"- {source['title']}: {source['url']}" for source in data["sources"])
    if fallback_warning:
        lines.extend(["", f"Warning: {fallback_warning}"])
    if data["limitations"]:
        lines.append("")
        lines.append("Limitations")
        lines.extend(f"- {limitation}" for limitation in data["limitations"])
    return "\n".join(lines)
