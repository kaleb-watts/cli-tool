from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class AnalysisOutput(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: Literal["csv", "log", "text"]
    file: str


class AnalysisJson(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: Literal["csv", "log", "text"]
    file: str
    line_count: int | None = None
    row_count: int | None = None
    columns: list[str] | None = None
    missing_values: dict[str, int] | None = None
    insights: list[str] | None = None
    error_count: int | None = None
    warning_count: int | None = None
    repeated_lines: list[dict[str, Any]] | None = None
    likely_focus: list[str] | None = None
    word_count: int | None = None
    themes: list[str] | None = None
    action_items: list[str] | None = None
    based_on_selected_context: bool | None = None
