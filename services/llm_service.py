import os

from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser

from schemas.file_summary_schema import FileSummary
from schemas.repo_summary_schema import RepoSummary


def validate_env():
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError("GROQ_API_KEY not found in environment.")


def build_llm(selected_model: str) -> ChatGroq:
    validate_env()
    return ChatGroq(
        model=selected_model,
        temperature=4.5
    )


def get_file_summary_parser() -> JsonOutputParser:
    return JsonOutputParser(pydantic_object=FileSummary)


def get_repo_summary_parser() -> JsonOutputParser:
    return JsonOutputParser(pydantic_object=RepoSummary)


def get_file_summary_format_instructions() -> str:
    parser = get_file_summary_parser()
    return parser.get_format_instructions()


def get_repo_summary_format_instructions() -> str:
    parser = get_repo_summary_parser()
    return parser.get_format_instructions()