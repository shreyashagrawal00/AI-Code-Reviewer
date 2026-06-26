import json
import re
from typing import List, Tuple

from langchain_core.output_parsers import JsonOutputParser

from prompts.repo_summary_prompt import build_repo_summary_prompt
from schemas.repo_summary_schema import RepoSummary
from schemas.file_summary_schema import FileSummary
from services.llm_service import build_llm


def get_repo_summary_format_instructions() -> str:
    parser = JsonOutputParser(pydantic_object=RepoSummary)
    return parser.get_format_instructions()


def strip_think_blocks(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def strip_code_fences(text: str) -> str:
    text = text.strip()

    json_fence = re.match(r"^```json\s*(.*?)\s*```$", text, flags=re.DOTALL | re.IGNORECASE)
    if json_fence:
        return json_fence.group(1).strip()

    any_fence = re.match(r"^```[a-zA-Z0-9_+\-#]*\s*(.*?)\s*```$", text, flags=re.DOTALL)
    if any_fence:
        return any_fence.group(1).strip()

    return text


def extract_first_balanced_json(text: str) -> str:
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object start found in model output.")

    depth = 0
    in_string = False
    escape = False

    for i in range(start, len(text)):
        ch = text[i]

        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start:i + 1]
                json.loads(candidate)
                return candidate

    raise ValueError("Could not find a complete balanced JSON object in model output.")


def extract_json_candidate(text: str) -> str:
    if not text or not text.strip():
        raise ValueError("Empty model output.")

    cleaned = strip_think_blocks(text)
    cleaned = strip_code_fences(cleaned)

    try:
        json.loads(cleaned)
        return cleaned
    except Exception:
        pass

    try:
        return extract_first_balanced_json(cleaned)
    except Exception:
        pass

    # json_repair as final fallback
    try:
        from json_repair import repair_json
        repaired = repair_json(cleaned)
        json.loads(repaired)  # validate
        return repaired
    except Exception:
        pass

    raise ValueError(f"Invalid json output: {text}")


def parse_repo_summary(raw_output: str) -> RepoSummary:
    candidate = extract_json_candidate(raw_output)
    data = json.loads(candidate)
    return RepoSummary.model_validate(data)


def build_repo_context(
    repo_name: str,
    file_records: List[dict],
    repo_metadata: dict,
) -> str:
    """
    Build compact repository metadata + file inventory context.
    """
    lines = []
    lines.append(f"Repository name: {repo_name}")
    lines.append(f"Owner: {repo_metadata.get('owner', 'Unknown')}")
    lines.append(f"Total selected files: {repo_metadata.get('total_files_selected', 0)}")
    lines.append(f"Total characters: {repo_metadata.get('total_chars', 0)}")
    lines.append("")

    lines.append("Files included:")
    for f in file_records:
        path = f.get("file_path", "unknown")
        language = f.get("language", "Unknown")
        char_count = len(f.get("content", "") or "")
        lines.append(f"- {path} | language={language} | chars={char_count}")

    return "\n".join(lines)


def build_file_summaries_text(file_summaries: List[FileSummary]) -> str:
    """
    Build a separate text block summarizing all file-level reviews.
    This is passed to the repo-summary prompt as {file_summaries_text}.
    """
    if not file_summaries:
        return "No file summaries were available."

    lines = []

    for summary in file_summaries:
        lines.append(f"FILE: {summary.file_path}")
        lines.append(f"Language: {summary.language}")
        lines.append(f"Purpose: {summary.purpose}")
        lines.append(f"Summary: {summary.summary}")

        if summary.key_components:
            lines.append("Key components:")
            for item in summary.key_components:
                lines.append(f"- {item}")

        if summary.issues:
            lines.append("Issues:")
            for issue in summary.issues:
                lines.append(
                    f"- [{issue.severity}] {issue.title}: {issue.explanation} | Fix: {issue.fix}"
                )

        if summary.suggestions:
            lines.append("Suggestions:")
            for s in summary.suggestions:
                lines.append(f"- {s}")

        lines.append("-" * 60)

    return "\n".join(lines)


def analyze_repository(
    selected_model: str,
    repo_name: str,
    file_records: List[dict],
    repo_metadata: dict,
    file_summaries: List[FileSummary],
) -> Tuple[RepoSummary, str]:
    """
    Run repository-level analysis using:
    - repo metadata / file inventory
    - file-level AI summaries
    Returns:
        (RepoSummary, raw_output)
    """
    prompt = build_repo_summary_prompt()
    llm = build_llm(selected_model)
    format_instructions = get_repo_summary_format_instructions()

    repo_context = build_repo_context(
        repo_name=repo_name,
        file_records=file_records,
        repo_metadata=repo_metadata,
    )

    file_summaries_text = build_file_summaries_text(file_summaries)

    chain = prompt | llm

    response = chain.invoke({
        "repo_name": repo_name,
        "repo_context": repo_context,
        "file_summaries_text": file_summaries_text,
        "format_instructions": format_instructions,
    })

    raw_output = response.content if hasattr(response, "content") else str(response)
    repo_summary = parse_repo_summary(raw_output)

    return repo_summary, raw_output