from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from .database import Base

tweet_media = Table(
    "tweet_media",
    Base.metadata,
    Column(
        "tweet_id",
        ForeignKey("tweets.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "media_id",
        ForeignKey("media.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    api_key = Column(String(100), unique=True, nullable=False, index=True)

    tweets = relationship(
        "Tweet",
        back_populates="author",
        cascade="all, delete-orphan",
    )

    likes = relationship(
        "Like",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    followers = relationship(
        "Follow",
        foreign_keys="Follow.following_id",
        back_populates="following",
        cascade="all, delete-orphan",
    )

    following = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
    )


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, index=True)
    tweet_data = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    author = relationship("User", back_populates="tweets")

    likes = relationship(
        "Like",
        back_populates="tweet",
        cascade="all, delete-orphan",
    )

    media = relationship(
        "Media",
        secondary=tweet_media,
        back_populates="tweets",
    )


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    content_type = Column(String(100), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    tweets = relationship(
        "Tweet",
        secondary=tweet_media,
        back_populates="media",
    )


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "tweet_id",
            name="uq_like_user_tweet",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tweet_id = Column(Integer, ForeignKey("tweets.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="likes")
    tweet = relationship("Tweet", back_populates="likes")


class Follow(Base):
    __tablename__ = "follows"
    __table_args__ = (
        UniqueConstraint(
            "follower_id",
            "following_id",
            name="uq_follower_following",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    follower = relationship(
        "User",
        foreign_keys=[follower_id],
        back_populates="following",
    )

    following = relationship(
        "User",
        foreign_keys=[following_id],
        back_populates="followers",
    )
