# Change Log

## 0.0.0

At the beginning, the aim of this project is to create a language server for
ArchLinux's PKGBUILD files/Gentoo's ebuild files/termux's build.sh files in
order to complete package names. They are bash scripts so improving
[bash-language-server](https://github.com/bash-lsp/bash-language-server) should
be a faster method. bash-language-server is written in javascript. However, many
libraries related to PKGBUILD and ebuild is written in python:

- [portage](https://github.com/gentoo/portage/): package manager for Gentoo.
- [pyalpm](https://gitlab.archlinux.org/archlinux/pyalpm): Arch linux's package
  manager is written in C and provide a python binding.
- [namcap](https://gitlab.archlinux.org/pacman/namcap): based on pyalpm, it is a
  linter to check PKGBUILD files.

So I have to choose create a new language server in python:
pkgbuild-language-server, portage-language-server, termux-language-server.

## 0.0.1

When the initial version is finished, I find those language servers share many
same code, such as the parser for bash scripts, so they are combined into a
single language server: termux-language-server.

## 0.0.2

Then I create more language servers. All of them share many same code,
too. So I decide to create a library to simplify their code. The library is
named as tree-sitter-lsp.

## 0.0.14

tree-sitter-lsp sounds like a tree sitter grammar for a language named lsp. So I
rename it to lsp-tree-sitter.

## 0.1.0

Some breaking changes.

## 0.2.0

Rewrite the code to use jq.
