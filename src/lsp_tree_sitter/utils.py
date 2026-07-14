import os


def pygmentize(text: str, filetype: str) -> None:
    TERM = os.getenv("TERM", "xterm")
    try:
        from pygments import highlight
        from pygments.formatters import get_formatter_by_name
        from pygments.lexers import get_lexer_by_name

        if TERM.split("-")[-1] == "256color":
            formatter_name = "terminal256"
        elif TERM != "dumb":
            formatter_name = "terminal"
        else:
            formatter_name = None
        if formatter_name:
            formatter = get_formatter_by_name(formatter_name)
            lexer = get_lexer_by_name(filetype)
            print(highlight(text, lexer, formatter), end="")
    except ImportError:
        TERM = "dumb"
    if TERM == "dumb":
        print(text)


def pprint(
    obj, filetype: str = "json", color: bool = True, *args, **kwargs
) -> None:
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
        pygmentize(text, filetype)
    else:
        print(text)
