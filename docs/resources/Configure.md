# How to enable LSP for editors

## [Vim](https://github.com/vim/vim)

### [coc.nvim](https://github.com/neoclide/coc.nvim)

`~/.config/nvim/coc-settings.json`:

```json
{
  "languageserver": {
    "XXX": {
      "command": "XXX-language-server",
      "args": [],
      "settings": {},
      "filetypes": [
        "XXX"
      ]
    }
  }
}
```

### [vim-lsp](https://github.com/prabirshrestha/vim-lsp)

`~/.config/nvim/init.vim`:

```vim
if executable('XXX-language-server')
  augroup lsp
    autocmd!
    autocmd User lsp_setup call lsp#register_server({
          \ 'name': 'XXX',
          \ 'cmd': {server_info->['XXX-language-server']},
          \ 'whitelist': ['XXX'],
          \ })
  augroup END
endif
```

## [NeoVim](https://neovim.io)

`~/.config/nvim/init.lua`:

```lua
vim.api.nvim_create_autocmd("FileType", {
  pattern = { "XXX" },
  callback = function()
    vim.lsp.start({
      name = "XXX",
      cmd = { "XXX-language-server" }
    })
  end,
})
```

## [Emacs](https://www.gnu.org/software/emacs)

`~/.emacs.d/init.el`:

```commonlisp
(make-lsp-client :new-connection
(lsp-stdio-connection
  `(,(executable-find "XXX-language-server")))
  :activation-fn (lsp-activate-on "*.XXX")
  :server-id "XXX")))
```

## [Helix](https://helix-editor.com)

`~/.config/helix/languages.toml`:

```toml
[[language]]
name = "XXX"
language-servers = ["XXX-language-server"]

[language_server.XXX-language-server]
command = "XXX-language-server"
```

## [KaKoune](https://kakoune.org/)

### [kak-lsp](https://github.com/kak-lsp/kak-lsp)

`~/.config/kak-lsp/kak-lsp.toml`:

```toml
[language_server.XXX-language-server]
filetypes = ["XXX"]
command = "XXX-language-server"
```

## [Sublime](https://www.sublimetext.com/)

`~/.config/sublime-text-3/Packages/Preferences.sublime-settings`:

```json
{
  "clients": {
    "XXX": {
      "command": [
        "XXX-language-server"
      ],
      "enabled": true,
      "selector": "source.XXX"
    }
  }
}
```

## [Visual Studio Code](https://code.visualstudio.com/)

### [vscode-glspc](https://gitlab.com/ruilvo/vscode-glspc)

`~/.config/Code/User/settings.json`:

```json
{
  "glspc.serverPath": "XXX-language-server",
  "glspc.languageId": "XXX"
}
```

## [Zed](https://zed.dev)

`~/.config/zed/settings.json`:

```json
{
  "languages": {
    "XXX": {
      "language_servers": [
        "XXX-language-server"
      ]
    }
  },
  "lsp": {
    "XXX-language-server": {
      "binary": {
        "path": "XXX-language-server",
        "arguments": []
      }
    }
  }
}
```
