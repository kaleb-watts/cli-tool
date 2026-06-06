import csv
from collections import Counter
from pathlib import Path
from typing import Any

from cli_tool.core.files import read_text_file


def analyze_path(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        return analyze_csv(file_path)
    if suffix in {".log", ".out", ".err"}:
        return analyze_log(file_path)
    return analyze_text(file_path)


def analyze_csv(path: Path) -> dict[str, Any]:
    with path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    columns = list(rows[0].keys()) if rows else []
    missing_values = {
        column: sum(1 for row in rows if not (row.get(column) or "").strip()) for column in columns
    }

    insights = []
    if not rows:
        insights.append("The CSV has headers but no data rows.")
    if columns:
        insights.append(f"Detected {len(columns)} columns across {len(rows)} rows.")
    columns_with_missing = [column for column, count in missing_values.items() if count]
    if columns_with_missing:
        insights.append(f"Columns with missing values: {', '.join(columns_with_missing)}.")

    return {
        "type": "csv",
        "file": str(path),
        "row_count": len(rows),
        "columns": columns,
        "missing_values": missing_values,
        "insights": insights,
    }


def analyze_log(path: Path) -> dict[str, Any]:
    text = read_text_file(path)
    lines = [line for line in text.splitlines() if line.strip()]
    error_lines = [line for line in lines if "error" in line.lower()]
    warning_lines = [line for line in lines if "warn" in line.lower()]
    repeated_lines = Counter(lines).most_common(5)

    return {
        "type": "log",
        "file": str(path),
        "line_count": len(lines),
        "error_count": len(error_lines),
        "warning_count": len(warning_lines),
        "repeated_lines": [
            {"line": line, "count": count} for line, count in repeated_lines if count > 1
        ],
        "likely_focus": error_lines[:5] or warning_lines[:5],
    }


def analyze_text(path: Path) -> dict[str, Any]:
    text = read_text_file(path)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    words = text.split()
    action_lines = [
        line
        for line in lines
        if any(marker in line.lower() for marker in ["todo", "action", "next", "follow up"])
    ]

    return {
        "type": "text",
        "file": str(path),
        "line_count": len(lines),
        "word_count": len(words),
        "themes": most_common_words(words),
        "action_items": action_lines[:10],
    }


def most_common_words(words: list[str]) -> list[str]:
    ignored = {"the", "and", "for", "with", "that", "this", "from", "are", "was", "you"}
    normalized = [
        word.strip(".,:;!?()[]{}\"'").lower()
        for word in words
        if len(word.strip(".,:;!?()[]{}\"'")) > 3
    ]
    return [
        word
        for word, _count in Counter(word for word in normalized if word not in ignored).most_common(
            8
        )
    ]


def format_analysis(data: dict[str, Any]) -> str:
    lines = [f"File: {data['file']}", f"Type: {data['type']}"]

    if data["type"] == "csv":
        lines.extend(
            [
                f"Rows: {data['row_count']}",
                f"Columns: {', '.join(data['columns']) or 'none'}",
                "Insights:",
                *[f"- {insight}" for insight in data["insights"]],
            ]
        )
    elif data["type"] == "log":
        lines.extend(
            [
                f"Lines: {data['line_count']}",
                f"Errors: {data['error_count']}",
                f"Warnings: {data['warning_count']}",
                "Likely focus:",
                *[f"- {line}" for line in data["likely_focus"]],
            ]
        )
    else:
        lines.extend(
            [
                f"Lines: {data['line_count']}",
                f"Words: {data['word_count']}",
                f"Themes: {', '.join(data['themes']) or 'none'}",
                "Action items:",
                *[f"- {line}" for line in data["action_items"]],
            ]
        )

    return "\n".join(lines)
