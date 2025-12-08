"""Health check routes for the API."""

from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/",
    tags=["Health"],
    summary="Health Check Endpoint",
    description="Endpoint to check the health status of the API.",
    response_description="Health status of the API.",
)
async def health_check():
    """Health check endpoint to verify that the API is running."""
    return {"status": "healthy"}
