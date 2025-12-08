"""Routes for v1 API."""

from .health import router as health_router
from .stream import router as stream_router

__all__ = ["health_router", "stream_router"]
