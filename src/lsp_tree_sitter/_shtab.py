r"""Fake shtab
==============
"""

from argparse import ArgumentParser
from typing import Any

FILE = None
DIRECTORY = DIR = None


def add_argument_to(parser: ArgumentParser, *args: Any, **kwargs: Any):
    r"""Add argument to.

    :param parser:
    :type parser: ArgumentParser
    :param args:
    :type args: Any
    :param kwargs:
    :type kwargs: Any
    """
    from argparse import Action

    Action.complete = None  # type: ignore
    return parser
