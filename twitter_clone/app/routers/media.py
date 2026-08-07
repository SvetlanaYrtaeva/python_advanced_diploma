from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from .. import models
from ..auth import get_current_user
from ..dependencies import get_db_session

router = APIRouter()

MEDIA_DIR = Path("app/media")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


@router.post("")
def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> dict:
    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
    }

    if file.content_type not in allowed_types:
        return {
            "result": False,
            "error_type": "ValidationError",
            "error_message": "Only image files are allowed",
        }

    original_name = file.filename or "image"
    extension = Path(original_name).suffix
    stored_name = f"{uuid4().hex}{extension}"
    file_path = MEDIA_DIR / stored_name

    with file_path.open("wb") as output:
        output.write(file.file.read())

    media = models.Media(
        filename=stored_name,
        file_path=str(file_path),
        content_type=file.content_type,
    )

    db.add(media)
    db.commit()
    db.refresh(media)

    return {
        "result": True,
        "media_id": media.id,
    }