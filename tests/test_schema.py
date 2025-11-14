r"""Test schema."""

from lsprotocol.types import Position, Range

from lsp_tree_sitter.schema import Trie


class Test:
    r"""Test."""

    @staticmethod
    def test_jq() -> None:
        r = Range(Position(0, 0), Position(1, 0))
        root = Trie(r)
        child0 = Trie(r, root, 1)
        child1 = Trie(r, root)
        root.value = [child0, child1]
        grandchild = Trie(r, child1, "A")
        child1.value = {"a": grandchild}
        assert str(grandchild) == "$[1].a"
        assert root["$[1].a"] is grandchild
