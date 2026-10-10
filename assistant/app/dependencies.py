from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db

def verify_admin_key(
    x_api_key: str = Header(None, alias="X-API-Key"),
    authorization: str = Header(None, alias="Authorization")
) -> bool:
    """
    Validates administrative access for ingestion and inspection endpoints.
    Accepts X-API-Key header or Authorization: Bearer <key>.
    """
    token = None
    if x_api_key:
        token = x_api_key
    elif authorization:
        parts = authorization.split(" ")
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
        else:
            token = authorization

    if not token or token != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Invalid or missing administrative credentials for knowledge management."
        )
    return True
