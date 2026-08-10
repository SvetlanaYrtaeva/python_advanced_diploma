from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from .. import models

MEDIA_DIR = Path("app/media")

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/avif",
}


def save_media(
    db: Session,
    file: UploadFile,
) -> models.Media:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Only image files are allowed")

    original_name = file.filename or "image"
    extension = Path(original_name).suffix.lower()

    stored_name = f"{uuid4().hex}{extension}"
    file_path = MEDIA_DIR / stored_name

    MEDIA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

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

    return media
