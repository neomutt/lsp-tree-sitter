r"""Provide ``__version__`` for
`importlib.metadata.version() <https://docs.python.org/3/library/importlib.metadata.html#distribution-versions>`_.
"""
import os

from platformdirs import user_cache_dir, user_config_dir

from ._version import __version__, __version_tuple__  # type: ignore

__all__ = ["__version__", "__version_tuple__"]

PATH = os.path.join(user_config_dir("pacman"), "template.md.j2")
CACHE = user_cache_dir("pacman.json")
CONFIG = {
    "template": PATH,
    "cache": CACHE,
}
if not os.path.exists(PATH):
    PATH = os.path.join(
        os.path.join(
            os.path.join(os.path.dirname(__file__), "assets"), "jinja2"
        ),
        "template.md.j2",
    )
with open(PATH, "r") as f:
    TEMPLATE = f.read()
