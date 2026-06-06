from html import escape

from cli_tool.core.models import ModelTask
from cli_tool.prompts.types import Prompt

PROMPT_VERSION = "2026-06-06"


def build_meeting_json_prompt(notes: str) -> Prompt:
    instructions = """
# Identity
You are an executive assistant.

# Instructions
Summarize the meeting notes according to the provided schema.

# Rules
- Use null when owner or due_date is unknown.
- Use an empty warnings list when there are no concerns.
- Do not invent facts.
""".strip()

    input_text = f"""
<meeting_notes>
{notes}
</meeting_notes>
""".strip()
    return Prompt(instructions=instructions, input=input_text, task=ModelTask.FAST)


def build_code_review_json_prompt(code: str, filename: str) -> Prompt:
    escaped_filename = escape(filename, quote=True)
    instructions = """
# Identity
You are a senior software engineer.

# Instructions
Review the file according to the provided schema.

# Rules
- If the file looks good, return an empty issues array.
- Use null for line when the line number is unknown.
- Do not invent line numbers, files, or evidence.
""".strip()

    input_text = f"""
<file path="{escaped_filename}">
{code}
</file>
""".strip()
    return Prompt(instructions=instructions, input=input_text, task=ModelTask.STRONG)


def build_research_prompt(query: str) -> Prompt:
    instructions = """
# Identity
You are a technical research assistant for builders and students.

# Instructions
- You do not have live web search in this CLI version.
- Be honest that the answer is model-generated and not freshly verified.
- Include sources only when you are confident they are stable, well-known references.

# Output Format
Return:
## Short answer
## Key findings
## Sources or references
## Suggested next action
""".strip()

    input_text = f"""
<query>
{query}
</query>
""".strip()
    return Prompt(instructions=instructions, input=input_text, task=ModelTask.STRONG)


def build_research_json_prompt(query: str, used_live_web: bool = False) -> Prompt:
    instructions = f"""
# Identity
You are a technical research assistant for builders and students.

# Instructions
Return valid JSON only.
Do not claim live verification unless used_live_web is true.
used_live_web must be {str(used_live_web).lower()}.

# Output Format
{{
  "query": "string",
  "used_live_web": {str(used_live_web).lower()},
  "summary": "string",
  "key_findings": [
    {{
      "claim": "string",
      "source_title": null,
      "source_url": null,
      "confidence": "low|medium|high"
    }}
  ],
  "sources": [
    {{
      "title": "string",
      "url": "string",
      "publisher": null,
      "date": null
    }}
  ],
  "follow_up_queries": ["string"],
  "limitations": ["string"]
}}
""".strip()

    input_text = f"""
<query>
{query}
</query>
""".strip()
    return Prompt(instructions=instructions, input=input_text, task=ModelTask.STRONG)


def build_ask_file_prompt(
    file_path: str, file_contents: str, user_question: str, truncated: bool
) -> Prompt:
    truncation_note = (
        "The file was truncated to a safe preview. Say that your answer is based on the preview."
        if truncated
        else "The full file content is included."
    )
    instructions = f"""
# Identity
You are a helpful code and document analysis assistant.

# Instructions
Answer the user's question using only the provided file content.
If the answer is not supported by the file, say so.
{truncation_note}
""".strip()

    input_text = f"""
<file path="{escape(file_path, quote=True)}">
{file_contents}
</file>

<question>
{user_question}
</question>
""".strip()
    return Prompt(instructions=instructions, input=input_text, task=ModelTask.STRONG)


def build_chat_prompt(history: list[dict[str, str]], user_message: str) -> Prompt:
    history_lines = "\n".join(
        f"{message.get('role', 'unknown')}: {message.get('content', '')}"
        for message in history[-12:]
    )
    instructions = """
# Identity
You are CLI Tool's interactive assistant for developer productivity.

# Instructions
Be practical, concise, and terminal-friendly.
""".strip()

    input_text = f"""
<history>
{history_lines}
</history>

<user_message>
{user_message}
</user_message>
""".strip()
    return Prompt(instructions=instructions, input=input_text, task=ModelTask.FAST)


def build_json_repair_prompt(raw_output: str, validation_error: str, schema_name: str) -> Prompt:
    instructions = f"""
# Identity
You repair JSON for a CLI command.

# Instructions
Return valid JSON only.
Repair the output so it conforms to the {schema_name} schema.
Do not add markdown fences, comments, or prose.
Preserve the original meaning when possible.
""".strip()

    input_text = f"""
<validation_error>
{validation_error}
</validation_error>

<raw_output>
{raw_output}
</raw_output>
""".strip()
    return Prompt(instructions=instructions, input=input_text, task=ModelTask.FAST)
