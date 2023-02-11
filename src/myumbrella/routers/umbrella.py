"""Module for the routing specific to the umbrella endpoint."""
import logging
import warnings

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..core import (
    LocationNotFoundException,
    UmbrellaReport,
    UmbrellaReportProvider,
    UnknownUmbrellaStateException,
)
from ..dependencies import umbrella_report_provider_dependency

router = APIRouter(tags=["umbrella"])
logger = logging.getLogger(__name__)


class MyUmbrellaResponse(BaseModel):
    """Response model for myumbrella endpoint."""

    city: str = "City"
    state: str = "State"
    country: str = "Country"
    weather: str = "Unknown"
    umbrella_needed: bool = True


async def _myumbrellaresponse_from_umbrella_report(
    report: UmbrellaReport,
) -> MyUmbrellaResponse:
    location = report.location

    try:
        umbrella_needed = report.umbrella_needed
    except UnknownUmbrellaStateException:
        msg = f"Unknown umbrella status for weather: {report.weather.value} -> set to True"

        warnings.warn(message=msg, category=RuntimeWarning)
        logger.warning(msg=msg)
        umbrella_needed = True

    return MyUmbrellaResponse(
        city=location.city,
        state=location.state,
        country=location.country,
        weather=report.weather.value,
        umbrella_needed=umbrella_needed,
    )


@router.get("/myumbrella", responses={404: {"description": "City not found"}})
async def view_umbrella(
    city: str,
    report_provider: UmbrellaReportProvider = Depends(
        umbrella_report_provider_dependency
    ),
) -> MyUmbrellaResponse:
    """Return the WeatherReport for a city."""
    logging.info("Getting Umbrella report for city: %s", city)
    try:
        report = report_provider.get_umbrella_report(city=city)
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=httpx.codes.GATEWAY_TIMEOUT, detail=exc.args[0]
        ) from exc
    except LocationNotFoundException as exc:
        raise HTTPException(
            status_code=httpx.codes.NOT_FOUND, detail=exc.args[0]
        ) from exc
    response = await _myumbrellaresponse_from_umbrella_report(report=report)
    return response
