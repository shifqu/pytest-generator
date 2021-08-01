import pytest

from pytest_generator import main


@pytest.mark.parametrize(
    ("args",),
    [
        ([],),
    ],
)
def test_main(args):
    main.main(*args)
