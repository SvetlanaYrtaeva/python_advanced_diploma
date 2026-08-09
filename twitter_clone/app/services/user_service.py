from sqlalchemy.orm import Session

from .. import models


def get_user(
    db: Session,
    user_id: int,
) -> models.User:
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        raise LookupError("User not found")

    return user


def follow_user(
    db: Session,
    current_user: models.User,
    user_id: int,
) -> None:
    if current_user.id == user_id:
        raise ValueError("You cannot follow yourself")

    get_user(db, user_id)

    existing_follow = (
        db.query(models.Follow)
        .filter(
            models.Follow.follower_id == current_user.id,
            models.Follow.following_id == user_id,
        )
        .first()
    )

    if existing_follow is not None:
        raise ValueError("Already following this user")

    db.add(
        models.Follow(
            follower_id=current_user.id,
            following_id=user_id,
        )
    )
    db.commit()


def unfollow_user(
    db: Session,
    current_user: models.User,
    user_id: int,
) -> None:
    follow = (
        db.query(models.Follow)
        .filter(
            models.Follow.follower_id == current_user.id,
            models.Follow.following_id == user_id,
        )
        .first()
    )

    if follow is None:
        raise LookupError("Follow relationship not found")

    db.delete(follow)
    db.commit()


def make_profile(user: models.User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "followers": [
            {
                "id": follow.follower.id,
                "name": follow.follower.name,
            }
            for follow in user.followers
        ],
        "following": [
            {
                "id": follow.following.id,
                "name": follow.following.name,
            }
            for follow in user.following
        ],
    }
