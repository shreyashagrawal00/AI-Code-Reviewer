import json
import re
from typing import Tuple

from prompts.review_prompt import build_review_prompt
from schemas.review_schema import CodeReview
from services.llm_service import build_llm
from langchain_core.output_parsers import JsonOutputParser


def get_review_format_instructions() -> str:
    parser = JsonOutputParser(pydantic_object=CodeReview)
    return parser.get_format_instructions()


def strip_code_fences(code: str) -> str:
    """
    Remove markdown code fences if the model accidentally returns them.
    """
    if not code:
        return code

    code = code.strip()
    code = re.sub(r"^```[a-zA-Z0-9_+\-#]*\n?", "", code)
    code = re.sub(r"\n?```$", "", code)
    return code.strip()


def extract_json_candidate(text: str) -> str:
    """
    Try to extract valid JSON from raw LLM output.
    Handles cases where the model adds extra text or wraps JSON in code fences.
    Uses json_repair as a final fallback for malformed-but-fixable JSON.
    """
    if not text:
        raise ValueError("Empty model output.")

    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    # Case 1: whole output is already valid JSON
    try:
        json.loads(cleaned)
        return cleaned
    except Exception:
        pass

    # Case 2: ```json ... ```
    fence_match = re.search(r"```json\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
    if fence_match:
        candidate = fence_match.group(1).strip()
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            pass

    # Case 3: any fenced block
    any_fence_match = re.search(r"```(?:[a-zA-Z0-9_+\-#]*)?\s*(.*?)\s*```", cleaned, re.DOTALL)
    if any_fence_match:
        candidate = any_fence_match.group(1).strip()
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            pass

    # Case 4: balanced brace extraction
    start = cleaned.find("{")
    if start != -1:
        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(cleaned)):
            ch = cleaned[i]
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
                    candidate = cleaned[start:i + 1]
                    try:
                        json.loads(candidate)
                        return candidate
                    except Exception:
                        # Case 5: try json_repair on the extracted block
                        try:
                            from json_repair import repair_json
                            repaired = repair_json(candidate)
                            json.loads(repaired)  # validate
                            return repaired
                        except Exception:
                            pass
                    break

    # Case 6: json_repair on the whole cleaned output as last resort
    try:
        from json_repair import repair_json
        repaired = repair_json(cleaned)
        json.loads(repaired)  # validate the repair worked
        return repaired
    except Exception:
        pass

    raise ValueError("Could not extract valid JSON from model output.")


def parse_review(raw_output: str) -> CodeReview:
    """
    Parse raw model output into a validated CodeReview object.
    """
    candidate = extract_json_candidate(raw_output)
    data = json.loads(candidate)
    review = CodeReview.model_validate(data)

    # cleanup if corrected_code accidentally comes back fenced
    review.corrected_code = strip_code_fences(review.corrected_code)
    return review


def run_code_review(
    selected_model: str,
    language: str,
    task_description: str,
    review_focus: str,
    code: str
) -> Tuple[CodeReview, str]:
    """
    Run single-code review through the LLM.

    Returns:
    - parsed CodeReview object
    - raw LLM output
    """
    if not code or not code.strip():
        raise ValueError("Code input is empty.")

    prompt = build_review_prompt()
    llm = build_llm(selected_model)
    format_instructions = get_review_format_instructions()

    chain = prompt | llm

    response = chain.invoke({
        "language": language,
        "task_description": task_description,
        "review_focus": review_focus,
        "code": code,
        "format_instructions": format_instructions,
    })

    raw_output = response.content if hasattr(response, "content") else str(response)
    review = parse_review(raw_output)

    return review, raw_output