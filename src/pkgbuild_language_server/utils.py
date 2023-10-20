r"""Utils
=========
"""


def diagnostic(path: str) -> list[tuple[str, str]]:
    r"""Diagnostic.

    :param path:
    :type path: str
    :rtype: list[tuple[str, str]]
    """
    try:
        from Namcap.rules import all_rules
    except ImportError:
        return []
    from Namcap.package import load_from_pkgbuild
    from Namcap.ruleclass import PkgbuildRule
    from Namcap.tags import format_message

    pkginfo = load_from_pkgbuild(path)
    items = []
    for value in all_rules.values():
        rule = value()
        if isinstance(rule, PkgbuildRule):
            rule.analyze(pkginfo, "PKGBUILD")  # type: ignore
        for msg in rule.errors:
            items += [(format_message(msg), "Error")]
        for msg in rule.warnings:
            items += [(format_message(msg), "Warning")]
    return items
