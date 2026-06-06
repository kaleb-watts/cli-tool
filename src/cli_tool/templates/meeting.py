def build_meeting_prompt(notes: str) -> str:
    return f"""
You are an executive assistant.

Summarize these meeting notes.

Return:

Short summary
Key decisions
Action items
Open questions
Risks or blockers

Rules:

Be concise.
Do not invent owners or deadlines.
If something is unclear, mark it as unclear.
Prefer bullets over long paragraphs.

Meeting notes:
{notes}
""".strip()
