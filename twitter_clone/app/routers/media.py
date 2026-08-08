from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..dependencies import get_db_session
from ..services import media_service

router = APIRouter()


@router.post(
    "",
    response_model=schemas.MediaResponse,
    status_code=201,
)
def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> schemas.MediaResponse:
    try:
        media = media_service.save_media(
            db=db,
            file=file,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return schemas.MediaResponse(
        result=True,
        media_id=media.id,
    )
