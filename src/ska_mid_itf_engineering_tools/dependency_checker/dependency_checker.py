"""DependencyChecker is used to check for stale project dependencies."""

import argparse
import logging
import os
import subprocess
from collections import OrderedDict
from typing import List

from ska_ser_logging import configure_logging

from .helm_dependency_checker import HelmDependencyChecker
from .log_notifier import LogDependencyNotifier
from .poetry_dependency_checker import PoetryDependencyChecker
from .slack_notifier import SlackDependencyNotifier
from .types import Dependency, DependencyChecker, DependencyGroup, DependencyNotifier, ProjectInfo


def run(checkers: List[DependencyChecker], notifiers: List[DependencyNotifier]):
    """
    Run the dependency checker.

    :param checkers: The list of dependency checkers.
    :type checkers: List[DependencyChecker]
    :param notifiers: The list of dependency notifiers.
    :type notifiers: List[DependencyNotifier]
    """
    project_info = get_project_info()
    dependency_map: OrderedDict[str : List[DependencyGroup]] = OrderedDict()
    chunk_size = 10
    i = 0
    for dc in checkers:
        if not dc.valid_for_project():
            logging.info("skipping %s dependency checker: not valid for this project", dc.name())
            continue
        logging.info("running %s dependency checker", dc.name())
        deps = dc.collect_stale_dependencies()
        dependency_map[dc.name()] = deps
        dp_list:List[Dependency] = []
        dg_list:List[DependencyGroup]=[]
        for n in notifiers:
            print(f".......................project_info={project_info}.....................i={i}")
            for dg in deps:
                for dp in dg.dependencies:
                    dp_list.append(Dependency(dp.name, str(dp.project_version), str(dp.available_version)))
                    if (i%chunk_size==0):
                        print(">>>>>>>>>>>>Sending>>>>>>>>>>>")
                        print(*dp_list, sep="||||")
                        dg_list.append(DependencyGroup(dp_list))
                        dependency_map[dc.name()] = ( dg_list  )
                        print(f"000*********type(deps)={type(deps[0])}")
                        print(f"111*********type(dg_list)={type ( dg_list[0]  )}")
                        n.send_notification(project_info, dependency_map)
                        print("=============Done=============")
                        dp_list.clear()
                        dg_list.clear()

                    i += 1


def get_project_info() -> ProjectInfo:
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
        default=["poetry", "helm"],
    )
    parser.add_argument(
        "--dependency-notifiers",
        nargs="+",
        help="Dependency notifiers to run.",
        default=["slack", "log"],
    )
    args = parser.parse_args()
    dependency_checkers: List[DependencyChecker] = []
    for d in args.dependency_checkers:
        if d == "poetry":
            dependency_checkers.append(PoetryDependencyChecker())
        elif d == "helm":
            dependency_checkers.append(HelmDependencyChecker())
        else:
            raise RuntimeError(f"Unsupported checker {d}")

    dependency_notifiers: List[DependencyNotifier] = []
    for d in args.dependency_notifiers:
        if d == "slack":
            if args.dry_run:
                logging.info("dry-run mode: not enabling SlackDependencyNotifier")
                continue
            slack_webhook_url = os.environ["DEPENDENCY_CHECKER_WEBHOOK_URL"]
            dependency_notifiers.append(
                SlackDependencyNotifier(slack_webhook_url=slack_webhook_url)
            )
        elif d == "log":
            dependency_notifiers.append(LogDependencyNotifier())
        else:
            raise RuntimeError(f"Unsupported checker {d}")

    run(checkers=dependency_checkers, notifiers=dependency_notifiers)


if __name__ == "__main__":
    main()
