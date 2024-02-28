"""DependencyChecker is used to check for stale project dependencies."""
import logging
import os
import subprocess
from dataclasses import dataclass
from typing import Dict, List

from ska_ser_logging import configure_logging
from slack_sdk.webhook import WebhookClient


@dataclass
class PoetryDependency:
    """PoetryDependency represents a stale poetry dependency."""

    name: str = ""
    project_version: str = ""
    available_version: str = ""

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
                "text": self.name,
                "type": "mrkdwn",
            },
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Project Version*",
                },
                {
                    "type": "mrkdwn",
                    "text": "*Available Version*",
                },
                {
                    "type": "mrkdwn",
                    "text": self.project_version,
                },
                {
                    "type": "mrkdwn",
                    "text": self.available_version,
                },
            ],
        }


@dataclass
class ProjectInfo:
    """ProjectInfo is store information about the current project."""

    name: str
    version: str


class DependencyChecker:
    """DependencyChecker is used to check for stale project dependencies."""

    __slack_webhook_url = ""

    def __init__(self, slack_webhook_url: str):
        """
        Initialise the dependency checker.

        :param slack_webhook_url: The webhook URL used to send Slack notifications.
        :type slack_webhook_url: str
        """
        self.__slack_webhook_url = slack_webhook_url
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Run the dependency checker."""
        project_info = self.get_project_info()
        deps = self.get_stale_poetry_dependencies()
        msg = self.build_slack_message(project_info, deps)
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

    def get_stale_poetry_dependencies(self) -> List[PoetryDependency]:
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
        return deps

    def parse_poetry_dependencies(self, poetry_dependencies: str) -> List[PoetryDependency]:
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
                PoetryDependency(
                    name=words[0], project_version=words[1], available_version=words[2]
                )
            )
        return dependencies

    def build_slack_message(
        self, project_info: ProjectInfo, dependencies: List[PoetryDependency]
    ) -> List[Dict]:
        """
        Create a slack message using Block Kit Builder.

        See: https://api.slack.com/block-kit

        :param project_info: The project name and version.
        :type project_info: ProjectInfo
        :param dependencies: The stale Poetry dependencies.
        :type dependencies: List[Dependency]
        :return: A message in Block Kit Builder format.
        :rtype: List[Dict]
        """
        msg_blocks = [
            {
                "type": "section",
                "text": {
                    "text": f"{project_info.name} - {project_info.version}",
                    "type": "mrkdwn",
                },
            },
        ]
        if len(dependencies) == 0:
            no_outdated = {
                "type": "section",
                "text": {
                    "text": "*No outdated dependencies found.*",
                    "type": "mrkdwn",
                },
            }
            msg_blocks.append(no_outdated)
            return msg_blocks

        outdated_msg = {
            "type": "section",
            "text": {
                "text": f"*{len(dependencies)} outdated python dependencies found!*",
                "type": "mrkdwn",
            },
        }
        msg_blocks.append(outdated_msg)
        for d in dependencies:
            msg_blocks.append(d.as_slack_section())

        return msg_blocks

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
    """Run the dependency checker."""
    configure_logging(level=logging.DEBUG)
    slack_webhook_url = os.environ["ATLAS_DEPENDENCY_CHECKER_WEBHOOK_URL"]
    DependencyChecker(slack_webhook_url).run()


if __name__ == "__main__":
    main()
