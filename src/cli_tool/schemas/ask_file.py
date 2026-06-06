from pydantic import BaseModel, ConfigDict


class AskFileSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    path: str
    truncated: bool


class AskFileJson(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str
    token_check: dict | None = None
    source: AskFileSource
