---
name: coconut
description: Write, read, debug, and verify code in Coconut, the functional superset of Python that compiles to Python (.coco files).
when_to_use: Use when creating or editing .coco/.coc/.coconut files, when a project uses the Coconut compiler, or when asked about Coconut syntax.
---

# Coconut

Before writing or changing Coconut code, run `coconut --ai-docs` and read its output: it's Coconut's own guide to writing idiomatic Coconut, kept up to date with the installed version (online at https://coconut.readthedocs.io/en/latest/llms.txt). Follow it, including its "Style standard" and "Common pitfalls" sections.

Write new code in a functional style that passes both `--strict` and `--pure` (no reassignment, no mutation). In an existing project whose code doesn't pass `--pure`, hold your new code to it but don't rewrite unrelated code. Fix what these checks report by restructuring the code, not by adding `# NOQA`.

To check your work:
- The Coconut language server reports errors and warnings, including `--strict` style warnings, after each edit to a `.coco` file.
- Use the `coconut_check` MCP tool with `strict` and `pure` set, or run `python -m coconut.lsp check --strict --pure <files or dirs>`, to check files or a whole project (add `mypy`/`--mypy` to type check).
- Use `coconut_compile` (or `python -m coconut.lsp compile <file>`) to see the Python a construct compiles to, and `coconut_docs` (or `python -m coconut.lsp docs <name>`) to look up a built-in, keyword, or operator such as `fmap`, `match`, or `|>`.
- Always edit `.coco` source files, never the `.py` files compiled from them.
