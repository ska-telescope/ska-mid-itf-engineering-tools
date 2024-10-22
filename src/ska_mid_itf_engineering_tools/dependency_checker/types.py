"""Types for the dependency checker."""

import logging
import re
from collections import OrderedDict
from typing import Any, Dict, List

import semver
from attr import dataclass


class Dependency:
    """Dependency represents a stale dependency."""

    name: str = ""
    project_version: semver.Version = ""
    available_version: semver.Version = ""

    def __init__(self, name: str, project_version: str, available_version: str) -> None:
        """
        Initialise the dependency.

        :param name: The name.
        :type name: str
        :param project_version: The current version used by the project.
        :type project_version: str
        :param available_version: The latest available version.
        :type available_version: str
        """
        self.name = name
        fixed_project_version = fix_known_semver_violations(project_version)
        self.project_version = semver.Version.parse(fixed_project_version)
        fixed_available_version = fix_known_semver_violations(available_version)
        self.available_version = semver.Version.parse(fixed_available_version)

    def __members(self):
        return (self.name, self.project_version, self.available_version)

    def __eq__(self, other: Any) -> bool:
        """
        Determine whether this Dependency is equal to other.

        :param other: The other object to compare this one to.
        :type other: Any
        :return: True if this Dependency is equal to other, False otherwise.
        :rtype: bool
        """
        if type(other) is type(self):
            return self.__members() == other.__members()
        else:
            return False

    def __hash__(self) -> int:
        """
        Return the hash value for the Dependency.

        :return: the hash value
        :rtype: int
        """
        return hash(self.__members())

    def as_slack_section(self) -> Dict:
        """
        Create a Slack section from the current dependency.

        See https://api.slack.com/reference/block-kit/blocks#section

        :return: A Slack section.
        :rtype: Dict
        """
        return {
            "type": "section",
            "text": {
                "text": f"*{self.name}*",
                "type": "mrkdwn",
            },
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "Project Version",
                },
                {
                    "type": "mrkdwn",
                    "text": "Available Version",
                },
                {
                    "type": "mrkdwn",
                    "text": str(self.project_version),
                },
                {
                    "type": "mrkdwn",
                    "text": str(self.available_version),
                },
            ],
        }


def fix_known_semver_violations(version: str):
    """Fix known errors in version specification.

    :param version: Version to be checked
    :return: Version fixed for known errors
    """
    # Fix X.X.XrcX cases
    pattern = r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)rc(?P<prerelease>.*?)$"
    match = re.match(pattern, version)

    if match:
        fixed_version = (
            f"{match.group('major')}.{match.group('minor')}"
            f".{match.group('patch')}-rc.{match.group('prerelease')}"
        )
        return fixed_version
    else:
        return version


@dataclass
class DependencyGroup:
    """Represents a group of dependencies, e.g. in a Helm chart."""

    group_name: str = ""
    dependencies: List[Dependency] = []


class DependencyChecker:
    """Base class for dependency checkers."""

    def __init__(self) -> None:
        """Initialise the DependencyChecker."""
        self.logger = logging.getLogger(__name__)

    def valid_for_project(self) -> bool:
        """Determine whether the DependencyChecker can be executed for the current project."""
        pass

    def collect_stale_dependencies(self) -> List[DependencyGroup]:
        """Collect all stale dependencies."""
        pass

    def name(self) -> str:
        """Retrieve the name of the dependency checker."""
        pass


@dataclass
class ProjectInfo:
    """ProjectInfo is store information about the current project."""

    name: str
    version: str


class DependencyNotifier:
    """DependencyNotifier sends notifications for a project's stale dependencies."""

    def __init__(self):
        """Initialise the dependency checker."""
        self.logger = logging.getLogger(__name__)

    def send_notification(
        self, project_info: ProjectInfo, dependency_map: OrderedDict[str : List[DependencyGroup]]
    ):
        """
        Send notifications for a project's stale dependencies.

        :param project_info: The project name and version.
        :type project_info: ProjectInfo
        :param dependency_map: The stale project dependencies.
        :type dependency_map: _type_
        """
        pass
