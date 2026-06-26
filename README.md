# 🔍 AI Code Reviewer

> **AI-powered code review tool** — review pasted code, uploaded files, or entire GitHub repositories with structured AI analysis, repository summaries, and a RAG-powered Ask Repo Q&A interface.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://langchain.com)
[![Groq](https://img.shields.io/badge/Groq-LLM-F55036?style=for-the-badge)](https://groq.com)
[![FAISS](https://img.shields.io/badge/FAISS-Vector_Store-0081CB?style=for-the-badge)](https://github.com/facebookresearch/faiss)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Architecture & Data Flow](#-architecture--data-flow)
- [Modules In Depth](#-modules-in-depth)
- [Supported Languages](#-supported-languages)
- [Available AI Models](#-available-ai-models)
- [Environment Variables](#-environment-variables)
- [Installation & Setup](#-installation--setup)
- [Running the App](#-running-the-app)
- [Configuration & Limits](#-configuration--limits)
- [App Modes & UI Guide](#-app-modes--ui-guide)
- [Contributing](#-contributing)

---

## 🌟 Overview

**AI Code Reviewer** is a full-stack AI tool built with **Streamlit** that lets developers review code at any scale from a single snippet to an entire GitHub repository. It uses **Groq's ultra-fast LLM API** via **LangChain** to produce structured, actionable code reviews with bug reports, corrected code, explanations, and optimization suggestions.

For repository-level analysis, it ingests GitHub repos through the GitHub API, runs per-file AI analysis, generates a holistic repository summary, chunks all code for vector search using **FAISS**, and enables a natural-language **Ask Repo Q&A** feature powered by Retrieval-Augmented Generation (RAG).

---

## ✨ Features

### 💻 Code Review Tab
- **Paste code** directly or **upload a file** (supports 19+ file extensions)
- Select the **programming language** or use auto-detection from the filename
- Provide an optional **task description** to give the AI context
- Choose a **review focus**: `All`, `Bug Fix Only`, `Explain Only`, or `Optimize Only`
- Receive a structured review with:
  - 📖 **Overall understanding** of what the code does
  - 🐛 **Bug/issue list** with severity levels (`High`, `Medium`, `Low`) and fix instructions
  - 🛠 **Corrected code** block with all fixes applied
  - 🗣 **Human-friendly explanation** of all changes
  - 🚀 **Extra suggestions** for best practices and optimizations
- Live **progress bar** and **status updates** during review

### 📦 Repo Review Tab
- Analyze a **full GitHub repository** by URL (public repos, no auth required)
- **7-step analysis pipeline** with real-time progress:
  1. Validate and fetch repository files via GitHub API
  2. Run **file-by-file AI analysis** with per-file summaries
  3. Generate a **repository-level summary** with architecture, tech stack, and insights
  4. **Chunk** all code files for retrieval
  5. Build a **FAISS vector store** from embeddings
- Repository metrics dashboard: repo name, files analyzed, total characters, chunks created
- **Repository Overview**: overview, architecture, tech stack, important files, strengths, issues, and a final verdict
- **File-by-File Review**: collapsible per-file panels with language, purpose, key components, issues, and suggestions
- **Session persistence**: previously analyzed repo stays visible until a new one is loaded

### 💬 Ask Repo Tab
- Ask **natural language questions** about the analyzed repository
- Two interaction modes:
  - 🔎 **Show Retrieved Chunks** — display the raw RAG context retrieved from the vector store
  - 🤖 **Answer with AI** — send retrieved context + question to the LLM for a comprehensive answer
- Powered by **FAISS similarity search** + **sentence-transformers** embeddings
- Displays the retrieved context used alongside the AI's answer for full transparency

### ⚙️ Global Settings (Sidebar)
- Switch between **Groq models** at any time
- Enable **Debug Mode** to view raw LLM outputs and file processing details

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **UI Framework** | [Streamlit](https://streamlit.io) >= 1.36.0 |
| **LLM Provider** | [Groq](https://groq.com) (via LangChain) |
| **LLM Orchestration** | [LangChain](https://langchain.com) >= 0.3.0 |
| **Embeddings** | [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) |
| **Vector Store** | [FAISS](https://github.com/facebookresearch/faiss) (CPU) |
| **Data Validation** | [Pydantic](https://docs.pydantic.dev) v2 |
| **GitHub API** | [requests](https://requests.readthedocs.io) (GitHub REST API v3) |
| **Tokenization** | [tiktoken](https://github.com/openai/tiktoken) |
| **Environment** | [python-dotenv](https://github.com/theskumar/python-dotenv) |

---

## 📁 Project Structure

```
AI Code Reviewer/
│
├── app.py                        # Main Streamlit application entry point
│
├── services/                     # Business logic and service layer
│   ├── __init__.py
│   ├── llm_service.py            # LLM builder (Groq + LangChain)
│   ├── review_service.py         # Single-file code review orchestration
│   ├── file_service.py           # File upload handling, language detection, validation
│   ├── github_service.py         # GitHub API calls (repo tree, file fetch)
│   ├── repo_ingestion_service.py # Repo ingestion, file prioritization
│   ├── file_analysis_service.py  # Per-file AI analysis pipeline
│   ├── repo_analysis_service.py  # Repository-level AI summary pipeline
│   ├── chunking_service.py       # Code chunking for RAG
│   ├── embedding_service.py      # Sentence-transformer embedding model loader
│   ├── vector_store_service.py   # FAISS vector store build and retrieval
│   ├── repo_qa_service.py        # Ask Repo RAG Q&A pipeline
│   └── parser_service.py         # LLM output JSON extraction and parsing
│
├── prompts/                      # LangChain prompt templates
│   ├── __init__.py
│   ├── review_prompt.py          # Prompt for single code review
│   ├── file_summary_prompt.py    # Prompt for per-file analysis
│   ├── repo_summary_prompt.py    # Prompt for repository-level summary
│   ├── repo_qa_prompt.py         # Prompt for Ask Repo Q&A
│   └── module_summary_prompt.py  # Prompt for module summaries
│
├── schemas/                      # Pydantic output schemas
│   ├── __init__.py
│   ├── review_schema.py          # CodeReview, BugItem schemas
│   ├── file_summary_schema.py    # FileSummary schema
│   ├── repo_summary_schema.py    # RepoSummary, RepoIssue schemas
│   └── module_summary_schema.py  # ModuleSummary schema
│
├── utils/                        # Shared utilities and constants
│   ├── __init__.py
│   ├── constants.py              # All app-wide constants and config values
│   └── language_utils.py         # Language detection helpers
│
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
├── .env                          # Local secrets (not committed to git)
└── .gitignore                    # Git ignore rules
```

---

## 🏗 Architecture & Data Flow

### Code Review Flow

```
User Input (paste/upload)
        |
        v
  file_service.py          <- Validate, decode, detect language
        |
        v
  review_service.py        <- Build prompt, invoke LLM (Groq)
        |
        v
  parser_service.py        <- Extract JSON, strip fences
        |
        v
  review_schema.py         <- Validate with Pydantic (CodeReview)
        |
        v
  app.py (render)          <- Display structured results in Streamlit UI
```

### Repository Review Flow

```
GitHub URL
    |
    v
github_service.py          <- Parse URL, fetch repo tree, download files
    |
    v
repo_ingestion_service.py  <- Prioritize and truncate files, build metadata
    |
    v
file_analysis_service.py   <- Per-file AI summaries (batched LLM calls)
    |
    v
repo_analysis_service.py   <- Holistic repo summary via LLM
    |
    v
chunking_service.py        <- Chunk code files (1800 chars, 250 overlap)
    |
    v
vector_store_service.py    <- Embed chunks into FAISS index (all-MiniLM-L6-v2)
    |
    v
app.py (render)            <- Metrics, repo summary, file-by-file panels
```

### Ask Repo (RAG) Flow

```
User Question
    |
    v
vector_store_service.py    <- similarity_search(query, top_k=6)
    |
    v
repo_qa_service.py         <- Format retrieved chunks -> build RAG prompt -> Groq LLM
    |
    v
app.py (render)            <- Display AI answer + show retrieved context
```

---

## 🔬 Modules In Depth

### `services/llm_service.py`
Builds the LangChain `ChatGroq` LLM instance for a given model name. Reads `GROQ_API_KEY` from the environment.

### `services/review_service.py`
Orchestrates the single-file code review:
- Builds the review prompt with format instructions from the Pydantic schema
- Invokes the Groq LLM via LangChain chain
- Robustly extracts JSON from the raw response (handles code fences, leading text, `<think>` tags)
- Validates and returns a typed `CodeReview` object

### `services/file_service.py`
Handles file uploads and code input:
- `safe_decode_uploaded_file()` — decodes bytes with UTF-8 fallback to latin-1
- `detect_language_from_filename()` — maps file extension to language name
- `validate_code_size()` — enforces the `MAX_CODE_CHARS` (30,000) limit
- `default_task_description_if_empty()` — provides a fallback task description

### `services/github_service.py`
Interfaces with the GitHub REST API:
- `parse_github_repo_url()` — extracts owner/repo from any GitHub URL
- `get_code_files_from_repo()` — recursively fetches the file tree, filtering by allowed extensions and ignoring noise directories
- `fetch_file_content()` — downloads raw file content by path

### `services/repo_ingestion_service.py`
Prepares a repository for analysis:
- **Priority scoring**: important files (`app.py`, `main.py`, `routes.py`, etc.) are ranked first
- **File capping**: up to `MAX_REPO_FILES` (20) files are selected
- **Character limits**: per-file cap of `MAX_CHARS_PER_FILE` (12,000 chars) and total cap of `MAX_TOTAL_REPO_CHARS` (120,000 chars)

### `services/file_analysis_service.py`
Runs AI analysis on each repository file individually to produce structured `FileSummary` objects (language, purpose, summary, key components, issues, suggestions).

### `services/repo_analysis_service.py`
Synthesizes all per-file summaries into a holistic `RepoSummary` (overview, architecture, tech stack, important files, strengths, repo-level issues, suggestions, final verdict).

### `services/chunking_service.py`
Splits repository file content into overlapping chunks for RAG:
- Chunk size: **1,800 characters**
- Overlap: **250 characters**
- Each chunk records its `file_path`, `language`, and `chunk_index`

### `services/embedding_service.py`
Loads the **`sentence-transformers/all-MiniLM-L6-v2`** embedding model via `langchain-huggingface`. Cached for reuse across requests.

### `services/vector_store_service.py`
Manages the FAISS vector store lifecycle:
- `build_vector_store()` — converts chunk records to LangChain `Document` objects and indexes them with FAISS
- `retrieve_relevant_chunks()` — performs similarity search for top-k (default 6) relevant chunks
- `format_retrieved_chunks()` — formats retrieved docs into a readable text block for the LLM context

### `services/repo_qa_service.py`
Implements the Ask Repo RAG pipeline:
- Retrieves relevant chunks from FAISS
- Constructs a context-enriched prompt using `repo_qa_prompt.py`
- Calls the Groq LLM and returns the answer alongside the retrieved context

### `services/parser_service.py`
Shared JSON parsing utilities used across multiple services:
- Strips `<think>...</think>` reasoning blocks from model output
- Extracts valid JSON from code-fenced or mixed-text responses
- Validates parsed data against Pydantic schemas

### `prompts/`
All LangChain `ChatPromptTemplate` prompt builders live here, one per task:

| File | Purpose |
|---|---|
| `review_prompt.py` | Single code review with dynamic review_focus |
| `file_summary_prompt.py` | Per-file analysis for repo ingestion |
| `repo_summary_prompt.py` | Holistic repository-level summary |
| `repo_qa_prompt.py` | RAG-powered Q&A about the repository |
| `module_summary_prompt.py` | Module-level summaries (extended use) |

### `schemas/`
Pydantic v2 models for strongly-typed, validated LLM output:

| Schema | Fields |
|---|---|
| `CodeReview` | `language`, `understanding`, `bugs` (List[BugItem]), `corrected_code`, `explanation`, `suggestions` |
| `BugItem` | `title`, `severity`, `explanation`, `fix` |
| `FileSummary` | `file_path`, `language`, `purpose`, `summary`, `key_components`, `issues`, `suggestions` |
| `RepoSummary` | `overview`, `architecture`, `tech_stack`, `important_files`, `strengths`, `issues`, `suggestions`, `final_verdict` |
| `RepoIssue` | `title`, `severity`, `explanation`, `affected_files`, `fix` |

---

## 🌐 Supported Languages

| Language | Extensions |
|---|---|
| Python | `.py` |
| JavaScript | `.js`, `.jsx` |
| TypeScript | `.ts`, `.tsx` |
| Java | `.java` |
| C | `.c` |
| C++ | `.cpp`, `.cc`, `.cxx` |
| C# | `.cs` |
| Go | `.go` |
| Ruby | `.rb` |
| PHP | `.php` |
| Rust | `.rs` |
| Kotlin | `.kt` |
| Swift | `.swift` |
| JSON | `.json` |
| Markdown | `.md` |
| Text | `.txt` |

---

## 🤖 Available AI Models

| Model | Description |
|---|---|
| `qwen/qwen3-32b` | (Default) High-quality, strong reasoning |
| `llama-3.3-70b-versatile` | Meta's powerful 70B model, well-rounded |
| `llama-3.1-8b-instant` | Fastest, lightweight for quick reviews |

> All models are served by [Groq](https://groq.com) for ultra-low latency inference.

---

## 🔐 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Your Groq API key from [console.groq.com](https://console.groq.com) |

Copy `.env.example` to `.env` and fill in your key:

```bash
cp .env.example .env
```

`.env.example`:
```env
GROQ_API_KEY=your_groq_api_key_here
```

> **Note:** A GitHub token is not required for public repositories. For private repos or to avoid rate limits, you can extend `github_service.py` to include a `GITHUB_TOKEN` header.

---

## 🚀 Installation & Setup

### Prerequisites

- Python **3.10+**
- A free [Groq API key](https://console.groq.com)

### Steps

**1. Clone the repository**

```bash
git clone https://github.com/your-username/ai-code-reviewer.git
cd ai-code-reviewer
```

**2. Create and activate a virtual environment**

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

---

## ▶️ Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## ⚙️ Configuration & Limits

All configurable constants live in `utils/constants.py`:

| Constant | Default | Description |
|---|---|---|
| `MAX_CODE_CHARS` | 30,000 | Max characters for single-file review |
| `MAX_REPO_FILES` | 20 | Max files fetched from a GitHub repo |
| `MAX_CHARS_PER_FILE` | 12,000 | Max characters read per repo file |
| `MAX_TOTAL_REPO_CHARS` | 120,000 | Total character budget for full repo |
| `CHUNK_SIZE` | 1,800 | Characters per RAG chunk |
| `CHUNK_OVERLAP` | 250 | Overlap between adjacent chunks |
| `VECTOR_TOP_K` | 6 | Number of chunks retrieved for RAG |
| `EMBEDDING_MODEL_NAME` | all-MiniLM-L6-v2 | HuggingFace embedding model |

### File Prioritization

When analyzing a repo, files are ranked by importance before the cap is applied:

| Priority | Criteria |
|---|---|
| 0 (Highest) | Priority filenames: `app.py`, `main.py`, `routes.py`, `config.py`, etc. |
| 1 | Files with `readme` in the path |
| 2 | Files with `app` or `main` in the path |
| 3 | Files with `service`, `api`, or `route` in the path |
| 4 | Files with `model` or `schema` in the path |
| 5 | Files with `utils` or `helper` in the path |
| 10 (Lowest) | All other files |

### Ignored Directories and Files

The GitHub ingestion pipeline automatically skips:

**Directories:** `node_modules`, `.git`, `dist`, `build`, `.next`, `__pycache__`, `.venv`, `venv`, `env`, `.idea`, `.vscode`, `coverage`, `target`, `out`, `.turbo`, `.cache`

**Files:** `.gitignore`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `Pipfile.lock`, `LICENSE`

---

## 🖥 App Modes & UI Guide

```
+-------------------------------------------------------------+
|  🔍 AI Code Reviewer                                        |
|  -----------------------------------------------------------  |
|  [ 💻 Code Review ] [ 📦 Repo Review ] [ 💬 Ask Repo ]     |
+-------------------------------------------------------------+
```

### Sidebar
- **Groq Model** — select the LLM to use for all operations
- **Debug Mode** — reveals raw LLM outputs and processing details

### 💻 Code Review Tab
1. Select language (or Auto Detect)
2. Optionally describe what the code should do
3. Choose a review focus
4. Paste code or upload a file
5. Click **🚀 Review My Code**

### 📦 Repo Review Tab
1. Paste a GitHub repository URL (e.g. `https://github.com/username/repo`)
2. Click **🚀 Analyze Repository**
3. Watch the 7-step analysis pipeline run in real-time
4. Browse the repo metrics, overview, and file-by-file review panels

### 💬 Ask Repo Tab
> Requires a repo to be analyzed first in the **Repo Review** tab.

1. Type a natural language question about the repo
2. Click **🔎 Show Retrieved Chunks** to inspect the RAG context, or
3. Click **🤖 Answer with AI** for a full AI-generated answer

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source. See the [LICENSE](LICENSE) file for details.

---

Built with love using Streamlit · LangChain · Groq · FAISS
