
from app.models.document_chunk import DocumentChunk
from app.ingestion.markdown_loader import MarkdownDocument


class DocumentChunker:

    def __init__(
        self,
        chunk_size: int = 1200,
        chunk_overlap: int = 150
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be non-negative and smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _split_long_text(self, text: str) -> list[str]:
        """Split a long paragraph into overlapping character windows."""
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunks.append(text[start:end].strip())

            if end == len(text):
                break

            start = end - self.chunk_overlap

        return [chunk for chunk in chunks if chunk]

    def _split_content(self, content: str) -> list[str]:
        paragraphs = [
            paragraph.strip()
            for paragraph in content.split("\n\n")
            if paragraph.strip()
        ]

        chunks = []
        current = ""

        for paragraph in paragraphs:

            # Split a paragraph if it exceeds the chunk size.
            if len(paragraph) > self.chunk_size:
                if current:
                    chunks.append(current)
                    current = ""

                chunks.extend(self._split_long_text(paragraph))
                continue

            candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph

            if len(candidate) <= self.chunk_size:
                current = candidate
            else:
                if current:
                    chunks.append(current)

                overlap = current[-self.chunk_overlap:] if self.chunk_overlap else ""
                current = f"{overlap}\n\n{paragraph}".strip()

        if current:
            chunks.append(current)

        return chunks

    def chunk_document(
        self,
        document: MarkdownDocument
    ) -> list[DocumentChunk]:

        text_chunks = self._split_content(document.content)

        result = []

        for index, content in enumerate(text_chunks, start=1):
            chunk = DocumentChunk(
                id=f"{document.id}-CHUNK-{index:04d}",
                document_id=document.id,
                document_title=document.title,
                document_type=document.document_type,
                chunk_index=index,
                content=content,
                source_file=document.source_file,
            )

            result.append(chunk)

        return result
