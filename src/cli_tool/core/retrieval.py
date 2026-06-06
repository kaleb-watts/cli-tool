import re
from collections import Counter

from cli_tool.core.chunking import TextChunk, chunk_text

WORD_RE = re.compile(r"[A-Za-z0-9_]+")
STOP_WORDS = {
    "about",
    "after",
    "and",
    "for",
    "from",
    "how",
    "into",
    "the",
    "this",
    "what",
    "when",
    "where",
    "with",
}


def tokenize(text: str) -> list[str]:
    return [
        token.lower()
        for token in WORD_RE.findall(text)
        if len(token) > 2 and token.lower() not in STOP_WORDS
    ]


def score_chunk(chunk: TextChunk, query_terms: Counter[str]) -> float:
    chunk_terms = Counter(tokenize(chunk.text))
    if not chunk_terms:
        return 0.0

    score = 0.0
    for term, query_count in query_terms.items():
        score += query_count * chunk_terms.get(term, 0)
    return score / max(len(chunk_terms), 1)


def select_relevant_chunks(
    text: str,
    query: str,
    chunk_size: int = 4_000,
    overlap: int = 400,
    max_chunks: int = 4,
) -> list[TextChunk]:
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    query_terms = Counter(tokenize(query))
    if not query_terms:
        return chunks[:max_chunks]

    ranked = sorted(chunks, key=lambda chunk: score_chunk(chunk, query_terms), reverse=True)
    selected = [chunk for chunk in ranked if score_chunk(chunk, query_terms) > 0][:max_chunks]
    return selected or chunks[:max_chunks]
