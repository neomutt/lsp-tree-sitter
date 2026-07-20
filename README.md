# lsp-tree-sitter

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Freed-Wu/lsp-tree-sitter/main.svg)](https://results.pre-commit.ci/latest/github/Freed-Wu/lsp-tree-sitter/main)
[![github/workflow](https://github.com/Freed-Wu/lsp-tree-sitter/actions/workflows/main.yml/badge.svg)](https://github.com/Freed-Wu/lsp-tree-sitter/actions)

[![github/downloads](https://shields.io/github/downloads/Freed-Wu/lsp-tree-sitter/total)](https://github.com/Freed-Wu/lsp-tree-sitter/releases)
[![github/downloads/latest](https://shields.io/github/downloads/Freed-Wu/lsp-tree-sitter/latest/total)](https://github.com/Freed-Wu/lsp-tree-sitter/releases/latest)
[![github/issues](https://shields.io/github/issues/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter/issues)
[![github/issues-closed](https://shields.io/github/issues-closed/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter/issues?q=is%3Aissue+is%3Aclosed)
[![github/issues-pr](https://shields.io/github/issues-pr/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter/pulls)
[![github/issues-pr-closed](https://shields.io/github/issues-pr-closed/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter/pulls?q=is%3Apr+is%3Aclosed)
[![github/discussions](https://shields.io/github/discussions/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter/discussions)
[![github/milestones](https://shields.io/github/milestones/all/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter/milestones)
[![github/forks](https://shields.io/github/forks/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter/network/members)
[![github/stars](https://shields.io/github/stars/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter/stargazers)
[![github/watchers](https://shields.io/github/watchers/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter/watchers)
[![github/contributors](https://shields.io/github/contributors/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter/graphs/contributors)
[![github/commit-activity](https://shields.io/github/commit-activity/w/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter/graphs/commit-activity)
[![github/last-commit](https://shields.io/github/last-commit/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter/commits)
[![github/release-date](https://shields.io/github/release-date/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter/releases/latest)

[![github/license](https://shields.io/github/license/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter/blob/main/LICENSE)
[![github/languages](https://shields.io/github/languages/count/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter)
[![github/languages/top](https://shields.io/github/languages/top/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter)
[![github/directory-file-count](https://shields.io/github/directory-file-count/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter)
[![github/code-size](https://shields.io/github/languages/code-size/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter)
[![github/repo-size](https://shields.io/github/repo-size/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter)
[![github/v](https://shields.io/github/v/release/Freed-Wu/lsp-tree-sitter)](https://github.com/Freed-Wu/lsp-tree-sitter)

[![aur/votes](https://img.shields.io/aur/votes/lsp-tree-sitter)](https://aur.archlinux.org/packages/lsp-tree-sitter)
[![aur/popularity](https://img.shields.io/aur/popularity/lsp-tree-sitter)](https://aur.archlinux.org/packages/lsp-tree-sitter)
[![aur/maintainer](https://img.shields.io/aur/maintainer/lsp-tree-sitter)](https://aur.archlinux.org/packages/lsp-tree-sitter)
[![aur/last-modified](https://img.shields.io/aur/last-modified/lsp-tree-sitter)](https://aur.archlinux.org/packages/lsp-tree-sitter)
[![aur/version](https://img.shields.io/aur/version/lsp-tree-sitter)](https://aur.archlinux.org/packages/lsp-tree-sitter)

[![pypi/status](https://shields.io/pypi/status/lsp-tree-sitter)](https://pypi.org/project/lsp-tree-sitter/#description)
[![pypi/v](https://shields.io/pypi/v/lsp-tree-sitter)](https://pypi.org/project/lsp-tree-sitter/#history)
[![pypi/downloads](https://shields.io/pypi/dd/lsp-tree-sitter)](https://pypi.org/project/lsp-tree-sitter/#files)
[![pypi/format](https://shields.io/pypi/format/lsp-tree-sitter)](https://pypi.org/project/lsp-tree-sitter/#files)
[![pypi/implementation](https://shields.io/pypi/implementation/lsp-tree-sitter)](https://pypi.org/project/lsp-tree-sitter/#files)
[![pypi/pyversions](https://shields.io/pypi/pyversions/lsp-tree-sitter)](https://pypi.org/project/lsp-tree-sitter/#files)

A library to create language servers.

## Features

- [x] [textDocument/documentLink](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.18/specification/#textDocument_documentLink)
- [x] [textDocument/publishDiagnostics](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.18/specification/#textDocument_publishDiagnostics)
- [x] [textDocument/hover](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.18/specification/#textDocument_hover)
- [x] [textDocument/completion](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.18/specification/#textDocument_completion)

## Examples

- [mutt-language-server](https://github.com/neomutt/mutt-language-server)
- [tmux-language-server](https://github.com/Freed-Wu/tmux-language-server)
- [zathura-language-server](https://github.com/Freed-Wu/zathura-language-server)
- [termux-language-server](https://github.com/termux/termux-language-server)
