from typing import Literal

from pydantic import BaseModel, ConfigDict


class ResearchFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim: str
    source_title: str
    source_url: str
    source_date: str | None = None
    confidence: Literal["low", "medium", "high"]


class ResearchSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    url: str
    publisher: str | None = None
    date: str | None = None


class ResearchJson(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str
    used_live_web: bool
    summary: str
    key_findings: list[ResearchFinding]
    sources: list[ResearchSource]
    follow_up_queries: list[str]
    limitations: list[str]
