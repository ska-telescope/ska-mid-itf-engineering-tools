"""Detect dependency conflicts between two repositories."""

import logging

import gitlab
import toml
from ska_ser_logging import configure_logging


def get_unique_repos(dictionary: dict, toml_kv: dict) -> dict:
    """
    Get unique repositories.

    :param dictionary: The dictionary containing poetry dependencies and their versions.
    :type dictionary: dict
    :param toml_kv: The dictionary poetry toml file dependencies.
    :type toml_kv: dict
    :return: A dictionary containing poetry dependency and version.
    :rtype: dict
    """
    for k, v in dict(toml_kv).items():
        if v != "*":
            if not isinstance(v, str):
                v = v["version"]
            if k not in dictionary:
                dictionary[k] = [v]
            else:
                # Only append unique i.e. different versions of same library
                if v not in dictionary[k]:
                    dictionary[k].append(v)
    return dictionary


def DetectConflicts(repo1: str, repo2: str):
    """
    Detect conflicts between two repositories.

    :param repo1: The dictionary containing poetry dependencies and their versions.
    :type repo1: str
    :param repo2: The dictionary containing poetry dependencies and their versions.
    :type repo2: str
    """
    configure_logging(level=logging.INFO)
    repo_list = [repo1, repo2]
    gl = gitlab.Gitlab("https://gitlab.com/")
    tmp_dict = {}
    for repo in repo_list:
        repo = repo.replace("https://gitlab.com/", "")
        project = gl.projects.get(repo)
        pytoml_file_contents = (
            project.files.get(file_path="pyproject.toml", ref="main").decode().decode()
        )

        toml_file = toml.loads(pytoml_file_contents)
        if "tool.poetry.dependencies" in pytoml_file_contents:
            get_unique_repos(tmp_dict, toml_file["tool"]["poetry"]["dependencies"])
        if "tool.poetry.group.docs.dependencies" in pytoml_file_contents:
            get_unique_repos(
                tmp_dict, toml_file["tool"]["poetry"]["group"]["docs"]["dependencies"]
            )
        if "tool.poetry.group.dev.dependencies" in pytoml_file_contents:
            get_unique_repos(tmp_dict, toml_file["tool"]["poetry"]["group"]["dev"]["dependencies"])

    print(f"*** Dependency conflicts between {repo_list[0]} and {repo_list[1]} ***")

    print("-------------------------------------------------------------------------")
    for module, conflicting_versions in tmp_dict.items():
        if len(conflicting_versions) > 1:
            print(f"{module}, conflict={conflicting_versions}")
    exit()
