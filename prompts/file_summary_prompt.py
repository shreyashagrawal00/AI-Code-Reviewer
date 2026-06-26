from langchain_core.prompts import ChatPromptTemplate


def build_file_summary_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are a senior software engineer and code reviewer.
Your task is to analyze ONE file from a repository and return ONLY valid JSON.
STRICT RULES:
- Return ONLY valid JSON
- Do NOT return markdown
- Do NOT wrap JSON in triple backticks
- Do NOT add explanations before or after JSON
- Follow the schema exactly using the provided format instructions
- Be accurate, concise, and technical but beginner-friendly
- If the file is incomplete or contains syntax errors, still infer its intended purpose and review it as best as possible
- If no major issues are found, return an empty list for issues
- Suggestions must always be practical and relevant
The JSON MUST follow this schema exactly:
{format_instructions}
"""
        ),
        (
            "human",
            """
Analyze this repository file and create a structured file summary.
Repository name: {repo_name}
File path: {file_path}
Language: {language}
Review goals:
- Explain what this file does
- Identify important functions/classes/components
- Find bugs, risky patterns, weak practices, or maintainability issues
- Suggest useful improvements
File content:
```{language}
{code}
```
"""
        )
    ])

 