from typing import Dict, List

from langchain_core.documents import Document


class CitationService:
    """
    Handles repository citations for retrieved documents.
    """

    @staticmethod
    def build_sources(documents: List[Document]) -> List[Dict]:

        sources = []

        seen = set()

        for doc in documents:

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

            key = (
                file_path,
                chunk,
            )

            if key in seen:
                continue

            seen.add(key)

            sources.append(
                {
                    "file_path": file_path,
                    "language": language,
                    "chunk": chunk,
                }
            )

        return sources

    # ---------------------------------------------------------

    @staticmethod
    def build_markdown(
        sources: List[Dict],
    ) -> str:

        if not sources:
            return "No sources available."

        markdown = []

        for index, source in enumerate(
            sources,
            start=1,
        ):

            markdown.append(
                f"""
### {index}

**File**

`{source['file_path']}`

**Language**

{source['language']}

**Chunk**

{source['chunk']}
"""
            )

        return "\n".join(markdown)

    # ---------------------------------------------------------

    @staticmethod
    def unique_files(
        sources: List[Dict],
    ) -> List[str]:

        files = []

        seen = set()

        for source in sources:

            file_path = source["file_path"]

            if file_path in seen:
                continue

            seen.add(file_path)

            files.append(file_path)

        return files

    # ---------------------------------------------------------

    @staticmethod
    def file_count(
        sources: List[Dict],
    ) -> int:

        return len(
            CitationService.unique_files(
                sources
            )
        )