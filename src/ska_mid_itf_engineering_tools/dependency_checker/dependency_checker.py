"""DependencyChecker is used to check for stale project dependencies."""

import argparse
import logging
import os
import subprocess
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List

from ska_ser_logging import configure_logging
from slack_sdk.webhook import WebhookClient

from .helm_dependency_collector import HelmDependencyCollector
from .poetry_dependency_collector import PoetryDependencyCollector
from .types import Dependency, DependencyCollector, DependencyGroup


@dataclass
class ProjectInfo:
    """ProjectInfo is store information about the current project."""

    name: str
    version: str


class DependencyChecker:
    """DependencyChecker is used to check for stale project dependencies."""

    __slack_webhook_url: str = ""
    __collectors: List[DependencyCollector] = []
    __dry_run: bool = False

    def __init__(
        self,
        slack_webhook_url: str,
        dependency_collectors: List[DependencyCollector],
        dry_run: bool = False,
    ):
        """
        Initialise the dependency checker.

        :param slack_webhook_url: The webhook URL used to send Slack notifications.
        :type slack_webhook_url: str
        :param dependency_collectors: The dependency collectors to run.
        :type dependency_collectors: List[DependencyCollector]
        :param dry_run: Whether to run in dry-run mode, defaults to False
        :type dry_run: bool
        """
        self.__slack_webhook_url = slack_webhook_url
        self.__collectors = dependency_collectors
        self.__dry_run = dry_run
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Run the dependency checker."""
        project_info = self.get_project_info()
        dependency_map: OrderedDict[str : List[DependencyGroup]] = OrderedDict()
        for dc in self.__collectors:
            if not dc.valid_for_project():
                self.logger.info(
                    "skipping %s dependency collector: not valid for this project", dc.name()
                )
                continue
            self.logger.info("running %s dependency collector", dc.name())
            deps = dc.collect_stale_dependencies()
            dependency_map[dc.name()] = deps
        if self.__dry_run:
            msg = self.build_log_message(project_info, dependency_map)
            self.logger.debug("dry-run mode: not sending message to slack. Message:\n%s", msg)
        else:
            msg = self.build_slack_message(project_info, dependency_map)
            self.send_slack_message(msg)

    def get_project_info(self) -> ProjectInfo:
        """
        Retrieve the project's info (name and version).

        :raises RuntimeError: If `poetry version` returns non-zero.
        :return: An object containing the project name and version.
        :rtype: ProjectInfo
        """
        result = subprocess.run(
            ["poetry", "version"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"'poetry version' failed: stderr={result.stderr}; stdout={result.stdout}"
            )
        vals = result.stdout.split()
        return ProjectInfo(name=vals[0], version=vals[1])

    def build_log_message(
        self,
        project_info: ProjectInfo,
        dependency_map: OrderedDict[str : List[DependencyGroup]],
    ) -> str:
        """
        Create a log message for the stale dependencies.

        :param project_info: The project name and version.
        :type project_info: ProjectInfo
        :param dependency_map: The stale Poetry dependencies.
        :type dependency_map: OrderedDict[str: List[DependencyGroup]]
        :return: A formatted log message.
        :rtype: str
        """
        msg = [f"{project_info.name} - {project_info.version}"]
        for collector_name, dependency_groups in dependency_map.items():
            if len(dependency_groups) == 1 and dependency_groups[0].group_name == "default":
                msg.append(self.build_log_message_single(collector_name, dependency_groups[0]))
            else:
                msg.append(self.build_log_message_groups(collector_name, dependency_groups))
        return "\n".join(msg)

    def build_log_message_single(
        self, collector_name: str, dependency_group: DependencyGroup
    ) -> str:
        """
        Build a log message for a single dependency groups.

        :param collector_name: Name of the dependency collector.
        :type collector_name: str
        :param dependency_group: The dependency group.
        :type dependency_group: DependencyGroup
        :return: The log message.
        :rtype: str
        """
        msg = [
            "",
            "",
            f"{collector_name} -- {len(dependency_group.dependencies)} stale dependencies!",
            "",
        ]
        for dep in dependency_group.dependencies:
            msg.append(f"{dep.name}: {str(dep.project_version)} --> {str(dep.available_version)}")
        return "\n".join(msg)

    def build_log_message_groups(
        self, collector_name: str, dependency_groups: List[DependencyGroup]
    ) -> str:
        """
        Build a log message for dependency groups.

        :param collector_name: Name of the dependency collector.
        :type collector_name: str
        :param dependency_groups: The dependency groups.
        :type dependency_groups: List[DependencyGroup]
        :return: The log message.
        :rtype: str
        """
        total_deps = sum(len(dg.dependencies) for dg in dependency_groups)
        msg = ["", "", f"{collector_name} -- {total_deps} stale dependencies!", ""]
        for dg in dependency_groups:
            msg.extend(
                ["", f"{dg.group_name} Chart -- {len(dg.dependencies)} stale dependencies!"]
            )
            for dep in dg.dependencies:
                msg.append(
                    f"{dep.name}: {str(dep.project_version)} --> {str(dep.available_version)}"
                )
        return "\n".join(msg)

    def build_slack_message(
        self, project_info: ProjectInfo, dependency_map: OrderedDict[str : List[DependencyGroup]]
    ) -> List[Dict]:
        """
        Create a slack message using Block Kit Builder.

        See: https://api.slack.com/block-kit

        :param project_info: The project name and version.
        :type project_info: ProjectInfo
        :param dependency_map: The stale Poetry dependencies.
        :type dependency_map: OrderedDict[str: List[Dependency]]
        :return: A message in Block Kit Builder format.
        :rtype: List[Dict]
        """
        msg_blocks = [
            {
                "type": "section",
                "text": {
                    "text": f"*{project_info.name} - {project_info.version}*",
                    "type": "mrkdwn",
                },
            },
        ]
        for collector_name, dependency_groups in dependency_map.items():
            sections: List[Dict] = []
            if len(dependency_groups) == 0 and dependency_groups[0].group_name == "default":
                sections = self.generate_slack_message_sections_single(
                    collector_name, dependency_groups[0]
                )
            else:
                sections = self.generate_slack_message_sections_groups(
                    collector_name, dependency_groups
                )
            msg_blocks.extend(sections)
        return msg_blocks

    def generate_slack_message_sections_groups(
        self, name: str, dependency_groups: List[DependencyGroup]
    ) -> List[Dict]:
        """
        Generate Slack message sections for the dependencies.

        :param name: Name of the associated dependency collector.
        :type name: str
        :param dependency_groups: The groups of stale dependencies.
        :type dependency_groups: List[DependencyGroup]
        :return: A list of Slack message sections.
        :rtype: List[Dict]
        """
        total_deps = sum(len(dg.dependencies) for dg in dependency_groups)
        if total_deps == 0:
            no_outdated = {
                "type": "section",
                "text": {
                    "text": "*{name}: No outdated dependencies found.*",
                    "type": "mrkdwn",
                },
            }
            return [no_outdated]

        outdated_msg = [
            {
                "type": "section",
                "text": {
                    "text": f"*{name}: {total_deps} outdated dependencies found!*",
                    "type": "mrkdwn",
                },
            }
        ]
        for dg in dependency_groups:
            if len(dg.dependencies) == 0:
                continue
            outdated_text = (
                f"*{dg.group_name}: {len(dg.dependencies)} outdated dependencies found!*"
            )
            outdated_msg.append(
                {
                    "type": "section",
                    "text": {
                        "text": outdated_text,
                        "type": "mrkdwn",
                    },
                }
            )
            for d in dg.dependencies:
                outdated_msg.append(d.as_slack_section())
        return outdated_msg

    def generate_slack_message_sections_single(
        self, name: str, dependencies: List[Dependency]
    ) -> List[Dict]:
        """
        Generate Slack message sections for the dependencies.

        :param name: Name of the associated dependency collector.
        :type name: str
        :param dependencies: The stale dependencies.
        :type dependencies: List[Dependency]
        :return: A list of Slack message sections.
        :rtype: List[Dict]
        """
        if len(dependencies) == 0:
            no_outdated = {
                "type": "section",
                "text": {
                    "text": "*No outdated {name} dependencies found.*",
                    "type": "mrkdwn",
                },
            }
            return [no_outdated]

        outdated_msg = [
            {
                "type": "section",
                "text": {
                    "text": f"*{len(dependencies)} outdated {name} dependencies found!*",
                    "type": "mrkdwn",
                },
            }
        ]
        for d in dependencies:
            outdated_msg.append(d.as_slack_section())
        return outdated_msg

    def send_slack_message(self, msg_blocks: List[Dict]):
        """
        Send a Slack notification to the configured webhook URL.

        :param msg_blocks: The blocks used to create the message.
        :type msg_blocks: List[Dict]
        :raises RuntimeError: If the request failed.
        """
        webhook = WebhookClient(self.__slack_webhook_url)
        response = webhook.send(
            blocks=msg_blocks,
            text="Failed to build message: please investigate!",
        )

        if response.status_code != 200:
            raise RuntimeError(f"Failed to send to slack: {response.status_code}")

        self.logger.info("Alert sent to slack")


def main():
    """
    Run the dependency checker.

    :raises RuntimeError: _description_
    """
    configure_logging(level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        prog="DependencyChecker", description="Check staleness of Project dependencies"
    )
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        help="Don't post messages to slack",
        default=False,
    )
    parser.add_argument(
        "--dependency-checkers",
        nargs="+",
        help="Dependency checkers to run.",
        default="poetry helm",
    )
    args = parser.parse_args()
    dependency_checkers: List[DependencyChecker] = []
    for d in args.dependency_checkers:
        if d == "poetry":
            dependency_checkers.append(PoetryDependencyCollector())
        elif d == "helm":
            dependency_checkers.append(HelmDependencyCollector())
        else:
            raise RuntimeError(f"Unsupported checker {d}")

    slack_webhook_url = ""
    if not args.dry_run:
        slack_webhook_url = os.environ["DEPENDENCY_CHECKER_WEBHOOK_URL"]
    DependencyChecker(
        slack_webhook_url=slack_webhook_url,
        dependency_collectors=dependency_checkers,
        dry_run=args.dry_run,
    ).run()


if __name__ == "__main__":
    main()
