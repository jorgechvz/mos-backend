"""Models for stream user requests and token responses."""

from pydantic import BaseModel, HttpUrl


class StreamUserRequest(BaseModel):
    """Model for stream user request."""

    user_id: str
    name: str | None = None
    image: HttpUrl | None = None
    role: str = "user"


class StreamTokenResponse(BaseModel):
    """Model for stream token response."""

    user_id: str
    token: str
    expires_in: int
    obtained_at: int


class MosRequest(BaseModel):
    """ Model for MOS evaluation request. """
    recording_url: str
    reference_filename: str = "reference.mp3"
