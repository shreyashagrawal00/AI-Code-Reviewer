import os
from typing import Dict, List, Tuple

from services.github_service import (
    parse_github_repo_url,
    get_code_files_from_repo,
    fetch_file_content,
)
from utils.constants import (
    EXTENSION_TO_LANGUAGE,
    MAX_FILES_TO_FETCH,
    MAX_FILE_CHARS,
    MAX_TOTAL_REPO_CHARS,
    PRIORITY_FILENAMES,
)


def detect_language_from_path(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    return EXTENSION_TO_LANGUAGE.get(ext, "Unknown")


def score_file_priority(file_path: str) -> int:
    """
    Lower score = higher priority.
    Used to review important files first.
    """
    filename = os.path.basename(file_path)

    if filename in PRIORITY_FILENAMES:
        return 0

    path_lower = file_path.lower()

    if "readme" in path_lower:
        return 1
    if "app" in path_lower or "main" in path_lower:
        return 2
    if "service" in path_lower or "api" in path_lower or "route" in path_lower:
        return 3
    if "model" in path_lower or "schema" in path_lower:
        return 4
    if "utils" in path_lower or "helper" in path_lower:
        return 5

    return 10


def prioritize_files(file_paths: List[str]) -> List[str]:
    return sorted(file_paths, key=lambda path: (score_file_priority(path), len(path)))


def ingest_github_repo(repo_url: str) -> Tuple[str, List[Dict], Dict]:
    """
    Fetch repo files and return:
    - repo_name
    - list of file records
    - repo metadata
    """
    owner, repo = parse_github_repo_url(repo_url)
    all_code_files = get_code_files_from_repo(owner, repo)

    if not all_code_files:
        raise ValueError("No supported code files found in this repository.")

    prioritized_files = prioritize_files(all_code_files)[:MAX_FILES_TO_FETCH]

    file_records = []
    total_chars = 0

    for file_path in prioritized_files:
        content = fetch_file_content(owner, repo, file_path)
        if not content:
            continue

        content = content[:MAX_FILE_CHARS]
        language = detect_language_from_path(file_path)

        if total_chars + len(content) > MAX_TOTAL_REPO_CHARS:
            remaining = MAX_TOTAL_REPO_CHARS - total_chars
            if remaining <= 0:
                break
            content = content[:remaining]

        file_records.append({
            "file_path": file_path,
            "language": language,
            "content": content,
            "char_count": len(content),
        })

        total_chars += len(content)

        if total_chars >= MAX_TOTAL_REPO_CHARS:
            break

    if not file_records:
        raise ValueError("Could not fetch readable code files from the repository.")

    repo_metadata = {
        "owner": owner,
        "repo": repo,
        "repo_url": repo_url,
        "total_files_selected": len(file_records),
        "total_chars": total_chars,
    }

    return repo, file_records, repo_metadata


def build_repo_context(file_records: List[Dict], repo_metadata: Dict) -> str:
    """
    Create a compact repo context text for repo-level analysis.
    """
    lines = [
        f"Repository name: {repo_metadata.get('repo', 'Unknown')}",
        f"Owner: {repo_metadata.get('owner', 'Unknown')}",
        f"Files selected for analysis: {repo_metadata.get('total_files_selected', 0)}",
        "",
        "Repository files:"
    ]

    for record in file_records:
        lines.append(
            f"- {record['file_path']} ({record['language']}, {record['char_count']} chars)"
        )

    return "\n".join(lines)