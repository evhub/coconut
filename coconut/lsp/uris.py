#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: Conversion between file paths and file:// URIs.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import os
import re
import sys

try:
    from urllib.parse import quote, unquote, urlparse
except ImportError:  # pragma: no cover
    from urllib import quote, unquote
    from urlparse import urlparse

IS_WINDOWS = sys.platform == "win32"


def uri_to_path(uri):
    """Convert a file:// URI to a local path; returns None for other schemes."""
    if not uri or not uri.startswith("file:"):
        return None
    parsed = urlparse(uri)
    path = unquote(parsed.path)
    if parsed.netloc:
        # UNC path
        path = "//" + parsed.netloc + path
    if re.match(r"^/[A-Za-z]:", path):
        path = path[1:]
    if IS_WINDOWS:
        path = path.replace("/", "\\")
    return os.path.normpath(path) if path else None


def path_to_uri(path):
    path = os.path.abspath(path)
    if IS_WINDOWS:
        path = path.replace("\\", "/")
    if re.match(r"^[A-Za-z]:", path):
        path = "/" + path
    if path.startswith("//"):
        return "file:" + quote(path)
    return "file://" + quote(path)
