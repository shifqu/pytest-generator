"""Pytest Generator.

Generate pytests for all classes, functions and methods
"""
from importlib.metadata import version as metadata_version

__version__ = str(metadata_version(__name__))
