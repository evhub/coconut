#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: Coconut documentation for built-ins, keywords, and operators (generated from Coconut's DOCS.md).
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import json
import keyword
import os
import re

_DOCS = None
DOCS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "docs.json")

# Coconut keywords beyond Python's (soft keywords are only keywords in certain positions)
COCONUT_KEYWORDS = (
    "data", "match", "case", "cases", "where", "addpattern", "copyclosure", "operator", "then",
    "async", "await", "type", "λ",
)

# operator keys that are too ambiguous to explain on hover
UNHOVERABLE = {".", "`", "\\(", "(|", "|)", "?(", "?[", "$[", "def =", "if then else"}

OPERATOR_CHARS = set("|<>*?.$:=&-`\\[(")


def all_docs():
    global _DOCS
    if _DOCS is None:
        try:
            with open(DOCS_PATH, encoding="utf-8") as f:
                _DOCS = json.load(f)
        except Exception:
            _DOCS = {}
    return _DOCS


def lookup(name):
    """Get the documentation entry for a name/operator, or None."""
    return all_docs().get(name)


def search(query, limit=10):
    """Search documentation entries by key and title (used by the CLI/MCP 'docs' tools)."""
    query_l = query.lower().strip()
    docs = all_docs()
    if query in docs:
        return [(query, docs[query])]
    results = []
    seen_titles = set()
    for key, entry in sorted(docs.items(), key=lambda kv: (len(kv[0]), kv[0])):
        hay = (key + " " + entry["title"]).lower()
        if query_l in hay and entry["title"] not in seen_titles:
            seen_titles.add(entry["title"])
            results.append((key, entry))
    if not results:
        words = [w for w in re.split(r"\W+", query_l) if w]
        for key, entry in docs.items():
            hay = (key + " " + entry["title"] + " " + entry["description"]).lower()
            if words and all(w in hay for w in words) and entry["title"] not in seen_titles:
                seen_titles.add(entry["title"])
                results.append((key, entry))
    return results[:limit]


def signature(entry):
    """A plain signature like 'fmap(func, obj)' from an entry's '**fmap**(_func_, _obj_)' line."""
    m = re.match(r"^\*\*([\w.]+)\*\*\((.*)\)\s*$", entry["description"].split("\n", 1)[0])
    if not m:
        return None
    args = m.group(2).replace("\\", "").replace("`", "")
    args = re.sub(r"(?<!\w)_|_(?!\w)", "", args)
    return m.group(1) + "(" + args + ")"


def format_entry(entry, include_example=True, max_chars=None):
    """Render a documentation entry as Markdown."""
    description = entry["description"]
    if max_chars is not None and len(description) > max_chars:
        cut = description.rfind("\n\n", 0, max_chars)
        description = description[:cut if cut > 0 else max_chars].rstrip()
        if description.count("```") % 2:
            description += "\n```"
        description += "\n\n..."
    parts = ["**Coconut: " + entry["title"] + "**", "", description]
    if include_example and entry.get("example"):
        parts += ["", "Example:", "```coconut", entry["example"], "```"]
    parts += ["", "[Coconut documentation](" + entry["url"] + ")"]
    return "\n".join(parts)


def operator_at(line, col):
    """Find a documented operator spanning col in line; returns (key, start, end) or None."""
    best = None
    for key in all_docs():
        if key in UNHOVERABLE or not key or not all(c in OPERATOR_CHARS for c in key):
            continue
        start = max(0, col - len(key) + 1)
        while True:
            idx = line.find(key, start, col + len(key))
            if idx < 0 or idx > col:
                break
            if idx <= col < idx + len(key) or (idx + len(key) == col and col > 0):
                if best is None or len(key) > len(best[0]):
                    best = (key, idx, idx + len(key))
            start = idx + 1
    return best


def keyword_entry(line, start, end):
    """If the word at line[start:end] is used as a Coconut keyword here, return its docs key."""
    word = line[start:end]
    before = line[:start].strip()
    after = line[end:]
    next_word = re.match(r"\s*(\w+)", after)
    next_word = next_word.group(1) if next_word else None
    docs = all_docs()
    statement_start = before == "" or before.endswith(":") or re.match(r"^(@.*|async|match|case|addpattern|copyclosure)$", before)
    if word in ("match", "case", "addpattern", "copyclosure", "yield") and next_word == "def":
        return word + " def"
    if word == "def":
        prev = re.search(r"(\w+)\s*$", before)
        if prev and (prev.group(1) + " def") in docs:
            return prev.group(1) + " def"
        return None
    if word == "match" and next_word in ("for", "data"):
        return "match " + next_word
    if word == "case" and next_word == "data" and before == "":
        return "case data"
    if word == "data" and line[:start].strip() == "case":
        return "case data"
    if word in ("match", "case") and statement_start:
        return word
    if word == "data" and statement_start and next_word:
        return "data"
    if word == "where" and after.strip() == ":":
        return "where"
    if word == "operator" and before == "":
        return "operator"
    return None


def is_keyword(word):
    return keyword.iskeyword(word) or word in COCONUT_KEYWORDS
