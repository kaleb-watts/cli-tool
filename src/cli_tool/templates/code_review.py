def build_code_review_prompt(code: str, filename: str) -> str:
    return f"""
You are a senior software engineer reviewing code.

Review this file: {filename}

Focus on:
1. Correctness bugs
2. Security issues
3. Edge cases
4. Readability
5. Maintainability
6. Simple improvements

Rules:
- Be direct and useful.
- Prioritize important issues first.
- Do not nitpick unnecessarily.
- If the code is already fine, say that.
- Include improved code only when it is clearly helpful.

Code:
```
{code}
```

""".strip()
