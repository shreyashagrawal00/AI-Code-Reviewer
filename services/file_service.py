import os
from typing import Optional

import streamlit as st
from utils.constants import EXT_MAP, MAX_CODE_CHARS


def safe_decode_uploaded_file(uploaded_file) -> str:
    """
    Read uploaded file bytes and decode safely.
    Tries UTF-8 first, then falls back to latin-1.
    """
    raw_bytes = uploaded_file.read()

    try:
        return raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return raw_bytes.decode("latin-1", errors="replace")


def detect_language_from_filename(filename: str) -> Optional[str]:
    """
    Detect programming language from file extension using EXT_MAP.
    Example:
        hello.py -> Python
        app.js   -> JavaScript
    """
    ext = os.path.splitext(filename)[1].lower()
    return EXT_MAP.get(ext)


def validate_code_size(code: str):
    """
    Stop the Streamlit app if the pasted/uploaded code is too large.
    """
    if len(code) > MAX_CODE_CHARS:
        st.error(
            f"Code is too large ({len(code)} chars). "
            f"Please keep it under {MAX_CODE_CHARS} characters for single-file review."
        )
        st.stop()


def default_task_description_if_empty(task_description: str) -> str:
    """
    Provide a fallback task description if the user leaves it blank.
    """
    if task_description and task_description.strip():
        return task_description.strip()

    return (
        "Review this code, infer its intended purpose, identify bugs, "
        "explain issues, and suggest improvements."
    )