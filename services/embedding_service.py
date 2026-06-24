from langchain_huggingface import HuggingFaceEmbeddings
from utils.constants import EMBEDDING_MODEL_NAME
from utils.constants import EMBEDDING_MODEL_NAME


_embedding_model = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Lazy-load the embedding model once and reuse it.
    """
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME
        )

    return _embedding_model