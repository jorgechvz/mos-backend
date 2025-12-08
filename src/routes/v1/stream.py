"""Stream Video related routes."""

import time
from fastapi import APIRouter, Depends, HTTPException, status
from getstream.models import UserRequest

from src.models import StreamUserRequest, StreamTokenResponse
from src.dependencies.stream_dep import get_stream_client
from src.config import settings

router = APIRouter(tags=["stream"])


@router.post("/token", response_model=StreamTokenResponse)
def create_stream_user_token(
    payload: StreamUserRequest,
    client=Depends(get_stream_client),
):
    """
    Generates a Stream Video user token.
    Ensures the user exists, then creates a signed JWT.
    """

    try:
        user_req = UserRequest(
            id=payload.user_id,
            name=payload.name,
            role=payload.role,
            image=str(payload.image) if payload.image else None,
            custom={},
        )
        client.upsert_users(user_req)

        ttl = settings.stream_token_seconds * 24
        token = client.create_token(payload.user_id, expiration=ttl)
        obtained_at = int(time.time())

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating Stream user token",
        ) from exc

    return StreamTokenResponse(
        user_id=payload.user_id,
        token=token,
        expires_in=ttl,
        obtained_at=obtained_at,
    )
