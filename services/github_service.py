import requests
from urllib.parse import urlparse
from utils.constants import ALLOWED_CODE_EXTENSIONS, IGNORE_DIRS, MAX_REPO_FILES, MAX_CHARS_PER_FILE

from utils.constants import (
    ALLOWED_CODE_EXTENSIONS,
    IGNORE_DIRS,
    IGNORE_FILES,
)

GITHUB_API_BASE = "https://api.github.com"


def parse_github_repo_url(repo_url: str):
    """
    Extract owner and repo name from:
    https://github.com/owner/repo
    https://github.com/owner/repo.git
    """
    repo_url = repo_url.strip().rstrip("/")
    parsed = urlparse(repo_url)

    if parsed.netloc not in {"github.com", "www.github.com"}:
        raise ValueError("Invalid GitHub URL. Please provide a github.com repository URL.")

    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub repo URL format.")

    owner = parts[0]
    repo = parts[1]

    if repo.endswith(".git"):
        repo = repo[:-4]

    return owner, repo


def is_ignored_path(path: str) -> bool:
    path_lower = path.lower()

    for ignored_dir in IGNORE_DIRS:
        if f"/{ignored_dir.lower()}/" in path_lower or path_lower.startswith(f"{ignored_dir.lower()}/"):
            return True

    filename = path.split("/")[-1]
    if filename in IGNORE_FILES:
        return True

    return False


def is_code_file(path: str) -> bool:
    if is_ignored_path(path):
        return False

    path_lower = path.lower()
    return any(path_lower.endswith(ext) for ext in ALLOWED_CODE_EXTENSIONS)


def get_repo_tree(owner: str, repo: str):
    """
    Fetch the full recursive tree of the repository.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
    response = requests.get(url, timeout=30)

    if response.status_code == 404:
        raise ValueError("Repository not found or it may be private.")

    if response.status_code != 200:
        raise ValueError(
            f"Failed to fetch repository tree. GitHub API returned {response.status_code}"
        )

    data = response.json()
    if "tree" not in data:
        raise ValueError("Could not fetch repository tree.")

    return data["tree"]


def get_code_files_from_repo(owner: str, repo: str):
    """
    Return a filtered list of code files from the repo.
    """
    tree = get_repo_tree(owner, repo)

    files = []
    for item in tree:
        if item.get("type") != "blob":
            continue

        path = item.get("path", "")
        if is_code_file(path):
            files.append(path)

    return files


def fetch_file_content(owner: str, repo: str, file_path: str):
    """
    Fetch raw file content from GitHub raw URL.
    """
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{file_path}"
    response = requests.get(raw_url, timeout=30)

    if response.status_code != 200:
        return None

    return response.text