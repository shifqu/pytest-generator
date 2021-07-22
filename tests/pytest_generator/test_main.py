import pytest

from pytest_generator import main


@pytest.mark.parametrize(("expected_output"), [("x")])
def test_main_main(expected_output):
    return_value = main.main()
    assert return_value == expected_output
