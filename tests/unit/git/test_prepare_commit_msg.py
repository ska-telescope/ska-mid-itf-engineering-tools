from dataclasses import dataclass
import os
import pathlib
import tempfile
from typing import Any, Generator, Iterator
from unittest.mock import MagicMock, PropertyMock

import pytest
from unittest.mock import patch
from ska_mid_itf_engineering_tools.git.prepare_commit_msg import CommitMsgPreparer


__testdata_dir = "tests/unit/git/testdata"

@dataclass
class CommitFixture:
    name: str
    path: str
    contents: str
    valid: bool


@pytest.fixture(params=[
    ("short_commit_without_jira_ticket.txt", True),
    ("short_commit_with_jira_ticket.txt", False),
    ("multiline_commit_without_jira_ticket.txt", True),
    ("multiline_commit_with_jira_ticket.txt", False),
])
def commit_fixture(request) -> Generator[CommitFixture, None, None]:
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
    name: str
    jira_issue: str = ""
    valid: bool = False

@pytest.fixture(params=[
    BranchFixture("at-1234-test-branch", valid=True, jira_issue="AT-1234"), 
    BranchFixture("map-1", valid=True, jira_issue="MAP-1"), 
    BranchFixture("main"), 
    BranchFixture(""), 
    BranchFixture("at3232")
])
def branch_fixture(request) -> Generator[BranchFixture, None, None]:
    yield request.param

def test_prepare_commmit_msg(commit_fixture: CommitFixture, branch_fixture: BranchFixture):
    preparer = CommitMsgPreparer(debug=True)
    with patch.object(preparer, 'repo') as mock_repo:
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
