"""Small script to support extracting tests from defined functions and classes.

This is a Python file to support running this script on multiple OS'es.
"""
import importlib
import inspect
from pathlib import Path
from types import MethodType, ModuleType
from typing import Any, Callable, Optional

import jinja2

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(Path("templates")), autoescape=jinja2.select_autoescape()
)


def generate(root: Path = Path("accountancy_automation")):
    if not root.is_absolute():
        root = root.absolute()

    test_root = root.parent.joinpath("tests")
    test_root.mkdir(exist_ok=True)
    test_root.joinpath("__init__.py").touch()

    _collect_members_and_write_tests(root, test_root)


def _collect_members_and_write_tests(root: Path, test_root: Path):
    for python_file in root.glob("**/*.py"):
        if python_file.name == "__init__.py":
            continue
        python_file_suffix = "".join(python_file.suffixes)
        module_parts_list = list(python_file.relative_to(root.parent).parts)
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
            print("Create fixture ;)", classname)
            functionmembers = _get_local_members(classobject, None)
            for functionname, _ in functionmembers:
                test_name = f"test_function_{module_name}_{classname.lower()}_{functionname}"
                function_details.append(
                    {
                        "test_name": test_name,
                        "function_to_test": functionname,
                        "classname": classname,
                    }
                )

        functionmembers = _get_local_members(module, inspect.isfunction)
        for functionname, _ in functionmembers:
            test_name = f"test_function_{module_name}_{functionname}"
            function_details.append({"test_name": test_name, "function_to_test": functionname})
        rendered = env.get_template("test.py.jinja").render(
            module_parent_path=module_parent_path,
            module_name=module_name,
            function_details=function_details,
        )
        module_test_path.write_text(rendered)
        print("wrote to", module_test_path)


def _get_local_members(obj: object, predicate: Optional[Callable]) -> list[tuple[str, Any]]:
    members = inspect.getmembers(obj, predicate)
    if isinstance(obj, type):
        local_members = []
        for member in members:
            try:
                self_is_obj = member[1].__self__ == obj
            except AttributeError:
                continue
            else:
                if any(
                    member[0] in [x[0] for x in inspect.getmembers(obj_base, predicate)]
                    for obj_base in obj.__bases__
                ):
                    continue
                if self_is_obj and isinstance(member[1], MethodType):
                    local_members.append(member)
        return local_members
    elif isinstance(obj, ModuleType):
        return [member for member in members if member[1].__module__ == obj.__name__]
    else:
        print(obj, "not compatible with _get_local_members")
        return []


def _write_tests(member_detail: dict[str, dict[str, Any]], test_root: Path):
    for module_path, details_dict in member_detail.items():
        module_name_path = Path(module_path.replace(".", "/"))
        module_test_path = test_root.joinpath(
            module_name_path.parent, f"test_{module_name_path.name}.py"
        )
        module_test_path.parent.mkdir(parents=True, exist_ok=True)
        module_split = module_path.split(".")
        module_parent_path = ".".join(module_split[:-1])
        module_name = module_split[-1]
        classmembers = _get_local_members(module, inspect.isclass)
        function_detail = [{"test_name": "x", "function_to_test": "y"}]
        import_string = f"from {'.'.join(module_split[:-1])} import {module_split[-1]}\n\n\n"
        module_test_path.write_text(import_string)
        tests = _get_writable_strings(details_dict, module_path, "class")
        tests.extend(_get_writable_strings(details_dict, module_path, "function"))

        with module_test_path.open("a") as file:
            file.write("\n\n\n".join(tests))
            file.write("\n")
            print("wrote to", module_test_path)


def _get_writable_strings(details_dict: dict[str, Any], module_path: str, key: str) -> list[str]:
    tests = []
    for member in details_dict[f"{key}members"]:
        test_name = f"test_{key}_{module_path.replace('.', '_').lower()}_{member[0].lower()}"
        if key == "class":
            tests.append(
                f"def {test_name}() -> None:\n    {module_path.split('.')[-1]}.{member[0]}()"
            )
            print("debug")
            tests.extend(
                _get_writable_strings(
                    {"functionmembers": _get_local_members(member[1], None)},
                    f"{module_path}.{member[0]}",
                    "function",
                )
            )
        else:
            tests.append(
                f"def {test_name}() -> None:\n"
                f"    {'.'.join(module_path.split('.')[1:])}.{member[0]}()"
            )
    return tests


def _write(sender, name, obj):
    import json
    from pathlib import Path

    with Path("/Users/sonny/Projects/PERSONAL/accountancy-automation/tests/data").joinpath(
        f"{sender.__name__}_{name}.json"
    ).open("w") as fp:
        json.dump(obj, fp)


if __name__ == "__main__":
    generate()
