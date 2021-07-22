import pytest
from pytest_generator import generate_tests



@pytest.mark.parametrize(("expected_output"), [("x")])
def test_generate_tests_generate(expected_output):
    return_value = generate_tests.generate()
    assert return_value == expected_output



@pytest.mark.parametrize(("expected_output"), [("x")])
def test_generate_tests__get_local_members(expected_output):
    return_value = generate_tests._get_local_members()
    assert return_value == expected_output



@pytest.mark.parametrize(("expected_output"), [("x")])
def test_generate_tests__collect_members_and_write_tests(expected_output):
    return_value = generate_tests._collect_members_and_write_tests()
    assert return_value == expected_output
