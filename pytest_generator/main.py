"""The main file for when the project is run."""
from argparse import ArgumentParser

from pytest_generator import __version__


def main() -> None:
    """Execute the main function for when the project is run."""
    parser = ArgumentParser("pytest_generator")
    parser.add_argument("--version", action="version", version=__version__)
    parser.parse_args()


if __name__ == "__main__":
    main()
