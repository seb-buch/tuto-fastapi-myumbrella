"""Module for router that handles generic or default endpoints."""
from fastapi import APIRouter

from .. import APP_NAME, APP_VERSION

router = APIRouter(tags=["default"])


@router.get(
    "/",
    description="Welcome the user with a nice greeting message.",
    response_description="Greeting message",
    name="Root view",
)
async def view_root() -> str:
    """Return a greeting to the user."""
    return f"Welcome to {APP_NAME} v.{APP_VERSION}!"
