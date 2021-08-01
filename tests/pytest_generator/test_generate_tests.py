import pytest

from pytest_generator import generate_tests


@pytest.mark.parametrize(
    ("args",),
    [
        (["root", "template_dir"],),
    ],
)
def test_generate(args):
    generate_tests.generate(*args)


@pytest.mark.parametrize(
    ("args",),
    [
        (["members", "test_root"],),
    ],
)
def test_write_tests(args):
    generate_tests.write_tests(*args)
