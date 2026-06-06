from typing import Literal

from pydantic import BaseModel, ConfigDict


class CodeIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: Literal["low", "medium", "high", "critical"]
    file: str | None
    line: int | None
    title: str
    explanation: str
    suggested_fix: str


class CodeReviewOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    issues: list[CodeIssue]
    next_steps: list[str]
    warnings: list[str]


CodeReview = CodeReviewOutput
