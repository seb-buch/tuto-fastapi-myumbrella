#!/usr/bin/env python3
"""Main script for the umbrella application."""
import asyncio
import logging

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from myumbrella.app import app
from myumbrella.dependencies import (
    DependencyNotInitializedException,
    umbrella_report_provider_dependency,
)
from myumbrella.openweather import (
    OpenweatherClient,
    load_openweather_api_key_from_env_variable,
)


def _dependency_exception_handler(
    _: Request, exc: DependencyNotInitializedException
) -> JSONResponse:
    response = JSONResponse(
        status_code=httpx.codes.INTERNAL_SERVER_ERROR, content={"detail": exc.args[0]}
    )

    return response


def setup_application(application: FastAPI) -> FastAPI:
    """Set up the application."""
    client = OpenweatherClient(api_key=load_openweather_api_key_from_env_variable())
    umbrella_report_provider_dependency.provider = client

    application.add_exception_handler(
        exc_class_or_status_code=DependencyNotInitializedException,
        handler=_dependency_exception_handler,
    )
    return application


async def main() -> None:  # pragma: nocover
    """Launch the umbrella app."""
    logging.basicConfig(level=logging.INFO)

    application = setup_application(application=app)

    config = uvicorn.Config(
        app=application, host="0.0.0.0", port=5000, log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":  # pragma: nocover
    asyncio.run(main=main())
