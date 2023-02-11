"""Module where app dependencies are defined and stored."""
import logging

from .core import UmbrellaReportProvider

logger = logging.getLogger("__name__")


class DependencyNotInitializedException(ValueError):
    """Exception when dependency has not been initialized."""


class UmbrellaReportProviderDependency:
    """TBD."""

    def __init__(self) -> None:
        """TBD."""
        self._provider: UmbrellaReportProvider | None = None

    @property
    def provider(self) -> UmbrellaReportProvider | None:
        """TBD."""
        logging.debug(
            "%s serving provider: %s",
            self.__class__.__name__,
            self._provider.__class__.__name__,
        )
        return self._provider

    @provider.setter
    def provider(self, provider: UmbrellaReportProvider) -> None:
        logging.info(
            "UmbrellaReportProvider is now set to '%s'", provider.__class__.__name__
        )
        self._provider = provider

    @provider.deleter
    def provider(self) -> None:
        self._provider = None

    def __call__(self) -> UmbrellaReportProvider:
        """TBD."""
        provider = self.provider
        if provider is None:
            raise DependencyNotInitializedException(
                "UmbrellaReportProvider has no provider!"
            )
        return provider


umbrella_report_provider_dependency = UmbrellaReportProviderDependency()
