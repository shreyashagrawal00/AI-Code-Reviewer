from typing import Dict, List
from utils.constants import VECTOR_TOP_K
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from services.embedding_service import get_embedding_model
from utils.constants import VECTOR_TOP_K


def build_chunk_documents(chunk_records: List[Dict]) -> List[Document]:
    """
    Convert chunk records into LangChain Documents for FAISS.
    """
    documents = []

    for chunk in chunk_records:
        doc = Document(
            page_content=chunk["chunk_text"],
            metadata={
                "file_path": chunk["file_path"],
                "language": chunk["language"],
                "chunk_index": chunk["chunk_index"],
            }
        )
        documents.append(doc)

    return documents


def build_vector_store(chunk_records: List[Dict]) -> FAISS:
    """
    Build a FAISS vector store from repo chunk records.
    """
    if not chunk_records:
        raise ValueError("No chunk records available to build vector store.")

    embeddings = get_embedding_model()
    documents = build_chunk_documents(chunk_records)

    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store


def retrieve_relevant_chunks(
    vector_store: FAISS,
    query: str,
    top_k: int = VECTOR_TOP_K
) -> List[Document]:
    """
    Retrieve top-k most relevant repo chunks for a query.
    """
    if not query.strip():
        return []

    return vector_store.similarity_search(query, k=top_k)


def format_retrieved_chunks(documents: List[Document]) -> str:
    """
    Convert retrieved Documents into a readable text block for the LLM.
    """
    if not documents:
        return "No relevant repository chunks found."

    lines = []
    for i, doc in enumerate(documents, 1):
        file_path = doc.metadata.get("file_path", "Unknown file")
        language = doc.metadata.get("language", "Unknown")
        chunk_index = doc.metadata.get("chunk_index", 0)

        lines.append(
            f"[Chunk {i}] File: {file_path} | Language: {language} | Chunk: {chunk_index}\n"
            f"{doc.page_content}\n"
        )

    return "\n".join(lines)


def get_repo_file_list_from_chunks(chunk_records: List[Dict]) -> List[str]:
    """
    Return unique file paths present in chunk records.
    """
    return sorted({chunk["file_path"] for chunk in chunk_records})