"""Send slack notifications for stale project dependencies."""

from collections import OrderedDict
from typing import Dict, List

from slack_sdk import WebhookClient

from .types import Dependency, DependencyGroup, DependencyNotifier, ProjectInfo


class SlackDependencyNotifier(DependencyNotifier):
    """SlackDependencyNotifier is sends slack notifications for stale project dependencies."""

    __slack_webhook_url: str = ""

    def __init__(self, slack_webhook_url: str):
        """
        Initialise the dependency checker.

        :param slack_webhook_url: The webhook URL used to send Slack notifications.
        :type slack_webhook_url: str
        """
        super().__init__()
        self.__slack_webhook_url = slack_webhook_url

    def send_notification(
        self, project_info: ProjectInfo, dependency_map: OrderedDict[str : List[DependencyGroup]]
    ):
        """
        Send a Slack message for a project's stale dependencies.

        :param project_info: The project name and version.
        :type project_info: ProjectInfo
        :param dependency_map: The stale project dependencies.
        :type dependency_map: _type_
        """
        msg_blocks = self.build_slack_message(project_info, dependency_map)
        self.send_slack_message(msg_blocks)

    def build_slack_message(
        self, project_info: ProjectInfo, dependency_map: OrderedDict[str : List[DependencyGroup]]
    ) -> List[Dict]:
        """
        Create a slack message using Block Kit Builder.

        See: https://api.slack.com/block-kit

        :param project_info: The project name and version.
        :type project_info: ProjectInfo
        :param dependency_map: The stale project dependencies.
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
        for checker_name in dependency_map:
            dependency_groups: List[DependencyGroup] = dependency_map[checker_name]
            sections: List[Dict] = []
            if len(dependency_groups) == 1 and dependency_groups[0].group_name == "default":
                sections = self.generate_slack_message_sections_single(
                    checker_name, dependency_groups[0].dependencies
                )
            else:
                sections = self.generate_slack_message_sections_groups(
                    checker_name, dependency_groups
                )
            msg_blocks.extend(sections)
        return msg_blocks

    def generate_slack_message_sections_groups(
        self, checker_name: str, dependency_groups: List[DependencyGroup]
    ) -> List[Dict]:
        """
        Generate Slack message sections for the dependencies.

        :param checker_name: Name of the associated dependency checker.
        :type checker_name: str
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
                    "text": f"*{checker_name}: No outdated dependencies found.*",
                    "type": "mrkdwn",
                },
            }
            return [no_outdated]

        outdated_msg = [
            {
                "type": "section",
                "text": {
                    "text": f"*{checker_name}: {total_deps} outdated dependencies found!*",
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
        self, checker_name: str, dependencies: List[Dependency]
    ) -> List[Dict]:
        """
        Generate Slack message sections for the dependencies.

        :param checker_name: Name of the associated dependency checker.
        :type checker_name: str
        :param dependencies: The stale dependencies.
        :type dependencies: List[Dependency]
        :return: A list of Slack message sections.
        :rtype: List[Dict]
        """
        if len(dependencies) == 0:
            no_outdated = {
                "type": "section",
                "text": {
                    "text": "*No outdated f{name} dependencies found.*",
                    "type": "mrkdwn",
                },
            }
            return [no_outdated]

        outdated_msg = [
            {
                "type": "section",
                "text": {
                    "text": f"*{len(dependencies)} outdated {checker_name} dependencies found!*",
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
