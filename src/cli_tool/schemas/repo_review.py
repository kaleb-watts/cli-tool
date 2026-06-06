from typing import Any

from pydantic import BaseModel, ConfigDict


class RepoReviewJson(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repo: str
    what_is_working: list[str]
    what_is_broken: list[str]
    highest_priority_fixes: list[str]
    next_3_commits: list[str]
    specific_files_to_edit: list[str]
    command_outputs: dict[str, str]
    git_status: str
    git_diff_stat: str
    token_check: dict[str, Any] | None = None
