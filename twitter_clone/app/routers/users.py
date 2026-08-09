from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..dependencies import get_db_session
from ..services import user_service

router = APIRouter()


@router.get(
    "/me",
    response_model=schemas.UserResponse,
)
def get_my_profile(
    current_user: models.User = Depends(get_current_user),
) -> schemas.UserResponse:
    profile = user_service.make_profile(current_user)

    return schemas.UserResponse(
        result=True,
        user=profile,
    )


@router.get(
    "/{user_id}",
    response_model=schemas.UserResponse,
)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> schemas.UserResponse:
    try:
        user = user_service.get_user(
            db=db,
            user_id=user_id,
        )
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    profile = user_service.make_profile(user)

    return schemas.UserResponse(
        result=True,
        user=profile,
    )


@router.post(
    "/{user_id}/follow",
    response_model=schemas.OperationResponse,
)
def follow_user(
    user_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> schemas.OperationResponse:
    try:
        user_service.follow_user(
            db=db,
            current_user=current_user,
            user_id=user_id,
        )
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return schemas.OperationResponse(result=True)


@router.delete(
    "/{user_id}/follow",
    response_model=schemas.OperationResponse,
)
def unfollow_user(
    user_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> schemas.OperationResponse:
    try:
        user_service.unfollow_user(
            db=db,
            current_user=current_user,
            user_id=user_id,
        )
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    return schemas.OperationResponse(result=True)
