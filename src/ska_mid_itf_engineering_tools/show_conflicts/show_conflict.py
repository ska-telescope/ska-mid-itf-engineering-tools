import gitlab
import toml
from time import sleep
from collections import defaultdict
import json

def detect_conflicts(dictionary, toml_kv)-> dict:
    for k, v in dict(toml_kv).items():
        if (k not in dictionary):
            dictionary[k] = [v]
        else:
            #Only append unique i.e. different versions of same library
            if(v not in dictionary[k]):
                dictionary[k].append(v)
        print(f"{k}={dictionary[k]}")
    return dictionary

def main():
    gitlab_base_link = "ska-telescope/"
    #"aiv/ska-mid-itf-environments",
    repo_list = ["ska-mid-itf-engineering-tools",
                "ska-te-mid-skysimctl"]

    gl = gitlab.Gitlab("https://gitlab.com/")
    tmp_dict = {}
    for repo in repo_list:
        project = gl.projects.get(gitlab_base_link + repo)
        pytoml_file_contents = project.files.get(file_path='pyproject.toml', ref='main').decode().decode()
        print(f"========================{repo}========================")
        toml_file = toml.loads(pytoml_file_contents)
        detect_conflicts(tmp_dict, toml_file["tool"]["poetry"]["dependencies"])
        detect_conflicts(tmp_dict, toml_file["tool"]["poetry"]["group"]["docs"]["dependencies"])
        #if("dev" in toml_file):
        detect_conflicts(tmp_dict, toml_file["tool"]["poetry"]["group"]["dev"]["dependencies"])
    print("Detected conflicts...")
    for module, versions_list in tmp_dict.items():
        print(f"{module}, versions_list={versions_list}")

if __name__ == "__main__":
    main()