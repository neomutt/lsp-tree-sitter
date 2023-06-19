r"""Test server"""
from pkgbuild_language_server.server import get_document


class Test:
    r"""Test."""

    @staticmethod
    def test_get_document() -> None:
        r"""Test get document.

        :rtype: None
        """
        assert get_document().get("pkgname")
