#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: The Coconut language server (coconut --lsp): compiler diagnostics and Python-level
code intelligence for Coconut, plus a command-line interface and an MCP server for AI agents.

Requires Python 3.8+; jedi (code intelligence) and pyflakes (linting) are optional and come with
coconut[lsp]. Nothing here may be imported by the rest of Coconut except behind --lsp, since the
compiler itself still supports Python 2.
"""
