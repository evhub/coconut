#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Claude
License: Apache 2.0
Description: Project configuration from the [tool.coconut] table of pyproject.toml.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import os
import re
import json

from coconut.util import univ_open
from coconut.exceptions import CoconutException
from coconut.terminal import logger

# -----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

project_config_file = "pyproject.toml"

project_config_table = ("tool", "coconut")

# directories that the search for a project configuration file never goes above
project_config_boundaries = ("site-packages", "dist-packages")

# key (with dashes, as in the command-line flags) -> expected type
project_config_keys = {
    "target": str,
    "strict": bool,
    "pure": bool,
    "no-tco": bool,
    "no-wrap-types": bool,
}

# -----------------------------------------------------------------------------------------------------------------------
# PARSING:
# -----------------------------------------------------------------------------------------------------------------------

_table_header_regex = re.compile(r"^\s*\[\s*([^\[\]]+?)\s*\]\s*(?:#.*)?$")
_key_value_regex = re.compile(r"""^\s*([A-Za-z0-9_-]+|"[^"]*"|'[^']*')\s*=\s*(.*?)\s*$""")
_simple_value_regex = re.compile(r"""^(true|false|[+-]?\d+|"(?:[^"\\]|\\.)*"|'[^']*')\s*(?:#.*)?$""")


def _parse_simple_value(raw):
    """Parse a TOML boolean, integer, or single-line string."""
    match = _simple_value_regex.match(raw)
    if not match:
        return None, False
    value = match.group(1)
    if value == "true":
        return True, True
    if value == "false":
        return False, True
    if value.startswith('"'):
        try:
            return json.loads(value), True
        except ValueError:
            return None, False
    if value.startswith("'"):
        return value[1:-1], True
    return int(value), True


def _fallback_parse_table(text, table, filepath):
    """Parse simple key = value pairs in the given table without a TOML library."""
    header = ".".join(table)
    result = {}
    in_table = False
    for line in text.splitlines():
        header_match = _table_header_regex.match(line)
        if header_match:
            in_table = re.sub(r"\s*\.\s*", ".", header_match.group(1)) == header
            continue
        if not in_table or not line.strip() or line.strip().startswith("#"):
            continue
        kv_match = _key_value_regex.match(line)
        value, ok = (None, False) if not kv_match else _parse_simple_value(kv_match.group(2))
        if not ok:
            raise CoconutException(
                "could not parse line in [" + header + "] of " + repr(filepath) + ": " + repr(line.strip()),
                extra="install 'tomli' for full TOML support",
            )
        result[kv_match.group(1).strip("\"'")] = value
    return result


def parse_table(text, table, filepath="<string>"):
    """Get the given TOML table (as a tuple of keys) from the given TOML text."""
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            tomllib = None
    if tomllib is None:
        return _fallback_parse_table(text, table, filepath)
    try:
        data = tomllib.loads(text)
    except Exception as err:
        raise CoconutException("invalid TOML in " + repr(filepath), extra=str(err))
    for key in table:
        data = data.get(key, {}) if isinstance(data, dict) else {}
    if not isinstance(data, dict):
        raise CoconutException("[" + ".".join(table) + "] in " + repr(filepath) + " must be a table")
    return data


# -----------------------------------------------------------------------------------------------------------------------
# LOADING:
# -----------------------------------------------------------------------------------------------------------------------

_config_cache = {}


def load_project_config(filepath):
    """Load and validate the [tool.coconut] table of the given pyproject.toml.

    Returns a dict mapping option names (with underscores, as in the argparse namespace) to values."""
    try:
        mtime = os.path.getmtime(filepath)
    except OSError:
        mtime = None
    cached = _config_cache.get(filepath)
    if cached is not None and cached[0] == mtime:
        return dict(cached[1])

    with univ_open(filepath, "r") as config_file:
        text = config_file.read()
    raw_config = parse_table(text, project_config_table, filepath)

    config = {}
    for raw_key, value in raw_config.items():
        key = raw_key.replace("_", "-")
        if key not in project_config_keys:
            # warn rather than error so that configs written for newer Coconut versions still work
            logger.warn(
                "ignoring unknown option " + repr(raw_key) + " in [tool.coconut] of " + repr(filepath),
                extra="valid options are: " + ", ".join(sorted(project_config_keys)),
            )
            continue
        if project_config_keys[key] is bool:
            if not isinstance(value, bool):
                raise CoconutException("option " + repr(raw_key) + " in [tool.coconut] of " + repr(filepath) + " must be true or false")
        elif not isinstance(value, (str, py_str)):
            raise CoconutException(
                "option " + repr(raw_key) + " in [tool.coconut] of " + repr(filepath) + " must be a string",
                extra='e.g. target = "3.10"',
            )
        config[key.replace("-", "_")] = value

    _config_cache[filepath] = (mtime, config)
    return dict(config)


def find_project_config_file(path):
    """Find the pyproject.toml that applies to the given file or directory, if any.

    As with other tools, the nearest pyproject.toml (searching upwards) marks the project
    root, even if it has no [tool.coconut] table."""
    dirpath = os.path.abspath(path)
    if not os.path.isdir(dirpath):
        dirpath = os.path.dirname(dirpath)
    while True:
        filepath = os.path.join(dirpath, project_config_file)
        if os.path.isfile(filepath):
            return filepath
        parent = os.path.dirname(dirpath)
        # installed packages (e.g. in a virtualenv inside a project) aren't part of the enclosing project
        if parent == dirpath or os.path.basename(dirpath) in project_config_boundaries:
            return None
        dirpath = parent


def find_project_config(path):
    """Get the [tool.coconut] configuration that applies to the given file or directory."""
    filepath = find_project_config_file(path)
    if filepath is None:
        return {}
    return load_project_config(filepath)
