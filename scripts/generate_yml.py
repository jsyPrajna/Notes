import yaml
import shutil
import difflib
import mkdocs.utils
from pathlib import Path


default_config_file = Path("default_config.yml")
config_file_path = "../mkdocs.yml"
md_suffix = ".md"
docs_root_path = Path("../docs")

def save_old_yml():
    old_yml = config_file_path
    saved_old_yml = Path("mkdocs_old.yml")
    saved_old_yml.touch(exist_ok=True)

    shutil.copy(str(old_yml), str(saved_old_yml))

    return saved_old_yml


def show_diff(old_file, new_file):

    old_str = old_file.read_text(encoding="utf-8").splitlines(keepends=True)
    new_str = new_file.read_text(encoding="utf-8").splitlines(keepends=True)
    d = difflib.HtmlDiff()
    html_result = Path("diff_result.html");
    html_result.write_text(d.make_file(old_str, new_str))

    return []


def generate():
    default_config = mkdocs.utils.yaml_load(default_config_file.read_text(encoding="utf-8"))
    default_config['nav'] = recursive_scan(docs_root_path)
    fd = open(config_file_path, "w+", encoding="utf-8")
    yaml.dump(default_config, fd)
    fd.close()

    print("generate successfully!!!")


def recursive_scan(path):
    file_list = []

    md_list = list(path.glob("*.md"))
    index_file = path / "index.md"
    if index_file in md_list:
        file_list.append(str(index_file.relative_to(str(docs_root_path))).replace("\\", "/"))
        md_list.remove(index_file)

    for md in md_list:
        file_list.append(str(md.relative_to(str(docs_root_path))).replace("\\", "/"))

    file_list.extend([{sub_path.name: recursive_scan(sub_path)} for sub_path in path.iterdir() if sub_path.is_dir() and not (list(sub_path.rglob("*.md")) == [])])

    return file_list

if __name__ == '__main__':
    old_yml = save_old_yml()
    generate()
    show_diff(old_yml, Path(config_file_path))