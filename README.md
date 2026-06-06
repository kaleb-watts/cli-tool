# CLI Tool

A terminal-native AI workflow CLI for builders, developers, and students. It turns rough notes, code, local files, and repo context into useful artifacts without becoming a generic chatbot wrapper.

The OpenAI provider uses the OpenAI Responses API through one shared client helper, and commands keep prompt instructions separate from dynamic user input where the workflow needs structured prompting. OpenAI-backed JSON workflows use Structured Outputs with `client.responses.parse(..., text_format=<PydanticModel>)` so command output follows real data contracts instead of prompt-only JSON requests.

## What It Does

- Draft emails from rough notes
- Review code files
- Summarize meetings
- Return schema-validated JSON for automation and `jq`
- Ask grounded questions about local files
- Analyze CSV, log, and text files locally
- Research topics with live OpenAI web search and explicit fallback labeling
- Review a repo using only safe allowlisted commands
- Run an interactive chat mode with local session history
- Count OpenAI input tokens before sending large prompts

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

## Environment Variables

- `OPENAI_API_KEY`: Required for OpenAI-backed commands, live web research, Structured Outputs, and token counting.
- `ANTHROPIC_API_KEY`: Required when using `--provider anthropic`.
- `OPENAI_MODEL`: Optional default OpenAI model override.
- `ANTHROPIC_MODEL`: Optional default Anthropic model override.

Example:

```bash
export OPENAI_API_KEY="your_key_here"
```

Never commit `.env`, API keys, shell history with secrets, local caches, virtual environments, or generated session files.

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
uv run cli-tool ask-file README.md "List the setup steps" --json
```

Analyze files locally:

```bash
uv run cli-tool analyze data.csv
uv run cli-tool analyze app.log --json
uv run cli-tool analyze notes.txt
```

Count tokens before sending a file to AI:

```bash
uv run cli-tool tokens README.md
uv run cli-tool tokens src/cli_tool/main.py --model gpt-4.1
uv run cli-tool tokens app.log --json
```

Count the saved chat session:

```bash
uv run cli-tool tokens-chat
uv run cli-tool tokens-chat --session default
uv run cli-tool tokens-chat --json
```

Research a topic:

```bash
uv run cli-tool research "best Python CLI packaging practices with uv"
uv run cli-tool research "best Python CLI packaging practices with uv" --json
uv run cli-tool research "best Python CLI packaging practices with uv" --no-web
```

OpenAI research uses the Responses API web search tool by default. If web search fails or `--no-web` is passed, the output is clearly labeled as model-only fallback and `used_live_web` is `false`.

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

Commands that currently support `--json`: `review`, `meeting`, `ask-file`, `analyze`, `repo-review`, `research`, `tokens`, and `tokens-chat`.

## Research

`research` returns a summary, key findings, cited sources, follow-up queries, and limitations. In JSON mode the output includes:

```json
{
  "query": "best Python CLI packaging practices with uv",
  "used_live_web": true,
  "summary": "Short verified summary.",
  "key_findings": [
    {
      "claim": "A sourced claim.",
      "source_title": "Source title",
      "source_url": "https://example.com",
      "confidence": "high"
    }
  ],
  "sources": [
    {
      "title": "Source title",
      "url": "https://example.com",
      "publisher": "Example",
      "date": null
    }
  ],
  "follow_up_queries": ["specific follow-up query"],
  "limitations": []
}
```

`used_live_web` is only `true` when live web search was actually used. Fallback output includes a limitation explaining why the answer is not web-verified.

## Structured JSON Output

JSON mode prints JSON only, without Rich panels or markdown fences, so it can be piped into tools like `jq`:

```bash
uv run cli-tool meeting notes.txt --json | jq .
uv run cli-tool review app.py --json | jq '.issues'
uv run cli-tool research "current uv packaging guidance" --json | jq '.sources[].url'
uv run cli-tool tokens README.md --json | jq .
```

For OpenAI-backed model-generated JSON commands, the CLI uses OpenAI Structured Outputs via `client.responses.parse` and reads `response.output_parsed`. The schema is passed as a Pydantic model through `text_format`, which keeps Python types and JSON output fields aligned.

For Anthropic or fallback model-only paths, the CLI validates raw JSON against the same Pydantic schemas and makes one repair attempt. If validation still fails, the command exits nonzero with a clear error instead of printing malformed or schema-invalid JSON.

Schemas forbid extra keys, use `Literal` values for fields such as `severity`, `priority`, `confidence`, and token `risk_level`, and keep optional values present as `null` rather than omitting fields. If the model refuses or the structured response is empty, the CLI reports a clean command error instead of a traceback.

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
  ],
  "warnings": []
}
```

Example review issue JSON:

```json
{
  "severity": "high",
  "file": "src/app.py",
  "line": 42,
  "title": "Unhandled missing configuration",
  "explanation": "The command assumes the variable is always present.",
  "suggested_fix": "Validate the configuration before using it and return a clean CLI error."
}
```

Structured schemas are available for `meeting`, `review`, `ask-file`, `analyze`, `repo-review`, `research`, `tokens`, and `tokens-chat`.

## Large File Handling

Large `ask-file` inputs use chunking plus lightweight keyword retrieval instead of silently sending the beginning of the file. The CLI splits the file into overlapping chunks, scores chunks against the user question, sends selected chunks in XML tags, and tells the user when selected chunks are being used.

`analyze` remains local and deterministic: CSV analysis reports row count, columns, missing values, and insights; log analysis reports warning/error counts, repeated lines, and likely focus lines; text analysis reports themes and action-like lines. This keeps analysis useful without dumping whole files into a model.

## Token Counting And Cost Safety

The CLI can count OpenAI input tokens before a request is sent to the model. This uses the official `client.responses.input_tokens.count(...)` endpoint with the same prompt shape used by Responses API calls: model, instructions, input, and tools when relevant.

Human-readable example:

```txt
Model: gpt-4.1-mini
Input tokens: 14,820
Risk: safe
Recommendation: Okay to send.
```

JSON example:

```json
{
  "model": "gpt-4.1-mini",
  "input_tokens": 14820,
  "risk_level": "safe",
  "should_send": true,
  "recommendation": "Okay to send.",
  "source": {
    "type": "file",
    "path": "README.md"
  }
}
```

Risk levels:

- `safe`: 25,000 input tokens or fewer. Send normally.
- `medium`: 25,001 to 75,000 input tokens. Allowed, but worth watching.
- `large`: 75,001 to 150,000 input tokens. The CLI blocks full sends and recommends preview or chunking.
- `too_large`: More than 150,000 input tokens. The CLI refuses to send the full request.

Token counting gives input token counts, not a final dollar cost. Output tokens are unknown until generation finishes, and current pricing is not implemented in this CLI.

Images, PDFs, tool definitions, schemas, instructions, file content, and chat history can all add tokens. Future image/PDF support should count those payloads with the official endpoint too, not by guessing from file size.

## Safety

- `repo-review` uses an exact allowlist: `git status --short`, `git diff --stat`, `find . -maxdepth 3 -type f`, `tree -L 3`, `uv run ruff check .`, and `uv run pytest`.
- `repo-review` never runs arbitrary user-provided shell commands and never modifies files.
- Large ask-file inputs use retrieved chunks with a warning instead of silent truncation.
- OpenAI-backed `ask-file`, `research`, `chat`, and JSON review/meeting workflows count tokens before generation.
- The CLI refuses to token-count `.env` files or secret environment files.
- Local chat sessions are stored under `.cli_tool/`, which is ignored by Git.
- The CLI never prints API keys.

## Remaining Boundaries

- Live web research is implemented for the OpenAI provider. Anthropic research uses the labeled model-only fallback.
- Local retrieval is keyword-based, not embeddings-based. The code is structured so embeddings can be added later.
- Token counting requires an OpenAI API key and reports input tokens only, not total cost.
- Anthropic-backed requests do not use the OpenAI token counting endpoint.
- PDF and image inputs are not implemented yet.

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

Type check:

```bash
uv run mypy src tests
```

Run all checks:

```bash
just check
```

`just check` runs formatting in check mode, Ruff linting, mypy, and pytest.

## Secrets

Never commit `.env`, API keys, local virtual environments, cache folders, or generated session files.
