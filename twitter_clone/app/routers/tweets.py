from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..dependencies import get_db_session
from ..services import tweet_service

router = APIRouter()


@router.post(
    "",
    response_model=schemas.CreateTweetResponse,
    status_code=201,
)
def create_tweet(
    payload: schemas.TweetCreate,
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> schemas.CreateTweetResponse:
    try:
        tweet = tweet_service.create_tweet(
            db=db,
            user=current_user,
            tweet_data=payload.tweet_data,
            media_ids=payload.tweet_media_ids,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return schemas.CreateTweetResponse(
        result=True,
        tweet_id=tweet.id,
    )


@router.delete(
    "/{tweet_id}",
    response_model=schemas.OperationResponse,
)
def delete_tweet(
    tweet_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> schemas.OperationResponse:
    try:
        tweet_service.delete_tweet(
            db=db,
            tweet_id=tweet_id,
            user=current_user,
        )
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except PermissionError as error:
        raise HTTPException(
            status_code=403,
            detail=str(error),
        ) from error

    return schemas.OperationResponse(result=True)


@router.post(
    "/{tweet_id}/likes",
    response_model=schemas.OperationResponse,
)
def like_tweet(
    tweet_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> schemas.OperationResponse:
    try:
        tweet_service.like_tweet(
            db=db,
            tweet_id=tweet_id,
            user=current_user,
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
    "/{tweet_id}/likes",
    response_model=schemas.OperationResponse,
)
def unlike_tweet(
    tweet_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> schemas.OperationResponse:
    try:
        tweet_service.unlike_tweet(
            db=db,
            tweet_id=tweet_id,
            user=current_user,
        )
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    return schemas.OperationResponse(result=True)


@router.get(
    "",
    response_model=schemas.FeedResponse,
)
def get_feed(
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> schemas.FeedResponse:
    tweets = tweet_service.get_feed(
        db=db,
        user=current_user,
    )

    result = []

    for tweet in tweets:
        result.append(
            schemas.TweetFeedResponse(
                id=tweet.id,
                content=tweet.tweet_data,
                attachments=[f"/media/{media.filename}" for media in tweet.media],
                author=schemas.UserShortResponse(
                    id=tweet.author.id,
                    name=tweet.author.name,
                ),
                likes=[
                    schemas.LikeResponse(
                        user_id=like.user_id,
                        name=like.user.name,
                    )
                    for like in tweet.likes
                ],
            )
        )

    return schemas.FeedResponse(
        result=True,
        tweets=result,
    )
