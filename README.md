# tree-sitter-lsp

[![readthedocs](https://shields.io/readthedocs/tree-sitter-lsp)](https://tree-sitter-lsp.readthedocs.io)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Freed-Wu/tree-sitter-lsp/main.svg)](https://results.pre-commit.ci/latest/github/Freed-Wu/tree-sitter-lsp/main)
[![github/workflow](https://github.com/Freed-Wu/tree-sitter-lsp/actions/workflows/main.yml/badge.svg)](https://github.com/Freed-Wu/tree-sitter-lsp/actions)
[![codecov](https://codecov.io/gh/Freed-Wu/tree-sitter-lsp/branch/main/graph/badge.svg)](https://codecov.io/gh/Freed-Wu/tree-sitter-lsp)
[![DeepSource](https://deepsource.io/gh/Freed-Wu/tree-sitter-lsp.svg/?show_trend=true)](https://deepsource.io/gh/Freed-Wu/tree-sitter-lsp)

[![github/downloads](https://shields.io/github/downloads/Freed-Wu/tree-sitter-lsp/total)](https://github.com/Freed-Wu/tree-sitter-lsp/releases)
[![github/downloads/latest](https://shields.io/github/downloads/Freed-Wu/tree-sitter-lsp/latest/total)](https://github.com/Freed-Wu/tree-sitter-lsp/releases/latest)
[![github/issues](https://shields.io/github/issues/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp/issues)
[![github/issues-closed](https://shields.io/github/issues-closed/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp/issues?q=is%3Aissue+is%3Aclosed)
[![github/issues-pr](https://shields.io/github/issues-pr/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp/pulls)
[![github/issues-pr-closed](https://shields.io/github/issues-pr-closed/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp/pulls?q=is%3Apr+is%3Aclosed)
[![github/discussions](https://shields.io/github/discussions/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp/discussions)
[![github/milestones](https://shields.io/github/milestones/all/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp/milestones)
[![github/forks](https://shields.io/github/forks/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp/network/members)
[![github/stars](https://shields.io/github/stars/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp/stargazers)
[![github/watchers](https://shields.io/github/watchers/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp/watchers)
[![github/contributors](https://shields.io/github/contributors/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp/graphs/contributors)
[![github/commit-activity](https://shields.io/github/commit-activity/w/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp/graphs/commit-activity)
[![github/last-commit](https://shields.io/github/last-commit/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp/commits)
[![github/release-date](https://shields.io/github/release-date/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp/releases/latest)

[![github/license](https://shields.io/github/license/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp/blob/main/LICENSE)
[![github/languages](https://shields.io/github/languages/count/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp)
[![github/languages/top](https://shields.io/github/languages/top/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp)
[![github/directory-file-count](https://shields.io/github/directory-file-count/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp)
[![github/code-size](https://shields.io/github/languages/code-size/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp)
[![github/repo-size](https://shields.io/github/repo-size/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp)
[![github/v](https://shields.io/github/v/release/Freed-Wu/tree-sitter-lsp)](https://github.com/Freed-Wu/tree-sitter-lsp)

[![pypi/status](https://shields.io/pypi/status/tree-sitter-lsp)](https://pypi.org/project/tree-sitter-lsp/#description)
[![pypi/v](https://shields.io/pypi/v/tree-sitter-lsp)](https://pypi.org/project/tree-sitter-lsp/#history)
[![pypi/downloads](https://shields.io/pypi/dd/tree-sitter-lsp)](https://pypi.org/project/tree-sitter-lsp/#files)
[![pypi/format](https://shields.io/pypi/format/tree-sitter-lsp)](https://pypi.org/project/tree-sitter-lsp/#files)
[![pypi/implementation](https://shields.io/pypi/implementation/tree-sitter-lsp)](https://pypi.org/project/tree-sitter-lsp/#files)
[![pypi/pyversions](https://shields.io/pypi/pyversions/tree-sitter-lsp)](https://pypi.org/project/tree-sitter-lsp/#files)

A library aimed to create language servers which connect:

- [tree-sitter](https://tree-sitter.github.io/tree-sitter/)
- [language server protocol](https://microsoft.github.io/language-server-protocol/specifications/specification-current)
- [json schema](https://json-schema.org/specification)

Some example language servers:

- [termux-language-server](https://github.com/termux/termux-language-server/):
  for some specific bash scripts:
  - [`build.sh`](https://github.com/termux/termux-packages/wiki/Creating-new-package)
  - [`PKGBUILD`](https://wiki.archlinux.org/title/PKGBUILD)
  - [`*.ebuild`](https://dev.gentoo.org/~zmedico/portage/doc/man/ebuild.5.html)
  - ...
- [autotools-language-server](https://github.com/Freed-Wu/autotools-language-server/):
  for `Makefile`
- [requirements-language-server](https://github.com/Freed-Wu/requirements-language-server/):
  for `requirements.txt`

Read
[![readthedocs](https://shields.io/readthedocs/tree-sitter-lsp)](https://tree-sitter-lsp.readthedocs.io)
to know more.
