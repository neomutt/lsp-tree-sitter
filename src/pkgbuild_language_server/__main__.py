r"""This module can be called by
`python -m <https://docs.python.org/3/library/__main__.html>`_.
"""
import logging
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from contextlib import suppress
from datetime import datetime

from . import CONFIG
from . import __name__ as NAME
from . import __version__

logger = logging.getLogger(__name__)
NAME = NAME.replace("_", "-")
VERSION = rf"""{NAME} {__version__}
Copyright (C) {datetime.now().year}
Written by Wu Zhenyu
"""
EPILOG = """
Report bugs to <wuzhenyu@ustc.edu>.
"""


def get_parser():
    r"""Get a parser for unit test."""
    parser = ArgumentParser(
        epilog=EPILOG,
        formatter_class=RawDescriptionHelpFormatter,
    )
    with suppress(ImportError):
        import shtab

        shtab.add_argument_to(parser)
    parser.add_argument("--version", version=VERSION, action="version")
    parser.add_argument(
        "--print-config",
        choices=["template", "cache", "all"],
        help="print config value",
    )
    parser.add_argument(
        "--generate-cache",
        action="store_true",
        help="generate cache for archlinux packages",
    )
    parser.add_argument(
        "--check",
        nargs="*",
        default=[],
        help="check file's errors and warnings",
    )
    parser.add_argument(
        "--format",
        nargs="*",
        default=[],
        help="format files",
    )
    parser.add_argument(
        "--color",
        choices=["auto", "always", "never"],
        default="auto",
        help="when to display color",
    )
    return parser


def main():
    r"""Parse arguments and provide shell completions."""
    parser = get_parser()
    args = parser.parse_args()

    if args.print_config:
        print(
            CONFIG.get(
                args.print_config,
                "\n".join([k + ": " + v for k, v in CONFIG.items()]),
            )
        )
        return None
    if args.generate_cache:
        from documents.package import generate_cache

        try:
            generate_cache()
        except ImportError as e:
            logger.error(f"Please install {e.name}!")
        return None

    from .parser import parse
    from .utils import check

    result = check(args.check, parse, args.color)
    if args.check:
        exit(result)

    from .server import PKGBUILDLanguageServer

    PKGBUILDLanguageServer(NAME, __version__).start_io()


if __name__ == "__main__":
    main()
