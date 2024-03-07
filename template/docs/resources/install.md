# Install

## [AUR](https://aur.archlinux.org/packages/{{ project }})

```sh
paru -S {{ project }}
```

## [NUR](https://nur.nix-community.org/repos/{{ user }})

```sh
nix-env -iA nixos.nur.repos.{{ user }}.{{ project }}
```

## [PYPI](https://pypi.org/project/{{ project }})

```sh
pip install {{ project }}
```

See [requirements](requirements) to know `extra_requires`.
