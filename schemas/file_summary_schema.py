from typing import List
from pydantic import BaseModel, Field


class FileIssue(BaseModel):
    title: str = Field(description="Short title of the issue found in the file")
    severity: str = Field(description="Severity level: low, medium, or high")
    explanation: str = Field(description="Why this issue is a problem")
    fix: str = Field(description="How to fix or improve it")


class FileSummary(BaseModel):
    file_path: str = Field(description="Path of the file inside the repository")
    language: str = Field(description="Programming language or file type")
    purpose: str = Field(description="What this file is doing in simple words")
    key_components: List[str] = Field(
        description="Important functions, classes, components, or sections present in the file"
    )
    issues: List[FileIssue] = Field(
        description="List of bugs, risky patterns, or code issues found in the file"
    )
    summary: str = Field(
        description="Short final summary of the file's role and quality"
    )
    suggestions: List[str] = Field(
        description="Improvements, refactoring ideas, or best-practice suggestions for this file"
    )