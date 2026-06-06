from typing import Literal

from pydantic import BaseModel, ConfigDict


class ReviewIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: Literal["critical", "warning", "suggestion"]
    file: str | None
    line: int | None = None
    explanation: str
    suggested_fix: str


class CodeReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    issues: list[ReviewIssue]
