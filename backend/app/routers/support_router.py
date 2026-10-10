"""Support tickets (CRUD) + policy search + RAG document ingestion (Module 2)."""
import random
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import get_db
from app.models.sqlalchemy.support import PolicyDocument, SupportTicket
from app.models.sqlalchemy.knowledge import KnowledgeDocument, DocumentChunk

support_router = APIRouter()


class TicketIn(BaseModel):
    subject: str = ""
    message: str = ""
    email: str = ""
    status: Optional[str] = None


class TicketOut(BaseModel):
    ticket_number: str
    subject: str = ""
    message: str = ""
    status: str = "OPEN"
    email: str = ""


def _ticket_number(db: Session) -> str:
    for _ in range(20):
        n = f"TCK-{random.randint(10000, 99999)}"
        if not db.query(SupportTicket).filter(SupportTicket.ticket_number == n).one_or_none():
            return n
    return f"TCK-{random.randint(100000, 999999)}"


@support_router.post("/ticket", response_model=TicketOut)
def submit_ticket(body: TicketIn, db: Session = Depends(get_db)):
    t = SupportTicket(
        ticket_number=_ticket_number(db),
        subject=body.subject,
        message=body.message,
        email=body.email,
        status="OPEN",
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return TicketOut(ticket_number=t.ticket_number, subject=t.subject, message=t.message, status=t.status, email=t.email)


@support_router.get("/ticket", response_model=List[TicketOut])
def read_tickets(status: Optional[str] = Query(None), db: Session = Depends(get_db)):
    q = db.query(SupportTicket).order_by(SupportTicket.id.desc())
    if status:
        q = q.filter(SupportTicket.status == status)
    return [
        TicketOut(ticket_number=t.ticket_number, subject=t.subject, message=t.message, status=t.status, email=t.email)
        for t in q.limit(50).all()
    ]


@support_router.get("/ticket/{ticket_id}", response_model=TicketOut)
def read_ticket(ticket_id: str, db: Session = Depends(get_db)):
    from fastapi import HTTPException

    t = (
        db.query(SupportTicket)
        .filter((SupportTicket.ticket_number == ticket_id) | (SupportTicket.id == ticket_id if ticket_id.isdigit() else False))
        .one_or_none()
    )
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketOut(ticket_number=t.ticket_number, subject=t.subject, message=t.message, status=t.status, email=t.email)


@support_router.put("/ticket/{ticket_id}", response_model=TicketOut)
def modify_ticket(ticket_id: str, body: TicketIn, db: Session = Depends(get_db)):
    from fastapi import HTTPException

    t = (
        db.query(SupportTicket)
        .filter((SupportTicket.ticket_number == ticket_id) | (SupportTicket.id == ticket_id if ticket_id.isdigit() else False))
        .one_or_none()
    )
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if body.status:
        t.status = body.status
    if body.subject:
        t.subject = body.subject
    if body.message:
        t.message = body.message
    db.commit()
    db.refresh(t)
    return TicketOut(ticket_number=t.ticket_number, subject=t.subject, message=t.message, status=t.status, email=t.email)


@support_router.get("/policies")
def list_policies(db: Session = Depends(get_db)):
    return [
        {"document": p.document, "section": p.section, "version": p.version, "content": p.content}
        for p in db.query(PolicyDocument).order_by(PolicyDocument.id.asc()).all()
    ]


# ----------------------------------------------------------------------------
# RAG document ingestion (Module 2: upload PDF / Markdown / JSON / TXT,
# chunk, embed, vector-store). The RAG assistant answers from these docs.
# ----------------------------------------------------------------------------

class DocumentIn(BaseModel):
    document: str
    section: str = "General"
    version: str = "2026.1"
    category: str = "policy"
    region: str = "global"
    text: str = ""


@support_router.post("/documents", status_code=201)
def create_document(body: DocumentIn, db: Session = Depends(get_db)):
    from app.services import rag_service

    if not body.document.strip() or not body.text.strip():
        raise HTTPException(status_code=400, detail="document and text are required")
    return rag_service.ingest_document(
        db, document=body.document.strip(), section=body.section or "General",
        version=body.version or "2026.1", category=body.category or "policy",
        region=body.region or "global", text=body.text,
    )


@support_router.post("/documents/upload", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    section: str = Form("General"),
    version: str = Form("2026.1"),
    category: str = Form("policy"),
    region: str = Form("global"),
    db: Session = Depends(get_db),
):
    from app.services import rag_service

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")
    try:
        return rag_service.ingest_upload(
            db, file.filename or "upload.txt", raw,
            section=section, version=version, category=category, region=region,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@support_router.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(KnowledgeDocument).order_by(KnowledgeDocument.id.desc()).all()
    counts = {}
    for (did,) in db.query(DocumentChunk.document_id).all():
        counts[did] = counts.get(did, 0) + 1
    return [
        {"id": d.id, "document": d.document, "section": d.section, "version": d.version,
         "category": d.category, "region": d.region, "source_filename": d.source_filename,
         "chunks": counts.get(d.id, 0)}
        for d in docs
    ]


@support_router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"deleted": doc_id}
