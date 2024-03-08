"""Out-of-date dependency checker for Helm."""

import os
import subprocess
from pathlib import Path
from typing import Dict, List

import requests
import semver

from .types import Dependency, DependencyChecker, DependencyGroup


class HelmDependencyChecker(DependencyChecker):
    """Out-of-date dependency checker for Helm."""

    def __init__(self, charts_dir: str = "charts") -> None:
        """
        Initialise the HelmDependencyChecker.

        :param charts_dir: The location of the charts, defaults to "charts"
        :type charts_dir: str
        """
        super().__init__()
        self.__charts_dir: Path = Path(charts_dir)

    def valid_for_project(self) -> bool:
        """
        Determine whether the dependency checker can be executed for the current project.

        :return: True if it can be executed, False otherwise.
        :rtype: bool
        """
        return os.path.isdir(self.__charts_dir)

    def collect_stale_dependencies(self) -> List[DependencyGroup]:
        """
        Retrieve all stale top-level helm dependencies in the project.

        :return: A list of stale helm dependencies.
        :rtype: List[Dependency]
        """
        grouped_deps: List[DependencyGroup] = []
        for dir in self.__charts_dir.glob("*"):
            if dir.is_dir():
                deps = self.collect_chart_dependencies(dir)
                grouped_deps.append(DependencyGroup(group_name=str(dir.name), dependencies=deps))
                self.logger.debug("collected dependencies for %s", dir)
        return grouped_deps

    def collect_chart_dependencies(self, chart_dir: Path) -> List[Dependency]:
        """
        Collect dependencies for a given Helm chart.

        :param chart_dir: The location of the chart.
        :type chart_dir: Path
        :raises RuntimeError: if 'helm dependency list' exits non-zero.
        :return: A list of the chart's dependencies.
        :rtype: List[Dependency]
        """
        result = subprocess.run(
            ["helm", "dependency", "list", str(chart_dir)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"'helm dependency list' failed: stderr={result.stderr}; stdout={result.stdout}"
            )
        self.logger.debug("'helm dependency list' result for %s: %s", str(dir), result.stdout)
        deps: List[Dependency] = self.parse_helm_dependencies(result.stdout)
        stale_deps: List[Dependency] = []
        for d in deps:
            version = self.find_latest_chart_version(d)
            if version.compare(d.available_version) > 0:
                d.available_version = version
                stale_deps.append(d)
        return stale_deps

    def parse_helm_dependencies(self, helm_dependencies: str) -> List[Dependency]:
        """
        Parse helm dependencies from 'helm dependencies list' output.

        :param helm_dependencies: The 'helm dependencies list' output.
        :type helm_dependencies: str
        :return: A list of dependencies. The available_version is set to the project_version.
        :rtype: List[Dependency]
        """
        dependencies = []
        lines = helm_dependencies.splitlines()
        for line in lines:
            if line.startswith("NAME") or line.startswith("WARNING"):
                continue
            words = line.split()
            if len(words) < 2:
                continue
            dependencies.append(
                Dependency(
                    name=words[0],
                    project_version=words[1],
                    available_version=words[1],
                )
            )
        return dependencies

    def find_latest_chart_version(self, chart: Dependency) -> semver.Version:
        """
        Find the latest version of the specified chart.

        :param chart: The chart to lookup.
        :type chart: Dependency
        :raises RuntimeError: If the request to Nexus fails.
        :return: The latest available version.
        :rtype: semver.Version
        """
        url = "https://artefact.skao.int/service/rest/v1/search"
        params = {
            "name": chart.name,
            "repository": "helm-internal",
        }
        response: requests.Response = requests.get(
            url=url,
            timeout=60,
            params=params,
        )
        if response.status_code != 200:
            raise RuntimeError(f"Request failed({response.status_code}): {response.text}")
        body = response.json()
        items: List[Dict] = body["items"]
        latest = chart.available_version
        done = False
        while not done:
            for item in items:
                item_name = item.get("name", "")
                if item_name != chart.name:
                    continue
                raw_version = item.get("version", "0.0.0")
                if not semver.Version.is_valid(raw_version):
                    self.logger.warn(
                        "Invalid version found in nexus search: %s -- %s", item_name, raw_version
                    )
                    continue
                item_version = semver.Version.parse(item.get("version", "0.0.0"))
                if latest.compare(item_version) < 0 and (
                    item_version.prerelease is None or len(item_version.prerelease) == 0
                ):
                    latest = item_version
            token = body.get("continuationToken", None)
            if token is not None:
                params["continuationToken"] = token
                response: Dict[List[Dict]] = requests.get(
                    url=url,
                    timeout=60,
                    params=params,
                )
            else:
                done = True
        return latest

    def name(self) -> str:
        """
        Retrieve the name of the dependency checker.

        :return: The name.
        :rtype: str
        """
        return "helm"
