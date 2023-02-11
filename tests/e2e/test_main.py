"""End-to-end tests for myapp"""
import httpx
from fastapi.testclient import TestClient

from myumbrella.dependencies import umbrella_report_provider_dependency
from myumbrella.main import app, setup_application

client = TestClient(app=setup_application(application=app))


def test_root_endpoint_should_return_name_and_version() -> None:
    """Check that the root entry point returns the name and the version of the app."""
    # Given a app client
    # When calling the "/" entry point
    response = client.get("/")

    # Then the response should return OK
    assert response.status_code == httpx.codes.OK

    # And the return message should contain the app name
    response_text = response.text
    assert app.title in response_text
    assert app.version in response_text


def test_umbrella_endpoint_should_error_when_no_provider() -> None:
    """Check that the umbrella endpoint returns an error 500 when not initialized."""
    # Test setup
    old_provider = umbrella_report_provider_dependency.provider
    del umbrella_report_provider_dependency.provider

    # Given a app client
    # When calling the "/myumbrella" entry point
    response = client.get("/myumbrella?city=toulouse")

    # Then the response should return OK
    assert response.status_code == httpx.codes.INTERNAL_SERVER_ERROR

    # And the return object should be a dict
    response_dict = response.json()
    assert isinstance(response_dict, dict)

    # And there should be a message
    assert response_dict.get("detail") is not None

    # Teardown Test
    if old_provider:
        umbrella_report_provider_dependency.provider = old_provider


def test_umbrella_endpoint_should_work_with_known_city() -> None:
    """Check that the umbrella endpoint works with a city that exists."""
    # Given a app client
    # When calling the "/myumbrella" entry point
    response = client.get("/myumbrella?city=toulouse")

    # Then the response should return OK
    assert response.status_code == httpx.codes.OK

    # And the return object should be a dict
    response_dict = response.json()
    assert isinstance(response_dict, dict)

    # And it should not contain default value
    assert response_dict["city"] == "Toulouse"
    assert response_dict["state"] == "Occitania"
    assert response_dict["country"] == "FR"
    assert isinstance(response_dict["umbrella_needed"], bool)
