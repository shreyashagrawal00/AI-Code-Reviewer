import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser

from schemas.review_schema import CodeReview
from schemas.file_summary_schema import FileSummary
from schemas.repo_summary_schema import RepoSummary


load_dotenv()


# ==========================================================
# Environment
# ==========================================================

def validate_env():

    if not os.getenv("GROQ_API_KEY"):
        raise ValueError(
            "GROQ_API_KEY not found in .env"
        )


# ==========================================================
# LLM Builders
# ==========================================================

# Groq qwen3 models emit a <think>...</think> reasoning block by default.
# This breaks JSON output parsing because the content field may be empty
# or the reasoning is separated into a different API field.
# Passing reasoning_effort="none" disables it cleanly via the Groq API.
_THINKING_MODELS = {"qwen/qwen3-32b", "qwen3-32b"}


def _extra_kwargs(selected_model: str) -> dict:
    """Return extra kwargs needed to disable thinking on reasoning models."""
    if selected_model in _THINKING_MODELS:
        return {"reasoning_effort": "none"}
    return {}


def build_llm(
    selected_model: str,
    temperature: float = 0,
) -> ChatGroq:

    validate_env()

    return ChatGroq(
        model=selected_model,
        temperature=temperature,
        streaming=False,
        **_extra_kwargs(selected_model),
    )


def build_streaming_llm(
    selected_model: str,
    temperature: float = 0,
) -> ChatGroq:

    validate_env()

    return ChatGroq(
        model=selected_model,
        temperature=temperature,
        streaming=True,
        **_extra_kwargs(selected_model),
    )


# ==========================================================
# Parsers
# ==========================================================

def get_review_parser():

    return JsonOutputParser(
        pydantic_object=CodeReview
    )


def get_file_summary_parser():

    return JsonOutputParser(
        pydantic_object=FileSummary
    )


def get_repo_summary_parser():

    return JsonOutputParser(
        pydantic_object=RepoSummary
    )


# ==========================================================
# Format Instructions
# ==========================================================

def get_review_format_instructions():

    return (
        get_review_parser()
        .get_format_instructions()
    )


def get_file_summary_format_instructions():

    return (
        get_file_summary_parser()
        .get_format_instructions()
    )


def get_repo_summary_format_instructions():

    return (
        get_repo_summary_parser()
        .get_format_instructions()
    )