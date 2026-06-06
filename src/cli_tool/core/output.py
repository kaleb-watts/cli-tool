import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel

console = Console()


def print_panel(content: str, title: str = "CLI Tool Output") -> None:
    console.print(Panel(content, title=title, border_style="green"))


def print_error(error: Exception) -> None:
    console.print(f"[bold red]Error:[/bold red] {error}")


def print_success(message: str) -> None:
    console.print(f"[bold green]{message}[/bold green]")


def print_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, indent=2))


def print_saved(path: str | Path) -> None:
    console.print(f"[bold green]Saved to:[/bold green] {path}")
