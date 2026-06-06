import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_SESSION_PATH = Path(".cli_tool/sessions/default.json")
MAX_HISTORY_MESSAGES = 20
RECENT_MESSAGES_TO_KEEP = 8


@dataclass
class ChatSession:
    messages: list[dict[str, str]] = field(default_factory=list)
    updated_at: str | None = None


def load_session(path: Path = DEFAULT_SESSION_PATH) -> ChatSession:
    if not path.exists():
        return ChatSession()

    data = json.loads(path.read_text(encoding="utf-8"))
    messages = data.get("messages", [])
    if not isinstance(messages, list):
        messages = []

    return ChatSession(messages=messages, updated_at=data.get("updated_at"))


def save_session(session: ChatSession, path: Path = DEFAULT_SESSION_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    trimmed_messages = session.messages[-MAX_HISTORY_MESSAGES:]
    payload: dict[str, Any] = {
        "updated_at": datetime.now(UTC).isoformat(),
        "messages": trimmed_messages,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def append_message(session: ChatSession, role: str, content: str) -> None:
    session.messages.append({"role": role, "content": content})


def compact_session(session: ChatSession) -> bool:
    if len(session.messages) <= RECENT_MESSAGES_TO_KEEP:
        return False

    older_messages = session.messages[:-RECENT_MESSAGES_TO_KEEP]
    recent_messages = session.messages[-RECENT_MESSAGES_TO_KEEP:]
    summary_parts = [
        f"{message.get('role', 'unknown')}: {message.get('content', '')[:240]}"
        for message in older_messages
    ]
    session.messages = [
        {
            "role": "system",
            "content": "Compact summary of older chat turns:\n" + "\n".join(summary_parts),
        },
        *recent_messages,
    ]
    return True
