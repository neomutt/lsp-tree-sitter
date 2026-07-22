# lsp-tree-sitter

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/neomutt/lsp-tree-sitter/main.svg)](https://results.pre-commit.ci/latest/github/neomutt/lsp-tree-sitter/main)
[![github/workflow](https://github.com/neomutt/lsp-tree-sitter/actions/workflows/main.yml/badge.svg)](https://github.com/neomutt/lsp-tree-sitter/actions)

[![github/downloads](https://shields.io/github/downloads/neomutt/lsp-tree-sitter/total)](https://github.com/neomutt/lsp-tree-sitter/releases)
[![github/downloads/latest](https://shields.io/github/downloads/neomutt/lsp-tree-sitter/latest/total)](https://github.com/neomutt/lsp-tree-sitter/releases/latest)
[![github/issues](https://shields.io/github/issues/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter/issues)
[![github/issues-closed](https://shields.io/github/issues-closed/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter/issues?q=is%3Aissue+is%3Aclosed)
[![github/issues-pr](https://shields.io/github/issues-pr/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter/pulls)
[![github/issues-pr-closed](https://shields.io/github/issues-pr-closed/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter/pulls?q=is%3Apr+is%3Aclosed)
[![github/discussions](https://shields.io/github/discussions/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter/discussions)
[![github/milestones](https://shields.io/github/milestones/all/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter/milestones)
[![github/forks](https://shields.io/github/forks/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter/network/members)
[![github/stars](https://shields.io/github/stars/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter/stargazers)
[![github/watchers](https://shields.io/github/watchers/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter/watchers)
[![github/contributors](https://shields.io/github/contributors/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter/graphs/contributors)
[![github/commit-activity](https://shields.io/github/commit-activity/w/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter/graphs/commit-activity)
[![github/last-commit](https://shields.io/github/last-commit/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter/commits)
[![github/release-date](https://shields.io/github/release-date/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter/releases/latest)

[![github/license](https://shields.io/github/license/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter/blob/main/LICENSE)
[![github/languages](https://shields.io/github/languages/count/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter)
[![github/languages/top](https://shields.io/github/languages/top/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter)
[![github/directory-file-count](https://shields.io/github/directory-file-count/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter)
[![github/code-size](https://shields.io/github/languages/code-size/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter)
[![github/repo-size](https://shields.io/github/repo-size/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter)
[![github/v](https://shields.io/github/v/release/neomutt/lsp-tree-sitter)](https://github.com/neomutt/lsp-tree-sitter)

[![aur/votes](https://img.shields.io/aur/votes/python-lsp-tree-sitter)](https://aur.archlinux.org/packages/python-lsp-tree-sitter)
[![aur/popularity](https://img.shields.io/aur/popularity/python-lsp-tree-sitter)](https://aur.archlinux.org/packages/python-lsp-tree-sitter)
[![aur/maintainer](https://img.shields.io/aur/maintainer/python-lsp-tree-sitter)](https://aur.archlinux.org/packages/python-lsp-tree-sitter)
[![aur/last-modified](https://img.shields.io/aur/last-modified/python-lsp-tree-sitter)](https://aur.archlinux.org/packages/python-lsp-tree-sitter)
[![aur/version](https://img.shields.io/aur/version/python-lsp-tree-sitter)](https://aur.archlinux.org/packages/python-lsp-tree-sitter)

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

```mermaid
graph LR
  code(source code) --> |tree-sitter| AST --> |jq| json1[JSON with node text]
  ---> |JSON schema| path[error node JSON path] --> range[error node range]
  AST --> |jq| json2[JSON with node range] --> range --> |LSP| diagnostic(diagnostic)
```

```mermaid
graph LR
  cursor[/cursor position/] --> node ---> |jq| information --> |LSP| result(completion/hover)
  code(source code) --> |tree-sitter| AST --> node[cursor node]
```

## Examples

- [mutt-language-server](https://github.com/neomutt/mutt-language-server)
  [![github/stars](https://shields.io/github/stars/neomutt/mutt-language-server)](https://github.com/neomutt/mutt-language-server/stargazers)
- [tmux-language-server](https://github.com/Freed-Wu/tmux-language-server)
  [![github/stars](https://shields.io/github/stars/Freed-Wu/tmux-language-server)](https://github.com/Freed-Wu/tmux-language-server/stargazers)
- [zathura-language-server](https://github.com/Freed-Wu/zathura-language-server)
  [![github/stars](https://shields.io/github/stars/Freed-Wu/zathura-language-server)](https://github.com/Freed-Wu/zathura-language-server/stargazers)
- [termux-language-server](https://github.com/termux/termux-language-server)
  [![github/stars](https://shields.io/github/stars/termux/termux-language-server)](https://github.com/termux/termux-language-server/stargazers)
- [requirements-language-server](https://github.com/Freed-Wu/requirements-language-server)
  [![github/stars](https://shields.io/github/stars/Freed-Wu/requirements-language-server)](https://github.com/Freed-Wu/requirements-language-server/stargazers)
- [autotools-language-server](https://github.com/Freed-Wu/autotools-language-server)
  [![github/stars](https://shields.io/github/stars/Freed-Wu/autotools-language-server)](https://github.com/Freed-Wu/autotools-language-server/stargazers)
