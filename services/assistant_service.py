from typing import Generator, List, Dict

from langchain_core.output_parsers import StrOutputParser

from prompts.assistant_prompt import build_assistant_prompt
from services.llm_service import build_streaming_llm
from services.retriever_service import RetrieverService


class AssistantService:

    def __init__(
        self,
        vector_store,
        selected_model: str,
        top_k: int = 5,
    ):

        self.retriever = RetrieverService(vector_store)

        self.prompt = build_assistant_prompt()

        self.llm = build_streaming_llm(selected_model)

        self.parser = StrOutputParser()

        self.top_k = top_k

    # ---------------------------------------------------------

    def ask(
        self,
        repo_name: str,
        question: str,
        chat_history: List[Dict],
    ) -> Generator[str, None, None]:

        repo_context = self.retriever.build_context(
            question=question,
            k=self.top_k,
        )

        chain = (
            self.prompt
            | self.llm
            | self.parser
        )

        response = ""

        for chunk in chain.stream(
            {
                "repo_name": repo_name,
                "repo_context": repo_context,
                "chat_history": chat_history,
                "question": question,
            }
        ):

            response += chunk

            yield response

    # ---------------------------------------------------------

    def get_sources(
        self,
        question: str,
    ):

        return self.retriever.get_sources(
            question=question,
            k=self.top_k,
        )

    # ---------------------------------------------------------

    def get_documents(
        self,
        question: str,
    ):

        return self.retriever.retrieve_documents(
            question=question,
            k=self.top_k,
        )

    # ---------------------------------------------------------

    def get_context(
        self,
        question: str,
    ):

        return self.retriever.build_context(
            question=question,
            k=self.top_k,
        )