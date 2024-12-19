"""DependencyChecker is used to check for stale project dependencies."""

import argparse
import logging
import os
import subprocess

# from collections import OrderedDict
from typing import List

from ska_ser_logging import configure_logging

from .helm_dependency_checker import HelmDependencyChecker
from .log_notifier import LogDependencyNotifier
from .poetry_dependency_checker import PoetryDependencyChecker
from .slack_notifier import SlackDependencyNotifier
from .types import DependencyChecker, DependencyGroup, DependencyNotifier, ProjectInfo


# Split a list into sub-lists of size chunk_size
def split_by_chunks(lst: List[DependencyGroup], chunk_size: int) -> List[DependencyGroup]:
    """
    Split thee dependencies.

    :param lst: The list of dependency group.
    :type lst: List[DependencyGroup]
    :param chunk_size: chuck size of the lists.
    :type chunk_size: int
    :return: List of dependency groups.
    :rtype: List[DependencyGroup]
    """
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def run(checkers: List[DependencyChecker], notifiers: List[DependencyNotifier]):
    """
    Run the dependency checker.

    :param checkers: The list of dependency checkers.
    :type checkers: List[DependencyChecker]
    :param notifiers: The list of dependency notifiers.
    :type notifiers: List[DependencyNotifier]
    """
    project_info = get_project_info()
    # dependency_map: OrderedDict[str : List[DependencyGroup]] = OrderedDict()
    for dc in checkers:
        if not dc.valid_for_project():
            logging.info("skipping %s dependency checker: not valid for this project", dc.name())
            continue
        logging.info("running %s dependency checker", dc.name())
        deps = dc.collect_stale_dependencies()

    for dependency_list in split_by_chunks(deps, 49):
        for n in notifiers:
            n.send_notification(project_info, dependency_list)


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
