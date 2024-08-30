#@dataclass
#class Repositories:
import gitlab
import toml
from time import sleep
from collections import defaultdict
import json

def read_toml_to_dict(dictionary, toml_kv)-> dict:
    for k, v in dict(toml_kv).items():
        if (k not in dictionary):
            dictionary[k] = [v]
            #print(f"{k}={v}")
        else:
            dictionary[k].append(v)
    return dictionary

def detect_conflicts(dictionary)-> dict:
    confct_dependencies = {}
    for k,v_list in dictionary.items():
        print(f"k={k} ||| v_list={v_list}  type={type(v_list[0])}")
        if(type(v_list[0]) != str):
            tmp_lst = []
            for v in v_list:
                print(f">>>>>>>>>>>>>>>>>>type={(v['version'])}")
                tmp_lst += v["version"]
                print(f"json={v['version']}")
            confct_dependencies[k] = tmp_lst
        else:
             print(f"<<<<<<<<<<<<<<<<< v_list={v_list}")
             if (len(set(confct_dependencies)) != len(confct_dependencies)): #not unique
                confct_dependencies[k] = v_list
             else:
                 confct_dependencies = {}  
            
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
    for module in detect_conflicts(tmp_dict):
        print(f"$$$$${module}")

if __name__ == "__main__":
    main()