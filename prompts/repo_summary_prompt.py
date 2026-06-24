from langchain_core.prompts import ChatPromptTemplate


def build_repo_summary_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are a senior software engineer, software architect, and code reviewer.

Your task is to analyze an ENTIRE repository using the provided repository context and file summaries, then return ONLY valid JSON.

STRICT RULES:
- Return ONLY valid JSON
- Do NOT return markdown
- Do NOT wrap JSON in triple backticks
- Do NOT add explanations before or after JSON
- Follow the schema exactly using the provided format instructions
- Focus on repository-level understanding, architecture, strengths, issues, and improvements
- Use the file summaries to infer how the project is structured
- If some details are missing, make careful, reasonable inferences from the available repository data
- Keep the final verdict concise but meaningful
- If no major repository-level issues are found, return an empty list for issues

The JSON MUST follow this schema exactly:
{format_instructions}
"""
        ),
        (
            "human",
            """
Analyze this repository and create a structured repository summary.

Repository name: {repo_name}

Repository context:
{repo_context}

File summaries:
{file_summaries_text}

Your job:
- Explain what the overall repository/project does
- Explain the architecture and how the project is structured
- Identify the main technologies used
- Point out the most important files or modules
- Find repository-level problems, risks, architectural weaknesses, or maintainability issues
- Mention strengths of the codebase
- Suggest practical improvements
- Give a short final verdict about the repository quality
"""
        )
    ])