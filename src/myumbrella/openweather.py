"""Module for the Openweather API Client."""
import logging
import os
from pathlib import Path
from typing import Any

import httpx

from .core import Location, LocationNotFoundException, UmbrellaReport, WeatherState

logger = logging.getLogger(__name__)

# Constants
OPENWEATHER_HOST = "https://api.openweathermap.org"
# See https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
_OPENWEATHER_CATEGORY_TO_WEATHERSTATE = {
    "2": WeatherState.THUNDERSTORM,
    "3": WeatherState.DRIZZLE,
    "5": WeatherState.RAIN,
    "6": WeatherState.SNOW,
    "8": WeatherState.CLOUDS,
}
_OPENWEATHER_CODE_TO_WEATHERSTATE = {800: WeatherState.CLEAR, 741: WeatherState.FOG}


class NoAPIKeyAvailableException(IOError):
    """Exception raised when no API key can be loaded."""


def load_openweather_api_key_from_env_variable(
    env_var_name: str = "OPENWEATHER_API_KEY",
) -> str:
    """Load Openweather's API key from an environment variable.

    This environment variable can contain either:
        1. the actual API key
    or
        2. the path to the file where the API key is stored
    """
    logger.info(
        "Loading Openweather API key using environment variable '%s'", env_var_name
    )
    try:
        env_var_value = os.environ[env_var_name]
    except KeyError as exc:
        raise NoAPIKeyAvailableException(
            f"Impossible to load API key: '{env_var_name}' env variable is not set"
        ) from exc

    env_var_as_path = Path(env_var_value)
    if env_var_as_path.is_file():
        logger.info("Loading Openweather API key from file '%s'", env_var_as_path)
        env_var_value = env_var_as_path.read_text(encoding="utf-8").strip()
    return env_var_value


def convert_openweather_code_to_weatherstate(code: int) -> WeatherState:
    """Convert an Openweather Condition code to a WeatherState.

    Details: https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2.
    """
    try:
        return _OPENWEATHER_CODE_TO_WEATHERSTATE[code]
    except KeyError:
        pass

    code_category = str(code)[0]

    try:
        return _OPENWEATHER_CATEGORY_TO_WEATHERSTATE[code_category]
    except KeyError:
        pass

    return WeatherState.UNKNOWN


class OpenweatherClient:
    """Main class to handle communication with the Openweather API."""

    def __init__(self, api_key: str, openweather_host: str = OPENWEATHER_HOST) -> None:
        """Initialize an OpenweatherClient based on a optionnally specified configuration."""
        self.host = openweather_host
        self.api_key = api_key

    def _call_rest_api(self, endpoint: str, params: dict) -> Any:
        url = f"{self.host}/{endpoint}"
        api_params = params.copy()
        api_params["appid"] = self.api_key

        api_response = httpx.get(url=url, params=api_params)
        return api_response.json()

    def _get_location_from_description(self, description: str) -> Location:
        logger.info("Calling Openweather geocoding API for '%s'", description)
        api_response: list[dict[str, str | float | dict]] = self._call_rest_api(
            endpoint="geo/1.0/direct", params={"q": description}
        )

        try:
            location_json = api_response[0]
        except (IndexError, KeyError) as exc:
            msg = f"Location '{description}' is unknown to Openweather Geocoding API!"
            logger.error(msg)
            raise LocationNotFoundException(msg) from exc

        city = str(location_json.get("name", "city"))
        state = str(location_json.get("state", "state"))
        country = str(location_json.get("country", "country"))
        latitude = float(location_json.get("lat", 0.0))  # type: ignore
        longitude = float(location_json.get("lon", 0.0))  # type: ignore

        location = Location(
            city=city,
            state=state,
            country=country,
            longitude=longitude,
            latitude=latitude,
        )
        logger.info(
            "Returned by Openweather: City=%s, State=%s, Country=%s, Lat=%.3f, Lon=%.3f",
            city,
            state,
            country,
            latitude,
            longitude,
        )
        return location

    def _get_weather_code_for_location(self, location: Location) -> int:
        logger.info(
            "Calling Openweather weather API for latitude=%.3f and longitude=%.3f",
            location.latitude,
            location.longitude,
        )
        weather_response = self._call_rest_api(
            "data/2.5/weather",
            params={"lat": location.latitude, "lon": location.longitude},
        )
        weather = weather_response.get("weather")[0]
        weather_code = int(weather["id"])
        logger.info(
            "Returned weather: %s (code: %i)",
            weather.get("description", "no description"),
            weather_code,
        )

        return weather_code

    def get_umbrella_report(self, city: str) -> UmbrellaReport:
        """Call Openweather API for a location and build a weather report."""
        location = self._get_location_from_description(description=city)

        weather_code = self._get_weather_code_for_location(location)

        weatherstate = convert_openweather_code_to_weatherstate(code=weather_code)

        return UmbrellaReport(location=location, weather=weatherstate)
