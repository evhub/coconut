#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Claude
License: Apache 2.0
Description: Generates the interactive version of Coconut's tutorial (HELP.md), in which every example can
be edited and run right in the browser (using Pyodide), for inclusion in the documentation.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

import os
import re
import sys
import json
import html

from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

# -----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

pyodide_version = "0.27.7"
pyodide_url = "https://cdn.jsdelivr.net/pyodide/v" + pyodide_version + "/full/"
codemirror_url = "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/"

# packages that come with Pyodide that we need (note that we can't load any that depend on pyparsing,
#  such as setuptools, since Pyodide's pyparsing is pyparsing 3, which Coconut doesn't support)
pyodide_packages = ["micropip"]

# code blocks in the tutorial that aren't complete examples (e.g. ones showing syntax or a single method)
non_example_prefixes = ("Coconut Interpreter", ".attr", "reduce(f,", "return ", "range(1, n+1) |> reduce")

# lexers for the non-runnable code blocks in the tutorial
lexer_names = {
    "coconut_python": "python",
    "coconut_pycon": "coconut_pycon",
    "toml": "toml",
}

# Python code run in Pyodide to set up Coconut and run examples like the Coconut interpreter would
runner_code = r'''
import os, sys, io
os.environ["COCONUT_PURE_PYTHON"] = "TRUE"

from coconut.terminal import logger
from coconut.compiler import Compiler

# since we compile one statement at a time, names defined by earlier statements look undefined
#  and imports used by later statements look unused, so don't warn about those
logger.setup(silence_warnings=["found undefined name", "found unused import"])

_compiler = Compiler()
_compiler.setup(line_numbers=False)

_namespace = {}
exec(_compiler.parse_sys("pass"), _namespace)


def _statements(code):
    """Split code into the statements one would enter into the interpreter one at a time."""
    out, cur = [], []
    for line in code.splitlines():
        if (
            line and not line[0].isspace() and cur
            and not cur[-1].rstrip().endswith(("=", "(", ",", "\\"))
            and not cur[-1].startswith("@")
            and not line.startswith((")", "]", "}", "else", "except", "elif", "finally"))
        ):
            out.append("\n".join(cur))
            cur = []
        cur.append(line)
    if cur:
        out.append("\n".join(cur))
    return [stmt for stmt in out if any(line.strip() and not line.strip().startswith("#") for line in stmt.splitlines())]


def _format_error(err):
    """Format an error the way the interpreter would, without the parts of the traceback that are ours."""
    msg = str(err).strip()
    if type(err).__name__.startswith("Coconut"):
        return msg
    return type(err).__name__ + (": " + msg if msg else "")


def run_example(code):
    """Run the given Coconut code like the interpreter would, returning its output."""
    out = io.StringIO()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = out
    got_name_error = False
    try:
        for stmt in _statements(code):
            try:
                try:
                    compiled = _compiler.parse_eval(stmt)
                except Exception:
                    exec(_compiler.parse_block(stmt), _namespace)
                else:
                    result = eval(compiled, _namespace)
                    if result is not None:
                        print(repr(result))
            except BaseException as err:
                got_name_error = got_name_error or isinstance(err, NameError)
                print(_format_error(err))
        if got_name_error:
            print("\n(Hint: something this example uses isn't defined yet. Try running the examples above it first, or, if this is an exercise, writing your solution above the test cases.)")
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
    return out.getvalue()


def reset_examples():
    """Clear everything that's been defined so far."""
    _namespace.clear()
    exec(_compiler.parse_sys("pass"), _namespace)
'''

# -----------------------------------------------------------------------------------------------------------------------
# PAGE TEMPLATE:
# -----------------------------------------------------------------------------------------------------------------------

page_template = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Coconut Tutorial (Interactive)</title>
<meta name="description" content="Learn Coconut, simple, elegant, Pythonic functional programming, by running and editing examples right in your browser.">
<link rel="stylesheet" href="{codemirror_url}codemirror.min.css">
<style>
:root {{
  --bg: #fbfaf7; --fg: #1f2328; --muted: #59636e; --accent: #8a5a19; --accent-fg: #fff;
  --panel: #f3f0e8; --border: #ddd6c6; --code-bg: #f6f4ee; --out-bg: #1e1e1e; --out-fg: #e6e6e6;
  --link: #0b5cad;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #16181c; --fg: #e6e6e6; --muted: #a0a7b0; --accent: #e0a458; --accent-fg: #16181c;
    --panel: #1f2228; --border: #353a43; --code-bg: #1c1f24; --out-bg: #0d0f12; --out-fg: #d8d8d8;
    --link: #7fb4ff;
  }}
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif; }}
a {{ color: var(--link); }}
header.top {{ position: sticky; top: 0; z-index: 10; display: flex; align-items: center; gap: 12px; padding: 10px 16px; background: var(--panel); border-bottom: 1px solid var(--border); }}
header.top .title {{ font-weight: 700; }}
header.top .status {{ margin-left: auto; color: var(--muted); font-size: 14px; }}
header.top a {{ font-size: 14px; }}
.layout {{ display: grid; grid-template-columns: 260px minmax(0, 1fr); max-width: 1200px; margin: 0 auto; }}
nav.toc {{ position: sticky; top: 49px; align-self: start; max-height: calc(100vh - 49px); overflow-y: auto; padding: 20px 12px 40px 16px; font-size: 14px; }}
nav.toc ul {{ list-style: none; padding-left: 12px; margin: 0; }}
nav.toc > ul {{ padding-left: 0; }}
nav.toc li {{ margin: 4px 0; }}
nav.toc a {{ color: var(--muted); text-decoration: none; }}
nav.toc a:hover {{ color: var(--fg); }}
main {{ padding: 20px 32px 80px; min-width: 0; }}
main h1 {{ font-size: 2.2em; margin-top: 0.4em; }}
main h2 {{ border-bottom: 1px solid var(--border); padding-bottom: 4px; margin-top: 2em; }}
code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.9em; background: var(--code-bg); padding: 1px 4px; border-radius: 4px; }}
pre {{ background: var(--code-bg); border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; overflow-x: auto; }}
pre code {{ background: none; padding: 0; }}
.example {{ border: 1px solid var(--border); border-radius: 8px; margin: 16px 0; overflow: hidden; background: var(--code-bg); }}
.example .CodeMirror {{ height: auto; background: var(--code-bg); color: var(--fg); font: 14px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
.example .CodeMirror-gutters {{ background: var(--code-bg); border-right: none; }}
.example .CodeMirror-cursor {{ border-left-color: var(--fg); }}
.example textarea.fallback {{ width: 100%; min-height: 6em; border: none; background: var(--code-bg); color: var(--fg); font: 14px/1.5 ui-monospace, monospace; padding: 10px; resize: vertical; }}
.example .bar {{ display: flex; gap: 8px; align-items: center; padding: 6px 8px; border-top: 1px solid var(--border); background: var(--panel); }}
.example .bar .hint {{ margin-left: auto; color: var(--muted); font-size: 12px; }}
button {{ font: inherit; font-size: 14px; border-radius: 6px; padding: 3px 12px; cursor: pointer; border: 1px solid var(--border); background: var(--bg); color: var(--fg); }}
button.run {{ background: var(--accent); color: var(--accent-fg); border-color: var(--accent); font-weight: 600; }}
button:disabled {{ opacity: 0.6; cursor: wait; }}
.example pre.output {{ margin: 0; border: none; border-top: 1px solid var(--border); border-radius: 0; background: var(--out-bg); color: var(--out-fg); white-space: pre-wrap; font-size: 14px; }}
.example pre.output:empty {{ display: none; }}
details {{ border: 1px solid var(--border); border-radius: 8px; padding: 6px 14px; margin: 16px 0; background: var(--panel); }}
details summary {{ cursor: pointer; font-weight: 600; color: var(--accent); }}
.intro-note {{ border-left: 4px solid var(--accent); background: var(--panel); padding: 10px 14px; border-radius: 4px; }}
/* CodeMirror syntax colors, readable in light and dark mode */
.cm-s-default .cm-keyword {{ color: #a2448f; }} .cm-s-default .cm-string {{ color: #2f7d32; }}
.cm-s-default .cm-number {{ color: #b0571b; }} .cm-s-default .cm-comment {{ color: var(--muted); font-style: italic; }}
.cm-s-default .cm-builtin {{ color: #1d6fa5; }} .cm-s-default .cm-def {{ color: #1d6fa5; font-weight: 600; }}
.cm-s-default .cm-operator {{ color: var(--fg); }} .cm-s-default .cm-variable {{ color: var(--fg); }}
@media (prefers-color-scheme: dark) {{
  .cm-s-default .cm-keyword {{ color: #e08ad1; }} .cm-s-default .cm-string {{ color: #8fd18f; }}
  .cm-s-default .cm-number {{ color: #f0a868; }} .cm-s-default .cm-builtin {{ color: #7fc1f0; }} .cm-s-default .cm-def {{ color: #7fc1f0; }}
}}
{pygments_css}
@media (max-width: 860px) {{
  .layout {{ grid-template-columns: 1fr; }}
  nav.toc {{ display: none; }}
  main {{ padding: 16px; }}
  header.top {{ flex-wrap: wrap; row-gap: 4px; }}
  header.top .status {{ flex-basis: 100%; margin-left: 0; }}
  .example .bar .hint {{ display: none; }}
}}
</style>
</head>
<body>
<header class="top">
  <span class="title">Coconut Tutorial</span>
  <a href="HELP.html">Text-only version</a>
  <a href="DOCS.html">Documentation</a>
  <button id="reset-all" title="Forget everything defined by the examples you've run">Reset</button>
  <span class="status" id="status">Examples run in your browser; nothing to install.</span>
</header>
<div class="layout">
<nav class="toc">{toc}</nav>
<main>
<p class="intro-note">This is the interactive version of the Coconut tutorial. Every Coconut example below can be edited and run right in your browser: click <b>Run</b> (or press <kbd>Ctrl</kbd>+<kbd>Enter</kbd> in an example). Like the Coconut interpreter, examples remember what earlier examples defined, so run them in order. The first run takes a few seconds while Coconut loads. Prefer to just read? See the <a href="HELP.html">text-only version</a>.</p>
{body}
</main>
</div>
<script src="{codemirror_url}codemirror.min.js"></script>
<script src="{codemirror_url}mode/python/python.min.js"></script>
<script>
const CONFIG = {config};
const statusEl = document.getElementById("status");
let runtime = null;

function setStatus(msg) {{ statusEl.textContent = msg; }}

function loadScript(src) {{
  return new Promise((resolve, reject) => {{
    const s = document.createElement("script");
    s.src = src; s.onload = resolve; s.onerror = () => reject(new Error("couldn't load " + src));
    document.head.appendChild(s);
  }});
}}

function getRuntime() {{
  if (!runtime) {{
    runtime = (async () => {{
      setStatus("Loading Python...");
      await loadScript(CONFIG.pyodideUrl + "pyodide.js");
      const py = await loadPyodide({{ indexURL: CONFIG.pyodideUrl }});
      setStatus("Loading Coconut...");
      await py.loadPackage(CONFIG.pyodidePackages);
      await py.runPythonAsync(`import micropip\nawait micropip.install(${{JSON.stringify(CONFIG.wheels)}}, deps=False)`);
      setStatus("Starting Coconut...");
      py.runPython(CONFIG.runnerCode);
      setStatus("Coconut " + py.runPython("import coconut.root; coconut.root.VERSION_STR") + " is running in your browser.");
      return py;
    }})();
    runtime.catch(err => {{ runtime = null; setStatus("Couldn't load Coconut: " + err.message); }});
  }}
  return runtime;
}}

const editors = [];
document.querySelectorAll(".example").forEach((ex, i) => {{
  const source = ex.querySelector("textarea");
  const original = source.value;
  let editor;
  if (window.CodeMirror) {{
    editor = CodeMirror.fromTextArea(source, {{
      mode: "python", viewportMargin: Infinity, indentUnit: 4, lineWrapping: false,
      extraKeys: {{ "Tab": cm => cm.replaceSelection("    "), "Ctrl-Enter": () => run(), "Cmd-Enter": () => run() }},
    }});
  }} else {{
    source.classList.add("fallback");
    editor = {{ getValue: () => source.value, setValue: v => {{ source.value = v; }} }};
    source.addEventListener("keydown", e => {{ if ((e.ctrlKey || e.metaKey) && e.key === "Enter") run(); }});
  }}
  const runBtn = ex.querySelector("button.run");
  const resetBtn = ex.querySelector("button.restore");
  const output = ex.querySelector("pre.output");
  async function run() {{
    runBtn.disabled = true;
    output.textContent = "Running...";
    try {{
      const py = await getRuntime();
      const result = py.globals.get("run_example")(editor.getValue());
      output.textContent = result || "(no output)";
    }} catch (err) {{
      output.textContent = "Error: " + err.message;
    }} finally {{
      runBtn.disabled = false;
    }}
  }}
  runBtn.addEventListener("click", run);
  resetBtn.addEventListener("click", () => {{ editor.setValue(original); output.textContent = ""; }});
  editors.push(editor);
}});

document.getElementById("reset-all").addEventListener("click", async () => {{
  document.querySelectorAll(".example pre.output").forEach(o => {{ o.textContent = ""; }});
  if (runtime) {{ (await runtime).globals.get("reset_examples")(); setStatus("Reset: everything the examples defined has been forgotten."); }}
}});

// CodeMirror can't measure itself inside closed <details>, so refresh editors when they're opened
document.querySelectorAll("details").forEach(d => d.addEventListener("toggle", () => editors.forEach(e => e.refresh && e.refresh())));
</script>
</body>
</html>
'''

example_template = '''<div class="example">
<textarea spellcheck="false">{code}</textarea>
<div class="bar"><button class="run">Run</button><button class="restore" title="Undo your edits to this example">Restore</button><span class="hint">Ctrl+Enter to run</span></div>
<pre class="output"></pre>
</div>
'''

# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


def slugify(text):
    """Make a GitHub/MyST-style heading anchor."""
    text = re.sub(r"<[^>]+>", "", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def is_example(code):
    """Whether the given Coconut code block from the tutorial is a complete example that can be run."""
    return not code.startswith((" ", "\t")) and "<body>" not in code and "<name>" not in code and not code.startswith(non_example_prefixes)


def get_lexer(lang):
    """Get the Pygments lexer for a non-runnable code block, if there is one."""
    try:
        return get_lexer_by_name(lexer_names.get(lang, lang))
    except ClassNotFound:
        return None


def rewrite_link(href, docs_base):
    """Point links to other documents at their rendered versions."""
    match = re.match(r"^\./([\w\-]+)\.md(#.*)?$", href)
    if match:
        return docs_base + match.group(1) + ".html" + (match.group(2) or "")
    return href


def coconut_wheels(version_str, develop):
    """The packages to install from PyPI to get the Coconut version these docs are for."""
    if develop:
        coconut_req = "coconut-develop"
    else:
        coconut_req = "coconut==" + version_str
    return ["pyparsing==2.4.7", coconut_req]


# -----------------------------------------------------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------------------------------------------------


def make_interactive_tutorial(tutorial, wheels, docs_base="", pyodide_url=pyodide_url, codemirror_url=codemirror_url):
    """Turn the Markdown source of the tutorial into the HTML of the interactive tutorial."""
    md = MarkdownIt("commonmark", {"html": True})
    formatter = HtmlFormatter(cssclass="highlight")
    headings = []

    def render_fence(renderer, tokens, idx, options, env):
        token = tokens[idx]
        lang = token.info.strip()
        code = token.content
        if lang.startswith("{"):  # MyST directives (e.g. the table of contents, which we make ourselves)
            return ""
        if lang == "coconut" and is_example(code):
            return example_template.format(code=html.escape(code.rstrip("\n")))
        lexer = get_lexer(lang) if lang else None
        if lexer is None:
            return "<pre><code>" + html.escape(code) + "</code></pre>\n"
        return highlight(code, lexer, formatter)

    def render_heading_open(renderer, tokens, idx, options, env):
        token = tokens[idx]
        title = tokens[idx + 1].content
        slug = slugify(md.renderInline(title))
        level = int(token.tag[1])
        headings.append((level, slug, md.renderInline(title)))
        return "<{tag} id=\"{slug}\">".format(tag=token.tag, slug=slug)

    def render_link_open(renderer, tokens, idx, options, env):
        token = tokens[idx]
        href = token.attrGet("href")
        if href:
            token.attrSet("href", rewrite_link(href, docs_base))
        return renderer.renderToken(tokens, idx, options, env)

    md.add_render_rule("fence", render_fence)
    md.add_render_rule("heading_open", render_heading_open)
    md.add_render_rule("link_open", render_link_open)

    body = md.render(tutorial)

    # the table of contents, nested by heading level (skipping the page title)
    toc_parts, depth = [], 0
    for level, slug, title in headings:
        if level < 2 or level > 3:
            continue
        while depth < level - 1:
            toc_parts.append("<ul>")
            depth += 1
        while depth > level - 1:
            toc_parts.append("</ul>")
            depth -= 1
        toc_parts.append('<li><a href="#{slug}">{title}</a></li>'.format(slug=slug, title=title))
    toc_parts += ["</ul>"] * depth

    config = {
        "pyodideUrl": pyodide_url,
        "pyodidePackages": pyodide_packages,
        "wheels": wheels,
        "runnerCode": runner_code,
    }
    return page_template.format(
        codemirror_url=codemirror_url,
        pygments_css=formatter.get_style_defs(".highlight"),
        toc="".join(toc_parts),
        body=body,
        config=json.dumps(config).replace("</", "<\\/"),
    )


def write_interactive_tutorial(tutorial_path, out_path, version_str, develop, docs_base=""):
    """Write the interactive tutorial for the given tutorial source file to out_path."""
    with open(tutorial_path, "r", encoding="utf-8") as tutorial_file:
        tutorial = tutorial_file.read()
    page = make_interactive_tutorial(tutorial, coconut_wheels(version_str, develop), docs_base)
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with open(out_path, "w", encoding="utf-8") as out_file:
        out_file.write(page)
    return out_path


if __name__ == "__main__":
    from coconut.root import VERSION, DEVELOP
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join("docs_extra", "interactive.html")
    print("Wrote", write_interactive_tutorial("HELP.md", out, VERSION, bool(DEVELOP)))
