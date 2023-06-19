# Configure

See customization in
<https://pkgbuild-language-server.readthedocs.io/en/latest/api/pkgbuild-language-server.html#pkgbuild_language_server.server.get_document>.

## (Neo)[Vim](https://www.vim.org)

### [coc.nvim](https://github.com/neoclide/coc.nvim)

```json
{
  "languageserver": {
    "pkgbuild": {
      "command": "pkgbuild-language-server",
      "filetypes": [
        "sh"
      ],
      "initializationOptions": {
        "method": "builtin"
      }
    }
  }
}
```

### [vim-lsp](https://github.com/prabirshrestha/vim-lsp)

```vim
if executable('pkgbuild-language-server')
  augroup lsp
    autocmd!
    autocmd User lsp_setup call lsp#register_server({
          \ 'name': 'pkgbuild',
          \ 'cmd': {server_info->['pkgbuild-language-server']},
          \ 'whitelist': ['sh'],
          \ 'initialization_options': {
          \   'method': 'builtin',
          \ },
          \ })
  augroup END
endif
```

## [Neovim](https://neovim.io)

```lua
vim.api.nvim_create_autocmd({ "BufEnter" }, {
  pattern = { "PKGBUILD" "*.install" },
  callback = function()
    vim.lsp.start({
      name = "pkgbuild",
      cmd = { "pkgbuild-language-server" }
    })
  end,
})
```

## [Emacs](https://www.gnu.org/software/emacs)

```elisp
(make-lsp-client :new-connection
(lsp-stdio-connection
  `(,(executable-find "pkgbuild-language-server")))
  :activation-fn (lsp-activate-on "PKGBUILD" "*.install")
  :server-id "pkgbuild")))
```

## [Sublime](https://www.sublimetext.com)

```json
{
  "clients": {
    "pkgbuild": {
      "command": [
        "pkgbuild-language-server"
      ],
      "enabled": true,
      "selector": "source.sh"
    }
  }
}
```
