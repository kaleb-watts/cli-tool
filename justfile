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

tree:
tree -I ".venv|pycache|.git|.pytest_cache|.ruff_cache"
