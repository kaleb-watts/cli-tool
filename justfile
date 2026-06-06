help:
uv run cli-tool --help

fmt:
uv run ruff format .

lint:
uv run ruff check .

test:
uv run pytest

check:
uv run ruff format .
uv run ruff check .
uv run pytest

email text:
uv run cli-tool email "{{text}}"

review file:
uv run cli-tool review "{{file}}"

meeting file:
uv run cli-tool meeting "{{file}}"

research query:
uv run cli-tool research "{{query}}"

ask file question:
uv run cli-tool ask-file "{{file}}" "{{question}}"

analyze file:
uv run cli-tool analyze "{{file}}"

repo-review:
uv run cli-tool repo-review

chat:
uv run cli-tool chat

tree:
tree -I ".venv|pycache|.git|.pytest_cache|.ruff_cache|.cli_tool"
