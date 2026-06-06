from typing import Annotated

import typer

from cli_tool.core.analysis import analyze_path, format_analysis
from cli_tool.core.errors import exit_with_error
from cli_tool.core.output import print_json, print_panel


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
            print_json(data)
            return
        print_panel(format_analysis(data), title="File Analysis")
    except (OSError, RuntimeError, ValueError) as error:
        exit_with_error(error)
