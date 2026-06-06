# CLI Tool

A small Python CLI for turning rough input into useful AI outputs.

## Features

- Draft emails from rough notes
- Review code files
- Summarize meeting notes
- Choose OpenAI or Anthropic
- Save output to a file

## Setup

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

## Usage

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
```

Summarize meeting notes:

```bash
uv run cli-tool meeting notes.txt
```

Use Anthropic instead of OpenAI:

```bash
uv run cli-tool email "Ask my instructor for a meeting." --provider anthropic
```

Save output:

```bash
uv run cli-tool meeting notes.txt --save summary.md
```

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
