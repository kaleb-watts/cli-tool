# CLI Tool

A terminal-native AI workflow CLI for builders, developers, and students. It turns rough notes, code, local files, and repo context into useful artifacts without becoming a generic chatbot wrapper.

The OpenAI provider uses the OpenAI Responses API through one shared client helper, and commands keep prompt instructions separate from dynamic user input where the workflow needs structured prompting.

## What It Does

- Draft emails from rough notes
- Review code files
- Summarize meetings
- Return structured JSON for meeting summaries and code reviews
- Ask grounded questions about local files
- Analyze CSV, log, and text files locally
- Research topics with a clear non-live-web disclaimer
- Review a repo using only safe allowlisted commands
- Run an interactive chat mode with local session history

## Installation

Install dependencies:

```bash
uv sync
```

Create your environment file:

```bash
cp .env.example .env
```

Add your API keys to `.env`:

```env
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
ANTHROPIC_MODEL=claude-3-5-haiku-latest
```

`.env` is ignored by Git. Do not commit API keys.

You can also export keys for a single shell session:

```bash
export OPENAI_API_KEY="your_key_here"
export ANTHROPIC_API_KEY="your_key_here"
```

Run the CLI:

```bash
uv run cli-tool --help
```

## Commands

Show help:

```bash
uv run cli-tool --help
```

Draft an email:

```bash
uv run cli-tool email "Tell John I finished the report and can send it tonight."
```

Review code:

```bash
uv run cli-tool review src/cli_tool/main.py
uv run cli-tool review src/cli_tool/main.py --json
```

Summarize a meeting:

```bash
uv run cli-tool meeting notes.txt
uv run cli-tool meeting notes.txt --json
```

Ask a grounded question about a file:

```bash
uv run cli-tool ask-file README.md "What is missing?"
uv run cli-tool ask-file src/cli_tool/main.py "How can this be cleaner?"
```

Analyze files locally:

```bash
uv run cli-tool analyze data.csv
uv run cli-tool analyze app.log --json
uv run cli-tool analyze notes.txt
```

Research a topic:

```bash
uv run cli-tool research "best Python CLI packaging practices with uv"
```

This version does not perform live web search. Research output is model-generated unless a future provider integration adds web search.

Review the current repo safely:

```bash
uv run cli-tool repo-review
uv run cli-tool repo-review --json
uv run cli-tool repo-review --skip-checks
```

Repo review uses an exact allowlist of safe commands and never runs arbitrary shell commands.

Start chat mode:

```bash
uv run cli-tool chat
uv run cli-tool chat --reset
```

Session history is stored locally at `.cli_tool/sessions/default.json`, which is ignored by Git.

Use Anthropic instead of OpenAI:

```bash
uv run cli-tool email "Ask my instructor for a meeting." --provider anthropic
```

Override the provider model for one run:

```bash
uv run cli-tool review src/cli_tool/main.py --model gpt-4.1
```

Save AI output:

```bash
uv run cli-tool meeting notes.txt --save summary.md
```

## JSON Output

JSON mode prints valid JSON only, without Rich panels or markdown fences, so it can be piped into tools like `jq`:

```bash
uv run cli-tool meeting notes.txt --json | jq .
uv run cli-tool review app.py --json | jq '.issues'
```

Example meeting JSON:

```json
{
  "summary": "The team agreed to ship the MVP by Friday.",
  "decisions": ["Use SQLite locally before adding Postgres."],
  "action_items": [
    {
      "task": "Finish CLI JSON output mode",
      "owner": null,
      "due_date": null,
      "priority": "high"
    }
  ]
}
```

If the model returns invalid JSON, the CLI exits with a clear error instead of printing malformed data as if it worked.

## Safety

- `repo-review` uses an exact allowlist: `git status --short`, `git diff --stat`, `find . -maxdepth 3 -type f`, `tree -L 3`, `uv run ruff check .`, and `uv run pytest`.
- `repo-review` never runs arbitrary user-provided shell commands and never modifies files.
- Large ask-file inputs are truncated to a safe preview with a warning.
- Local chat sessions are stored under `.cli_tool/`, which is ignored by Git.
- The CLI never prints API keys.

## Known Limitations

- `research` does not use live web search yet. Its answers are model-generated and not freshly verified.
- JSON mode validates that the model returned parseable JSON with required top-level keys, but it does not yet enforce a full schema for every field.
- Large files use preview truncation instead of chunking, embeddings, or full RAG.
- No dedicated type checker is configured yet; development checks currently use Ruff and pytest.

## Development

Format:

```bash
uv run ruff format .
```

Lint:

```bash
uv run ruff check .
```

Test:

```bash
uv run pytest
```

Run all checks:

```bash
just check
```

## Secrets

Never commit `.env`, API keys, local virtual environments, cache folders, or generated session files.
