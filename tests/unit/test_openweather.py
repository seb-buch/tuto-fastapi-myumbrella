"""Tests in relation with the Openwather API client"""
import os
import random
import string
import tempfile
from typing import Any

import pytest

from myumbrella.core import Location, UmbrellaReport, WeatherState
from myumbrella.openweather import (
    LocationNotFoundException,
    NoAPIKeyAvailableException,
    OpenweatherClient,
    convert_openweather_code_to_weatherstate,
    load_openweather_api_key_from_env_variable,
)


def _create_mocked_client(api_responses: dict[str, list]) -> OpenweatherClient:
    class _MockedClient(OpenweatherClient):
        def __init__(
            self,
            api_responses: dict[str, list] | None = None,
        ) -> None:
            super().__init__(api_key="testapikey")
            if api_responses is None:
                api_responses = {}
            self.api_responses = api_responses

        def _call_rest_api(self, endpoint: str, params: dict) -> Any:
            reponses = self.api_responses.get(endpoint, None)
            if reponses is None:
                raise RuntimeError(f"Unmocked API call to '{endpoint}'")

            try:
                response = reponses.pop(0)
            except IndexError as exc:
                raise RuntimeError(f"Exhausted responses for '{endpoint}'") from exc

            return response

    client = _MockedClient(
        api_responses=api_responses,
    )

    return client


class TestLoadAPIKEY:
    """Check the Openweather API key loading mecanisms.

    This class is just there to aggregate all the tests related to API key loading."""

    _EXPECTED_API_KEY = "1234abc"

    @staticmethod
    def _create_unexisting_env_varname() -> str:
        letters = string.ascii_lowercase

        var_name = "test_env_variable_"
        while var_name in os.environ:
            var_name += random.choice(letters)

        return var_name

    def _create_new_env_variable_from_value(self, value: str) -> str:
        var_name = self._create_unexisting_env_varname()
        os.environ[var_name] = value
        return var_name

    def _create_new_file_env_variable_from_content(self, content: str) -> str:
        _, tmpfile_path = tempfile.mkstemp(text=True)

        with open(tmpfile_path, "w", encoding="utf-8") as file_pointer:
            file_pointer.write(content)

        var_name = self._create_new_env_variable_from_value(value=tmpfile_path)

        return var_name

    @staticmethod
    def _teardown_env_variable(env_var_name: str) -> None:
        del os.environ[env_var_name]

    def _teardown_file_env_variable(self, env_var_name: str) -> None:
        tmp_file_path = os.environ[env_var_name]

        os.remove(tmp_file_path)

        self._teardown_env_variable(env_var_name=env_var_name)

    def test_loadapikey_should_work_with_raw_key(self) -> None:
        """Check loading API key from raw environment variable."""
        # Given a environment variable that contains an API key
        env_var_name = self._create_new_env_variable_from_value(
            value=self._EXPECTED_API_KEY
        )

        # When load the api key
        api_key = load_openweather_api_key_from_env_variable(env_var_name=env_var_name)

        # Test teardown before assertion that may fail
        self._teardown_env_variable(env_var_name)

        # Then the expected API key should be loaded
        assert api_key == self._EXPECTED_API_KEY

    def test_loadapikey_should_work_with_file_env_variable(self) -> None:
        """Check loading API key from a file which path is from an environment variable."""
        # Given a environment variable that contains an API key
        env_var_name = self._create_new_file_env_variable_from_content(
            content=self._EXPECTED_API_KEY
        )

        # When load the api key
        api_key = load_openweather_api_key_from_env_variable(env_var_name=env_var_name)

        # Test teardown before assertion that may fail
        self._teardown_file_env_variable(env_var_name=env_var_name)

        # Then the expected API key should be loaded
        assert api_key == self._EXPECTED_API_KEY

    def test_loadapikey_should_raise_if_env_variable_is_not_set(self) -> None:
        """Check that loading API key fails when the environment variable does not exist."""
        # Given an environment that does not exist
        env_var_name = self._create_unexisting_env_varname()

        # When trying to load the API key from that env variable
        # Then it should fail with the proper exception
        with pytest.raises(NoAPIKeyAvailableException):
            _ = load_openweather_api_key_from_env_variable(env_var_name=env_var_name)


@pytest.mark.parametrize(
    argnames="code, expected_state",
    argvalues=[
        (200, WeatherState.THUNDERSTORM),
        (201, WeatherState.THUNDERSTORM),
        (202, WeatherState.THUNDERSTORM),
        (210, WeatherState.THUNDERSTORM),
        (211, WeatherState.THUNDERSTORM),
        (212, WeatherState.THUNDERSTORM),
        (221, WeatherState.THUNDERSTORM),
        (230, WeatherState.THUNDERSTORM),
        (231, WeatherState.THUNDERSTORM),
        (232, WeatherState.THUNDERSTORM),
        (300, WeatherState.DRIZZLE),
        (301, WeatherState.DRIZZLE),
        (302, WeatherState.DRIZZLE),
        (310, WeatherState.DRIZZLE),
        (311, WeatherState.DRIZZLE),
        (312, WeatherState.DRIZZLE),
        (313, WeatherState.DRIZZLE),
        (314, WeatherState.DRIZZLE),
        (321, WeatherState.DRIZZLE),
        (500, WeatherState.RAIN),
        (501, WeatherState.RAIN),
        (502, WeatherState.RAIN),
        (503, WeatherState.RAIN),
        (504, WeatherState.RAIN),
        (511, WeatherState.RAIN),
        (520, WeatherState.RAIN),
        (521, WeatherState.RAIN),
        (522, WeatherState.RAIN),
        (531, WeatherState.RAIN),
        (600, WeatherState.SNOW),
        (601, WeatherState.SNOW),
        (602, WeatherState.SNOW),
        (611, WeatherState.SNOW),
        (612, WeatherState.SNOW),
        (613, WeatherState.SNOW),
        (615, WeatherState.SNOW),
        (616, WeatherState.SNOW),
        (620, WeatherState.SNOW),
        (621, WeatherState.SNOW),
        (622, WeatherState.SNOW),
        (701, WeatherState.UNKNOWN),
        (711, WeatherState.UNKNOWN),
        (721, WeatherState.UNKNOWN),
        (731, WeatherState.UNKNOWN),
        (741, WeatherState.FOG),
        (751, WeatherState.UNKNOWN),
        (761, WeatherState.UNKNOWN),
        (762, WeatherState.UNKNOWN),
        (771, WeatherState.UNKNOWN),
        (781, WeatherState.UNKNOWN),
        (800, WeatherState.CLEAR),
        (801, WeatherState.CLOUDS),
        (802, WeatherState.CLOUDS),
        (803, WeatherState.CLOUDS),
        (804, WeatherState.CLOUDS),
    ],
)
def test_convert_code_to_state_should_handle_all_codes(
    code: int, expected_state: WeatherState
) -> None:
    """Check that the helper function convert_code_to_state handles all possible codes.

    See https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2 for all codes.
    """

    # Given a openweather condition code
    # When it is converted to a WeatherState
    # Then the resulting WeatherState should be correct
    assert convert_openweather_code_to_weatherstate(code=code) == expected_state


def test_openweatherclient_should_retrieve_report_when_ok() -> None:
    """Check that the openweatherclient successfully build a weather report
    when everything is working as intented."""

    # Test setup
    expected_location = Location(
        city="Toulouse",
        state="Occitania",
        country="FR",
        longitude=1.4442469,
        latitude=43.6044622,
    )
    expected_report = UmbrellaReport(
        location=expected_location, weather=WeatherState.CLEAR
    )
    api_responses: dict[str, list] = {
        "geo/1.0/direct": [
            [
                {
                    "name": expected_location.city,
                    "lat": expected_location.latitude,
                    "lon": expected_location.longitude,
                    "country": expected_location.country,
                    "state": expected_location.state,
                }
            ],
        ],
        "data/2.5/weather": [
            {
                "coord": {
                    "lon": expected_location.longitude,
                    "lat": expected_location.latitude,
                },
                "weather": [{"id": 800}],
                "main": {"temp": 298.15, "feels_like": 295.5},
                "name": expected_location.city,
            },
        ],
    }

    # Given a Openweather client
    client = _create_mocked_client(api_responses=api_responses)

    # When retrieving a report that is expected to be retrievable
    report = client.get_umbrella_report(expected_location.city)

    # Then the report should be the one expected
    assert report == expected_report


@pytest.mark.parametrize(
    argnames="error_obj",
    argvalues=[
        [],
        {"cod": "400", "message": "Nothing to geocode"},
    ],
)
def test_openweatherclient_should_raise_when_openweather_returns_nothing(
    error_obj: Any,
) -> None:
    """Check that an exception is raised when openweather returns an error or nothing."""

    # Test setup
    api_responses: dict[str, list] = {
        "geo/1.0/direct": [
            error_obj,
        ],
    }

    # Given a Openweather client
    client = _create_mocked_client(api_responses=api_responses)

    # When trying to get report
    # Then an exception should be raised
    with pytest.raises(LocationNotFoundException):
        client.get_umbrella_report(city="test")
