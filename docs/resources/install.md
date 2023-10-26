# Install

## [AUR](https://aur.archlinux.org/packages/python-tree-sitter-lsp)

```sh
yay -S python-tree-sitter-lsp
```

## [NUR](https://nur.nix-community.org/repos/Freed-Wu)

```nix
{ config, pkgs, ... }:
{
  nixpkgs.config.packageOverrides = pkgs: {
    nur = import
      (
        builtins.fetchTarball
          "https://github.com/nix-community/NUR/archive/master.tar.gz"
      )
      {
        inherit pkgs;
      };
  };
  environment.systemPackages = with pkgs;
      (
        python3.withPackages (
          p: with p; [
            nur.repos.Freed-Wu.tree-sitter-lsp
          ]
        )
      )
}
```

## [PYPI](https://pypi.org/project/tree-sitter-lsp)

```sh
pip install tree-sitter-lsp
```

See [requirements](requirements) to know `extra_requires`.
