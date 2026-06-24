from typing import Dict, List
from utils.constants import CHUNK_SIZE, CHUNK_OVERLAP
from utils.constants import CHUNK_SIZE, CHUNK_OVERLAP, MAX_CHARS_PER_CHUNKED_FILE


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split plain text into overlapping chunks.
    """
    if not text:
        return []

    text = text[:MAX_CHARS_PER_CHUNKED_FILE]

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end]
        chunks.append(chunk)

        if end >= text_len:
            break

        start = max(end - overlap, 0)

    return chunks


def chunk_file_record(file_record: Dict) -> List[Dict]:
    """
    Convert one file record into chunk records.
    """
    file_path = file_record["file_path"]
    language = file_record["language"]
    content = file_record["content"]

    chunks = chunk_text(content)

    chunk_records = []
    for idx, chunk in enumerate(chunks):
        chunk_records.append({
            "file_path": file_path,
            "language": language,
            "chunk_index": idx,
            "chunk_text": chunk,
        })

    return chunk_records


def chunk_repo_files(file_records: List[Dict]) -> List[Dict]:
    """
    Chunk all files in the repository.
    """
    all_chunks = []

    for file_record in file_records:
        file_chunks = chunk_file_record(file_record)
        all_chunks.extend(file_chunks)

    return all_chunks