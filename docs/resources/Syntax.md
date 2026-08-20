# Query Syntax

```{mermaid}
graph LR
  code(source code) --> |tree-sitter| AST --> |jq| json1[JSON with node text]
  ---> |JSON schema| path[error node JSON path] --> range[error node range]
  AST --> |jq| json2[JSON with node range] --> range --> |LSP| diagnostic(diagnostic)
```

```{mermaid}
graph LR
  cursor[/cursor position/] --> node ---> |jq| information --> |LSP| result(completion/hover)
  code(source code) --> |tree-sitter| AST --> node[cursor node]
```

`SchemaLinter` needs a `schema.scm` file to convert a file to JSON, then use
JSON schema to check it.

## Objects

`schema.scm`:

```query
(set_directive
  (option) @--option
  (string) @set.-option)

(set_directive
  (option) @--option
  (int) @set.-option.--integer)
```

will convert

```zathurarc
set fontname "Arial"
set fontsize 12
```

to

```json
{
  "set": {
    "fontname": "Arial",
    "fontsize": 12
  }
}
```

Then you can use JSON schema to check it, such as fontsize must be greater then
10, etc.

1. `--option` means a variable `option` is named as the node's text.
2. `set.-option` means JSON's `.set.{option}` have value of the node's text.
3. `--integer`/`--string`/`--number`/`--boolean` means the type.

## Default

A default value is also allowed:

```query
(set_directive
  (option)? @--option
  (string)? @set.-option
  (#set! @--option "default-option")
  (#set! @set.-option "default-value")
  )
```

## Arrays

For:

```zathurarc
include /etc/a.conf
include /etc/b.conf
```

`schema.scm`:

```query
(path) @include.-
```

will convert it to

```json
{
  "include": [
    "/etc/a.conf",
    "/etc/b.conf"
  ]
}
```

`schema.scm`:

```query
(path) @include.--
```

will convert it to

```json
{
  "include": [
    "/etc/b.conf"
  ]
}
```

the last will override the previous one.
