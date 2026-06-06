from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class TokenRiskLevel(StrEnum):
    SAFE = "safe"
    MEDIUM = "medium"
    LARGE = "large"
    TOO_LARGE = "too_large"


SAFE_INPUT_TOKENS = 25_000
MEDIUM_INPUT_TOKENS = 75_000
LARGE_INPUT_TOKENS = 150_000


@dataclass(frozen=True)
class TokenPolicyResult:
    model: str
    input_tokens: int
    risk_level: TokenRiskLevel
    should_send: bool
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["risk_level"] = self.risk_level.value
        return data


def evaluate_token_policy(model: str, input_tokens: int) -> TokenPolicyResult:
    if input_tokens <= SAFE_INPUT_TOKENS:
        return TokenPolicyResult(
            model=model,
            input_tokens=input_tokens,
            risk_level=TokenRiskLevel.SAFE,
            should_send=True,
            recommendation="Okay to send.",
        )

    if input_tokens <= MEDIUM_INPUT_TOKENS:
        return TokenPolicyResult(
            model=model,
            input_tokens=input_tokens,
            risk_level=TokenRiskLevel.MEDIUM,
            should_send=True,
            recommendation=(
                "Moderate request size. Consider using --json or a narrower file if cost matters."
            ),
        )

    if input_tokens <= LARGE_INPUT_TOKENS:
        return TokenPolicyResult(
            model=model,
            input_tokens=input_tokens,
            risk_level=TokenRiskLevel.LARGE,
            should_send=False,
            recommendation=(
                "Large request. Use a preview, smaller file, or chunked workflow before sending."
            ),
        )

    return TokenPolicyResult(
        model=model,
        input_tokens=input_tokens,
        risk_level=TokenRiskLevel.TOO_LARGE,
        should_send=False,
        recommendation=(
            "Too large to send safely. Use a smaller file, preview, or future chunking workflow."
        ),
    )


def format_token_policy(result: TokenPolicyResult) -> str:
    return "\n".join(
        [
            f"Model: {result.model}",
            f"Input tokens: {result.input_tokens:,}",
            f"Risk: {result.risk_level.value}",
            f"Recommendation: {result.recommendation}",
        ]
    )
