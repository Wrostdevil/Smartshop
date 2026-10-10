import re
from typing import List, Dict, Any, Tuple
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.schemas import SourceCitation
from app.utils.logging import logger

class CitationService:
    @staticmethod
    def extract_and_validate_citations(
        answer_text: str,
        retrieved_items: List[Tuple[DocumentChunk, Document, float]]
    ) -> List[SourceCitation]:
        """
        Validates citations against the actual retrieved chunks.
        Guarantees that only genuine chunks retrieved by the server are returned.
        Prevents hallucinated or fabricated source IDs.
        """
        if not retrieved_items:
            return []

        # Map of valid retrieved chunk_id -> (chunk, doc)
        retrieved_map: Dict[str, Tuple[DocumentChunk, Document]] = {
            chunk.id: (chunk, doc) for chunk, doc, sim in retrieved_items
        }

        # Look for explicit citations in the text: [Chunk: <uuid>] or [Source: <uuid>]
        cited_ids = set(re.findall(r"\[(?:Chunk|Source):\s*([a-zA-Z0-9\-]+)\]", answer_text))

        # Check which cited IDs actually belong to the retrieved set
        valid_citations: List[SourceCitation] = []
        already_added = set()

        for cid in cited_ids:
            if cid in retrieved_map and cid not in already_added:
                chunk, doc = retrieved_map[cid]
                citation = SourceCitation(
                    documentId=doc.id,
                    document=doc.title,
                    section=chunk.section,
                    version=doc.version,
                    effectiveDate=doc.effective_date,
                    region=doc.region,
                    page=chunk.page_number,
                    chunkId=chunk.id
                )
                valid_citations.append(citation)
                already_added.add(cid)

        # If model did not explicitly format bracketed chunk IDs, but provided a grounded answer
        # using the retrieved evidence, include the top matching retrieved chunks as cited sources
        if not valid_citations:
            for chunk, doc, sim in retrieved_items:
                if sim >= 0.25 and chunk.id not in already_added:
                    citation = SourceCitation(
                        documentId=doc.id,
                        document=doc.title,
                        section=chunk.section,
                        version=doc.version,
                        effectiveDate=doc.effective_date,
                        region=doc.region,
                        page=chunk.page_number,
                        chunkId=chunk.id
                    )
                    valid_citations.append(citation)
                    already_added.add(chunk.id)

        logger.info(f"Validated {len(valid_citations)} authentic source citations for response.")
        return valid_citations

citation_service = CitationService()
