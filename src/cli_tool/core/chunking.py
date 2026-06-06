from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    id: str
    text: str
    start: int
    end: int


def chunk_text(text: str, chunk_size: int = 4_000, overlap: int = 400) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    chunks = []
    start = 0
    index = 1
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(TextChunk(id=f"chunk-{index}", text=text[start:end], start=start, end=end))
        if end == len(text):
            break
        start = end - overlap
        index += 1

    return chunks


def format_chunks_xml(chunks: list[TextChunk], path: str) -> str:
    return "\n\n".join(
        f'<chunk id="{chunk.id}" path="{path}" start="{chunk.start}" end="{chunk.end}">\n'
        f"{chunk.text}\n"
        "</chunk>"
        for chunk in chunks
    )
