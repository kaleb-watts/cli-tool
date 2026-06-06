import typer

from cli_tool.core.output import print_error


class CliToolError(ValueError):
    """User-facing error that should not render a traceback."""


type CommandError = OSError | RuntimeError | ValueError | CliToolError


def exit_with_error(error: CommandError) -> None:
    print_error(error)
    raise typer.Exit(1) from error
