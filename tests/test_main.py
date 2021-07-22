"""Tests for the `main` method."""
import subprocess

import pytest

from pytest_generator import __version__


@pytest.mark.parametrize(
    ("cmd", "expected_output"),
    [
        ("python -m pytest_generator --version", __version__),
        ("python -m pytest_generator.main --version", __version__),
    ],
)
def test_main(cmd, expected_output):
    """Test that calling the application from a script with --version returns the __version__."""
    return_value = subprocess.run(cmd.split(" "), capture_output=True)
    assert return_value.stdout.decode("utf-8").strip() == __version__
