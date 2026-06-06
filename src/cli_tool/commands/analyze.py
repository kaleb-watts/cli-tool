from typing import Annotated, Any

import typer

from cli_tool.core.analysis import analyze_path, format_analysis
from cli_tool.core.errors import exit_with_error
from cli_tool.core.json_output import model_to_json_dict, validate_json_model
from cli_tool.core.output import print_json, print_panel
from cli_tool.schemas.analyze import AnalysisJson


def analyze(
    file: Annotated[str, typer.Argument(help="CSV, log, or text file to analyze.")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Return valid machine-readable JSON only.")
    ] = False,
) -> None:
    """Analyze a CSV, log, or text file locally."""
    try:
        data = analyze_path(file)
        if json_output:
            validated = validate_json_model(to_analysis_json(data), AnalysisJson)
            print_json(model_to_json_dict(validated))
            return
        print_panel(format_analysis(data), title="File Analysis")
    except (OSError, RuntimeError, ValueError) as error:
        exit_with_error(error)


def to_analysis_json(data: dict[str, Any]) -> dict[str, Any]:
    file_type = data["type"]
    warnings: list[str] = []
    findings = []
    patterns: list[str] = []
    recommended_actions: list[str] = []

    if file_type == "csv":
        findings.append(
            {
                "title": "CSV structure",
                "explanation": (
                    f"Detected {data['row_count']} rows and {len(data['columns'])} columns."
                ),
                "evidence": ", ".join(data["columns"]) or None,
                "severity": "low",
            }
        )
        patterns.extend(data.get("insights", []))
        missing = [column for column, count in data.get("missing_values", {}).items() if count]
        if missing:
            recommended_actions.append(f"Review missing values in: {', '.join(missing)}.")
    elif file_type == "log":
        findings.append(
            {
                "title": "Log issue summary",
                "explanation": (
                    f"Found {data['error_count']} errors and {data['warning_count']} warnings."
                ),
                "evidence": "\n".join(data.get("likely_focus", [])[:3]) or None,
                "severity": "medium" if data["error_count"] else "low",
            }
        )
        patterns.extend(item["line"] for item in data.get("repeated_lines", []))
        if data["error_count"]:
            recommended_actions.append("Investigate repeated errors before warnings.")
    else:
        findings.append(
            {
                "title": "Text summary",
                "explanation": (
                    f"Detected {data['word_count']} words across {data['line_count']} lines."
                ),
                "evidence": ", ".join(data.get("themes", [])) or None,
                "severity": "low",
            }
        )
        patterns.extend(data.get("themes", []))
        recommended_actions.extend(data.get("action_items", []))

    if data.get("based_on_selected_context"):
        warnings.append("Analysis is based on selected context, not the full file.")

    return {
        "file_type": file_type,
        "summary": f"Analyzed {data['file']} as {file_type}.",
        "findings": findings,
        "patterns": patterns,
        "recommended_actions": recommended_actions,
        "warnings": warnings,
    }
