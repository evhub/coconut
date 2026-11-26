#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: The Coconut language server.

Run with `coconut --lsp` or `python -m coconut.lsp` (communicates over stdio).
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from lsprotocol import types
from pygls.lsp.server import LanguageServer
from pygls.uris import to_fs_path, from_fs_path

from coconut.root import VERSION_STR
from coconut.terminal import logger
from coconut.lsp.analysis import (
    Analyzer,
    document_symbols,
)

# -----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

# how long to wait after the last change before recompiling
debounce_secs = 0.3

severities = {
    "error": types.DiagnosticSeverity.Error,
    "warning": types.DiagnosticSeverity.Warning,
}

completion_kinds = {
    "module": types.CompletionItemKind.Module,
    "class": types.CompletionItemKind.Class,
    "instance": types.CompletionItemKind.Variable,
    "function": types.CompletionItemKind.Function,
    "param": types.CompletionItemKind.Variable,
    "path": types.CompletionItemKind.File,
    "keyword": types.CompletionItemKind.Keyword,
    "property": types.CompletionItemKind.Property,
    "statement": types.CompletionItemKind.Variable,
}

symbol_kinds = {
    "function": types.SymbolKind.Function,
    "class": types.SymbolKind.Class,
    "type": types.SymbolKind.TypeParameter,
    "operator": types.SymbolKind.Operator,
}

# -----------------------------------------------------------------------------------------------------------------------
# SERVER:
# -----------------------------------------------------------------------------------------------------------------------


class CoconutLanguageServer(LanguageServer):
    """Language server for Coconut."""

    def __init__(self, *args, **kwargs):
        super(CoconutLanguageServer, self).__init__(*args, **kwargs)
        self.analyzer = Analyzer()
        # the Coconut compiler isn't thread-safe, so we do all compilation on a single thread
        self.compile_executor = ThreadPoolExecutor(max_workers=1)
        self.pending_versions = {}

    def run_in_compile_thread(self, func, *args):
        """Run func(*args) on the compilation thread."""
        return asyncio.get_event_loop().run_in_executor(self.compile_executor, func, *args)

    async def schedule_analysis(self, uri, version):
        """Analyze the given document once it has stopped changing."""
        self.pending_versions[uri] = version
        await asyncio.sleep(debounce_secs)
        if self.pending_versions.get(uri) != version:
            return  # a newer change is pending
        document = self.workspace.get_text_document(uri)
        source = document.source
        diagnostics = await self.run_in_compile_thread(self.analyzer.analyze, uri, source, to_fs_path(uri))
        # don't publish stale diagnostics
        if self.pending_versions.get(uri) != version:
            return
        self.text_document_publish_diagnostics(types.PublishDiagnosticsParams(
            uri=uri,
            version=version,
            diagnostics=[
                types.Diagnostic(
                    range=types.Range(
                        start=types.Position(line=diag.start[0], character=diag.start[1]),
                        end=types.Position(line=diag.end[0], character=diag.end[1]),
                    ),
                    message=diag.message,
                    severity=severities[diag.severity],
                    source="coconut",
                )
                for diag in diagnostics
            ],
        ))


server = CoconutLanguageServer("coconut-lsp", VERSION_STR)


@server.feature(types.INITIALIZED)
async def initialized(ls, params):
    """Warm up the compiler in the background as soon as the client is ready."""
    await ls.run_in_compile_thread(ls.analyzer.warm_up)


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params):
    await ls.schedule_analysis(params.text_document.uri, params.text_document.version)


@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
async def did_change(ls, params):
    await ls.schedule_analysis(params.text_document.uri, params.text_document.version)


@server.feature(types.TEXT_DOCUMENT_DID_SAVE)
async def did_save(ls, params):
    document = ls.workspace.get_text_document(params.text_document.uri)
    await ls.schedule_analysis(params.text_document.uri, document.version)


@server.feature(types.TEXT_DOCUMENT_DID_CLOSE)
def did_close(ls, params):
    uri = params.text_document.uri
    ls.pending_versions.pop(uri, None)
    ls.analyzer.forget(uri)
    ls.text_document_publish_diagnostics(types.PublishDiagnosticsParams(uri=uri, diagnostics=[]))


@server.feature(types.TEXT_DOCUMENT_HOVER)
async def hover(ls, params):
    compiled = ls.analyzer.get_compiled(params.text_document.uri)
    if compiled is None:
        return None
    text = await ls.run_in_compile_thread(compiled.hover, params.position.line, params.position.character)
    if text is None:
        return None
    return types.Hover(contents=types.MarkupContent(kind=types.MarkupKind.Markdown, value=text))


@server.feature(types.TEXT_DOCUMENT_DEFINITION)
async def definition(ls, params):
    uri = params.text_document.uri
    compiled = ls.analyzer.get_compiled(uri)
    if compiled is None:
        return None
    locations = await ls.run_in_compile_thread(compiled.definitions, params.position.line, params.position.character)
    return [
        types.Location(
            uri=uri if path is None else from_fs_path(path),
            range=types.Range(
                start=types.Position(line=line, character=character),
                end=types.Position(line=line, character=character),
            ),
        )
        for path, line, character in locations
    ]


@server.feature(
    types.TEXT_DOCUMENT_COMPLETION,
    types.CompletionOptions(trigger_characters=["."]),
)
async def completion(ls, params):
    uri = params.text_document.uri
    compiled = ls.analyzer.get_compiled(uri)
    if compiled is None:
        return None
    current_source = ls.workspace.get_text_document(uri).source
    results = await ls.run_in_compile_thread(compiled.completions, current_source, params.position.line, params.position.character)
    return types.CompletionList(
        is_incomplete=False,
        items=[
            types.CompletionItem(
                label=name,
                kind=completion_kinds.get(kind, types.CompletionItemKind.Text),
                detail=description,
            )
            for name, kind, description in results
        ],
    )


@server.feature(types.TEXT_DOCUMENT_DOCUMENT_SYMBOL)
def document_symbol(ls, params):
    source = ls.workspace.get_text_document(params.text_document.uri).source
    lines = source.splitlines()
    symbols = []
    for name, kind, line, character, _ in document_symbols(source):
        name_range = types.Range(
            start=types.Position(line=line, character=character),
            end=types.Position(line=line, character=character + len(name)),
        )
        symbols.append(types.DocumentSymbol(
            name=name,
            kind=symbol_kinds.get(kind, types.SymbolKind.Variable),
            range=types.Range(
                start=types.Position(line=line, character=0),
                end=types.Position(line=line, character=len(lines[line])),
            ),
            selection_range=name_range,
        ))
    return symbols


def main(args=None):
    """Start the Coconut language server over stdio."""
    logging.basicConfig(level=logging.WARNING)
    # the compiler's console output would corrupt the LSP stdio stream
    logger.quiet = True
    server.start_io()


if __name__ == "__main__":
    main()
