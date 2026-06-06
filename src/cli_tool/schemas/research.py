from typing import Literal

from pydantic import BaseModel, ConfigDict


class ResearchSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    url: str | None
    publisher: str | None
    date: str | None


class ResearchFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim: str
    source_title: str | None
    source_url: str | None
    confidence: Literal["low", "medium", "high"]


class ResearchOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    used_live_web: bool
    summary: str
    key_findings: list[ResearchFinding]
    sources: list[ResearchSource]
    follow_up_queries: list[str]
    limitations: list[str]


ResearchJson = ResearchOutput
