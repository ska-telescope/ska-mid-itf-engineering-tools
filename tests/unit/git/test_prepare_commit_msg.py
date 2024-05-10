"""Tests for prepare_commit_msg.py."""

import os
import pathlib
import tempfile
from dataclasses import dataclass
from typing import Any, Generator
from unittest.mock import patch

import pytest

from ska_mid_itf_engineering_tools.git.prepare_commit_msg import CommitMsgPreparer

__testdata_dir = "tests/unit/git/testdata"


@dataclass
class CommitFixture:
    """CommitFixture contains details about the commit being tested."""

    name: str
    path: str
    contents: str
    valid: bool


@pytest.fixture(
    params=[
        ("short_commit_without_jira_ticket.txt", True),
        ("short_commit_with_jira_ticket.txt", False),
        ("multiline_commit_without_jira_ticket.txt", True),
        ("multiline_commit_with_jira_ticket.txt", False),
    ]
)
def commit_fixture(request: Any) -> Generator[CommitFixture, None, None]:
    """
    Yield a fixture containing details about the commit.

    :param request: pytest fixture containing commit params.
    :type request: Any
    :yield: a fixture containing details about the commit.
    :rtype: Generator[CommitFixture, None, None]
    """
    commit_file_name: str = request.param[0]
    commit_valid: bool = request.param[1]
    with open(pathlib.Path(__testdata_dir, commit_file_name), encoding="utf-8") as f:
        contents = f.read()
    temp_dir = tempfile.mkdtemp("test-prepare-commit-msg")
    temp_path = pathlib.Path(temp_dir, commit_file_name)
    with open(temp_path, encoding="utf-8", mode="w") as f:
        f.write(contents)
    yield CommitFixture(commit_file_name, temp_path, contents, commit_valid)
    os.remove(temp_path)
    os.rmdir(temp_dir)


@dataclass
class BranchFixture:
    """BranchFixture contains details about the branch being tested."""

    name: str
    jira_issue: str = ""
    valid: bool = False


@pytest.fixture(
    params=[
        BranchFixture("at-1234-test-branch", valid=True, jira_issue="AT-1234"),
        BranchFixture("map-1", valid=True, jira_issue="MAP-1"),
        BranchFixture("main"),
        BranchFixture(""),
        BranchFixture("at3232"),
    ]
)
def branch_fixture(request: Any) -> Generator[BranchFixture, None, None]:
    """
    Yield a fixture containing details about the branch.

    :param request: pytest fixture containing branch params.
    :type request: Any
    :yield: a fixture containing details about the branch.
    :rtype: Generator[BranchFixture, None, None]
    """
    yield request.param


def test_prepare_commmit_msg(commit_fixture: CommitFixture, branch_fixture: BranchFixture):
    """
    Test the prepare_commit_msg script.

    :param commit_fixture: Fixture containing details about the commit message.
    :type commit_fixture: CommitFixture
    :param branch_fixture: Fixture containing details about the branch.
    :type branch_fixture: BranchFixture
    """
    preparer = CommitMsgPreparer(debug=True)
    with patch.object(preparer, "repo") as mock_repo:
        mock_repo.active_branch.name = branch_fixture.name
        mock_repo.remote.return_value.url = "git@gitlab.com:ska-telescope"
        preparer.prepare_msg(commit_fixture.path)
        with open(commit_fixture.path, encoding="utf-8") as result_file:
            result = result_file.read()
        if commit_fixture.valid and branch_fixture.valid:
            expected = f"{branch_fixture.jira_issue} - {commit_fixture.contents}"
            assert expected == result
        else:
            assert commit_fixture.contents == result
