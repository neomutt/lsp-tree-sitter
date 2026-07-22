from argparse import ArgumentParser

try:
    import shtab
except ImportError:
    from . import _shtab as shtab

from . import __version__


def get_parser(version: str, *args, **kwargs):
    r"""Get a parser for unit test."""
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
    return parser


def main():
    parser = get_parser(__version__)
    parser.add_argument("--version", version=__version__, action="version")
    args = parser.parse_args()

    r"""
    from .server import XXXLanguageServer as Server

    server = Server(version=__version__)
    server.run(args)
    """
    print(args)


if __name__ == "__main__":
    main()
