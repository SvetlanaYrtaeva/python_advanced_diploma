from sqlalchemy.orm import Session

from . import models


def seed_users(db: Session) -> None:
    users = [
        models.User(
            name="Alice",
            api_key="alice-key",
        ),
        models.User(
            name="Bob",
            api_key="bob-key",
        ),
        models.User(
            name="Charlie",
            api_key="charlie-key",
        ),
    ]

    for user in users:
        existing_user = (
            db.query(models.User)
            .filter(models.User.api_key == user.api_key)
            .first()
        )

        if existing_user is None:
            db.add(user)

    db.commit()