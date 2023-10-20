r"""Test documents"""
from pkgbuild_language_server.documents import get_document


class Test:
    r"""Test."""

    @staticmethod
    def test_get_document() -> None:
        r"""Test get document.

        :rtype: None
        """
        assert get_document().get("pkgname")
