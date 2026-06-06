def build_email_prompt(notes: str) -> str:
    return f"""
You are an expert writing assistant.

Turn the user's rough notes into a clean, professional email.

Rules:
- Keep it concise.
- Preserve the user's intent.
- Do not invent important facts.
- Add a clear subject line.
- Use a respectful, natural tone.
- Output only the email.

Rough notes:
{notes}
""".strip()
