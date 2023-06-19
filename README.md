# pkgbuild-language-server

[![readthedocs](https://shields.io/readthedocs/pkgbuild-language-server)](https://pkgbuild-language-server.readthedocs.io)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Freed-Wu/pkgbuild-language-server/main.svg)](https://results.pre-commit.ci/latest/github/Freed-Wu/pkgbuild-language-server/main)
[![github/workflow](https://github.com/Freed-Wu/pkgbuild-language-server/actions/workflows/main.yml/badge.svg)](https://github.com/Freed-Wu/pkgbuild-language-server/actions)
[![codecov](https://codecov.io/gh/Freed-Wu/pkgbuild-language-server/branch/main/graph/badge.svg)](https://codecov.io/gh/Freed-Wu/pkgbuild-language-server)
[![DeepSource](https://deepsource.io/gh/Freed-Wu/pkgbuild-language-server.svg/?show_trend=true)](https://deepsource.io/gh/Freed-Wu/pkgbuild-language-server)

[![github/downloads](https://shields.io/github/downloads/Freed-Wu/pkgbuild-language-server/total)](https://github.com/Freed-Wu/pkgbuild-language-server/releases)
[![github/downloads/latest](https://shields.io/github/downloads/Freed-Wu/pkgbuild-language-server/latest/total)](https://github.com/Freed-Wu/pkgbuild-language-server/releases/latest)
[![github/issues](https://shields.io/github/issues/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server/issues)
[![github/issues-closed](https://shields.io/github/issues-closed/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server/issues?q=is%3Aissue+is%3Aclosed)
[![github/issues-pr](https://shields.io/github/issues-pr/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server/pulls)
[![github/issues-pr-closed](https://shields.io/github/issues-pr-closed/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server/pulls?q=is%3Apr+is%3Aclosed)
[![github/discussions](https://shields.io/github/discussions/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server/discussions)
[![github/milestones](https://shields.io/github/milestones/all/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server/milestones)
[![github/forks](https://shields.io/github/forks/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server/network/members)
[![github/stars](https://shields.io/github/stars/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server/stargazers)
[![github/watchers](https://shields.io/github/watchers/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server/watchers)
[![github/contributors](https://shields.io/github/contributors/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server/graphs/contributors)
[![github/commit-activity](https://shields.io/github/commit-activity/w/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server/graphs/commit-activity)
[![github/last-commit](https://shields.io/github/last-commit/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server/commits)
[![github/release-date](https://shields.io/github/release-date/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server/releases/latest)

[![github/license](https://shields.io/github/license/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server/blob/main/LICENSE)
[![github/languages](https://shields.io/github/languages/count/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server)
[![github/languages/top](https://shields.io/github/languages/top/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server)
[![github/directory-file-count](https://shields.io/github/directory-file-count/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server)
[![github/code-size](https://shields.io/github/languages/code-size/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server)
[![github/repo-size](https://shields.io/github/repo-size/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server)
[![github/v](https://shields.io/github/v/release/Freed-Wu/pkgbuild-language-server)](https://github.com/Freed-Wu/pkgbuild-language-server)

[![pypi/status](https://shields.io/pypi/status/pkgbuild-language-server)](https://pypi.org/project/pkgbuild-language-server/#description)
[![pypi/v](https://shields.io/pypi/v/pkgbuild-language-server)](https://pypi.org/project/pkgbuild-language-server/#history)
[![pypi/downloads](https://shields.io/pypi/dd/pkgbuild-language-server)](https://pypi.org/project/pkgbuild-language-server/#files)
[![pypi/format](https://shields.io/pypi/format/pkgbuild-language-server)](https://pypi.org/project/pkgbuild-language-server/#files)
[![pypi/implementation](https://shields.io/pypi/implementation/pkgbuild-language-server)](https://pypi.org/project/pkgbuild-language-server/#files)
[![pypi/pyversions](https://shields.io/pypi/pyversions/pkgbuild-language-server)](https://pypi.org/project/pkgbuild-language-server/#files)

Language server for [PKGBUILD](https://wiki.archlinux.org/title/PKGBUILD).

PKGBUILD is a subtype of bash. See
[bash-language-server](https://github.com/bash-lsp/bash-language-server) to get
support of bash language server.

- [x] document hover
- [x] completion

![document hover](https://github.com/Freed-Wu/requirements-language-server/assets/32936898/91bfde00-28f7-4376-8b7a-10a0bd56ba51)

![completion](https://github.com/Freed-Wu/requirements-language-server/assets/32936898/b4444ba5-44ab-473c-9691-b3d61ed09acd)

Read
[![readthedocs](https://shields.io/readthedocs/pkgbuild-language-server)](https://pkgbuild-language-server.readthedocs.io)
to know more.
