import yaml
import mkdocs.utils
from pathlib import Path


default_config_file = Path("default_config.yml")
generated_config_file = "../mkdocs.yml"
md_suffix = ".md"
docs_root_path = Path("../docs")


def generate():
    default_config = mkdocs.utils.yaml_load(default_config_file.read_text(encoding="utf-8"))
    default_config['nav'] = recursive_scan(docs_root_path)
    fd = open(generated_config_file, "w+", encoding="utf-8")
    yaml.dump(default_config, fd)
    fd.close()

    print("generate successfully!!!")


def recursive_scan(path):
    file_list = []

    # if has index.md, firstly add it and then remove it from subpath list
    subpath_list = [sub_path for sub_path in path.iterdir()]

    index_file = path / "index.md";
    if index_file.is_file():
        file_list.append(str(index_file.relative_to(str(docs_root_path))).replace("\\", "/"))
        subpath_list.remove(index_file)

    for sub_path in subpath_list:
        if sub_path.is_dir() and not (list(sub_path.rglob("*.md")) == []):
            file_list.append({sub_path.name: recursive_scan(sub_path)})
        elif sub_path.is_file() and sub_path.suffix == md_suffix:
            file_list.append(str(sub_path.relative_to(str(docs_root_path))).replace("\\", "/"))
    return file_list

if __name__ == '__main__':
    generate()
