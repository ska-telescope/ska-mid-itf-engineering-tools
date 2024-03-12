"""A dependency checker for poetry."""

import os
import subprocess
from typing import List

from .types import Dependency, DependencyChecker, DependencyGroup


class PoetryDependencyChecker(DependencyChecker):
    """A dependency checker for poetry."""

    def valid_for_project(self) -> bool:
        """
        Determine whether the PoetryDependencyChecker can be executed for the current project.

        :return: True if it can be executed, False otherwise.
        :rtype: bool
        """
        return os.path.isfile("pyproject.toml")

    def collect_stale_dependencies(self) -> List[DependencyGroup]:
        """
        Retrieve all stale top-level python dependencies in the project.

        :raises RuntimeError: If `poetry show --outdated --top-level` returns non-zero.
        :return: The parsed list of stale dependencies.
        :rtype: List[Dependency]
        """
        result = subprocess.run(
            ["poetry", "show", "--outdated", "--top-level"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"'poetry show' failed: stderr={result.stderr}; stdout={result.stdout}"
            )
        deps = self.parse_poetry_dependencies(result.stdout)
        return [DependencyGroup(group_name="default", dependencies=deps)]

    def parse_poetry_dependencies(self, poetry_dependencies: str) -> List[Dependency]:
        """
        Parse dependencies from the string output of `poetry show --outdated --top-level`.

        :param poetry_dependencies: The Poetry output.
        :type poetry_dependencies: str
        :return: The parsed list of stale dependencies.
        :rtype: List[Dependency]
        """
        dependencies = []
        lines = poetry_dependencies.splitlines()
        for line in lines:
            words = line.split()
            dependencies.append(
                Dependency(name=words[0], project_version=words[1], available_version=words[2])
            )
        return dependencies

    def name(self) -> str:
        """
        Retrieve the name of the dependency checker.

        :return: The name.
        :rtype: str
        """
        return "poetry"
