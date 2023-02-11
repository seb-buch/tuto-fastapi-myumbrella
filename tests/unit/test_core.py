"""Tests related to the domain core."""
import pytest

from myumbrella.core import UmbrellaReport, UnknownUmbrellaStateException, WeatherState


@pytest.mark.parametrize(
    argnames="good_weather",
    argvalues=[WeatherState.CLEAR, WeatherState.CLOUDS, WeatherState.FOG],
)
def test_weatherreport_should_assess_good_weather(good_weather: WeatherState) -> None:
    """Check that the weather report successfully assess when an umbrella is not needed"""

    # Given a weather report with a good weather
    report = UmbrellaReport(weather=good_weather)

    # When assessing if the umbrella is needed
    umbrella_needed = report.umbrella_needed

    # Then the results should be that an umbrella is not needed
    assert umbrella_needed is False


@pytest.mark.parametrize(
    argnames="bad_weather",
    argvalues=[
        WeatherState.THUNDERSTORM,
        WeatherState.RAIN,
        WeatherState.SNOW,
        WeatherState.DRIZZLE,
    ],
)
def test_weatherreport_should_assess_bad_weather(bad_weather: WeatherState) -> None:
    """Check that the weather report successfully assess when an umbrella is needed"""

    # Given a weather report with a bad weather
    report = UmbrellaReport(weather=bad_weather)

    # When assessing if the umbrella is needed
    umbrella_needed = report.umbrella_needed

    # Then the results should be that an umbrella is needed
    assert umbrella_needed is True


def test_weatherreport_should_raise_on_unknown_conditions() -> None:
    """Check that weather report raises an exception when
    the need for an umbrella cannot be assessed."""

    # Given a weather report with unknown weather
    report = UmbrellaReport(weather=WeatherState.UNKNOWN)

    # When assessing the need for an umbrella
    # Then an exception should be raised
    with pytest.raises(UnknownUmbrellaStateException):
        _ = report.umbrella_needed
