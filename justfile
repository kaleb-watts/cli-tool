help:
	uv run cli-tool --help

fmt:
	uv run ruff format .

lint:
	uv run ruff check .

typecheck:
	uv run mypy src tests

test:
	uv run pytest

check:
	uv run ruff format --check .
	uv run ruff check .
	uv run mypy src tests
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

tokens file:
	uv run cli-tool tokens "{{file}}"

tokens-chat:
	uv run cli-tool tokens-chat

tree:
	tree -I ".venv|pycache|.git|.pytest_cache|.ruff_cache|.cli_tool"
