import json
import re
from schemas.review_schema import CodeReview


def strip_code_fences(code: str) -> str:
    if not code:
        return code

    code = code.strip()
    code = re.sub(r"^```[a-zA-Z0-9_+\-#]*\n?", "", code)
    code = re.sub(r"\n?```$", "", code)
    return code.strip()


def extract_json_candidate(text: str) -> str:
    if not text:
        raise ValueError("Empty model output.")

    # remove <think>...</think>
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    # remove leading/trailing markdown noise
    cleaned = cleaned.strip()

    # 1) direct parse
    try:
        json.loads(cleaned)
        return cleaned
    except Exception:
        pass

    # 2) fenced ```json ... ```
    fence_match = re.search(
        r"```json\s*(.*?)\s*```",
        cleaned,
        re.DOTALL | re.IGNORECASE
    )
    if fence_match:
        candidate = fence_match.group(1).strip()
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            pass

    # 3) any fenced block
    any_fence_match = re.search(
        r"```(?:[a-zA-Z0-9_+\-#]*)?\s*(.*?)\s*```",
        cleaned,
        re.DOTALL
    )
    if any_fence_match:
        candidate = any_fence_match.group(1).strip()
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            pass

    # 4) extract first top-level {...}
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = cleaned[start:end + 1]
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            pass

    raise ValueError("Could not extract valid JSON from model output.")


def parse_review(raw_output: str) -> CodeReview:
    candidate = extract_json_candidate(raw_output)
    data = json.loads(candidate)
    review = CodeReview.model_validate(data)
    review.corrected_code = strip_code_fences(review.corrected_code)
    return review