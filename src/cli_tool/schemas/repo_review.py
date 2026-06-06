from typing import Literal

from pydantic import BaseModel, ConfigDict


class RepoFix(BaseModel):
    model_config = ConfigDict(extra="forbid")

    priority: Literal["low", "medium", "high"]
    title: str
    reason: str
    files_to_edit: list[str]


class RepoReviewOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    working: list[str]
    broken_or_risky: list[str]
    highest_priority_fixes: list[RepoFix]
    next_3_commits: list[str]
    warnings: list[str]


RepoReviewJson = RepoReviewOutput
