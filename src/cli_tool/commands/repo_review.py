from typing import Annotated

import typer

from cli_tool.core.errors import exit_with_error
from cli_tool.core.output import print_json, print_panel
from cli_tool.core.repo_review import build_repo_report, format_repo_report


def repo_review(
    json_output: Annotated[
        bool, typer.Option("--json", help="Return valid machine-readable JSON only.")
    ] = False,
    skip_checks: Annotated[
        bool, typer.Option("--skip-checks", help="Skip Ruff and pytest for a faster report.")
    ] = False,
) -> None:
    """Inspect the current repo with safe allowlisted commands."""
    try:
        report = build_repo_report(run_checks=not skip_checks)
        if json_output:
            print_json(report)
            return
        print_panel(format_repo_report(report), title="Repo Review")
    except (OSError, RuntimeError, ValueError) as error:
        exit_with_error(error)
