"""Dependency to provide Stream Video client."""

from fastapi import Depends
from getstream import Stream

from src.config import Settings, settings


def get_stream_client(cfg: Settings = Depends(lambda: settings)) -> Stream:
    """
    Creates the server-side Stream Video client.
    """
    return Stream(
        api_key=cfg.stream_api_key,
        api_secret=cfg.stream_api_secret,
    )
