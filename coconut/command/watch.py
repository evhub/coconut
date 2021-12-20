#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Fred Buchanan
License: Apache 2.0
Description: Handles interfacing with watchdog to make --watch work.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys

from coconut.exceptions import CoconutException

try:
    from watchdog.events import FileSystemEventHandler
    # import Observer to provide it for others to import
    from watchdog.observers import Observer  # NOQA
except ImportError:
    raise CoconutException(
        "--watch flag requires watchdog library",
        extra="run '{python} -m pip install coconut[watch]' to fix".format(python=sys.executable),
    )

# -----------------------------------------------------------------------------------------------------------------------
# CLASSES:
# -----------------------------------------------------------------------------------------------------------------------


class RecompilationWatcher(FileSystemEventHandler):
    """Watcher that recompiles modified files."""

    def __init__(self, recompile, *args, **kwargs):
        super(RecompilationWatcher, self).__init__()
        self.recompile = recompile
        self.args = args
        self.kwargs = kwargs
        self.keep_watching()

    def keep_watching(self):
        """Allows recompiling previously-compiled files."""
        self.saw = set()

    def on_modified(self, event):
        """Handle a file modified event."""
        path = event.src_path
        if path not in self.saw:
            self.saw.add(path)
            self.recompile(path, *self.args, **self.kwargs)
