from typing import List, Dict, Any
from app.config import settings
from app.services.document_loader import LoadedDocument
from app.utils.logging import logger

class ChunkingService:
    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, chunk_overlap: int = settings.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, loaded_doc: LoadedDocument) -> List[Dict[str, Any]]:
        """
        Splits a LoadedDocument into section-aware chunks respecting token limits and overlap.
        Preserves section names, document title, and page numbers.
        """
        chunks = []
        chunk_idx = 0

        # If sections exist, chunk within each section to maintain thematic unity
        sections = loaded_doc.sections
        if not sections:
            sections = [{"section": "General", "content": loaded_doc.raw_text, "page": 1}]

        for sec in sections:
            sec_name = sec.get("section", "General")
            sec_content = sec.get("content", "").strip()
            page_num = sec.get("page")

            if not sec_content:
                continue

            words = sec_content.split()
            # If section fits within chunk_size, keep as a single chunk
            if len(words) <= self.chunk_size:
                chunks.append({
                    "chunk_index": chunk_idx,
                    "section": sec_name,
                    "page_number": page_num,
                    "content": f"[{loaded_doc.title} - Section: {sec_name}]\n{sec_content}"
                })
                chunk_idx += 1
            else:
                # Sliding window chunking with overlap
                start = 0
                step = max(1, self.chunk_size - self.chunk_overlap)
                while start < len(words):
                    end = min(start + self.chunk_size, len(words))
                    sub_words = words[start:end]
                    sub_content = " ".join(sub_words)

                    chunks.append({
                        "chunk_index": chunk_idx,
                        "section": sec_name,
                        "page_number": page_num,
                        "content": f"[{loaded_doc.title} - Section: {sec_name}]\n{sub_content}"
                    })
                    chunk_idx += 1
                    if end >= len(words):
                        break
                    start += step

        logger.info(f"Chunked document '{loaded_doc.title}' into {len(chunks)} chunks.")
        return chunks
