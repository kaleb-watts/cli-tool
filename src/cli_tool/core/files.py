from pathlib import Path

type PathInput = str | Path


def read_text_file(path: PathInput) -> str:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    return file_path.read_text(encoding="utf-8")


def save_text_file(path: PathInput, content: str) -> None:
    file_path = Path(path)

    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_text(content, encoding="utf-8")
