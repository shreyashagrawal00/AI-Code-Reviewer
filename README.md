# AI Code Reviewer & GitHub Repository Analyzer

An AI-powered **code review + GitHub repository analysis** platform built with **Streamlit, LangChain, Groq, and RAG**.

This project can:

* **Review pasted code**
* **Review uploaded code files**
* **Analyze a GitHub repository**
* **Summarize a repository file-by-file**
* **Generate a repository-level architectural summary**
* **Use chunking + embeddings + vector search (RAG)** for better understanding of larger repositories
* Show **live progress updates in the UI** while repo files are being fetched, chunked, embedded, and analyzed

---

# Features

## 1) Single Code Review

Review code by either:

* **Pasting code**
* **Uploading a code file**

The AI can:

* explain what the code does
* find bugs / risky patterns
* fix the code
* suggest improvements
* return structured review output

---

## 2) GitHub Repository Review

Paste a **GitHub repository URL** and the app will:

* fetch repository files
* filter relevant code files
* analyze important files one-by-one
* create **file-level summaries**
* generate a **repository-level summary**
* show architecture, tech stack, strengths, issues, and suggestions

---

## 3) File-by-File Repository Analysis

For each selected repository file, the app can generate:

* file purpose
* summary of what the file does
* key components / functions / classes
* issues / bugs / weak practices
* improvement suggestions

---

## 4) RAG for Larger Repositories

For bigger repositories, the project uses a **RAG pipeline**:

* fetch repository files
* split them into chunks
* create embeddings
* store them in a vector database (FAISS)
* retrieve the most relevant chunks when needed

This makes the repo analysis more scalable than sending the whole repo to the LLM at once.

---

## 5) Better Streamlit UI

The app is designed to show **what is happening in the background**, such as:

* fetching repository files
* selecting important files
* chunking files
* generating embeddings
* analyzing files one-by-one
* generating the final repo summary

This makes the app feel much more transparent and interactive.

---

# Tech Stack

## Frontend / UI

* **Streamlit**

## LLM / AI

* **Groq**
* **LangChain**

## Repository / File Analysis

* **GitHub API / raw GitHub file fetching**
* **Pydantic schemas for structured outputs**

## RAG / Retrieval

* **Sentence Transformers**
* **FAISS**
* **LangChain text splitting / document handling**

## Language / Backend

* **Python 3.11+**

---

# Project Structure

```bash
AI_Code_Reviewer/
│
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
│
├── prompts/
│   ├── review_prompt.py
│   ├── file_summary_prompt.py
│   └── repo_summary_prompt.py
│
├── schemas/
│   ├── review_schema.py
│   ├── file_summary_schema.py
│   └── repo_summary_schema.py
│
├── services/
│   ├── llm_service.py
│   ├── review_service.py
│   ├── file_service.py
│   ├── github_service.py
│   ├── repo_ingestion_service.py
│   ├── file_analysis_service.py
│   ├── repo_analysis_service.py
│   ├── chunking_service.py
│   ├── embedding_service.py
│   └── vector_store_service.py
│
├── utils/
│   └── constants.py
│
├── outputs/
│   └── (optional generated reports / exports)
│
└── faiss_index/
    └── (optional local vector DB files)
```

---

# Folder / File Explanation

## `app.py`

Main Streamlit application.

Handles:

* UI layout
* mode selection (code review / GitHub repo review)
* progress updates
* displaying code review results
* displaying file-by-file repo summaries
* displaying repository-level summary

---

## `prompts/`

Contains all LLM prompts.

### `review_prompt.py`

Prompt for **single code review**.

### `file_summary_prompt.py`

Prompt for **repository file-by-file analysis**.

### `repo_summary_prompt.py`

Prompt for **repository-level summary generation** using:

* repo metadata
* file summaries
* repo context

---

## `schemas/`

Contains Pydantic schemas for structured AI output.

### `review_schema.py`

Schema for single code review output.

Example fields:

* understanding
* bugs
* corrected_code
* explanation
* suggestions

### `file_summary_schema.py`

Schema for one repository file summary.

Example fields:

* file_path
* language
* purpose
* summary
* key_components
* issues
* suggestions

### `repo_summary_schema.py`

Schema for repository-level analysis.

Example fields:

* repo_name
* overview
* architecture
* tech_stack
* important_files
* strengths
* issues
* suggestions
* final_verdict

---

## `services/`

Contains all application logic.

### `llm_service.py`

Creates the LLM instance and returns formatting instructions / parsers if needed.

Responsibilities:

* validate `GROQ_API_KEY`
* build Groq LLM client
* expose schema formatting instructions

---

### `review_service.py`

Handles **single pasted/uploaded code review**.

Responsibilities:

* run the code review prompt
* parse LLM JSON output safely
* clean code fences / `<think>` blocks if present
* return a validated `CodeReview` object

---

### `file_service.py`

Handles uploaded file utilities.

Responsibilities:

* safely decode uploaded files
* detect language from file extension
* validate file size
* provide fallback task descriptions

---

### `github_service.py`

Handles GitHub repository fetching.

Responsibilities:

* parse GitHub repo URL
* fetch repo tree / files
* filter code files
* ignore unwanted folders/files
* fetch raw file content

---

### `repo_ingestion_service.py`

Builds the **repository file set** for analysis.

Responsibilities:

* select important repo files
* apply limits (max files / max chars)
* infer language from extension
* return `file_records` in a consistent format

Typical `file_record` structure:

```python
{
    "file_path": "backend/server.js",
    "language": "JavaScript",
    "content": "..."
}
```

---

### `file_analysis_service.py`

Analyzes repository files **one by one**.

Responsibilities:

* run file summary prompt for each file
* safely extract JSON from model output
* parse into `FileSummary`
* store debug logs per file
* return all file summaries

---

### `repo_analysis_service.py`

Generates **repository-level summary** from:

* repo metadata
* selected file list
* file-level summaries

Responsibilities:

* build repo context
* combine file summaries
* run repo summary prompt
* parse final structured repo summary

---

### `chunking_service.py`

Used for **RAG**.

Responsibilities:

* split repo files into chunks
* attach metadata like file path / language / chunk index
* keep chunk size under control

---

### `embedding_service.py`

Creates embeddings for repository chunks.

Responsibilities:

* load embedding model
* generate embeddings for chunks

---

### `vector_store_service.py`

Stores and queries repository chunks using FAISS.

Responsibilities:

* create FAISS vector store
* add chunked documents
* run similarity search for repo Q&A / context retrieval

---

## `utils/constants.py`

Stores all constants used across the project.

Examples:

* supported file extensions
* language mappings
* ignored repo folders/files
* chunk sizes
* model options
* repo limits

---

# How the App Works

# A) Single Code Review Flow

## Input

User either:

* pastes code
* uploads a file

## Flow

1. detect / choose language
2. collect task description and review focus
3. send prompt to LLM
4. parse JSON response into `CodeReview`
5. show:

   * understanding
   * bugs
   * corrected code
   * explanation
   * suggestions

---

# B) GitHub Repository Review Flow

## Input

User pastes a GitHub repository URL

## Flow

1. parse GitHub repo URL
2. fetch repository file tree
3. filter important code files
4. fetch file contents
5. generate **file-by-file summaries**
6. combine file summaries + repo metadata
7. generate **repository-level summary**
8. optionally build chunked vector index for RAG
9. show results in UI

---

# C) RAG Flow for Larger Repositories

## Why RAG is needed

A large repository may have:

* too many files
* too much code
* too many tokens for one prompt

So instead of sending the whole repo directly to the LLM:

## RAG pipeline

1. fetch repository files
2. split into chunks
3. create embeddings
4. store in FAISS
5. retrieve the most relevant chunks for a repo question / analysis step

This helps the model analyze bigger repositories more intelligently.

---

# JSON Parsing Problem & Robust Fix

Some LLMs may return output like:

```text
<think>...</think>
{ valid json }
extra text...
```

This project handles that by:

* removing `<think>...</think>`
* removing code fences
* extracting the **first balanced JSON object**
* validating with Pydantic schemas

This makes the app much more stable.

---

# Installation

## 1) Clone the repository

```bash
git clone https://github.com/your-username/AI_Code_Reviewer.git
cd AI_Code_Reviewer
```

## 2) Create virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Mac / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3) Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4) Create `.env`

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## 5) Run the app

```bash
streamlit run app.py
```

---

# Example `requirements.txt`

A typical version for this project may include:

```txt
streamlit
python-dotenv
pydantic
requests

langchain
langchain-core
langchain-groq
langchain-community

faiss-cpu
sentence-transformers
tiktoken
```

You can add or pin versions based on your environment.

---

# Supported Review Modes

## Code Review

* paste code
* upload file
* choose language
* choose review focus:

  * all
  * bug fix only
  * explain only
  * optimize only

## GitHub Repo Review

* paste repo URL
* analyze important files
* generate file summaries
* generate repo summary
* optionally use vector retrieval for larger repos

---

# Example Output Sections

## Single Code Review Output

* Understanding
* Bugs Found
* Corrected Code
* Explanation
* Suggestions

## GitHub Repo Review Output

* Repository Overview
* Architecture
* Tech Stack
* Important Files
* Strengths
* Issues
* Suggestions
* Final Verdict
* File-by-File Review

---

# Future Improvements

* chat with repository using vector retrieval
* export repo review as PDF / Markdown
* support private GitHub repos via token
* multi-file local folder upload
* repository dependency graph visualization
* architecture diagram generation
* severity filtering for file issues
* test generation for selected files
* code smell / security-focused review modes

---

# Example Use Cases

* review your DSA / college code quickly
* analyze hackathon repositories
* inspect open-source GitHub projects
* understand unfamiliar repos faster
* prepare for code reviews / interviews
* generate project documentation summaries

---

# Known Limitations

* very large repositories still require aggressive file filtering
* LLM quality depends on chosen model
* GitHub rate limits may affect public repo fetching
* if prompts / schemas mismatch, parsing can fail
* file selection quality affects repo summary quality

---

# Author

**Shreyash Agrawal**

If you use this project, feel free to extend it with:

* better repo ranking
* architecture graphing
* multi-agent analysis
* deeper RAG-based repo Q&A

---

## Quick Summary

This project is a **Streamlit-based AI code review platform** that can review **single code files** as well as **entire GitHub repositories**. It uses **Groq + LangChain** for structured analysis and **RAG + FAISS** to scale repository understanding for larger projects.
