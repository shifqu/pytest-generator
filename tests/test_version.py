"""Tests for the version string."""
import re

from pytest_generator import __version__

official_semver_re = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>"
    r"(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)  # https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string


def test_version() -> None:
    """Ensure the version is a string that matches semver format."""
    assert isinstance(__version__, str), f"__version__ must be a str, not '{type(__version__)}'."
    assert official_semver_re.match(
        __version__
    ), f"'{__version__}' is not in the official semver.org format."
