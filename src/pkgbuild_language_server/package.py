r"""Package
===========
"""
import json

from jinja2 import Template
from pyalpm import Handle, Package

from . import CACHE, TEMPLATE

DB = Handle(".", "/var/lib/pacman").get_localdb()


def search_document(pkg: Package, template: str) -> str:
    r"""Search document.

    :param pkg:
    :type pkg: Package
    :param template:
    :type template: str
    :rtype: str
    """
    output = Template(template).render(pkg=pkg)
    return output


def generate_cache() -> None:
    r"""Generate cache.

    :rtype: None
    """
    documents = {x.name: search_document(x, TEMPLATE) for x in DB.pkgcache}
    with open(CACHE, "w") as f:
        json.dump(documents, f)
