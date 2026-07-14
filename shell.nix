{
  pkgs ? import <nixpkgs> { },
}:

with pkgs;
mkShell {
  name = "lsp-tree-sitter";
  buildInputs = [
    (python3.withPackages (
      p: with p; [
        uv
        pytest

        jq
        jsonschema
        pygls
        tree-sitter
      ]
    ))
  ];
}
