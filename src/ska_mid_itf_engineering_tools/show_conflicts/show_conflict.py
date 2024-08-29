#@dataclass
#class Repositories:
import gitlab
import toml
from time import sleep
from collections import defaultdict

def read_toml_to_dict(dictionary, toml_kv)-> dict:
    for k, v in dict(toml_kv).items():
        if (k not in dictionary):
            dictionary[k] = [v]
            print(f"{k}={v}")
        else:
            dictionary[k].append(v)
            print(f"****Append {v}")
    return dictionary

def detect_conflicts(dictionary)-> dict:
    confct_dependencies = {}
    for k,v_list in dictionary.items():
        if (len({}.fromkeys(v_list)) != len(v_list)):
            confct_dependencies.append(k, v_list)
    return confct_dependencies

def main():
    gitlab_base_link = "ska-telescope/"
    repo_list = ["aiv/ska-mid-itf-environments",
                "ska-mid-itf-engineering-tools"]

    gl = gitlab.Gitlab("https://gitlab.com/")
    tmp_dict = {}
    for repo in repo_list:
        project = gl.projects.get(gitlab_base_link + repo)
        #print(str(project.files.get(file_path='pyproject.toml', ref='main').decode(), "utf-8"))
        print(f"========================{repo}========================")
        with open("pyproject.toml","r") as f:
            toml_file = toml.load(f)
            read_toml_to_dict(tmp_dict, toml_file["tool"]["poetry"]["dependencies"])
            read_toml_to_dict(tmp_dict, toml_file["tool"]["poetry"]["group"]["docs"]["dependencies"])
            read_toml_to_dict(tmp_dict, toml_file["tool"]["poetry"]["group"]["dev"]["dependencies"])
            #print(f"{k}={v}")
            for k,v in tmp_dict.items():
                print(f"{k},{v}")

if __name__ == "__main__":
    main()