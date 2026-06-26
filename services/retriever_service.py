from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS


class RetrieverService:
    """
    Handles semantic retrieval from the repository FAISS index.
    """

    def __init__(self, vector_store: FAISS):

        if vector_store is None:
            raise ValueError(
                "Repository is not indexed yet."
            )

        self.vector_store = vector_store

    # -----------------------------------------------------
    # Retrieve documents
    # -----------------------------------------------------

    def retrieve(
        self,
        question: str,
        k: int = 5,
        filter_metadata: Optional[Dict] = None,
    ) -> List[Document]:

        if filter_metadata:

            return self.vector_store.similarity_search(
                query=question,
                k=k,
                filter=filter_metadata,
            )

        return self.vector_store.similarity_search(
            query=question,
            k=k,
        )

    # -----------------------------------------------------
    # Retrieve with similarity scores
    # -----------------------------------------------------

    def retrieve_with_scores(
        self,
        question: str,
        k: int = 5,
    ) -> List[Tuple[Document, float]]:

        return self.vector_store.similarity_search_with_score(
            query=question,
            k=k,
        )

    # -----------------------------------------------------
    # Build prompt context
    # -----------------------------------------------------

    def build_context(
        self,
        question: str,
        k: int = 5,
    ) -> str:

        docs = self.retrieve(
            question=question,
            k=k,
        )

        if not docs:
            return "No repository context found."

        sections = []

        for index, doc in enumerate(docs, start=1):

            metadata = doc.metadata

            file_path = metadata.get(
                "file_path",
                "Unknown"
            )

            language = metadata.get(
                "language",
                "Unknown"
            )

            chunk = metadata.get(
                "chunk_index",
                0
            )

            sections.append(
                f"""
========================
Context {index}

File:
{file_path}

Language:
{language}

Chunk:
{chunk}

Code:
{doc.page_content}
"""
            )

        return "\n".join(sections)

    # -----------------------------------------------------
    # Sources
    # -----------------------------------------------------

    def get_sources(
        self,
        question: str,
        k: int = 5,
    ) -> List[Dict]:

        docs = self.retrieve(
            question=question,
            k=k,
        )

        sources = []

        for doc in docs:

            metadata = doc.metadata

            sources.append(
                {
                    "file_path": metadata.get(
                        "file_path",
                        "Unknown",
                    ),
                    "language": metadata.get(
                        "language",
                        "Unknown",
                    ),
                    "chunk": metadata.get(
                        "chunk_index",
                        0,
                    ),
                }
            )

        return sources

    # -----------------------------------------------------
    # Retrieve complete documents
    # -----------------------------------------------------

    def retrieve_documents(
        self,
        question: str,
        k: int = 5,
    ) -> List[Document]:

        return self.retrieve(
            question=question,
            k=k,
        )