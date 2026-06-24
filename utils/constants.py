# =========================================================
# APP / UI CONSTANTS
# =========================================================
APP_TITLE = "AI Code Reviewer"
APP_ICON = "🔍"

MODEL_OPTIONS = [
    "qwen/qwen3-32b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

# =========================================================
# CODE REVIEW CONSTANTS
# =========================================================
MAX_CODE_CHARS = 30000

SUPPORTED_EXTENSIONS = [
    "py", "js", "ts", "jsx", "tsx", "java", "cpp", "c", "cs",
    "go", "rb", "php", "rs", "kt", "swift", "txt", "json", "md"
]

STREAMLIT_LANG_MAP = {
    "Python": "python",
    "JavaScript": "javascript",
    "TypeScript": "typescript",
    "Java": "java",
    "C": "c",
    "C++": "cpp",
    "C#": "csharp",
    "Go": "go",
    "Ruby": "ruby",
    "PHP": "php",
    "Rust": "rust",
    "Kotlin": "kotlin",
    "Swift": "swift",
    "JSON": "json",
    "Markdown": "markdown",
    "Text": "text",
    "Unknown": "text",
    "Auto Detect": "text",
}

LANGUAGE_OPTIONS = [
    "Auto Detect",
    "Python",
    "JavaScript",
    "TypeScript",
    "Java",
    "C",
    "C++",
    "C#",
    "Go",
    "Ruby",
    "PHP",
    "Rust",
    "Kotlin",
    "Swift",
    "JSON",
    "Markdown",
    "Text",
]

REVIEW_FOCUS_MAP = {
    "All (Bug fix + Explain + Optimize)": "all",
    "Bug Fix Only": "bug_fix",
    "Explain Only": "explain",
    "Optimize Only": "optimize",
}

EXT_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JavaScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".cs": "C#",
    ".go": "Go",
    ".rb": "Ruby",
    ".php": "PHP",
    ".rs": "Rust",
    ".kt": "Kotlin",
    ".swift": "Swift",
    ".json": "JSON",
    ".md": "Markdown",
    ".txt": "Text",
}

# backward-compatible alias
EXTENSION_TO_LANGUAGE = EXT_MAP

# =========================================================
# GITHUB REPO REVIEW CONSTANTS
# =========================================================
ALLOWED_CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".cpp", ".c", ".cs",
    ".go", ".rb", ".php", ".rs",
    ".kt", ".swift", ".json", ".md", ".txt"
}

IGNORE_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    ".next",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".idea",
    ".vscode",
    "coverage",
    "target",
    "out",
    ".turbo",
    ".cache",
}

IGNORE_FILES = {
    ".gitignore",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Pipfile.lock",
    "README.md",
    "LICENSE",
}

PRIORITY_FILENAMES = {
    "main.py",
    "app.py",
    "server.py",
    "index.js",
    "app.js",
    "main.js",
    "main.ts",
    "app.ts",
    "server.ts",
    "routes.py",
    "router.py",
    "api.py",
    "train.py",
    "model.py",
    "config.py",
    "settings.py",
    "database.py",
    "db.py",
    "auth.py",
    "middleware.py",
    "requirements.txt",
    "package.json",
    "dockerfile",
    "docker-compose.yml",
}

MAX_REPO_FILES = 20
MAX_CHARS_PER_FILE = 12000
MAX_TOTAL_REPO_CHARS = 120000

# backward-compatible aliases for older repo-side files
MAX_FILES_TO_FETCH = MAX_REPO_FILES
MAX_FILE_CHARS = MAX_CHARS_PER_FILE

# =========================================================
# CHUNKING / RAG CONSTANTS
# =========================================================
CHUNK_SIZE = 1800
CHUNK_OVERLAP = 250
VECTOR_TOP_K = 6
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# old chunking_service compatibility
MAX_CHARS_PER_CHUNKED_FILE = MAX_CHARS_PER_FILE