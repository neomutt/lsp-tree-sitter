import os


def ts_highlight(text: str, filetype: str) -> str | None:
    r"""Use tree sitter to highlight.

    :param text:
    :type text: str
    :param filetype:
    :type filetype: str
    :rtype: str | None
    """
    from tree_sitter_highlight import highlight, search_parsers

    match filetype:
        case "yaml":
            import tree_sitter_yaml as module
        case "toml":
            import tree_sitter_toml as module
        case "json":
            import tree_sitter_json as module
        case _:
            return
    parsers = search_parsers(module)
    code = highlight(
        source=text, parsers=parsers, language=filetype, format="terminal"
    )
    return code


def pygmentize(text: str, filetype: str) -> str | None:
    r"""Use pygments to highlight.

    :param text: text to highlight
    :type text: str
    :param filetype: filetype to highlight
    :type filetype: str
    :rtype: str | None
    """
    from pygments import highlight
    from pygments.formatters import get_formatter_by_name
    from pygments.lexers import get_lexer_by_name

    TERM = os.getenv("TERM", "xterm")
    if TERM.split("-")[-1] == "256color":
        formatter_name = "terminal256"
    elif TERM != "dumb":
        formatter_name = "terminal"
    else:
        formatter_name = None
    if formatter_name:
        formatter = get_formatter_by_name(formatter_name)
        lexer = get_lexer_by_name(filetype)
        return highlight(text, lexer, formatter)


def pprint(
    obj, filetype: str = "json", color: bool = True, *args, **kwargs
) -> None:
    r"""Pretty print.

    :param obj:
    :param filetype: any filetype except yaml, toml, json will be plaintext
    :type filetype: str
    :param color: whether to use color
    :type color: bool
    :param args:
    :param kwargs:
    :rtype: None
    """
    match filetype:
        case "yaml":
            from yaml import dump as dumps
        case "toml":
            from tomli_w import dumps
        case "json":
            from json import dumps
        case _:
            dumps = str
    text = dumps(obj, *args, **kwargs)
    if color:
        try:
            code = ts_highlight(text, filetype)
        except ImportError:
            try:
                code = pygmentize(text, filetype)
            except ImportError:
                code = None
    else:
        code = None
    if code:
        print(code, end="")
    else:
        print(text)
