"""Small script to support extracting tests from defined functions and classes.

This is a Python file to support running this script on multiple OS'es.
"""
import subprocess
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from typer import Typer

from pytest_generator.collect_from_ast import collect_members

try:
    import black

    __BLACK_ENABLED__ = True
except ImportError:
    __BLACK_ENABLED__ = False


DEFAULT_TEMPLATES_PATH = Path(__file__).parent.parent / "templates"
env = Environment(
    loader=None,
    autoescape=select_autoescape(),
)
cli = Typer(name="pytest-generator")


@cli.command()
def generate(root: Path, template_dir: Path = DEFAULT_TEMPLATES_PATH):
    """Generate tests for all modules under `root`.

    Args:
        root (Path): The root path of the package. Can be relative.
        template_dir (Path, optional): Directory from which templates are loaded.
    """
    if not root.is_absolute():
        root = root.absolute()

    if env.loader is None:
        # Modifications on environments after the first template was loaded
        # will lead to surprising effects and undefined behavior.
        env.loader = FileSystemLoader(template_dir)

    test_root = root.parent.joinpath("tests")
    test_root.mkdir(exist_ok=True)
    test_root.joinpath("__init__.py").touch()

    members = collect_members(root)
    write_tests(members, test_root)


def write_tests(members: dict[str, dict[str, Any]], test_root: Path):
    tests: dict[Path, str] = {}
    for member, details in members.items():
        if not any(detail for detail in details.values()):
            print(f"Skipping {member}, it has no details {details}")
            continue
        handle_function(details)
        for class_detail in details["class"]:
            # TODO: write fixture
            handle_function(class_detail)
        module_name_split = member.split(".")
        rendered = env.get_template("test.py.jinja").render(
            from_=".".join(module_name_split[:-1]),
            import_=module_name_split[-1],
            functions=details["function"],
            classes=details["class"],
        )
        test_path = (
            test_root.joinpath(*module_name_split[:-1])
            .joinpath(f"test_{module_name_split[-1]}")
            .with_suffix(".py")
        )
        tests[test_path] = rendered
    print("collecting tests finished.")
    print("commencing write operations.")
    for path, test in tests.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(test)
        print("wrote to", path)
        if __BLACK_ENABLED__:
            subprocess.run(["black", path])
            print("black formatting finished successfully", path)


def handle_function(details: dict[str, Any]):
    for fn in details.get("function", []):
        arguments = []
        if any(fn["args"].values()):
            for k, v in fn["args"].items():
                if k not in ["posonlyargs", "args", "kwonlyargs"]:
                    continue
                for a in v:
                    if a in ["self", "cls"]:
                        continue
                    arguments.append(a)
        fn["args"] = arguments
    return None


if __name__ == "__main__":
    # TODO: Add opts to force
    cli()
