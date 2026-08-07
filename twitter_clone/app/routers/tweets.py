from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from .. import models, schemas
from ..auth import get_current_user
from ..dependencies import get_db_session

router = APIRouter()


@router.post(
    "",
    response_model=schemas.CreateTweetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_tweet(
    payload: schemas.TweetCreate,
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> schemas.CreateTweetResponse:
    media_objects = []

    if payload.tweet_media_ids:
        unique_media_ids = set(payload.tweet_media_ids)

        media_objects = (
            db.query(models.Media)
            .filter(models.Media.id.in_(unique_media_ids))
            .all()
        )

        if len(media_objects) != len(unique_media_ids):
            raise HTTPException(
                status_code=400,
                detail="One or more media files do not exist",
            )

    tweet = models.Tweet(
        tweet_data=payload.tweet_data,
        user_id=current_user.id,
        media=media_objects,
    )

    db.add(tweet)
    db.commit()
    db.refresh(tweet)

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
    tweet = (
        db.query(models.Tweet)
        .filter(models.Tweet.id == tweet_id)
        .first()
    )

    if tweet is None:
        raise HTTPException(
            status_code=404,
            detail="Tweet not found",
        )

    if tweet.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can delete only your own tweet",
        )

    db.delete(tweet)
    db.commit()

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
    tweet = (
        db.query(models.Tweet)
        .filter(models.Tweet.id == tweet_id)
        .first()
    )

    if tweet is None:
        raise HTTPException(
            status_code=404,
            detail="Tweet not found",
        )

    existing_like = (
        db.query(models.Like)
        .filter(
            models.Like.tweet_id == tweet_id,
            models.Like.user_id == current_user.id,
        )
        .first()
    )

    if existing_like is not None:
        raise HTTPException(
            status_code=400,
            detail="Tweet already liked",
        )

    db.add(
        models.Like(
            tweet_id=tweet_id,
            user_id=current_user.id,
        )
    )
    db.commit()

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
    like = (
        db.query(models.Like)
        .filter(
            models.Like.tweet_id == tweet_id,
            models.Like.user_id == current_user.id,
        )
        .first()
    )

    if like is None:
        raise HTTPException(
            status_code=404,
            detail="Like not found",
        )

    db.delete(like)
    db.commit()

    return schemas.OperationResponse(result=True)


@router.get(
    "",
    response_model=schemas.FeedResponse,
)
def get_feed(
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(get_current_user),
) -> schemas.FeedResponse:
    following_ids_query = (
        db.query(models.Follow.following_id)
        .filter(models.Follow.follower_id == current_user.id)
    )

    tweets_with_likes = (
        db.query(
            models.Tweet,
            func.count(models.Like.id).label("likes_count"),
        )
        .outerjoin(
            models.Like,
            models.Like.tweet_id == models.Tweet.id,
        )
        .filter(models.Tweet.user_id.in_(following_ids_query))
        .group_by(models.Tweet.id)
        .order_by(
            func.count(models.Like.id).desc(),
            models.Tweet.created_at.desc(),
        )
        .all()
    )

    result = []

    for tweet, _likes_count in tweets_with_likes:
        likes = [
            {
                "user_id": like.user_id,
                "name": like.user.name,
            }
            for like in tweet.likes
        ]

        attachments = [
            f"/media/{media.filename}"
            for media in tweet.media
        ]

        result.append(
            schemas.TweetFeedResponse(
                id=tweet.id,
                content=tweet.tweet_data,
                attachments=attachments,
                author=schemas.UserShortResponse(
                    id=tweet.author.id,
                    name=tweet.author.name,
                ),
                likes=likes,
            )
        )

    return schemas.FeedResponse(
        result=True,
        tweets=result,
    )