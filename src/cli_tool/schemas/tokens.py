from typing import Literal

from pydantic import BaseModel, ConfigDict


class TokenSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["file", "chat", "repo", "raw"]
    path: str | None = None


class TokenReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str
    input_tokens: int
    risk_level: Literal["safe", "medium", "large", "too_large"]
    should_send: bool
    recommendation: str
    source: TokenSource
