r"""Schema
==========
"""

from dataclasses import dataclass

from lsp_tree_sitter import UNI
from lsp_tree_sitter.schema import Trie
from lsprotocol.types import Position, Range
from tree_sitter import Node

DIRECTIVES = {
    "set_directive",
    "map_directive",
    "unmap_directive",
    "include_directive",
}


@dataclass
class {{ language | title }}Trie(Trie):
    r"""{{ language | title }} Trie."""

    value: dict[str, "Trie"] | list["Trie"] | str | int | float | bool | None

    @classmethod
    def from_node(cls, node: Node, parent: "Trie | None") -> "Trie":
        r"""From node.

        :param node:
        :type node: Node
        :param parent:
        :type parent: Trie | None
        :rtype: "Trie"
        """
        if node.type == "set_directive":
            node = node.children[2]
            _type = node.type
            if _type == "int":
                convert = int
            elif _type == "float":
                convert = float
            elif _type == "bool":

                def convert(x):
                    return x == "true"
            else:

                def convert(x):
                    return x.strip("'\"")

            text = UNI(node).text
            if text != "":
                text = convert(text)
            return cls(UNI(node).range, parent, text)
        if node.type == "map_directive":
            trie = cls(UNI(node).range, parent, {})
            key: Node = node.children[1]
            if key.type == "mode":
                key: Node = key.next_sibling  # type: ignore
            function: Node = key.next_sibling  # type: ignore
            argument = function.next_sibling

            value: dict[str, Trie] = trie.value  # type: ignore
            value["key"] = cls(UNI(key).range, trie, UNI(key).text)  # type: ignore
            value["function"] = cls(
                UNI(function).range, trie, UNI(function).text
            )  # type: ignore
            if argument := function.next_sibling:
                value["argument"] = cls(
                    UNI(argument).range, trie, UNI(argument).text
                )  # type: ignore
            return trie
        if node.type == "unmap_directive":
            key = node.children[1]
            if key.type == "mode":
                key = key.next_sibling  # type: ignore
            return cls(UNI(key).range, parent, UNI(key).text)
        if node.type == "file":
            trie = cls(Range(Position(0, 0), Position(1, 0)), parent, {})
            for directive in DIRECTIVES:
                _type = directive.split("_")[0]
            for child in node.children:
                if child.type not in DIRECTIVES:
                    continue
                _type = child.type.split("_")[0]
                value: dict[str, Trie] = trie.value  # type: ignore
                if _type not in value:
                    trie.value[_type] = cls(  # type: ignore
                        UNI(child).range,
                        trie,
                        {} if _type != "include" else [],
                    )
                subtrie: Trie = trie.value[child.type.split("_")[0]]  # type: ignore
                value: dict[str, Trie] | list[Trie] = subtrie.value  # type: ignore
                if child.type == "set_directive":
                    value: dict[str, Trie]
                    value[UNI(child.children[1]).text] = cls.from_node(
                        child, subtrie
                    )
                elif child.type == "include_directive":
                    value += [  # type: ignore
                        cls(
                            UNI(child.children[1]).range,
                            subtrie,
                            UNI(child.children[1]).text,
                        )
                    ]
                else:
                    mode = "normal"
                    if child.children[1].type == "mode":
                        mode = (
                            UNI(child.children[1]).text
                            .lstrip("[")
                            .rstrip("]")
                        )
                    if mode not in value:
                        value[mode] = cls(
                            Range(Position(0, 0), Position(1, 0)),
                            subtrie,
                            [],
                        )
                    if child.type == "unmap_directive":
                        value[mode].value += [  # type: ignore
                            cls.from_node(child, value[mode])
                        ]
                    else:
                        value[mode].value += [
                            cls.from_node(child, value[mode])
                        ]  # type: ignore
            return trie
        raise NotImplementedError(node.type)
