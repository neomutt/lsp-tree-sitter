# Queries

There are many queries:

## [tree-sitter](https://github.com/tree-sitter/tree-sitter/)

- highlights.scm: for syntax highlight
- injections.scm: for syntax highlight in embedded languages
- locals.scm: for symbols

## [neovim](https://github.com/neovim/neovim/)

- folds.scm: for code folding

## [nvim-treesitter](https://github.com/nvim-treesitter/nvim-treesitter/)

- indent.scm: for indent

## [nvim-treesitter-textobjects](https://github.com/nvim-treesitter/nvim-treesitter-textobjects)

- textobjects.scm: for text objects

## [lumis](https://github.com/leandrocp/lumis/tree/main/queries/brackets)

- brackets.scm: for rainbow brackets

## lsp-tree-sitter

Diagnose needs the following queries:

- highlights.scm: `PathLinter` check if `string.special.path` is a legal path
- packages.scm: `PackageLinter` check if `package.*` is a legal package
- schema.scm: `SchemaLinter` check if a file respect JSON schema
