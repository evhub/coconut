---
name: coconut
description: Write, read, debug, and verify code in Coconut, the functional superset of Python that compiles to Python (.coco files).
when_to_use: Use when creating or editing .coco/.coc/.coconut files, when a project uses the Coconut compiler, or when asked about Coconut syntax.
---

# Coconut

Before writing or changing Coconut code, run `coconut --ai-docs` and read its output: it's Coconut's own guide to writing idiomatic Coconut, kept up to date with the installed version (online at https://coconut.readthedocs.io/en/latest/llms.txt). Follow it, including its "Common pitfalls" section.

To check your work:
- The Coconut language server reports errors and warnings after each edit to a `.coco` file.
- Use the `coconut_check` MCP tool, or run `python -m coconut.lsp check <files or dirs>`, to check files or a whole project (add `--mypy` to type check).
- Use `coconut_compile` (or `python -m coconut.lsp compile <file>`) to see the Python a construct compiles to, and `coconut_docs` (or `python -m coconut.lsp docs <name>`) to look up a built-in, keyword, or operator such as `fmap`, `match`, or `|>`.
- Always edit `.coco` source files, never the `.py` files compiled from them.
