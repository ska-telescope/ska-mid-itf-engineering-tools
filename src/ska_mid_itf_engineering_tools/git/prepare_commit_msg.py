import argparse
import logging
import re
from typing import List
import git

class CommitMsgPreparer:

    def __init__(self,
                 excluded_branches=["develop", "master", "release/", "main"],
                 included_origins=["git@gitlab.com:ska-telescope"],
                 debug=False,
    ) -> None:
        self.repo = git.Repo(".")
        self.excluded_branches = excluded_branches
        self.included_origins = included_origins
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.WARNING)

    def branch_jira_ticket_matches(self, branch: str) -> List[str]:
        return re.findall("^[a-z]+-\d+", branch)

    def commit_contains_jira_ticket(self, commit: str) -> str:
        return re.search("^[A-Z]+-\d+", commit) is not None

    def current_branch(self) -> str:
        # git rev-parse --abbrev-ref HEAD
        return self.repo.active_branch.name

    def origin_url(self) -> str:
        # git config --get remote.origin.url
        return self.repo.remote("origin").url

    def prepare_msg(self, messageFile: str):
        ## This is meant to use with the prepare-commit-msg hook on a global configuration.
        ## This script uses a whitelist `IncludedOrigins` so it would only work for explicit sources,
        ## and also uses a blacklist for branches to ignore `ExcludedBranches` 
        ## that way it would only work for the projects and branches that you want
        branch = self.current_branch()
        if any(branch.startswith(excluded) for excluded in self.excluded_branches):
            self.logger.debug("not modifying commit: on excluded branch: %s", branch)
            return

        origin = self.origin_url()
        if not any(origin.startswith(url) for url in self.included_origins):
            self.logger.debug("not modifying commit: origin %s does not match included origins %s", origin, self.included_origins)
            return

        matches: List[str]  = self.branch_jira_ticket_matches(branch)
        if len(matches) == 0:
            self.logger.debug("not modifying commit: branch %s does not match", branch)
            return

        with open(messageFile, encoding="utf-8", mode="r+") as commit_msg_file:
            commit_msg = commit_msg_file.read()
            if self.commit_contains_jira_ticket(commit_msg):
                self.logger.debug("not modifying commit: commit %s does not match", commit_msg)
                return
            
            modified_commit_msg = f"{matches[0].upper()} - {commit_msg}"
            commit_msg_file.seek(0)
            commit_msg_file.write(modified_commit_msg)
            self.logger.debug("modified commit message to:\n%s", modified_commit_msg)
        return

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="prepare_commit_msg",
        description="Adds the active Jira Ticket ID to commit message if it is not present."
    )
    parser.add_argument("commit_file")
    args = parser.parse_args()
    preparer = CommitMsgPreparer()
    preparer.prepare_msg(args.commit_file)
    return 0
