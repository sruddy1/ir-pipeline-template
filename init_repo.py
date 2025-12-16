#!/usr/bin/env python
# coding: utf-8

# In[36]:


import re
import sys
from pathlib import Path
from ruamel.yaml import YAML
import toml
from datetime import datetime


# In[ ]:


def normalize_package_name(name: str) -> str:
    """
    Convert a repo name into a valid-ish Python package name:
    - lowercase
    - spaces/dashes -> underscore
    - remove non [a-z0-9_]
    - collapse multiple underscores
    - ensure starts with letter or underscore
    """
    s = name.strip().lower()
    s = re.sub(r"[\s\-]+", "_", s)
    s = re.sub(r"[^a-z0-9_]", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s or not re.match(r"^[a-z_]", s):
        s = f"pkg_{s}" if s else "pkg"
    return s


def update_pyproject(root: Path) -> None:
    file = Path(root) / Path("pyproject.toml")
    if not file.exists():
        raise FileNotFoundError(
            f"pyproject.toml file not found at {file}. "
        )
    tml = toml.load(file)
    tml["project"]["name"] = normalize_package_name(root.name)
    with open(file, "w") as toml_file:
        toml.dump(tml, toml_file)
    

def update_mkdocs(root: Path) -> None:
    yaml = YAML()
    yaml.preserve_quotes = True
    file = Path(root) / Path("mkdocs.yml")
    if not file.exists():
        raise FileNotFoundError(
            f"mkdocs.yml file not found at {file}. "
        )
    with file.open("r") as f:
        yml = yaml.load(f)
    yml["site_name"] = root.name
    with file.open("w") as f:
        yaml.dump(yml, f)


def update_package_name(root: Path) -> None:
    old_dir = Path(root) / Path("src/ir_pipeline_template")
    new_dir = Path(root) / Path("src") / normalize_package_name(root.name)

    if not old_dir.exists():
        raise RuntimeError(f"Template source directory does not exist: {old_dir}")
    if new_dir.exists():
        raise RuntimeError(f"New source directory already exists: {new_dir}")

    old_dir.rename(new_dir)


SENTINEL_FILE = ".repo_initialized"
def main() -> int:
    repo_root = Path.cwd()
    if not repo_root.exists():
        print(f"ERROR: repo root not found: {repo_root}", file=sys.stderr)
        return 2

    sentinel = repo_root / SENTINEL_FILE
    if sentinel.exists():
        print(
            f"ERROR: Repo already initialized (found {SENTINEL_FILE}).\n"
            f"Delete {SENTINEL_FILE} if you really want to run this again.",
            file=sys.stderr,
        )
        return 1

    update_package_name(repo_root)
    update_pyproject(repo_root)
    update_mkdocs(repo_root)

    #this ensures the script is not run a second time
    sentinel.write_text(
        f"Initialized successfully at {datetime.now().isoformat()}\n",
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# In[ ]:


# def main() -> int:
#     parser = argparse.ArgumentParser(
#         description="Initialize a template repo: rename src package, update mkdocs.yml + pyproject.toml."
#     )
#     parser.add_argument(
#         "--repo-root",
#         type=Path,
#         default=Path.cwd(),
#         help="Repo root (default: current working directory). Run this from the repo root.",
#     )
#     parser.add_argument(
#         "--site-name",
#         type=str,
#         default=None,
#         help="Override mkdocs site_name (default: repo folder name).",
#     )
#     parser.add_argument(
#         "--project-name",
#         type=str,
#         default=None,
#         help='Override pyproject [project].name (default: repo folder name).',
#     )
#     parser.add_argument(
#         "--package-name",
#         type=str,
#         default=None,
#         help="Override python package dir name under src/ (default: normalized repo name).",
#     )
#     parser.add_argument(
#         "--no-replace",
#         action="store_true",
#         help="Do not replace old package references across repo files.",
#     )
#     args = parser.parse_args()
#     repo_root: Path = args.repo_root.resolve()
    


# In[ ]:




