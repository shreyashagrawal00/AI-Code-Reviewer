from prompts.repo_qa_prompt import build_repo_qa_prompt
from services.llm_service import build_llm
from services.vector_store_service import (
    retrieve_relevant_chunks,
    format_retrieved_chunks,
)


def answer_repo_question(
    selected_model: str,
    repo_name: str,
    vector_store,
    question: str,
    top_k: int = 6
):
    """
    Retrieve relevant repository chunks and ask the LLM to answer
    the user's repo question using only that retrieved context.

    Returns:
    - answer_text
    - retrieved_context_text
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    docs = retrieve_relevant_chunks(vector_store, question, top_k=top_k)
    retrieved_context = format_retrieved_chunks(docs)

    prompt = build_repo_qa_prompt()
    llm = build_llm(selected_model)

    chain = prompt | llm

    response = chain.invoke({
        "repo_name": repo_name,
        "question": question,
        "retrieved_context": retrieved_context,
    })

    answer_text = response.content if hasattr(response, "content") else str(response)
    return answer_text, retrieved_context