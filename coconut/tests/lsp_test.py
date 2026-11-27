#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: Tests for the Coconut language server (coconut --lsp), its CLI, and its MCP server.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import json
import os
import subprocess
import sys
import textwrap
import threading

import pytest

if sys.version_info < (3, 8):
    pytest.skip("the language server requires Python 3.8+", allow_module_level=True)

import queue  # noqa: E402

from coconut.lsp import docs  # noqa: E402
from coconut.lsp.compiler import compile_coconut, repair_source  # noqa: E402
from coconut.lsp.sourcemap import CompiledDocument, LineDiff, blank_strings_and_comments, word_occurrences  # noqa: E402
from coconut.lsp.uris import path_to_uri, uri_to_path  # noqa: E402


# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------

SERVER_CMD = [sys.executable, "-m", "coconut.lsp"]

try:
    import pyflakes  # noqa: F401
except ImportError:
    HAS_PYFLAKES = False
else:
    HAS_PYFLAKES = True


class LspClient(object):

    def __init__(self, root, init_options=None, cmd=None):
        self.proc = subprocess.Popen(
            cmd or SERVER_CMD,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.next_id = 0
        self.responses = {}
        self.notifications = queue.Queue()
        self.cond = threading.Condition()
        self.reader = threading.Thread(target=self._read)
        self.reader.daemon = True
        self.reader.start()
        self.stderr_lines = []
        self.err_reader = threading.Thread(target=self._read_err)
        self.err_reader.daemon = True
        self.err_reader.start()
        self.root = root
        self.init_result = self.request("initialize", {
            "processId": os.getpid(),
            "rootUri": self.uri(root),
            "workspaceFolders": [{"uri": self.uri(root), "name": "root"}],
            "capabilities": {},
            "initializationOptions": init_options or {},
        })
        self.notify("initialized", {})

    @staticmethod
    def uri(path):
        from coconut.lsp.uris import path_to_uri
        return path_to_uri(path)

    def _read_err(self):
        for line in self.proc.stderr:
            self.stderr_lines.append(line.decode("utf-8", "replace"))

    def _read(self):
        stream = self.proc.stdout
        while True:
            headers = {}
            while True:
                line = stream.readline()
                if not line:
                    return
                line = line.decode("ascii").strip()
                if not line:
                    break
                key, value = line.split(":", 1)
                headers[key.lower()] = value.strip()
            body = stream.read(int(headers["content-length"]))
            msg = json.loads(body.decode("utf-8"))
            if "id" in msg and "method" not in msg:
                with self.cond:
                    self.responses[msg["id"]] = msg
                    self.cond.notify_all()
            elif "id" in msg:
                # server -> client request: answer with null
                self._send({"jsonrpc": "2.0", "id": msg["id"], "result": None})
            else:
                self.notifications.put(msg)

    def _send(self, msg):
        body = json.dumps(msg).encode("utf-8")
        self.proc.stdin.write(b"Content-Length: " + str(len(body)).encode("ascii") + b"\r\n\r\n" + body)
        self.proc.stdin.flush()

    def request(self, method, params, timeout=60):
        self.next_id += 1
        msg_id = self.next_id
        self._send({"jsonrpc": "2.0", "id": msg_id, "method": method, "params": params})
        with self.cond:
            ok = self.cond.wait_for(lambda: msg_id in self.responses, timeout)
        if not ok:
            raise AssertionError("timed out waiting for " + method + "\nstderr:\n" + "".join(self.stderr_lines))
        response = self.responses.pop(msg_id)
        if "error" in response:
            raise LspError(response["error"])
        return response.get("result")

    def notify(self, method, params):
        self._send({"jsonrpc": "2.0", "method": method, "params": params})

    def wait_notification(self, method, predicate=None, timeout=60):
        import time
        deadline = time.time() + timeout
        while True:
            remaining = deadline - time.time()
            if remaining <= 0:
                raise AssertionError("timed out waiting for " + method + "\nstderr:\n" + "".join(self.stderr_lines))
            try:
                msg = self.notifications.get(timeout=remaining)
            except queue.Empty:
                continue
            if msg["method"] == method and (predicate is None or predicate(msg["params"])):
                return msg["params"]

    def open(self, path, text, version=1):
        uri = self.uri(path)
        self.notify("textDocument/didOpen", {"textDocument": {"uri": uri, "languageId": "coconut", "version": version, "text": text}})
        return uri

    def change(self, uri, text, version):
        self.notify("textDocument/didChange", {"textDocument": {"uri": uri, "version": version}, "contentChanges": [{"text": text}]})

    def diagnostics(self, uri, version=None, timeout=60):
        return self.wait_notification(
            "textDocument/publishDiagnostics",
            lambda p: p["uri"] == uri and (version is None or p.get("version") == version),
            timeout,
        )["diagnostics"]

    def close(self):
        try:
            self.request("shutdown", None, timeout=10)
            self.notify("exit", None)
            self.proc.wait(timeout=10)
        except Exception:
            self.proc.kill()


class LspError(Exception):
    def __init__(self, error):
        super(LspError, self).__init__(error.get("message"))
        self.error = error


# -----------------------------------------------------------------------------------------------------------------------
# LANGUAGE SERVER TESTS:
# -----------------------------------------------------------------------------------------------------------------------

MAIN = textwrap.dedent('''\
    import os
    from helpers import double

    data Point(x, y):
        def norm(self) = (self.x**2 + self.y**2)**0.5

    def add(a, b) = a + b

    match def fact(0) = 1
    addpattern def fact(n) = n * fact(n - 1)

    result = [1, 2, 3] |> map$(x => x * 2) |> list
    p = Point(1, 2)
    print(p.norm(), os.path.join("a", "b"), result |> fmap$(double), add(1, 2))
''')

HELPERS = textwrap.dedent('''\
    def double(x) = x * 2

    def triple(x) = x * 3
''')


def pos(text, line, needle, offset=0, nth=0):
    """Position of the nth occurrence of needle on (0-based) line, plus offset."""
    src = text.splitlines()[line]
    idx = -1
    for _ in range(nth + 1):
        idx = src.index(needle, idx + 1)
    return {"line": line, "character": idx + offset}


@pytest.fixture(scope="module")
def project(tmp_path_factory):
    root = tmp_path_factory.mktemp("proj")
    (root / "main.coco").write_text(MAIN)
    (root / "helpers.coco").write_text(HELPERS)
    return str(root)


@pytest.fixture(scope="module")
def client(project):
    c = LspClient(project)
    yield c
    c.close()


@pytest.fixture(scope="module")
def main_uri(client, project):
    uri = client.open(os.path.join(project, "main.coco"), MAIN)
    diags = client.diagnostics(uri)
    assert [d for d in diags if d["severity"] == 1] == []
    return uri


def td(uri):
    return {"uri": uri}


def test_capabilities(client):
    caps = client.init_result["capabilities"]
    for cap in ("hoverProvider", "completionProvider", "definitionProvider", "referencesProvider",
                "documentSymbolProvider", "workspaceSymbolProvider", "renameProvider", "signatureHelpProvider"):
        assert caps[cap]


def test_syntax_error_diagnostic(client, project):
    text = "x = 1\ny = (1 +\nz = 3\n"
    uri = client.open(os.path.join(project, "broken.coco"), text)
    diags = client.diagnostics(uri)
    errors = [d for d in diags if d["severity"] == 1]
    assert len(errors) == 1
    assert "unclosed" in errors[0]["message"]
    assert errors[0]["range"]["start"] == {"line": 1, "character": 4}
    # fix it: diagnostics clear
    client.change(uri, "x = 1\ny = (1 + 2)\nz = 3\n", 2)
    assert [d for d in client.diagnostics(uri, version=2) if d["severity"] == 1] == []


def test_lint_diagnostics(client, project):
    text = "import sys\ndef f(x) = x + undefined_name\ndef g():\n    unused_local = 3\n    return 1\n"
    uri = client.open(os.path.join(project, "lint.coco"), text)
    diags = client.diagnostics(uri)
    messages = [d["message"] for d in diags]
    assert any("sys" in m and "unused" in m for m in messages)
    assert any("undefined_name" in m for m in messages)
    if HAS_PYFLAKES:  # (pyflakes comes with coconut[lsp] on Python 3.9+; the checks above are Coconut's own)
        assert any("unused_local" in m for m in messages)
    undefined = [d for d in diags if "undefined_name" in d["message"]][0]
    assert undefined["range"]["start"] == {"line": 1, "character": 15}
    # code actions: remove the unused import / suppress with NOQA
    unused = [d for d in diags if "sys" in d["message"]][0]
    actions = client.request("textDocument/codeAction", {
        "textDocument": td(uri), "range": unused["range"], "context": {"diagnostics": [unused]},
    })
    titles = [a["title"] for a in actions]
    assert "Remove unused import 'sys'" in titles
    noqa = [d for d in diags if d.get("source") == "coconut" and "NOQA" in d["message"]]
    if noqa:
        actions = client.request("textDocument/codeAction", {
            "textDocument": td(uri), "range": noqa[0]["range"], "context": {"diagnostics": [noqa[0]]},
        })
        assert any(a["title"] == "Suppress with # NOQA" for a in actions)


def test_hover_user_function(client, main_uri):
    result = client.request("textDocument/hover", {"textDocument": td(main_uri), "position": pos(MAIN, 13, "norm")})
    assert "norm" in result["contents"]["value"]
    assert result["range"]["start"] == pos(MAIN, 13, "norm")


def test_hover_coconut_builtin(client, main_uri):
    result = client.request("textDocument/hover", {"textDocument": td(main_uri), "position": pos(MAIN, 13, "fmap", 1)})
    value = result["contents"]["value"]
    assert "Coconut" in value and "fmap" in value
    assert "coconut.readthedocs.io" in value


def test_hover_operator_and_keyword(client, main_uri):
    result = client.request("textDocument/hover", {"textDocument": td(main_uri), "position": pos(MAIN, 11, "|>", 1)})
    assert "Pipes" in result["contents"]["value"]
    result = client.request("textDocument/hover", {"textDocument": td(main_uri), "position": pos(MAIN, 3, "data", 1)})
    assert "data" in result["contents"]["value"]
    result = client.request("textDocument/hover", {"textDocument": td(main_uri), "position": pos(MAIN, 8, "match", 1)})
    assert "Pattern-Matching Functions" in result["contents"]["value"]


def test_definition_same_file(client, main_uri):
    result = client.request("textDocument/definition", {"textDocument": td(main_uri), "position": pos(MAIN, 12, "Point", 2)})
    assert result[0]["uri"] == main_uri
    assert result[0]["range"]["start"] == pos(MAIN, 3, "Point")
    result = client.request("textDocument/definition", {"textDocument": td(main_uri), "position": pos(MAIN, 13, "norm", 1)})
    assert result[0]["range"]["start"] == pos(MAIN, 4, "norm")


def test_definition_other_coconut_file(client, main_uri, project):
    result = client.request("textDocument/definition", {"textDocument": td(main_uri), "position": pos(MAIN, 13, "double", 1)})
    uris = [r["uri"] for r in result]
    assert any(u.endswith("helpers.coco") for u in uris), result
    target = [r for r in result if r["uri"].endswith("helpers.coco")][0]
    assert target["range"]["start"] == {"line": 0, "character": 4}


def test_references_and_highlight(client, main_uri):
    result = client.request("textDocument/references", {
        "textDocument": td(main_uri), "position": pos(MAIN, 12, "p"), "context": {"includeDeclaration": True},
    })
    starts = [r["range"]["start"] for r in result]
    assert pos(MAIN, 12, "p") in starts and pos(MAIN, 13, "p.", 0) in starts
    highlights = client.request("textDocument/documentHighlight", {"textDocument": td(main_uri), "position": pos(MAIN, 6, "a", 0, 1)})
    assert len(highlights) == 2


def test_rename(client, main_uri):
    prep = client.request("textDocument/prepareRename", {"textDocument": td(main_uri), "position": pos(MAIN, 9, "n)")})
    assert prep["placeholder"] == "n"
    edit = client.request("textDocument/rename", {"textDocument": td(main_uri), "position": pos(MAIN, 9, "n)"), "newName": "k"})
    edits = edit["changes"][main_uri]
    assert len(edits) == 3
    assert all(e["range"]["start"]["line"] == 9 for e in edits)
    with pytest.raises(LspError):
        client.request("textDocument/rename", {"textDocument": td(main_uri), "position": pos(MAIN, 9, "n)"), "newName": "not valid"})


def test_document_symbols(client, main_uri):
    symbols = client.request("textDocument/documentSymbol", {"textDocument": td(main_uri)})
    names = [s["name"] for s in symbols]
    assert names[:5] == ["Point", "add", "fact", "result", "p"]
    point = symbols[0]
    assert point["detail"] == "data"
    assert [c["name"] for c in point["children"]] == ["norm"]
    fact = symbols[2]
    assert fact["range"]["start"]["line"] == 8 and fact["range"]["end"]["line"] == 9


def test_workspace_symbols(client, main_uri):
    result = client.request("workspace/symbol", {"query": "trip"})
    assert [r["name"] for r in result] == ["triple"]
    assert result[0]["location"]["uri"].endswith("helpers.coco")
    result = client.request("workspace/symbol", {"query": "Point"})
    assert any(r["name"] == "Point" for r in result)


def test_completion_while_typing(client, project):
    path = os.path.join(project, "typing.coco")
    base = MAIN.replace("from helpers import double\n", "")
    uri = client.open(path, base)
    client.diagnostics(uri)
    # start typing a new line: the document no longer compiles, completion must still work
    typed = base + "p.no"
    client.change(uri, typed, 2)
    line = len(typed.splitlines()) - 1
    result = client.request("textDocument/completion", {"textDocument": td(uri), "position": {"line": line, "character": 4}})
    labels = [i["label"] for i in result["items"]]
    assert "norm" in labels
    typed = base + "os.path.jo"
    client.change(uri, typed, 3)
    result = client.request("textDocument/completion", {"textDocument": td(uri), "position": {"line": line, "character": 10}})
    assert "join" in [i["label"] for i in result["items"]]
    # completion inside a method body, on self
    typed = base.replace(
        "    def norm(self) = (self.x**2 + self.y**2)**0.5\n",
        "    def norm(self) = (self.x**2 + self.y**2)**0.5\n    def other(self):\n        self.\n",
    )
    client.change(uri, typed, 4)
    result = client.request("textDocument/completion", {"textDocument": td(uri), "position": {"line": 5, "character": 13}})
    labels = [i["label"] for i in result["items"]]
    assert "norm" in labels and "x" in labels
    # Coconut built-ins and keywords
    typed = base + "fm"
    client.change(uri, typed, 5)
    result = client.request("textDocument/completion", {"textDocument": td(uri), "position": {"line": line, "character": 2}})
    fmap = [i for i in result["items"] if i["label"] == "fmap"]
    assert fmap and "Coconut" in fmap[0]["documentation"]["value"]


def test_signature_help(client, main_uri, project):
    path = os.path.join(project, "sig.coco")
    text = "def add(a, b) = a + b\nadd(1, "
    uri = client.open(path, text)
    result = client.request("textDocument/signatureHelp", {"textDocument": td(uri), "position": {"line": 1, "character": 7}})
    assert result["signatures"][0]["label"] == "add(a, b)"
    assert result["activeParameter"] == 1


def test_compiled_request(client, main_uri):
    result = client.request("coconut/compiled", {"textDocument": td(main_uri)})
    assert result["upToDate"]
    assert "class Point" in result["compiled"]
    info = client.request("coconut/info", {})
    assert info["coconut_version"]


def test_settings_change_recompiles(client, project):
    # 'match x:' style errors aside, use a target-dependent feature: walrus requires 3.8+
    text = "if (n := 10) > 5:\n    print(n)\n"
    uri = client.open(os.path.join(project, "target.coco"), text)
    assert [d for d in client.diagnostics(uri) if d["severity"] == 1] == []
    client.notify("workspace/didChangeConfiguration", {"settings": {"coconut": {"target": "2.7"}}})
    diags = client.diagnostics(uri)
    assert any(d["severity"] == 1 for d in diags), diags
    client.notify("workspace/didChangeConfiguration", {"settings": {"coconut": {"target": "sys"}}})
    assert [d for d in client.diagnostics(uri) if d["severity"] == 1] == []


PURE_CODE = textwrap.dedent('''\
    def total(xs):
        acc = []
        acc.append(sum(xs))
        return acc
''')


def test_pure_setting(client, project):
    uri = client.open(os.path.join(project, "impure.coco"), PURE_CODE)
    assert not any("--pure" in d["message"] for d in client.diagnostics(uri))
    client.notify("workspace/didChangeConfiguration", {"settings": {"coconut": {"pure": True}}})
    diags = [d for d in client.diagnostics(uri) if "mutating method" in d["message"]]
    assert len(diags) == 1 and diags[0]["range"]["start"]["line"] == 2, diags
    client.notify("workspace/didChangeConfiguration", {"settings": {"coconut": {"pure": False}}})
    assert not any("--pure" in d["message"] for d in client.diagnostics(uri))


def test_coconut_lsp_flags_set_defaults(project):
    # flags passed to 'coconut --lsp' become the server's default settings
    c = LspClient(project, cmd=[sys.executable, "-m", "coconut", "--lsp", "--strict", "--pure"])
    try:
        uri = c.open(os.path.join(project, "impure_cli.coco"), PURE_CODE)
        diags = [d for d in c.diagnostics(uri) if "mutating method" in d["message"]]
        # reported once (as a style error), even though the server also recompiles without --strict
        assert len(diags) == 1 and diags[0]["code"] == "CoconutStyleError", diags
    finally:
        c.close()


def test_project_config(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[tool.coconut]\npure = true\n')
    impure = tmp_path / "impure.coco"
    impure.write_text(PURE_CODE)
    c = LspClient(str(tmp_path))
    try:
        uri = c.open(str(impure), PURE_CODE)
        diags = [d for d in c.diagnostics(uri) if "mutating method" in d["message"]]
        assert len(diags) == 1, diags
    finally:
        c.close()
    code, out, err = run_cli("check", str(impure))
    assert "mutating method 'append'" in out, out + err
    (tmp_path / "pyproject.toml").write_text('[tool.coconut]\npure = 1\n')
    code, out, err = run_cli("check", str(impure))
    assert "invalid project configuration" in out and "must be true or false" in out, out + err


def test_cross_module_intelligence(client, project):
    # helpers.coco has no compiled helpers.py, so jedi only sees it through the overlay
    assert not os.path.exists(os.path.join(project, "helpers.py"))
    text = "import helpers\nfrom helpers import double\nhelpers.tr\ndouble(\n"
    uri = client.open(os.path.join(project, "importer.coco"), text)
    client.diagnostics(uri)
    result = client.request("textDocument/completion", {"textDocument": td(uri), "position": {"line": 2, "character": 10}})
    assert "triple" in [i["label"] for i in result["items"]]
    sig = client.request("textDocument/signatureHelp", {"textDocument": td(uri), "position": {"line": 3, "character": 7}})
    assert sig["signatures"][0]["label"] == "double(x)"
    hover = client.request("textDocument/hover", {"textDocument": td(uri), "position": {"line": 1, "character": 22}})
    assert "double(x)" in hover["contents"]["value"]
    result = client.request("textDocument/definition", {"textDocument": td(uri), "position": {"line": 3, "character": 2}})
    assert result and result[0]["uri"].endswith("helpers.coco")
    assert result[0]["range"]["start"] == {"line": 0, "character": 4}


def test_mypy_type_checking(project):
    pytest.importorskip("mypy")
    client = LspClient(project, init_options={"mypy": True})
    try:
        text = "def g() -> int = 1\ndef f(x: int) -> str = x\nw: str = g()\nok: int = g()\n"
        uri = client.open(os.path.join(project, "typed.coco"), text)
        diags = client.wait_notification(
            "textDocument/publishDiagnostics",
            lambda p: p["uri"] == uri and any(d.get("source") == "mypy" for d in p["diagnostics"]),
            timeout=330,  # a cold mypy run on a slow CI machine can take a while
        )["diagnostics"]
        mypy = sorted((d["range"]["start"]["line"], d["range"]["start"]["character"], d["code"]) for d in diags if d.get("source") == "mypy")
        assert mypy == [(1, 23, "return-value"), (2, 9, "assignment")], diags
    finally:
        client.close()


def test_utf16_positions(client, project):
    # columns are UTF-16 code units in LSP; the emoji takes two of them
    text = 'foo = 1\nprint("\U0001F600", foo)\n'
    uri = client.open(os.path.join(project, "emoji.coco"), text)
    client.diagnostics(uri)
    refs = client.request("textDocument/references", {
        "textDocument": td(uri), "position": {"line": 1, "character": 12}, "context": {"includeDeclaration": True},
    })
    starts = sorted((r["range"]["start"]["line"], r["range"]["start"]["character"], r["range"]["end"]["character"]) for r in refs)
    assert starts == [(0, 0, 3), (1, 12, 15)]
    edit = client.request("textDocument/rename", {"textDocument": td(uri), "position": {"line": 1, "character": 13}, "newName": "bar"})
    assert sorted(e["range"]["start"]["character"] for e in edit["changes"][uri]) == [0, 12]


def test_rename_refused_when_file_has_errors(client, project):
    text = "foo = 1\nprint(foo +)\nprint(foo)\n"
    uri = client.open(os.path.join(project, "broken_rename.coco"), text)
    client.diagnostics(uri)
    with pytest.raises(LspError):
        client.request("textDocument/rename", {"textDocument": td(uri), "position": {"line": 0, "character": 0}, "newName": "bar"})


def test_no_diagnostics_after_close(client, project):
    uri = client.open(os.path.join(project, "closed.coco"), "x = (\n")
    client.notify("textDocument/didClose", {"textDocument": {"uri": uri}})
    cleared = client.wait_notification("textDocument/publishDiagnostics", lambda p: p["uri"] == uri)
    assert cleared["diagnostics"] == []
    # nothing may be published for the closed document afterwards
    import time
    time.sleep(2)
    while not client.notifications.empty():
        msg = client.notifications.get()
        assert not (msg["method"] == "textDocument/publishDiagnostics" and msg["params"]["uri"] == uri), msg


# -----------------------------------------------------------------------------------------------------------------------
# CLI AND MCP TESTS:
# -----------------------------------------------------------------------------------------------------------------------

CODE = textwrap.dedent('''\
    import sys

    data Point(x, y)

    def scale(p, k) = Point(p.x * k, p.y * k)

    origin = Point(0, 0) |> scale$(k=2)
''')


@pytest.fixture(scope="module")
def coco_file(tmp_path_factory):
    path = tmp_path_factory.mktemp("cli") / "geo.coco"
    path.write_text(CODE)
    return str(path)


@pytest.fixture(scope="module")
def mcp():
    # stderr must be drained (or discarded): a full pipe would block the server (Windows pipes are tiny)
    proc = subprocess.Popen(SERVER_CMD + ["mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, universal_newlines=True, bufsize=1)
    lines = queue.Queue()

    def reader():
        for line in proc.stdout:
            lines.put(line)

    threading.Thread(target=reader, daemon=True).start()
    state = {"id": 0}

    def call(method, params=None, notify=False):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            state["id"] += 1
            msg["id"] = state["id"]
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()
        if notify:
            return None
        response = json.loads(lines.get(timeout=120))
        assert response["id"] == state["id"]
        return response

    init = call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "test", "version": "0"}})
    assert init["result"]["protocolVersion"] == "2025-06-18"
    call("notifications/initialized", notify=True)
    yield call
    proc.stdin.close()
    proc.wait(timeout=10)


def tool(mcp, name, **args):
    response = mcp("tools/call", {"name": name, "arguments": args})
    result = response["result"]
    return result["content"][0]["text"], result["isError"]


def test_mcp_tools_list(mcp):
    names = [t["name"] for t in mcp("tools/list")["result"]["tools"]]
    assert names == ["coconut_check", "coconut_compile", "coconut_docs", "coconut_hover",
                     "coconut_definition", "coconut_references", "coconut_symbols"]


def test_mcp_check(mcp, coco_file):
    text, err = tool(mcp, "coconut_check", path=coco_file)
    assert not err
    assert "0 errors" in text and "'sys'" in text
    text, err = tool(mcp, "coconut_check", code="x = (1 +\n")
    assert "1 error" in text and ":1:5: error: unclosed" in text


def test_mcp_check_pure(mcp):
    text, err = tool(mcp, "coconut_check", code=PURE_CODE)
    assert "mutating method" not in text
    text, err = tool(mcp, "coconut_check", code=PURE_CODE, pure=True)
    assert "3:5" in text and "mutating method 'append'" in text, text


def test_mcp_compile(mcp):
    text, err = tool(mcp, "coconut_compile", code="x = [1, 2] |> map$(.+1) |> list\n")
    assert not err
    assert "Coconut Header" not in text and "(line in Coconut source)" not in text
    assert "map" in text and "list" in text
    text, err = tool(mcp, "coconut_compile", code="x = (\n")
    assert err and "doesn't compile" in text


def test_mcp_docs(mcp):
    text, err = tool(mcp, "coconut_docs", query="|>")
    assert not err and "Pipes" in text
    text, err = tool(mcp, "coconut_docs", query="addpattern")
    assert "addpattern" in text
    text, err = tool(mcp, "coconut_docs")
    assert "`fmap`" in text
    text, err = tool(mcp, "coconut_docs", query="zzzz-nothing")
    assert err


def test_mcp_code_intelligence(mcp, coco_file):
    text, err = tool(mcp, "coconut_definition", path=coco_file, line=7, column=25)
    assert not err and ":5:5:" in text  # scale
    text, err = tool(mcp, "coconut_hover", path=coco_file, line=7, column=25)
    assert "scale" in text
    text, err = tool(mcp, "coconut_references", path=coco_file, line=5, column=5)
    assert text.count("geo.coco") == 2
    text, err = tool(mcp, "coconut_symbols", path=coco_file)
    assert "data Point" in text and "function scale" in text and "variable origin" in text
    text, err = tool(mcp, "coconut_hover", path=coco_file, line=0, column=1)
    assert err


def test_mcp_unknown(mcp):
    assert mcp("bogus/method")["error"]["code"] == -32601
    text, err = tool(mcp, "nope")
    assert err


def run_cli(*args):
    proc = subprocess.run(SERVER_CMD + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True, timeout=240)
    return proc.returncode, proc.stdout, proc.stderr


def test_cli_check(coco_file, tmp_path):
    code, out, err = run_cli("check", coco_file)
    assert code == 0 and "unused import 'sys'" in out
    code, out, err = run_cli("check", coco_file, "-W")
    assert code == 1
    bad = tmp_path / "bad.coco"
    bad.write_text("def f(x) =\n")
    code, out, err = run_cli("check", str(tmp_path), "--json")
    assert code == 1
    data = json.loads(out)
    assert data["files_checked"] == 1 and data["diagnostics"][0]["severity"] == "error"


def test_cli_check_pure(tmp_path):
    impure = tmp_path / "impure.coco"
    impure.write_text(PURE_CODE)
    code, out, err = run_cli("check", str(impure), "--pure")
    assert "mutating method 'append'" in out, out + err
    code, out, err = run_cli("check", str(impure))
    assert "mutating method" not in out


def test_cli_position_commands(coco_file):
    code, out, err = run_cli("definition", coco_file, "7", "25")
    assert code == 0 and ":5:5:" in out
    code, out, err = run_cli("symbols", coco_file, "--json")
    assert [s["name"] for s in json.loads(out)] == ["Point", "scale", "origin"]
    code, out, err = run_cli("compile", coco_file, "--no-line-comments")
    assert code == 0 and "def scale(p, k):" in out
    code, out, err = run_cli("docs", "fmap")
    assert code == 0 and "fmap" in out


def test_cli_accepts_stdio_flag():
    # LSP clients often launch servers with --stdio; it must start the server, not error out
    proc = subprocess.Popen(SERVER_CMD + ["--stdio"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate(b"", timeout=30)
    assert b"unrecognized arguments" not in err


def test_cli_check_mypy(tmp_path):
    pytest.importorskip("mypy")
    path = tmp_path / "typed.coco"
    path.write_text("def f(x: int) -> str = x\n")
    code, out, err = run_cli("check", str(path), "--mypy")
    assert code == 1 and ":1:24: error: Incompatible return value type" in out, out + err


# -----------------------------------------------------------------------------------------------------------------------
# UNIT TESTS:
# -----------------------------------------------------------------------------------------------------------------------

def test_blank_strings_and_comments():
    line = '''x = f("a(b)", 'c') + g(f"{x}") # comment x'''
    blanked = blank_strings_and_comments(line)
    assert len(blanked) == len(line)
    assert "a(b)" not in blanked and "comment" not in blanked and "{x}" in blanked
    assert word_occurrences(line, "x") == [0, 26]


def test_line_diff():
    old = ["a", "b", "c", "d"]
    new = ["a", "b", "X", "c", "d"]
    diff = LineDiff(old, new)
    assert diff.new_to_old(3) == 2 and diff.old_to_new(2) == 3
    assert diff.new_to_old(2) is None
    assert diff.nearest_new_to_old_before(2) == 1


def test_source_mapping_roundtrip():
    src = "def add(a, b) = a + b\nresult = [1, 2] |> map$(add$(1)) |> list\n"
    doc = CompiledDocument(src, compile_coconut(src)["compiled"])
    line = src.splitlines()[1]
    col = line.index("add")
    cl, cc = doc.source_to_compiled(1, col)
    assert doc.compiled_line(cl)[cc:cc + 3] == "add"
    assert doc.compiled_to_source(cl, cc, word="add") == (1, col, col + 3)


@pytest.mark.parametrize("code, line, col", [
    ("x = 1\ny = (1 +\nz = 3\n", 1, 4),
    ("def f(x) =\n", 0, None),
    ("a = 1\nb = 2 3\n", 1, None),
])
def test_error_positions(code, line, col):
    result = compile_coconut(code)
    assert result["compiled"] is None
    errors = [d for d in result["diagnostics"] if d["severity"] == 1]
    assert errors and errors[0]["range"]["start"]["line"] == line
    if col is not None:
        assert errors[0]["range"]["start"]["character"] == col
    rng = errors[0]["range"]
    assert (rng["end"]["line"], rng["end"]["character"]) >= (rng["start"]["line"], rng["start"]["character"])


def test_repair_source():
    assert repair_source("x = 1\ny = (\nz = 2", 1) == "x = 1\npass\nz = 2"
    assert repair_source("def f(x) =\n    x +\n", 0) == "if True:\n    x +\n"
    repaired = repair_source("a = 1\ndef g():\n    b = (\n    return 1\n", 2)
    assert compile_coconut(repaired)["compiled"] is not None


def test_docs():
    assert docs.lookup("fmap")["url"].endswith("#fmap")
    assert docs.operator_at("x |> f", 3)[0] == "|>"
    assert docs.operator_at("f ..> g", 2)[0] == "..>"
    assert docs.operator_at("a + b", 2) is None
    assert docs.keyword_entry("match def f(x) = x", 0, 5) == "match def"
    assert docs.keyword_entry("data = 5", 0, 4) is None
    assert docs.keyword_entry("data Point(x, y)", 0, 4) == "data"
    assert docs.search("pattern matching")


def test_uris():
    path = os.path.abspath("some dir/file.coco")
    assert uri_to_path(path_to_uri(path)) == path
    assert uri_to_path("untitled:Untitled-1") is None


def test_works_without_jedi(monkeypatch):
    from coconut.lsp import intel
    monkeypatch.setattr(intel, "jedi", None)
    src = "x = [1] |> fmap$(y => y)\n"
    doc = CompiledDocument(src, compile_coconut(src)["compiled"])
    analyzer = intel.Analyzer("/tmp/nojedi.coco", src + "fm", doc)
    hover = analyzer.hover(0, src.index("fmap") + 1)
    assert hover and "fmap" in hover[0]
    labels = [i["label"] for i in analyzer.completions(1, 2)]
    assert "fmap" in labels
    assert analyzer.definitions(0, 0) == [] or analyzer.definitions(0, 0)
    assert analyzer.signature_help(0, 5) is None


def test_claude_code_plugin():
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    marketplace_path = os.path.join(repo, ".claude-plugin", "marketplace.json")
    if not os.path.exists(marketplace_path):
        pytest.skip("not running from a source checkout")
    with open(marketplace_path) as f:
        marketplace = json.load(f)
    entry = marketplace["plugins"][0]
    plugin_dir = os.path.join(repo, entry["source"])
    with open(os.path.join(plugin_dir, ".claude-plugin", "plugin.json")) as f:
        plugin = json.load(f)
    assert plugin["name"] == entry["name"]
    # the plugin runs the language server and the MCP server that this package provides
    with open(os.path.join(plugin_dir, ".lsp.json")) as f:
        lsp = json.load(f)
    assert [lsp["coconut"]["command"]] + lsp["coconut"]["args"] == ["coconut", "--lsp", "--strict"]
    assert lsp["coconut"]["extensionToLanguage"][".coco"] == "coconut"
    # both go through the same 'coconut' entry point, so they run in the same environment
    mcp = plugin["mcpServers"]["coconut"]
    assert [mcp["command"]] + mcp["args"] == ["coconut", "--mcp"]
    # the skill defers to the maintained AI guide rather than duplicating it
    with open(os.path.join(plugin_dir, "skills", "coconut", "SKILL.md")) as f:
        skill = f.read()
    assert "coconut --ai-docs" in skill


def test_worker_env_never_shadows_stdlib(monkeypatch):
    from coconut.lsp import worker
    package_parent = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(worker.__file__))))
    # installed in a site directory: PYTHONPATH must be left alone (it would come before the stdlib)
    monkeypatch.setattr(worker, "_site_dirs", lambda: {os.path.normcase(os.path.abspath(package_parent))})
    env = worker.worker_env({"PYTHONPATH": "/existing"})
    assert env["PYTHONPATH"] == "/existing"
    # e.g. a source checkout: the worker needs to find this copy of Coconut
    monkeypatch.setattr(worker, "_site_dirs", lambda: set())
    env = worker.worker_env({})
    assert env["PYTHONPATH"] == package_parent


def test_hover_docs_up_to_date():
    from coconut.lsp import generate_docs
    if not os.path.exists(generate_docs.DEFAULT_SOURCE):
        pytest.skip("not running from a source checkout")
    with open(generate_docs.DEFAULT_SOURCE, encoding="utf-8") as f:
        expected = json.dumps(generate_docs.generate(f.read()), indent=2, sort_keys=True) + "\n"
    with open(generate_docs.OUT_PATH, encoding="utf-8") as f:
        actual = f.read()
    assert actual == expected, "coconut/lsp/data/docs.json is out of date with DOCS.md; run: python -m coconut.lsp.generate_docs"
