from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models


def create_tweet(
    db: Session,
    user: models.User,
    tweet_data: str,
    media_ids: list[int],
) -> models.Tweet:
    media_objects = []

    if media_ids:
        unique_media_ids = set(media_ids)

        media_objects = (
            db.query(models.Media).filter(models.Media.id.in_(unique_media_ids)).all()
        )

        if len(media_objects) != len(unique_media_ids):
            raise ValueError("One or more media files do not exist")

    tweet = models.Tweet(
        tweet_data=tweet_data,
        user_id=user.id,
        media=media_objects,
    )

    db.add(tweet)
    db.commit()
    db.refresh(tweet)

    return tweet


def get_tweet(
    db: Session,
    tweet_id: int,
) -> models.Tweet:
    tweet = db.query(models.Tweet).filter(models.Tweet.id == tweet_id).first()

    if tweet is None:
        raise LookupError("Tweet not found")

    return tweet


def delete_tweet(
    db: Session,
    tweet_id: int,
    user: models.User,
) -> None:
    tweet = get_tweet(db, tweet_id)

    if tweet.user_id != user.id:
        raise PermissionError(
            "You can delete only your own tweet",
        )

    db.delete(tweet)
    db.commit()


def like_tweet(
    db: Session,
    tweet_id: int,
    user: models.User,
) -> None:
    get_tweet(db, tweet_id)

    existing_like = (
        db.query(models.Like)
        .filter(
            models.Like.tweet_id == tweet_id,
            models.Like.user_id == user.id,
        )
        .first()
    )

    if existing_like is not None:
        raise ValueError("Tweet already liked")

    db.add(
        models.Like(
            tweet_id=tweet_id,
            user_id=user.id,
        )
    )
    db.commit()


def unlike_tweet(
    db: Session,
    tweet_id: int,
    user: models.User,
) -> None:
    like = (
        db.query(models.Like)
        .filter(
            models.Like.tweet_id == tweet_id,
            models.Like.user_id == user.id,
        )
        .first()
    )

    if like is None:
        raise LookupError("Like not found")

    db.delete(like)
    db.commit()


def get_feed(
    db: Session,
    user: models.User,
) -> list[models.Tweet]:
    following_ids = select(
        models.Follow.following_id,
    ).where(
        models.Follow.follower_id == user.id,
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
        .filter(models.Tweet.user_id.in_(following_ids))
        .group_by(models.Tweet.id)
        .order_by(
            func.count(models.Like.id).desc(),
            models.Tweet.created_at.desc(),
        )
        .all()
    )

    return [tweet for tweet, _likes_count in tweets_with_likes]
