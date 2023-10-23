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

Language server for [ArchLinux](https://archlinux.org)/[Windows Msys2](https://msys2.org)'s
[PKGBUILD](https://wiki.archlinux.org/title/PKGBUILD) and
[`*.install`](https://wiki.archlinux.org/title/PKGBUILD#install).

`PKGBUILD` is a subtype of bash.
This language server only provides extra features for `build.sh` which
[bash-language-server](https://github.com/bash-lsp/bash-language-server)
doesn't support:

- [x] [Diagnostic](https://microsoft.github.io/language-server-protocol/specifications/specification-current#diagnostic):
  - [x] [namcap](https://wiki.archlinux.org/title/Namcap)
  - [x] variable type. Such as: `depends` shouldn't be a function
  - [ ] unsorted builtin variables/functions
  - [ ] unsorted array. Such as: `depends=(pyalpm namcap)` should be
    `depends=(namcap pyalpm)`
- [ ] [Document Formatting](https://microsoft.github.io/language-server-protocol/specifications/specification-current#textDocument_formatting):
  - [ ] sort builtin variables/functions
  - [ ] sort array
- [x] [Document Link](https://microsoft.github.io/language-server-protocol/specifications/specification-current#textDocument_documentLink):
  jump to <https://archlinux.org/packages/package_name>
- [x] [Hover](https://microsoft.github.io/language-server-protocol/specifications/specification-current#textDocument_hover)
  - [x] packages
  - [x] builtin variables/functions
- [x] [Completion](https://microsoft.github.io/language-server-protocol/specifications/specification-current#textDocument_completion):
  - [x] packages
  - [x] builtin variables/functions
- [ ] [Code Action](https://microsoft.github.io/language-server-protocol/specifications/specification-current#textDocument_codeAction)
  - [ ] generate a template by the name of directory containing `PKGBUILD`, the
    templates comes from:
    - [ ] customized by user
    - [ ] [pip2pkgbuild](https://github.com/wenLiangcan/pip2pkgbuild)
    - [ ] [cpan2aur](https://metacpan.org/release/CPANPLUS-Dist-Arch)
    - [ ] [gem2arch](https://github.com/anatol/gem2arch)
    - [ ] [arch-hs](https://github.com/berberman/arch-hs)
  - [ ] update `.SRCINFO` by `makepkg --printsrcinfo > .SRCINFO`
  - [ ] update `pkgsums` by [`updpkgsums`](https://gitlab.archlinux.org/pacman/pacman-contrib)
  - [ ] update version by a `nvcheck.toml` to tell this
    program where to search new version:

```toml
[package_name]
source = "github"
github = "author_name/repo_name"
use_max_tag = true
```

Other features:

- [x] pre-commit-hooks
  - [x] linter
  - [ ] formatter

## Document Link

![document link](https://github.com/Freed-Wu/pkgbuild-language-server/assets/32936898/d3777f3c-9b75-41f9-b6b3-1c4ec55c7283)

## Hover

![keyword](https://github.com/Freed-Wu/requirements-language-server/assets/32936898/91bfde00-28f7-4376-8b7a-10a0bd56ba51)

![package](https://github.com/Freed-Wu/pkgbuild-language-server/assets/32936898/3d9fa906-35ea-4063-a9eb-06282d3e8596)

## Completion

![keyword](https://github.com/Freed-Wu/requirements-language-server/assets/32936898/b4444ba5-44ab-473c-9691-b3d61ed09acd)

![package](https://github.com/Freed-Wu/pkgbuild-language-server/assets/32936898/090dae36-52fe-47f9-ae2d-cd3256cb55e8)

## Diagnostic

![namcap](https://github.com/Freed-Wu/pkgbuild-language-server/assets/32936898/71337b4c-87f3-4b95-9edd-f194cacb5cdf)

Read
[![readthedocs](https://shields.io/readthedocs/pkgbuild-language-server)](https://pkgbuild-language-server.readthedocs.io)
to know more.
