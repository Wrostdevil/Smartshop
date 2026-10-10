import hashlib
import json
import re
from typing import Dict, Any, List, Optional
from pypdf import PdfReader
from app.utils.logging import logger

class DocumentLoaderError(Exception):
    """Exception raised when document loading or parsing fails."""
    pass

class LoadedDocument:
    def __init__(
        self,
        raw_text: str,
        content_hash: str,
        title: str,
        category: str,
        version: str = "1.0",
        effective_date: Optional[str] = None,
        region: str = "IN",
        sections: Optional[List[Dict[str, Any]]] = None,
        pages: Optional[List[Dict[str, Any]]] = None
    ):
        self.raw_text = raw_text
        self.content_hash = content_hash
        self.title = title
        self.category = category
        self.version = version
        self.effective_date = effective_date
        self.region = region
        self.sections = sections or []
        self.pages = pages or []

class DocumentLoader:
    @staticmethod
    def calculate_hash(content_bytes: bytes) -> str:
        return hashlib.sha256(content_bytes).hexdigest()

    @classmethod
    def load_markdown(
        cls,
        content_bytes: bytes,
        filename: str,
        metadata_override: Optional[Dict[str, Any]] = None
    ) -> LoadedDocument:
        content_str = content_bytes.decode("utf-8", errors="replace").strip()
        if not content_str:
            raise DocumentLoaderError(f"Document '{filename}' is empty.")

        content_hash = cls.calculate_hash(content_bytes)

        # Extract title from first H1 if present
        title = filename
        title_match = re.search(r"^#\s+(.+)$", content_str, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()

        # Extract metadata lines (e.g. - **Version**: 2026.1)
        version = "1.0"
        category = "general"
        region = "IN"
        effective_date = None

        ver_match = re.search(r"-\s+\*\*Version\*\*:\s*([^\n\r]+)", content_str, re.IGNORECASE)
        if ver_match:
            version = ver_match.group(1).strip()

        cat_match = re.search(r"-\s+\*\*Category\*\*:\s*([^\n\r]+)", content_str, re.IGNORECASE)
        if cat_match:
            category = cat_match.group(1).strip().lower()

        reg_match = re.search(r"-\s+\*\*Region\*\*:\s*([^\n\r]+)", content_str, re.IGNORECASE)
        if reg_match:
            region = reg_match.group(1).strip().upper()

        date_match = re.search(r"-\s+\*\*Effective Date\*\*:\s*([^\n\r]+)", content_str, re.IGNORECASE)
        if date_match:
            effective_date = date_match.group(1).strip()

        # Apply overrides
        if metadata_override:
            title = metadata_override.get("title", title)
            category = metadata_override.get("category", category).lower()
            version = metadata_override.get("version", version)
            region = metadata_override.get("region", region).upper()
            if "effective_date" in metadata_override:
                effective_date = metadata_override["effective_date"]

        # Parse sections based on markdown headings
        sections = []
        heading_splits = re.split(r"(^##\s+.+$)", content_str, flags=re.MULTILINE)
        current_section = "Overview"
        current_text = ""

        if len(heading_splits) > 1:
            # First preamble before any ##
            if heading_splits[0].strip():
                sections.append({"section": "Overview", "content": heading_splits[0].strip(), "page": 1})
            for i in range(1, len(heading_splits), 2):
                h_name = heading_splits[i].replace("##", "").strip()
                h_content = heading_splits[i+1].strip() if i+1 < len(heading_splits) else ""
                sections.append({"section": h_name, "content": h_content, "page": 1})
        else:
            sections.append({"section": "General", "content": content_str, "page": 1})

        return LoadedDocument(
            raw_text=content_str,
            content_hash=content_hash,
            title=title,
            category=category,
            version=version,
            effective_date=effective_date,
            region=region,
            sections=sections
        )

    @classmethod
    def load_pdf(
        cls,
        content_bytes: bytes,
        filename: str,
        metadata_override: Optional[Dict[str, Any]] = None
    ) -> LoadedDocument:
        import io
        try:
            reader = PdfReader(io.BytesIO(content_bytes))
        except Exception as e:
            raise DocumentLoaderError(f"Failed to read PDF file '{filename}': {str(e)}")

        pages_data = []
        full_text = []

        for idx, page in enumerate(reader.pages):
            text = (page.extract_text() or "").strip()
            if text:
                pages_data.append({"page_number": idx + 1, "text": text})
                full_text.append(text)

        joined_text = "\n\n".join(full_text).strip()
        if not joined_text:
            raise DocumentLoaderError(
                f"PDF '{filename}' contained no extractable text. Scanned or empty PDFs cannot be indexed without OCR."
            )

        content_hash = cls.calculate_hash(content_bytes)

        title = metadata_override.get("title", filename.replace(".pdf", "")) if metadata_override else filename
        category = metadata_override.get("category", "general").lower() if metadata_override else "general"
        version = metadata_override.get("version", "1.0") if metadata_override else "1.0"
        region = metadata_override.get("region", "IN").upper() if metadata_override else "IN"
        effective_date = metadata_override.get("effective_date") if metadata_override else None

        # Build sections from pages
        sections = []
        for p in pages_data:
            sections.append({
                "section": f"Page {p['page_number']}",
                "content": p["text"],
                "page": p["page_number"]
            })

        return LoadedDocument(
            raw_text=joined_text,
            content_hash=content_hash,
            title=title,
            category=category,
            version=version,
            effective_date=effective_date,
            region=region,
            sections=sections,
            pages=pages_data
        )

    @classmethod
    def load_json(
        cls,
        content_bytes: bytes,
        filename: str,
        metadata_override: Optional[Dict[str, Any]] = None
    ) -> LoadedDocument:
        try:
            data = json.loads(content_bytes.decode("utf-8", errors="replace"))
        except Exception as e:
            raise DocumentLoaderError(f"Invalid JSON in file '{filename}': {str(e)}")

        if not isinstance(data, dict):
            raise DocumentLoaderError(f"JSON policy file must be an object at the root level.")

        content_hash = cls.calculate_hash(content_bytes)

        title = data.get("title") or (metadata_override.get("title") if metadata_override else filename)
        category = (data.get("category") or (metadata_override.get("category") if metadata_override else "general")).lower()
        version = str(data.get("version") or (metadata_override.get("version") if metadata_override else "1.0"))
        region = (data.get("region") or (metadata_override.get("region") if metadata_override else "IN")).upper()
        effective_date = data.get("effective_date") or (metadata_override.get("effective_date") if metadata_override else None)

        sections = []
        raw_parts = []
        if "sections" in data and isinstance(data["sections"], list):
            for s in data["sections"]:
                s_name = s.get("name") or s.get("section") or "General"
                s_content = s.get("content") or s.get("text") or ""
                sections.append({"section": s_name, "content": s_content, "page": s.get("page", 1)})
                raw_parts.append(f"## {s_name}\n{s_content}")
        else:
            # Fallback to key-value string
            text_rep = json.dumps(data, indent=2)
            sections.append({"section": "General", "content": text_rep, "page": 1})
            raw_parts.append(text_rep)

        joined_text = "\n\n".join(raw_parts)
        if not joined_text.strip():
            raise DocumentLoaderError(f"JSON document '{filename}' contained no policy content.")

        return LoadedDocument(
            raw_text=joined_text,
            content_hash=content_hash,
            title=title,
            category=category,
            version=version,
            effective_date=effective_date,
            region=region,
            sections=sections
        )
