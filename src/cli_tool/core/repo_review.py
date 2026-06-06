import subprocess
from pathlib import Path
from typing import Any

from cli_tool.core.errors import CliToolError

SAFE_COMMANDS: dict[str, list[str]] = {
    "uv run ruff check .": ["uv", "run", "ruff", "check", "."],
    "uv run pytest": ["uv", "run", "pytest"],
    "git status --short": ["git", "status", "--short"],
    "git diff --stat": ["git", "diff", "--stat"],
    "tree -L 3": ["tree", "-L", "3"],
    "find . -maxdepth 3 -type f": ["find", ".", "-maxdepth", "3", "-type", "f"],
}


def run_safe_command(command: str, cwd: Path | None = None) -> str:
    if command not in SAFE_COMMANDS:
        raise CliToolError(f"Unsafe command is not allowed: {command}")

    result = subprocess.run(
        SAFE_COMMANDS[command],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    return output or f"Command exited with code {result.returncode} and no output."


def build_repo_report(cwd: Path | None = None, run_checks: bool = True) -> dict[str, Any]:
    repo_path = cwd or Path.cwd()
    commands = ["git status --short", "git diff --stat", "find . -maxdepth 3 -type f"]
    if run_checks:
        commands.extend(["uv run ruff check .", "uv run pytest"])

    command_outputs = {}
    for command in commands:
        try:
            command_outputs[command] = run_safe_command(command, repo_path)
        except (OSError, CliToolError) as error:
            command_outputs[command] = f"Unavailable: {error}"

    status = command_outputs.get("git status --short", "")
    diff_stat = command_outputs.get("git diff --stat", "")
    ruff = command_outputs.get("uv run ruff check .", "Skipped")
    pytest = command_outputs.get("uv run pytest", "Skipped")

    broken = []
    if "All checks passed" not in ruff and run_checks:
        broken.append("Ruff reported issues or could not run.")
    if "passed" not in pytest and run_checks:
        broken.append("Pytest reported failures or could not run.")
    if not broken:
        broken.append("No obvious breakages detected by the safe checks.")

    return {
        "repo": str(repo_path),
        "what_is_working": [
            "Safe repo inspection completed.",
            "Git status and diff stat were collected.",
        ],
        "what_is_broken": broken,
        "highest_priority_fixes": [
            "Address any lint or test failures first.",
            "Review uncommitted files before adding new features.",
        ],
        "next_3_commits": [
            "Stabilize tests and command boundaries.",
            "Add or refine one CLI feature with focused tests.",
            "Update README examples after behavior changes.",
        ],
        "specific_files_to_edit": suggest_files(
            command_outputs.get("find . -maxdepth 3 -type f", "")
        ),
        "command_outputs": command_outputs,
        "git_status": status,
        "git_diff_stat": diff_stat,
    }


def suggest_files(file_listing: str) -> list[str]:
    candidates = []
    for line in file_listing.splitlines():
        if line.endswith((".py", "README.md", "pyproject.toml", "justfile")):
            candidates.append(line.removeprefix("./"))
    return candidates[:10]


def format_repo_report(report: dict[str, Any]) -> str:
    sections = [
        ("What is working", report["what_is_working"]),
        ("What is broken", report["what_is_broken"]),
        ("Highest-priority fixes", report["highest_priority_fixes"]),
        ("Suggested next 3 commits", report["next_3_commits"]),
        ("Specific files to edit", report["specific_files_to_edit"]),
    ]
    lines = [f"Repo: {report['repo']}"]
    for title, items in sections:
        lines.append("")
        lines.append(title)
        lines.extend(f"- {item}" for item in items)
    return "\n".join(lines)
