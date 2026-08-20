"""Configure the Sphinx documentation builder.

https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import os
from datetime import datetime

from pygit2 import clone_repository

try:
    import tomllib  # type: ignore
except ImportError:
    import tomli as tomllib

ROOT = os.path.dirname(os.path.dirname(__file__))
for url in (
    "https://github.com/neomutt/mutt-language-server",
    "https://github.com/Freed-Wu/tmux-language-server",
    "https://github.com/Freed-Wu/zathura-language-server",
    "https://github.com/termux/termux-language-server",
    "https://github.com/Freed-Wu/requirements-language-server",
    "https://github.com/Freed-Wu/autotools-language-server",
):
    name = os.path.basename(url)
    dir = os.path.join(ROOT, "docs", "examples", name)
    if not os.path.isfile(os.path.join(dir, "README.md")):
        clone_repository(url, dir)

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

# -- Project information -----------------------------------------------------
language = "en"
copyright = "2026-" + str(datetime.now().year)

PROJECT_FILE = os.path.join(ROOT, "pyproject.toml")

with open(PROJECT_FILE, "rb") as f:
    data: dict = tomllib.load(f)
project: dict = data["project"]
author: str = project["authors"][0]["name"]
project: str = project["name"]

# -- General configuration ---------------------------------------------------

html_theme = "furo"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "myst_parser",
    "sphinxcontrib.mermaid",
    "sphinxcontrib.tree_sitter",
    "sphinxcontrib.autofile",
]

myst_heading_anchors = 3

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]
html_favicon = (
    "https://microsoft.github.io/language-server-protocol/img/favicon.svg"
)
