"""Tests for poetry dependency checker."""

from typing import List

import pytest

from ska_mid_itf_engineering_tools.dependency_checker import poetry_dependency_checker
from ska_mid_itf_engineering_tools.dependency_checker.types import Dependency


@pytest.fixture(name="poetry_output_valid")
def fixture_poetry_output_valid() -> str:
    """
    Fixture providing valid poetry show output.

    :return: The poetry output.
    :rtype: str
    """
    return """flake8           6.1.0  7.0.0       the modular source code checker
kubernetes       21.7.1 29.0.0      Kubernetes python client
nbqa             1.7.1  1.8.3       Run any standard Python code quality tool on a Jupyter Notebook
sphinx-rtd-theme 1.3.0  2.0.0       Read the Docs theme for Sphinx"""


@pytest.fixture(name="dependencies_valid")
def fixture_dependencies_valid() -> List[Dependency]:
    """
    Fixture with expected list of dependencies for poetry_output_valid fixture.

    :return: List of dependencies
    :rtype: List[Dependency]
    """
    return [
        Dependency("flake8", "6.1.0", "7.0.0"),
        Dependency("kubernetes", "21.7.1", "29.0.0"),
        Dependency("nbqa", "1.7.1", "1.8.3"),
        Dependency("sphinx-rtd-theme", "1.3.0", "2.0.0"),
    ]


@pytest.fixture(name="poetry_output_invalid")
def fixture_poetry_output_invalid() -> str:
    """
    Fixture providing invalid poetry show output.

    :return: The poetry output.
    :rtype: str
    """
    return """flake8           6.1.0  7.0.a       the modular source code checker
nbqa             Run any standard Python code quality tool on a Jupyter Notebook
sphinx-rtd-theme  2.0.0       Read the Docs theme for Sphinx"""


def test_parse_poetry_valid(poetry_output_valid: str, dependencies_valid: List[Dependency]):
    """
    Tests that valid poetry output is parsed correctly.

    :param poetry_output_valid: The output to parse
    :type poetry_output_valid: str
    :param dependencies_valid: The expected results
    :type dependencies_valid: List[Dependency]
    """
    dc = poetry_dependency_checker.PoetryDependencyChecker()
    result = dc.parse_poetry_dependencies(poetry_output_valid)
    assert result == dependencies_valid


def test_parse_poetry_empty():
    """Tests that empty poetry output is handled correctly."""
    dc = poetry_dependency_checker.PoetryDependencyChecker()
    result = dc.parse_poetry_dependencies("")
    assert len(result) == 0


def test_parse_poetry_invalid(poetry_output_invalid: str):
    """
    Tests that invalid poetry output is handled correctly.

    :param poetry_output_invalid: Invalid poetry output string.
    :type poetry_output_invalid: str
    """
    dc = poetry_dependency_checker.PoetryDependencyChecker()
    with pytest.raises(ValueError):
        dc.parse_poetry_dependencies(poetry_output_invalid)
