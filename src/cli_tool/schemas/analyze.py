from typing import Literal

from pydantic import BaseModel, ConfigDict


class AnalysisFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    explanation: str
    evidence: str | None
    severity: Literal["low", "medium", "high"]


class AnalysisOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_type: Literal["csv", "log", "text", "unknown"]
    summary: str
    findings: list[AnalysisFinding]
    patterns: list[str]
    recommended_actions: list[str]
    warnings: list[str]


AnalysisJson = AnalysisOutput
