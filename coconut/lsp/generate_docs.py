#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: Regenerates coconut/lsp/data/docs.json, the documentation the language server shows on
hover and completion for Coconut built-ins, keywords, and operators, from DOCS.md.

Run from a source checkout after changing DOCS.md (coconut/tests/lsp_test.py checks that it's up to date):

    python -m coconut.lsp.generate_docs [path/or/url/to/DOCS.md]
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import json
import os
import re
import sys

# DOCS.md in a source checkout of Coconut (it isn't installed with the package)
DEFAULT_SOURCE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "DOCS.md")
DOCS_URL = "https://coconut.readthedocs.io/en/latest/DOCS.html"
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "docs.json")

MAX_DESCRIPTION_CHARS = 2500
MAX_EXAMPLE_LINES = 16

# top-level (## ...) sections whose subsections document language features
FEATURE_SECTIONS = ("Operators", "Keywords", "Expressions", "Function Definition", "Statements", "Built-Ins")

# subsection titles to skip entirely (not features)
SKIP_TITLES = ("Precedence", "Unicode Alternatives", "Handling Keyword/Variable Name Overlap")

# operators/keywords that don't appear in a heading verbatim -> heading title documenting them
EXTRA_KEYS = {
    "Pipes": ["|>", "|*>", "|**>", "<|", "<*|", "<**|", "|?>", "|?*>", "|?**>", "<?|", "<*?|", "<**?|"],
    "Function Composition": [
        "..", "..>", "<..", "..*>", "<*..", "..**>", "<**..",
        "..?>", "<?..", "..?*>", "<*?..", "..?**>", "<**?..",
    ],
    "Lambdas": ["=>", "->"],
    "Partial Application": ["$"],
    "Iterator Slicing": ["$["],
    "Iterator Chaining": ["::"],
    "Infix Functions": ["`"],
    "Custom Operators": ["operator"],
    "None Coalescing": ["??", "??="],
    "Other None-Aware Operators": ["?.", "?[", "?("],
    "Protocol Intersection": ["&:"],
    "Statement Lambdas": ["def ="],
    "Implicit Partial Application": ["."],
    "Pattern-Matching Functions": ["match def"],
    "`case` Functions": ["case def"],
    "`addpattern` Functions": ["addpattern def"],
    "`copyclosure` Functions": ["copyclosure", "copyclosure def"],
    "Explicit Generators": ["yield def"],
    "Code Passthrough": ["\\("],
    "Lazy Lists": ["(|", "|)"],
    "Alternative Ternary Operator": ["if then else"],
    "Tail Call Optimization": ["tco"],
    "`match for`": ["match for"],
    "`match data`": ["match data"],
    "`case data`": ["case data"],
    "`async with for`": ["async with for"],
    "`strict` Mode": ["strict"],
    "Enhanced Built-Ins": ["map", "zip", "filter", "reversed", "enumerate"],
    "Anonymous Namedtuples": ["_namedtuple_of"],
    "`data`": ["data"],
    "`where`": ["where"],
    "`match`": ["match"],
    "`case`": ["case"],
}


def slugify(title):
    """GitHub/MyST-style heading anchor."""
    slug = title.strip().lower()
    slug = re.sub(r"[^\w\- ]", "", slug)
    return slug.replace(" ", "-")


def absolutize_links(text):
    """Make intra-document links absolute so they work in editor hovers."""
    return re.sub(r"\]\(#([^)]+)\)", lambda m: "](" + DOCS_URL + "#" + m.group(1) + ")", text)


def read_source(source):
    if re.match(r"https?://", source):
        from urllib.request import urlopen
        with urlopen(source) as resp:
            return resp.read().decode("utf-8")
    with open(source, encoding="utf-8") as f:
        return f.read()


def parse_sections(md):
    """Yield (level, title, body_lines, parent_l2) for every heading, ignoring headings inside code fences."""
    sections = []
    current = None
    in_fence = False
    parent_l2 = None
    for line in md.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        m = None if in_fence else re.match(r"^(#{2,5}) (.+?)\s*$", line)
        if m:
            level = len(m.group(1))
            title = m.group(2)
            if level == 2:
                parent_l2 = title
            current = {"level": level, "title": title, "lines": [], "parent": parent_l2}
            sections.append(current)
        elif current is not None:
            current["lines"].append(line)
    return sections


def first_example(sections, index):
    """Find the first ```coconut block in the ##### subsections following the section at index."""
    level = sections[index]["level"]
    for sec in sections[index + 1:]:
        if sec["level"] <= level:
            break
        if sec["level"] < 5:
            # a nested #### under a ### is its own feature
            break
        if "example" not in sec["title"].lower():
            continue
        lines = sec["lines"]
        for i, line in enumerate(lines):
            if line.strip() == "```coconut":
                block = []
                for code_line in lines[i + 1:]:
                    if code_line.strip() == "```":
                        break
                    block.append(code_line)
                if len(block) > MAX_EXAMPLE_LINES:
                    block = block[:MAX_EXAMPLE_LINES] + ["..."]
                return "\n".join(block).strip("\n")
    return None


def clean_description(lines):
    text = "\n".join(lines).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = absolutize_links(text)
    if len(text) > MAX_DESCRIPTION_CHARS:
        cut = text.rfind("\n\n", 0, MAX_DESCRIPTION_CHARS)
        if cut < MAX_DESCRIPTION_CHARS // 3:
            cut = MAX_DESCRIPTION_CHARS
        text = text[:cut].rstrip()
        # don't leave a code fence open
        if text.count("```") % 2:
            text += "\n```"
        text += "\n\n..."
    return text


def keys_for_title(title):
    """Names documented by a heading like '`lift` and `lift_apart`' or '`fmap`'."""
    keys = re.findall(r"`([^`]+)`", title)
    # only single-identifier names count as built-in names (e.g. not `match for`)
    return [k for k in keys if re.match(r"^[A-Za-z_]\w*$", k)]


def generate(md):
    sections = parse_sections(md)
    entries = {}
    for i, sec in enumerate(sections):
        if sec["level"] not in (3, 4) or sec["parent"] not in FEATURE_SECTIONS or sec["title"] in SKIP_TITLES:
            continue
        title = sec["title"]
        lines = list(sec["lines"])
        # include signature subsections (e.g. '##### **lift**(_func_)') in the description
        for sub in sections[i + 1:]:
            if sub["level"] <= sec["level"] or sub["level"] < 5:
                break
            if sub["title"].startswith("**"):
                lines += ["", sub["title"], ""] + sub["lines"]
        description = clean_description(lines)
        if not description:
            continue
        entry = {
            "title": title.replace("`", ""),
            "category": sec["parent"],
            "url": DOCS_URL + "#" + slugify(title),
            "description": description,
        }
        example = first_example(sections, i)
        if example:
            entry["example"] = example
        keys = list(EXTRA_KEYS.get(title, []))
        if sec["parent"] == "Built-Ins" or sec["parent"] == "Keywords":
            keys += keys_for_title(title)
        for key in keys:
            entries.setdefault(key, entry)
    return entries


def main(argv):
    source = argv[1] if len(argv) > 1 else DEFAULT_SOURCE
    entries = generate(read_source(source))
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, sort_keys=True)  # the format the pretty-format-json pre-commit hook uses
        f.write("\n")
    print("wrote {n} entries to {path}".format(n=len(entries), path=OUT_PATH))


if __name__ == "__main__":
    main(sys.argv)
