"""Tests for the main module."""
import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from myumbrella.app import app
from myumbrella.core import (
    Location,
    LocationNotFoundException,
    UmbrellaReport,
    WeatherState,
)
from myumbrella.dependencies import umbrella_report_provider_dependency
from myumbrella.routers.umbrella import MyUmbrellaResponse, UmbrellaReportProvider


class TestApp:
    """Class used to aggregate the tests for the umbrella app."""

    _app: FastAPI

    @property
    def app(self) -> FastAPI:
        """Return the application that is under test."""
        try:
            return self._app
        except AttributeError:
            self._app = app
        return self._app

    def _get_client(self) -> TestClient:
        client = TestClient(app=self.app)
        return client

    @staticmethod
    def _create_mocked_provider_from_reports(
        reports: list[UmbrellaReport],
    ) -> UmbrellaReportProvider:
        class _FakeUmbrellaProvider:
            def __init__(self, reports: list[UmbrellaReport]) -> None:
                self.reports = {report.location.city: report for report in reports}

            def get_umbrella_report(self, city: str) -> UmbrellaReport:
                """Get a test report."""
                return self.reports[city]

        return _FakeUmbrellaProvider(reports=reports)

    @staticmethod
    def _create_mocked_provider_from_exception(
        exception: Exception,
    ) -> UmbrellaReportProvider:
        class _FailingProvider:
            def get_umbrella_report(self, city: str) -> UmbrellaReport:
                """Will fail"""
                raise exception

        return _FailingProvider()

    def test_root_view_should_welcome_with_app_name(self) -> None:
        """Check that calling root returns a greeting that contains the app name."""
        # Given a app client
        client = self._get_client()

        # When calling the "/" entry point
        response = client.get("/")

        # Then the response should return OK
        assert response.status_code == httpx.codes.OK

        # And the return message should contain the app name
        assert app.title in response.text

    def test_root_view_should_welcome_with_app_version(self) -> None:
        """Check that calling root returns a greeting that contains the app version."""
        # Given a app client
        client = self._get_client()

        # When calling the "/" entry point
        response = client.get("/")

        # Then the response should return OK
        assert response.status_code == httpx.codes.OK

        # And the return message should contain the app version
        assert app.version in response.text

    def test_myumbrella_view_should_return_report_ok(self) -> None:
        """Check that the umbrella view returns the correct response when everything is OK."""
        # Test setup
        expected_weather = WeatherState.CLEAR
        expected_report = MyUmbrellaResponse(
            city="testcity",
            state="teststate",
            country="testcountry",
            weather=expected_weather.value,
            umbrella_needed=False,
        )
        fake_report = UmbrellaReport(
            location=Location(
                city=expected_report.city,
                state=expected_report.state,
                country=expected_report.country,
            ),
            weather=expected_weather,
        )
        mocked_report_provider = self._create_mocked_provider_from_reports(
            reports=[fake_report]
        )
        umbrella_report_provider_dependency.provider = mocked_report_provider

        # Given a app client
        client = self._get_client()

        # When calling the "/" entry point
        response = client.get(f"/myumbrella?city={expected_report.city}")

        # Then the response should return OK
        assert response.status_code == httpx.codes.OK

        # And the returned json should be a dict
        report_dict = response.json()
        assert isinstance(report_dict, dict)

        # And the returned json should match the expected report
        report = MyUmbrellaResponse(**report_dict)
        assert report == expected_report

        # Test teardown
        del umbrella_report_provider_dependency.provider

    def test_myumbrella_view_should_handle_timeout(self) -> None:
        """Check that the view returns a valid error when openweather times out."""
        # Test setup
        expected_expection = httpx.TimeoutException("OpenWeather API is unreachable")
        expected_http_code = httpx.codes.GATEWAY_TIMEOUT
        failing_provider = self._create_mocked_provider_from_exception(
            exception=expected_expection
        )
        umbrella_report_provider_dependency.provider = failing_provider

        # Given a app client
        client = self._get_client()

        # When calling the "/" entry point
        response = client.get("/myumbrella?city=timeoutcity")

        # Then the response should return OK
        assert response.status_code == expected_http_code

        # And the returned json should be a dict
        response_dict = response.json()
        assert isinstance(response_dict, dict)

        # And the returned json should match the expected report
        assert response_dict["detail"] == expected_expection.args[0]

        # Test teardown
        del umbrella_report_provider_dependency.provider

    def test_myumbrella_view_should_handle_nocity(self) -> None:
        """Check that the view returns a valid error when openweather can't find a city."""
        # Test setup
        expected_expection = LocationNotFoundException("Unknown city!")
        expected_http_code = httpx.codes.NOT_FOUND
        failing_provider = self._create_mocked_provider_from_exception(
            exception=expected_expection
        )
        umbrella_report_provider_dependency.provider = failing_provider

        # Given a app client
        client = self._get_client()

        # When calling the "/" entry point
        response = client.get("/myumbrella?city=testcity")

        # Then the response should return OK
        assert response.status_code == expected_http_code

        # And the returned json should be a dict
        response_dict = response.json()
        assert isinstance(response_dict, dict)

        # And the returned json should match the expected report
        assert response_dict["detail"] == expected_expection.args[0]

        # Test teardown
        del umbrella_report_provider_dependency.provider

    def test_myumbrella_view_should_warn_on_unknown_weather(self) -> None:
        """Check that the umbrella view returns the correct response when everything is OK."""
        # Test setup
        expected_weather = WeatherState.UNKNOWN
        expected_report = MyUmbrellaResponse(
            city="testcity",
            state="teststate",
            country="testcountry",
            weather=expected_weather.value,
            umbrella_needed=True,
        )
        fake_report = UmbrellaReport(
            location=Location(
                city=expected_report.city,
                state=expected_report.state,
                country=expected_report.country,
            ),
            weather=expected_weather,
        )
        mocked_report_provider = self._create_mocked_provider_from_reports(
            reports=[fake_report]
        )
        umbrella_report_provider_dependency.provider = mocked_report_provider

        # Given a app client
        client = self._get_client()

        # When calling the "/" entry point with a city with unknown weather
        # Then a warning should be present
        with pytest.warns(RuntimeWarning):
            response = client.get(f"/myumbrella?city={expected_report.city}")

        # And the response should return OK
        assert response.status_code == httpx.codes.OK

        # And the returned json should be a dict
        report_dict = response.json()
        assert isinstance(report_dict, dict)

        # And the returned json should match the expected report
        report = MyUmbrellaResponse(**report_dict)
        assert report == expected_report

        # Test teardown
        del umbrella_report_provider_dependency.provider
