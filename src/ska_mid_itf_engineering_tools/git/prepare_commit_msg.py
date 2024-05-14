"""Tooling to modify the commit message to include the Jira issue ID."""

import argparse
import logging
import re
from typing import Optional

import git


class CommitMsgPreparer:
    """CommitMsgPreparer is used to modify the commit message to include the Jira issue ID."""

    def __init__(
        self,
        excluded_branches=["develop", "master", "release/", "main"],
        included_origins=["git@gitlab.com:ska-telescope"],
        debug=False,
    ) -> None:
        """
        Initialise the CommitMsgPreparer.

        :param excluded_branches: branches to exclude when modifying commit messages.
        :type excluded_branches: List[str]
        :param included_origins: origins which are allowed when modifying commit messages.
        :type included_origins: List[str]
        :param debug: whether log messages should be printed or not.
        :type debug: bool
        """
        self.repo = git.Repo(".")
        self.excluded_branches = excluded_branches
        self.included_origins = included_origins
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.WARNING)

    def jira_issue_id_from_branch(self, branch: str) -> Optional[str]:
        """
        Extract the Jira issue ID from the branch name.

        :param branch: the current branch.
        :type branch: str
        :return: The Jira issue ID if it is present, None otherwise.
        :rtype: Optional[str]
        """
        matches = re.findall(r"^[a-z]+-\d+", branch)
        if len(matches) == 0:
            return None
        return matches[0]

    def commit_contains_jira_issue_id(self, commit: str) -> bool:
        """
        Determine whether the commit contains a Jira issue ID.

        :param commit: The current commit message.
        :type commit: str
        :return: True if it contains a Jira issue ID, False otherwise.
        :rtype: bool
        """
        return re.search(r"^[A-Z]+-\d+", commit) is not None

    def current_branch(self) -> str:
        """
        Get the current branch.

        :return: the current branch.
        :rtype: str
        """
        return self.repo.active_branch.name

    def origin_url(self) -> str:
        """
        Get the origin URL.

        :return: the origin URL.
        :rtype: str
        """
        return self.repo.remote("origin").url

    def prepare_msg(self, commit_message_file: str):
        """
        Prepends the Jira issue ID to the current commit message.

        The Jira issue ID is extracted from the branch name.
        If there is already a Jira issue ID in the commit message,
        or the branch does not contain an issue ID, nothing is done.
        The commit message is also not modified if the branch is an excluded branch
        or if the origin does not match the whitelisted origins.

        :param commit_message_file: the file containing the commit message to modify.
        :type commit_message_file: str
        """
        try:
            branch = self.current_branch()
        except TypeError as te:
            self.logger.warn(
                "Failed to retrieve branch info: not adding Jira ID to commit message."
            )
            # log this at debug level so that we don't log exceptions while creating commits.
            self.logger.debug("Exception: %s", te)
            return

        if any(branch.startswith(excluded) for excluded in self.excluded_branches):
            self.logger.debug("not modifying commit: on excluded branch: %s", branch)
            return

        try:
            origin = self.origin_url()
        except ValueError as ve:
            self.logger.warn(
                "Failed to retrieve origin info: not adding Jira ID to commit message."
            )
            # log this at debug level so that we don't log exceptions while creating commits.
            self.logger.debug("Exception: %s", ve)
            return

        if not any(origin.startswith(url) for url in self.included_origins):
            self.logger.debug(
                "not modifying commit: origin %s does not match included origins %s",
                origin,
                self.included_origins,
            )
            return

        jira_issue_id = self.jira_issue_id_from_branch(branch)
        if jira_issue_id is None:
            self.logger.debug("not modifying commit: branch %s does not match", branch)
            return

        with open(commit_message_file, encoding="utf-8", mode="r+") as commit_msg_file:
            commit_msg = commit_msg_file.read()
            if self.commit_contains_jira_issue_id(commit_msg):
                self.logger.debug("not modifying commit: commit %s does not match", commit_msg)
                return

            modified_commit_msg = f"{jira_issue_id.upper()} - {commit_msg}"
            commit_msg_file.seek(0)
            commit_msg_file.write(modified_commit_msg)
            self.logger.debug("modified commit message to:\n%s", modified_commit_msg)
        return


def main() -> int:
    """
    Run the CommitMsgPreparer.

    :return: The exit code: should always be 0 so that committing does not fail.
    :rtype: int
    """
    parser = argparse.ArgumentParser(
        prog="prepare_commit_msg",
        description="Adds the active Jira Ticket ID to commit message if it is not present.",
    )
    parser.add_argument("commit_file")
    args = parser.parse_args()
    preparer = CommitMsgPreparer()
    preparer.prepare_msg(args.commit_file)
    return 0
