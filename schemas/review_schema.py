from typing import List
from pydantic import BaseModel, Field


class BugItem(BaseModel):
    title: str = Field(description="Short title of the bug/problem")
    severity: str = Field(description="Severity level: low, medium, or high")
    explanation: str = Field(description="Why this is a bug/problem")
    fix: str = Field(description="How to fix it")


class CodeReview(BaseModel):
    language: str = Field(description="Programming language of the reviewed code")
    understanding: str = Field(
        description="Short explanation of what the code is trying to do"
    )
    bugs: List[BugItem] = Field(
        default_factory=list,
        description="List of bugs, risky patterns, logic issues, or bad practices"
    )
    corrected_code: str = Field(
        description="Corrected or improved version of the code as plain code text, not markdown"
    )
    explanation: str = Field(
        description="Human-friendly explanation of the fixes and improvements"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Extra improvements, best practices, readability tips, or optimizations"
    )