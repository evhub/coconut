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

from functools import partial

from coconut.terminal import logger
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
        self.saw = set()
        self.saw_twice = set()

    def on_modified(self, event):
        """Handle a file modified event."""
        self.handle(event.src_path)

    def handle(self, path):
        """Handle a potential recompilation event for the given path."""
        if path in self.saw:
            logger.log("Skipping watch event for: " + repr(path) + "\n\t(currently compiling: " + repr(self.saw) + ")")
            self.saw_twice.add(path)
        else:
            logger.log("Handling watch event for: " + repr(path) + "\n\t(currently compiling: " + repr(self.saw) + ")")
            self.saw.add(path)
            self.saw_twice.discard(path)
            self.recompile(path, callback=partial(self.callback, path), *self.args, **self.kwargs)

    def callback(self, path):
        """Callback for after recompiling the given path."""
        self.saw.discard(path)
        if path in self.saw_twice:
            logger.log("Submitting deferred watch event for: " + repr(path) + "\n\t(currently deferred: " + repr(self.saw_twice) + ")")
            self.saw_twice.discard(path)
            self.handle(path)
