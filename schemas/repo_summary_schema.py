from typing import List
from pydantic import BaseModel, Field


class RepoIssue(BaseModel):
    title: str = Field(description="Short title of the repository-level issue")
    severity: str = Field(description="Severity level: low, medium, or high")
    explanation: str = Field(description="Why this is a problem at repo/project level")
    affected_files: List[str] = Field(
        default_factory=list,
        description="List of file paths related to this issue if known"
    )
    fix: str = Field(description="How to fix or improve this issue")


class RepoSummary(BaseModel):
    repo_name: str = Field(description="Repository name")
    overview: str = Field(
        description="High-level explanation of what the repository/project does"
    )
    architecture: str = Field(
        description="Short explanation of project structure, modules, and architecture"
    )
    tech_stack: List[str] = Field(
        default_factory=list,
        description="Technologies, frameworks, and tools used in the repository"
    )
    important_files: List[str] = Field(
        default_factory=list,
        description="Most important files in the repository"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="What is good about the codebase or project structure"
    )
    issues: List[RepoIssue] = Field(
        default_factory=list,
        description="Repository-level issues, risks, or architectural problems"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Overall improvements, refactoring ideas, or best-practice suggestions"
    )
    final_verdict: str = Field(
        description="Short concluding evaluation of the repository quality"
    )