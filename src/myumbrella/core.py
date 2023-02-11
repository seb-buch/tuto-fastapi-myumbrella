"""Domain entities and logics for myapp."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


@dataclass()
class Location:
    """Describes a location."""

    city: str = "City"
    state: str = "State"
    country: str = "Country"
    latitude: float = 0.0
    longitude: float = 0.0


class WeatherState(Enum):
    """Stores the different weather states."""

    UNKNOWN = "Unknown"
    THUNDERSTORM = "Thunderstorm"
    DRIZZLE = "Drizzle"
    RAIN = "Rain"
    SNOW = "Snow"
    FOG = "Fog"
    CLEAR = "Clear"
    CLOUDS = "Clouds"


class UnknownUmbrellaStateException(ValueError):
    """Exception raised when umbrella state cannot be assessed."""


class LocationNotFoundException(ValueError):
    """Exception raised when e.g. OpenWeather Geocoding API returns nothing or fails."""


_NO_UMBRELLA_WEATHERS = [WeatherState.CLEAR, WeatherState.CLOUDS, WeatherState.FOG]


@dataclass()
class UmbrellaReport:
    """Stores an umbrella report."""

    location: Location = field(default_factory=Location)
    weather: WeatherState = WeatherState.UNKNOWN

    @property
    def umbrella_needed(self) -> bool:
        """Check if an umbrella is needed."""
        if self.weather == WeatherState.UNKNOWN:
            raise UnknownUmbrellaStateException(
                f"Cannot assess the need for an umbrella from condition '{self.weather}'"
            )

        if self.weather in _NO_UMBRELLA_WEATHERS:
            return False

        return True


class UmbrellaReportProvider(Protocol):
    """Interface for Classes that provides UmbrellaReport."""

    def get_umbrella_report(self, city: str) -> UmbrellaReport:  # pragma: nocover
        """Retrieve the umbrella report for a city."""
        ...  # pylint: disable=unnecessary-ellipsis
