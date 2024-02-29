# Install

## [AUR](https://aur.archlinux.org/packages/python-lsp-tree-sitter)

```sh
yay -S python-lsp-tree-sitter
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
            nur.repos.Freed-Wu.lsp-tree-sitter
          ]
        )
      )
}
```

## [PYPI](https://pypi.org/project/lsp-tree-sitter)

```sh
pip install lsp-tree-sitter
```

See [requirements](requirements) to know `extra_requires`.
