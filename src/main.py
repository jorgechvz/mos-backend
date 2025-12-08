"""Main application entry point for the FastAPI server."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.v1 import health_router, stream_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # NOTE: Adjust for production use
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health_router,
    prefix="/health",
)
app.include_router(
    stream_router,
    prefix="/stream",
)
