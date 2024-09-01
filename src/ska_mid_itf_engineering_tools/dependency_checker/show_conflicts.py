"""Detect dependency conflicts between two repositories."""

import json
from collections import defaultdict

import gitlab
import toml


def detect_conflicts(dictionary, toml_kv) -> dict:
    for k, v in dict(toml_kv).items():
        if v != "*":
            if type(v) != str:
                v = v["version"]
            if k not in dictionary:
                dictionary[k] = [v]
            else:
                # Only append unique i.e. different versions of same library
                if v not in dictionary[k]:
                    dictionary[k].append(v)
            print(f"{k}={dictionary[k]}")
    return dictionary


def main():
    """This method is designed to only process two repositories at a time."""
    gitlab_base_link = "ska-telescope/"
    # "aiv/ska-mid-itf-environments",
    repo_list = ["ska-mid-itf-engineering-tools", "ska-te-mid-skysimctl"]

    gl = gitlab.Gitlab("https://gitlab.com/")
    tmp_dict = {}
    for repo in repo_list:
        project = gl.projects.get(gitlab_base_link + repo)
        pytoml_file_contents = (
            project.files.get(file_path="pyproject.toml", ref="main").decode().decode()
        )
        print(f"========================{repo}========================")
        toml_file = toml.loads(pytoml_file_contents)
        if "tool.poetry.dependencies" in pytoml_file_contents:
            detect_conflicts(tmp_dict, toml_file["tool"]["poetry"]["dependencies"])
        if "tool.poetry.group.docs.dependencies" in pytoml_file_contents:
            detect_conflicts(
                tmp_dict, toml_file["tool"]["poetry"]["group"]["docs"]["dependencies"]
            )
        if "tool.poetry.group.dev.dependencies" in pytoml_file_contents:
            detect_conflicts(tmp_dict, toml_file["tool"]["poetry"]["group"]["dev"]["dependencies"])
    print(f"*** Detected conflicts... between {repo_list[0]} and {repo_list[1]} *** ")
    print("-------------------------------------------------------------------------")
    for module, conflicting_versions in tmp_dict.items():
        if len(conflicting_versions) > 1:
            print(f"{module}, conflicting_versions={conflicting_versions}")


if __name__ == "__main__":
    main()
