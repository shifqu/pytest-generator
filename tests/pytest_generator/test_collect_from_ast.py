import pytest

from pytest_generator import collect_from_ast


@pytest.mark.parametrize(
    ("args",),
    [
        (["root"],),
    ],
)
def test_collect_members(args):
    collect_from_ast.collect_members(*args)


@pytest.mark.parametrize(
    ("args",),
    [
        ([],),
    ],
)
def test___init__(args, analyzer_fixture):
    analyzer_fixture.__init__(*args)


@pytest.mark.parametrize(
    ("args",),
    [
        (["node"],),
    ],
)
def test_visit_ClassDef(args, analyzer_fixture):
    analyzer_fixture.visit_ClassDef(*args)


@pytest.mark.parametrize(
    ("args",),
    [
        (["node"],),
    ],
)
def test_visit_AsyncFunctionDef(args, analyzer_fixture):
    analyzer_fixture.visit_AsyncFunctionDef(*args)


@pytest.mark.parametrize(
    ("args",),
    [
        (["node"],),
    ],
)
def test_visit_FunctionDef(args, analyzer_fixture):
    analyzer_fixture.visit_FunctionDef(*args)


@pytest.mark.parametrize(
    ("args",),
    [
        (["node"],),
    ],
)
def test__visit_function(args, analyzer_fixture):
    analyzer_fixture._visit_function(*args)


@pytest.mark.parametrize(
    ("args",),
    [
        (["node"],),
    ],
)
def test__visit_arguments(args, analyzer_fixture):
    analyzer_fixture._visit_arguments(*args)
