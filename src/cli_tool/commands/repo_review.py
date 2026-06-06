from typing import Annotated, Any

import typer

from cli_tool.core.errors import exit_with_error
from cli_tool.core.json_output import model_to_json_dict, validate_json_model
from cli_tool.core.output import print_json, print_panel
from cli_tool.core.repo_review import build_repo_report, format_repo_report
from cli_tool.schemas.repo_review import RepoReviewJson


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
            validated = validate_json_model(to_repo_review_json(report), RepoReviewJson)
            print_json(model_to_json_dict(validated))
            return
        print_panel(format_repo_report(report), title="Repo Review")
    except (OSError, RuntimeError, ValueError) as error:
        exit_with_error(error)


def to_repo_review_json(report: dict[str, Any]) -> dict[str, Any]:
    files = report.get("specific_files_to_edit", [])
    return {
        "summary": f"Reviewed repo: {report['repo']}",
        "working": report["what_is_working"],
        "broken_or_risky": report["what_is_broken"],
        "highest_priority_fixes": [
            {
                "priority": "high" if index == 0 else "medium",
                "title": fix,
                "reason": "Identified by safe repo-review inspection.",
                "files_to_edit": files,
            }
            for index, fix in enumerate(report["highest_priority_fixes"])
        ],
        "next_3_commits": report["next_3_commits"],
        "warnings": [],
    }
