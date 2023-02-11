"""Main package for myapp."""
import warnings
from importlib.metadata import PackageNotFoundError, version

APP_NAME = "MyUmbrella"
try:
    __version__ = version(APP_NAME.lower())
except PackageNotFoundError:  # pragma: nocover; just a fail safe
    warnings.warn(
        f"Could not find package for {APP_NAME}. Development environment is assumed"
    )
    __version__ = "0.0.0-dev"
APP_VERSION = __version__
