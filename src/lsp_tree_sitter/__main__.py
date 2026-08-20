from argparse import ArgumentParser

try:
    import shtab
except ImportError:
    from . import _shtab as shtab

from . import __version__


def get_parser(version: str, *args, **kwargs):
    r"""Get a parser for unit test.

    :param version:
    :type version: str
    :param args:
    :param kwargs:
    """
    parser = ArgumentParser(*args, **kwargs)
    shtab.add_argument_to(parser)
    parser.add_argument("--version", version=version, action="version")
    parser.add_argument(
        "--color",
        choices=["auto", "always", "never"],
        default="auto",
        help="when to display color. default: %(default)s",
    )

    parser.add_argument(
        "--lookup",
        nargs="*",
        default=(),
        help="lookup help documentation. default: %(default)s",
    )
    parser.add_argument(
        "--type",
        default="option",
        help="lookup help documentation for which type. default: %(default)s",
    )
    parser.add_argument(
        "--path",
        default="",
        help="lookup help documentation for which file. default: %(default)s",
    ).complete = shtab.FILE  # type: ignore
    parser.add_argument(
        "--complete",
        action="store_true",
        help="lookup help documentation for prefix. default: %(default)s",
    )

    parser.add_argument(
        "--check",
        nargs="*",
        default=(),
        help="check file's errors and warnings. default: %(default)s",
    ).complete = shtab.FILE  # type: ignore
    parser.add_argument(
        "--message-format",
        default="{file}:{range}: {severity}: {message}",
        help="error message format. default: %(default)s",
    )

    parser.add_argument(
        "--convert",
        nargs="*",
        default=(),
        help="convert files to output format. default: %(default)s",
    ).complete = shtab.FILE  # type: ignore
    parser.add_argument(
        "--output-format",
        choices=["json", "yaml", "toml"],
        default="json",
        help="output format. default: %(default)s",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="indent json, yaml. default: %(default)s",
    )

    # from pygls.cls import start_server
    parser.add_argument(
        "--tcp",
        action="store_true",
        help="start a TCP server. default: %(default)s",
    )
    parser.add_argument(
        "--ws",
        action="store_true",
        help="start a WebSocket server. default: %(default)s",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="bind to this address. default: %(default)s",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8888,
        help="bind to this port. default: %(default)s",
    )

    return parser


def main():
    r"""Usage:
    .. code-block: python
    from lsp_tree_sitter.__main__ import get_parser

    parser = get_parser(__version__)
    args = parser.parse_args()

    from .server import XXXLanguageServer as Server

    server = Server(version=__version__)
    server.run(args)
    """
    parser = get_parser(__version__)
    args = parser.parse_args()

    print(args)


if __name__ == "__main__":
    main()
