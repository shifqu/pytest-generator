from collections.abc import Callable

from pytest_generator.collect_from_ast import Analyzer


def analyzer_fixture() -> Callable[..., Analyzer]:
    def _inner(*args, **kwargs) -> Analyzer:
        return Analyzer(*args, **kwargs)

    return _inner


def single_analyzer_fixture():
    return Analyzer(name="dummy_analyzer")
