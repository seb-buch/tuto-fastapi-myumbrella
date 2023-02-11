"""Main module for the application."""
import logging

from fastapi import FastAPI

from . import APP_NAME, APP_VERSION
from .routers.default import router as router_default
from .routers.umbrella import router as router_umbrella

logger = logging.getLogger(__name__)

app = FastAPI(
    description="The API app that tells you if you need your umbrella!",
    version=APP_VERSION,
    title=APP_NAME,
)

app.include_router(router=router_default)
app.include_router(router=router_umbrella)
