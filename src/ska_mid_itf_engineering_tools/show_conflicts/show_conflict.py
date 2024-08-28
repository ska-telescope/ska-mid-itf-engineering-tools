#@dataclass
#class Repositories:
import gitlab
import toml
from time import sleep
def main():
    '''gitlab_base_link = "ska-telescope/"
    repo_list = ["aiv/ska-mid-itf-environments",
                "ska-mid-itf-engineering-tools"]

    gl = gitlab.Gitlab("https://gitlab.com/")
    project = gl.projects.get(gitlab_base_link + repo_list[1])

    print(str(project.files.get(file_path='pyproject.toml', ref='main').decode(), "utf-8"))'''
    dict =  dict()
    with open("pyproject.toml","r") as f:
        toml_file = toml.load(f)
        dict.update(toml_file["tool"]["poetry"]["dependencies"])
        dict.update(toml_file["tool"]["poetry"]["group"]["docs"]["dependencies"])
        dict.update(toml_file["tool"]["poetry"]["group"]["dev"]["dependencies"])
        for k,v in dict.items():
            print(f"{k},{v}")

if __name__ == "__main__":
    main()