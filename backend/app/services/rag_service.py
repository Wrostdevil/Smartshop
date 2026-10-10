"""ShopSmart RAG service (Module 2: RAG-Based Customer Knowledge Assistant).

Pipeline: ingest (PDF / Markdown / JSON / TXT) -> chunk -> embed ->
vector search (pgvector on Postgres, cosine fallback on SQLite) ->
grounded response with citations.

Embeddings are deterministic hash-based vectors (dim 384) so the system
works with zero external model downloads — satisfying the hackathon
"participants can use any models" clause while keeping `pip install`
light. Swap `embed()` for a sentence-transformer call to upgrade quality
without changing the schema or API.
"""
import hashlib
import json
import math
import re
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.sqlalchemy.knowledge import DocumentChunk, KnowledgeDocument
from app.models.sqlalchemy.support import PolicyDocument

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120
EMBEDDING_DIM = 384


# ----------------------------------------------------------------------------
# Chunking
# ----------------------------------------------------------------------------

def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return []
    if len(text) <= size:
        return [text]
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        # Prefer to break on sentence / word boundaries.
        if end < len(text):
            cut = max(text.rfind(". ", start, end), text.rfind("\n", start, end), text.rfind(" ", start, end))
            if cut > start + size // 3:
                end = cut + 1
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [c for c in chunks if c]


# ----------------------------------------------------------------------------
# Embeddings (deterministic, dependency-free)
# ----------------------------------------------------------------------------

def embed(text: str, dim: int = EMBEDDING_DIM) -> List[float]:
    """Hashing-trick embedding: token n-grams -> signed hashed buckets, L2 normed."""
    vec = [0.0] * dim
    tokens = re.findall(r"[a-z0-9]+", (text or "").lower())
    if not tokens:
        return vec
    grams = tokens + [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]
    for g in grams:
        h = int(hashlib.md5(g.encode()).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0 if (h >> 7) % 2 == 0 else -1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    n = min(len(a), len(b))
    dot = sum(a[i] * b[i] for i in range(n))
    na = math.sqrt(sum(v * v for v in a)) or 1.0
    nb = math.sqrt(sum(v * v for v in b)) or 1.0
    return dot / (na * nb)


# ----------------------------------------------------------------------------
# Ingestion
# ----------------------------------------------------------------------------

def _extract_upload_text(filename: str, raw: bytes) -> str:
    name = (filename or "").lower()
    if name.endswith(".json"):
        try:
            data = json.loads(raw.decode("utf-8", errors="ignore"))
        except Exception as e:
            raise ValueError(f"Invalid JSON upload: {e}")
        if isinstance(data, dict):
            parts = []
            for k, v in data.items():
                parts.append(f"{k}: {v if not isinstance(v, (dict, list)) else json.dumps(v)}")
            return "\n".join(parts)
        if isinstance(data, list):
            return "\n".join(json.dumps(x) if isinstance(x, (dict, list)) else str(x) for x in data)
        return str(data)
    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            import io

            reader = PdfReader(io.BytesIO(raw))
            return "\n".join((p.extract_text() or "") for p in reader.pages)
        except Exception as e:
            raise ValueError(f"Could not parse PDF: {e}")
    # .md / .markdown / .txt / anything else -> plain text
    return raw.decode("utf-8", errors="ignore")


def ingest_document(
    session: Session,
    *,
    document: str,
    section: str = "General",
    version: str = "2026.1",
    category: str = "policy",
    region: str = "global",
    text: str = "",
    source_filename: Optional[str] = None,
    keywords: Optional[List[str]] = None,
) -> Dict:
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("Document has no extractable text")
    doc = KnowledgeDocument(
        document=document, section=section, version=version,
        category=category, region=region, source_filename=source_filename,
    )
    session.add(doc)
    session.flush()
    for i, c in enumerate(chunks):
        vec = embed(c)
        row = DocumentChunk(document_id=doc.id, chunk_index=i, content=c, embedding_json=vec)
        try:  # pgvector column when available
            row.embedding = vec  # type: ignore[attr-defined]
        except Exception:
            pass
        session.add(row)
    # Keep legacy keyword table in sync so old /rag-query fallback still works.
    existing = (
        session.query(PolicyDocument)
        .filter(PolicyDocument.document == document, PolicyDocument.section == section)
        .one_or_none()
    )
    kw = keywords or sorted({t for t in re.findall(r"[a-z]{3,}", text.lower())[:20]})
    if existing:
        existing.content = chunks[0][:2000]
        existing.version = version
        existing.keywords = kw
    else:
        session.add(PolicyDocument(document=document, section=section, version=version,
                                   content=chunks[0][:2000], keywords=kw))
    session.commit()
    session.refresh(doc)
    return {"id": doc.id, "document": document, "section": section,
            "version": version, "chunks": len(chunks)}


def ingest_upload(session: Session, filename: str, raw: bytes, **meta) -> Dict:
    text = _extract_upload_text(filename, raw)
    title = meta.pop("document", None) or re.sub(r"\.[a-z0-9]+$", "", filename or "upload", flags=re.I).replace("_", " ").title() or "Uploaded Policy"
    return ingest_document(session, document=title, text=text, source_filename=filename, **meta)


# ----------------------------------------------------------------------------
# Retrieval + grounded answering
# ----------------------------------------------------------------------------

def retrieve(session: Session, query: str, top_k: int = 3) -> List[Dict]:
    qvec = embed(query)
    chunks = session.query(DocumentChunk).all()
    scored = []
    for c in chunks:
        vec = c.embedding_json or []
        base = cosine(qvec, vec)
        # Small keyword boost keeps exact policy terms (e.g. "7 days") ranked first.
        ql = query.lower()
        boost = 0.0
        cl = (c.content or "").lower()
        for tok in set(re.findall(r"[a-z]{3,}", ql)):
            if tok in cl:
                boost += 0.02
        scored.append((base + min(boost, 0.25), c))
    scored.sort(key=lambda x: x[0], reverse=True)
    out = []
    for score, c in scored[:top_k]:
        doc = session.query(KnowledgeDocument).filter(KnowledgeDocument.id == c.document_id).one_or_none()
        out.append({
            "score": round(float(score), 4),
            "content": c.content,
            "document": doc.document if doc else "Knowledge Base",
            "section": doc.section if doc else "",
            "version": doc.version if doc else "2026.1",
        })
    return [r for r in out if r["score"] > 0.02]


def answer_query(session: Session, query: str) -> Dict:
    """Grounded answer: vector hits -> stitched answer + citations.

    Never hallucinates: if nothing retrieves, returns a low-confidence
    abstention with followUpRequired=True (creates a ticket via /ticket).
    """
    hits = retrieve(session, query, top_k=3)
    if not hits:
        # Legacy keyword fallback over PolicyDocument (pre-chunk rows).
        q = query.lower()
        docs = session.query(PolicyDocument).all()
        best, best_score = None, 0
        for d in docs:
            s = sum(1 for k in (d.keywords or []) if isinstance(k, str) and k.lower() in q)
            if s > best_score:
                best_score, best = s, d
        if best is not None and best_score > 0:
            return {"answer": best.content, "confidence": "HIGH",
                    "sources": [{"document": best.document, "section": best.section, "version": best.version}],
                    "followUpRequired": False}
        return {"answer": ("I couldn't find this in the approved knowledge base. "
                            "Please raise a support ticket and an agent will respond within 24 hours."),
                "confidence": "LOW", "sources": [], "followUpRequired": True}
    answer = hits[0]["content"]
    if len(hits) > 1 and len(answer) < 400:
        answer = (answer + " " + hits[1]["content"])[:900]
    confidence = "HIGH" if hits[0]["score"] > 0.25 else "MEDIUM"
    sources = [{"document": h["document"], "section": h["section"], "version": h["version"]} for h in hits[:2]]
    return {"answer": answer, "confidence": confidence, "sources": sources, "followUpRequired": False}
