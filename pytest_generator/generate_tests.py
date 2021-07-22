"""Small script to support extracting tests from defined functions and classes.

This is a Python file to support running this script on multiple OS'es.
"""
import importlib
import inspect
import sys
from pathlib import Path
from types import MethodType, ModuleType
from typing import Any, Callable, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader(Path(__file__).parent.parent / "templates"),
    autoescape=select_autoescape(),
)


def generate(root: Path):
    """Generate tests for all modules under `root`."""
    if not root.is_absolute():
        root = root.absolute()

    test_root = root.parent.joinpath("tests")
    test_root.mkdir(exist_ok=True)
    test_root.joinpath("__init__.py").touch()

    _collect_members_and_write_tests(root, test_root)


def _collect_members_and_write_tests(root: Path, test_root: Path):
    for python_file in root.glob("**/*.py"):
        if python_file.name == "__init__.py":
            module_parts_list = list(python_file.relative_to(root.parent).parts[:-1])
        else:
            module_parts_list = list(python_file.relative_to(root.parent).parts)

        python_file_suffix = "".join(python_file.suffixes)
        module_parts = ".".join(module_parts_list).removesuffix(python_file_suffix)
        module = importlib.import_module(module_parts)
        classmembers = _get_local_members(module, inspect.isclass)
        module_name_path = Path(module_parts.replace(".", "/"))
        module_test_path = test_root.joinpath(
            module_name_path.parent, f"test_{module_name_path.name}.py"
        )
        module_test_path.parent.mkdir(parents=True, exist_ok=True)
        module_split = module_parts.split(".")
        module_parent_path = ".".join(module_split[:-1])
        module_name = module_split[-1]
        function_details = []
        for classname, classobject in classmembers:
            # create fixture
            fixture_name = classname.lower() + "_fixture"
            print("Create fixture ;)", fixture_name)
            functionmembers = _get_local_members(classobject, None)
            for functionname, _ in functionmembers:
                function_details.append(
                    {
                        "function_to_test": functionname,
                        "classname": classname,
                        "type": "method",
                    }
                )

        functionmembers = _get_local_members(module, inspect.isfunction)
        for functionname, _ in functionmembers:
            function_details.append({"function_to_test": functionname, "type": "function"})
        if not function_details:
            continue
        rendered = env.get_template("test.py.jinja").render(
            module_parent_path=module_parent_path,
            module_name=module_name,
            function_details=function_details,
        )
        module_test_path.write_text(rendered)
        print("wrote to", module_test_path)


def _get_local_members(
    obj: object, predicate: Optional[Callable], reverse=True
) -> list[tuple[str, Any]]:
    members = inspect.getmembers(obj, predicate)
    if reverse:
        members.reverse()
    if isinstance(obj, type):
        local_members = []
        for member in members:
            try:
                self_is_obj = member[1].__self__ == obj
            except AttributeError:
                continue
            else:
                if self_is_obj and isinstance(member[1], MethodType):
                    local_members.append(member)
        return local_members
    elif isinstance(obj, ModuleType):
        return [member for member in members if member[1].__module__ == obj.__name__]
    else:
        print(obj, "not compatible with _get_local_members")
        return []


if __name__ == "__main__":
    # TODO: Add opts to force and specify templates dir
    generate(Path(sys.argv[1]))
