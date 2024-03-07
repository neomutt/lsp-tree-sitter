# Configure

- For windows, change `~/.config` to `~/AppData/Local`
- For macOS, change `~/.config` to `~/Library`

## (Neo)[Vim](https://www.vim.org)

For vim:

- Change `~/.config/nvim` to `~/.vim`
- Change `init.vim` to `vimrc`

### [coc.nvim](https://github.com/neoclide/coc.nvim)

`~/.config/nvim/coc-settings.json`:

```json
{
  "languageserver": {
    "{{ language }}": {
      "command": "{{ project }}",
      "filetypes": [
        "{{ language }}"
      ]
    }
  }
}
```

### [vim-lsp](https://github.com/prabirshrestha/vim-lsp)

`~/.config/nvim/init.vim`:

```vim
if executable('{{ project }}')
  augroup lsp
    autocmd!
    autocmd User lsp_setup call lsp#register_server({
          \ 'name': '{{ language }}',
          \ 'cmd': {server_info->['{{ project }}']},
          \ 'whitelist': ['{{ language }}'],
          \ })
  augroup END
endif
```

## [Neovim](https://neovim.io)

`~/.config/nvim/init.lua`:

```lua
vim.api.nvim_create_autocmd({ "BufEnter" }, {
  pattern = { "{{ language }}*" },
  callback = function()
    vim.lsp.start({
      name = "{{ language }}",
      cmd = { "{{ project }}" }
    })
  end,
})
```

## [Emacs](https://www.gnu.org/software/emacs)

`~/.emacs.d/init.el`:

```lisp
(make-lsp-client :new-connection
(lsp-stdio-connection
  `(,(executable-find "{{ project }}")))
  :activation-fn (lsp-activate-on "{{ language }}*")
  :server-id "{{ language }}")))
```

## [Helix](https://helix-editor.com/)

`~/.config/helix/languages.toml`:

```toml
[[language]]
name = "{{ language }}"
language-servers = [ "{{ project }}",]

[language_server.{{ project }}]
command = "{{ project }}"
```

## [KaKoune](https://kakoune.org/)

### [kak-lsp](https://github.com/kak-lsp/kak-lsp)

`~/.config/kak-lsp/kak-lsp.toml`:

```toml
[language_server.{{ project }}]
filetypes = [ "{{ language }}",]
command = "{{ project }}"
```

## [Sublime](https://www.sublimetext.com)

`~/.config/sublime-text-3/Packages/Preferences.sublime-settings`:

```json
{
  "clients": {
    "{{ language }}": {
      "command": [
        "{{ project }}"
      ],
      "enabled": true,
      "selector": "source.{{ language }}"
    }
  }
}
```

## [Visual Studio Code](https://code.visualstudio.com/)

[An official support of generic LSP client is pending](https://github.com/microsoft/vscode/issues/137885).

### [vscode-glspc](https://gitlab.com/ruilvo/vscode-glspc)

`~/.config/Code/User/settings.json`:

```json
{
  "glspc.serverPath": "{{ project }}",
  "glspc.languageId": "{{ language }}"
}
```
