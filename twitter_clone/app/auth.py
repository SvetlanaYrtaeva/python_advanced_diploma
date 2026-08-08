from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from . import models
from .dependencies import get_db_session

def get_current_user(
    api_key: str | None = Header(
        default=None,
        alias="api-key",
    ),
    db: Session = Depends(get_db_session),
) -> models.User:
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="api-key header is required",
        )

    user = (
        db.query(models.User)
        .filter(models.User.api_key == api_key)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid api-key",
        )

    return user