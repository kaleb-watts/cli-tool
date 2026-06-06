from typing import Literal

from pydantic import BaseModel, ConfigDict


class ActionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: str
    owner: str | None
    due_date: str | None
    priority: Literal["low", "medium", "high"]


class MeetingSummaryOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    decisions: list[str]
    action_items: list[ActionItem]
    warnings: list[str]


MeetingSummary = MeetingSummaryOutput
