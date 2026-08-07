from pydantic import BaseModel, ConfigDict, Field


class TweetCreate(BaseModel):
    tweet_data: str = Field(
        ...,
        min_length=1,
        max_length=280,
    )
    tweet_media_ids: list[int] = Field(default_factory=list)


class CreateTweetResponse(BaseModel):
    result: bool
    tweet_id: int


class OperationResponse(BaseModel):
    result: bool


class MediaResponse(BaseModel):
    result: bool
    media_id: int


class UserShortResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class LikeResponse(BaseModel):
    user_id: int
    name: str


class AttachmentResponse(BaseModel):
    id: int
    url: str


class TweetFeedResponse(BaseModel):
    id: int
    content: str
    attachments: list[str]
    author: UserShortResponse
    likes: list[LikeResponse]


class FeedResponse(BaseModel):
    result: bool
    tweets: list[TweetFeedResponse]


class ProfileResponse(BaseModel):
    id: int
    name: str
    followers: list[UserShortResponse]
    following: list[UserShortResponse]


class UserResponse(BaseModel):
    result: bool
    user: ProfileResponse


class ErrorResponse(BaseModel):
    result: bool = False
    error_type: str
    error_message: str