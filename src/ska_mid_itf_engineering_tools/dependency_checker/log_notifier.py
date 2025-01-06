"""Log messages for stale project dependencies."""

from collections import OrderedDict
from typing import List

from .types import DependencyGroup, DependencyNotifier, ProjectInfo


class LogDependencyNotifier(DependencyNotifier):
    """LogDependencyNotifier is used to log messages for stale project dependencies."""

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
        msg = self.build_log_message(project_info, dependency_map)
        self.logger.debug("Stale dependencies:\n%s", msg)
        print(f"=============={project_info}========================")
        print(*dependency_map, sep="\n")
        print("==================================================")

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
        for checker_name, dependency_groups in dependency_map.items():
            if len(dependency_groups) == 1 and dependency_groups[0].group_name == "default":
                msg.append(self.build_log_message_single(checker_name, dependency_groups[0]))
            else:
                msg.append(self.build_log_message_groups(checker_name, dependency_groups))
        return "\n".join(msg)

    def build_log_message_single(
        self, checker_name: str, dependency_group: DependencyGroup
    ) -> str:
        """
        Build a log message for a single dependency groups.

        :param checker_name: Name of the dependency checker.
        :type checker_name: str
        :param dependency_group: The dependency group.
        :type dependency_group: DependencyGroup
        :return: The log message.
        :rtype: str
        """
        msg = [
            "",
            "",
            f"{checker_name} -- {len(dependency_group.dependencies)} stale dependencies!",
            "",
        ]
        for dep in dependency_group.dependencies:
            msg.append(f"{dep.name}: {str(dep.project_version)} --> {str(dep.available_version)}")
        return "\n".join(msg)

    def build_log_message_groups(
        self, checker_name: str, dependency_groups: List[DependencyGroup]
    ) -> str:
        """
        Build a log message for dependency groups.

        :param checker_name: Name of the dependency checker.
        :type checker_name: str
        :param dependency_groups: The dependency groups.
        :type dependency_groups: List[DependencyGroup]
        :return: The log message.
        :rtype: str
        """
        total_deps = sum(len(dg.dependencies) for dg in dependency_groups)
        msg = ["", "", f"{checker_name} -- {total_deps} stale dependencies!", ""]
        for dg in dependency_groups:
            msg.extend(
                ["", f"{dg.group_name} Chart -- {len(dg.dependencies)} stale dependencies!"]
            )
            for dep in dg.dependencies:
                msg.append(
                    f"{dep.name}: {str(dep.project_version)} --> {str(dep.available_version)}"
                )
        return "\n".join(msg)
