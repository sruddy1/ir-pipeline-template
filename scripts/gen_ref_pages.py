"""Generate API reference pages and navigation for mkdocstrings.

Assumes a src/ layout:
  repo/
    mkdocs.yml
    src/<your_package>/...
    docs/...
    scripts/gen_ref_pages.py
"""

from pathlib import Path
import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

root = Path(__file__).parent.parent
src = root / "src"

# Optional: skip these top-level folders if they exist under src/
SKIP_DIRS = {"tests", "test", "__pycache__"}

for path in sorted(src.rglob("*.py")):
    # Skip cache / tests / etc.
    if any(part in SKIP_DIRS for part in path.parts):
        continue

    module_path = path.relative_to(src).with_suffix("")      # e.g., ir_pkg/foo/bar
    doc_path = path.relative_to(src).with_suffix(".md")      # e.g., ir_pkg/foo/bar.md
    full_doc_path = Path("reference", doc_path)             # e.g., reference/ir_pkg/foo/bar.md

    parts = tuple(module_path.parts)

    if parts[-1] == "__main__":
        continue

    # Treat packages (__init__.py) as section index pages
    if parts[-1] == "__init__":
        parts = parts[:-1]
        full_doc_path = full_doc_path.with_name("index.md")  # .../package/index.md

    nav[parts] = full_doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)  # mkdocstrings identifier
        fd.write(f"::: {ident}\n")

    # Make "edit" links point to real source files, not generated docs
    mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))

# Write literate nav file consumed by mkdocs-literate-nav
#with mkdocs_gen_files.open("SUMMARY.md", "w") as nav_file:
#    nav_file.writelines(nav.build_literate_nav())

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
