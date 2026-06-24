import json
import re
from typing import Dict, List, Tuple

from langchain_core.output_parsers import JsonOutputParser

from prompts.file_summary_prompt import build_file_summary_prompt
from schemas.file_summary_schema import FileSummary
from services.llm_service import build_llm


def get_file_summary_format_instructions() -> str:
    parser = JsonOutputParser(pydantic_object=FileSummary)
    return parser.get_format_instructions()


def strip_think_blocks(text: str) -> str:
    """
    Remove model reasoning blocks like <think>...</think>.
    """
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def strip_code_fences(text: str) -> str:
    """
    Remove fenced JSON/code if the entire response is wrapped in ```...```.
    """
    text = text.strip()

    json_fence = re.match(r"^```json\s*(.*?)\s*```$", text, flags=re.DOTALL | re.IGNORECASE)
    if json_fence:
        return json_fence.group(1).strip()

    any_fence = re.match(r"^```[a-zA-Z0-9_+\-#]*\s*(.*?)\s*```$", text, flags=re.DOTALL)
    if any_fence:
        return any_fence.group(1).strip()

    return text


def extract_first_balanced_json(text: str) -> str:
    """
    Extract the first balanced top-level JSON object from a string.
    Handles cases where the model adds extra text before/after the JSON.
    """
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
                json.loads(candidate)  # validate before returning
                return candidate

    raise ValueError("Could not find a complete balanced JSON object in model output.")


def extract_json_candidate(text: str) -> str:
    """
    Robust JSON extraction from raw LLM output.
    Handles:
    - <think>...</think>
    - fenced JSON
    - raw JSON with trailing text
    """
    if not text or not text.strip():
        raise ValueError("Empty model output.")

    cleaned = strip_think_blocks(text)
    cleaned = strip_code_fences(cleaned)

    # Case 1: whole cleaned output is valid JSON
    try:
        json.loads(cleaned)
        return cleaned
    except Exception:
        pass

    # Case 2: extract first balanced JSON object
    try:
        return extract_first_balanced_json(cleaned)
    except Exception:
        pass

    raise ValueError(f"Invalid json output: {text}")


def parse_file_summary(raw_output: str) -> FileSummary:
    """
    Convert raw model output into validated FileSummary object.
    """
    candidate = extract_json_candidate(raw_output)
    data = json.loads(candidate)
    return FileSummary.model_validate(data)


def format_file_summary_for_repo(file_summary: FileSummary) -> str:
    """
    Convert one FileSummary object into a readable text block
    for repository-level summarization.
    """
    lines = [
        f"File: {file_summary.file_path}",
        f"Language: {file_summary.language}",
        f"Purpose: {file_summary.purpose}",
        f"Key Components: {', '.join(file_summary.key_components) if file_summary.key_components else 'None'}",
        f"Summary: {file_summary.summary}",
    ]

    if file_summary.issues:
        lines.append("Issues:")
        for issue in file_summary.issues:
            lines.append(
                f"- [{issue.severity}] {issue.title}: {issue.explanation} | Fix: {issue.fix}"
            )
    else:
        lines.append("Issues: None")

    if file_summary.suggestions:
        lines.append("Suggestions:")
        for suggestion in file_summary.suggestions:
            lines.append(f"- {suggestion}")
    else:
        lines.append("Suggestions: None")

    return "\n".join(lines)


def analyze_single_file(
    selected_model: str,
    repo_name: str,
    file_record: Dict
) -> Tuple[FileSummary, str]:
    """
    Analyze a single repository file and return:
    - parsed FileSummary object
    - raw model output
    """
    prompt = build_file_summary_prompt()
    llm = build_llm(selected_model)
    format_instructions = get_file_summary_format_instructions()

    chain = prompt | llm

    response = chain.invoke({
        "repo_name": repo_name,
        "file_path": file_record["file_path"],
        "language": file_record["language"],
        "code": file_record["content"],
        "format_instructions": format_instructions,
    })

    raw_output = response.content if hasattr(response, "content") else str(response)
    file_summary = parse_file_summary(raw_output)

    return file_summary, raw_output


def analyze_repo_files(
    selected_model: str,
    repo_name: str,
    file_records: List[Dict]
) -> Tuple[List[FileSummary], List[Dict]]:
    """
    Analyze all repository files one by one.

    Returns:
    - list of FileSummary objects
    - list of debug records
    """
    file_summaries: List[FileSummary] = []
    debug_records: List[Dict] = []

    for file_record in file_records:
        try:
            summary, raw_output = analyze_single_file(
                selected_model=selected_model,
                repo_name=repo_name,
                file_record=file_record
            )
            file_summaries.append(summary)

            debug_records.append({
                "file_path": file_record["file_path"],
                "status": "success",
                "raw_output": raw_output
            })

        except Exception as e:
            debug_records.append({
                "file_path": file_record.get("file_path", "unknown"),
                "status": "error",
                "error": str(e)
            })

    return file_summaries, debug_records


def combine_file_summaries_text(file_summaries: List[FileSummary]) -> str:
    """
    Convert all FileSummary objects into one combined text block
    for repository-level summarization.
    """
    if not file_summaries:
        return "No file summaries available."

    blocks = []
    for summary in file_summaries:
        blocks.append(format_file_summary_for_repo(summary))

    return ("\n\n" + "=" * 80 + "\n\n").join(blocks)