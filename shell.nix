{ pkgs ? import <nixpkgs> { } }:

with pkgs;
mkShell {
  name = "lsp-tree-sitter";
  buildInputs = [
      (python3.withPackages (
        p: with p; [
          pytest

          jinja2
          pygls
          tree-sitter
        ]
      ))
  ];
}
