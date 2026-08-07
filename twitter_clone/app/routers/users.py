from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..dependencies import get_db_session

router = APIRouter()


def make_profile(user: models.User) -> schemas.ProfileResponse:
    return schemas.ProfileResponse(
        id=user.id,
        name=user.name,
        followers=[
            schemas.UserShortResponse(
                id=follow.follower.id,
                name=follow.follower.name,
            )
            for follow in user.followers
        ],
        following=[
            schemas.UserShortResponse(
                id=follow.following.id,
                name=follow.following.name,
            )
            for follow in user.following
        ],
    )


@router.get(
    "/me",
    response_model=schemas.UserResponse,
)
def get_my_profile(
    current_user: models.User = Depends(get_current_user),
) -> schemas.UserResponse:
    return schemas.UserResponse(
        result=True,
        user=make_profile(current_user),
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
    user = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return schemas.UserResponse(
        result=True,
        user=make_profile(user),
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
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot follow yourself",
        )

    target_user = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    existing_follow = (
        db.query(models.Follow)
        .filter(
            models.Follow.follower_id == current_user.id,
            models.Follow.following_id == user_id,
        )
        .first()
    )

    if existing_follow is not None:
        raise HTTPException(
            status_code=400,
            detail="Already following this user",
        )

    db.add(
        models.Follow(
            follower_id=current_user.id,
            following_id=user_id,
        )
    )
    db.commit()

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
    follow = (
        db.query(models.Follow)
        .filter(
            models.Follow.follower_id == current_user.id,
            models.Follow.following_id == user_id,
        )
        .first()
    )

    if follow is None:
        raise HTTPException(
            status_code=404,
            detail="Follow relationship not found",
        )

    db.delete(follow)
    db.commit()

    return schemas.OperationResponse(result=True)