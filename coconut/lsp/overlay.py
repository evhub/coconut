#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Claude
License: Apache 2.0
Description: A compiled mirror of the workspace, so that jedi can follow imports of other Coconut modules.

jedi only understands Python files, so an `import helpers` of a `helpers.coco` that hasn't been
compiled to `helpers.py` would be invisible to it. For each document, the modules it imports
(transitively, up to a limit) are compiled into a mirror directory tree, next to copies of the
real `.py` files in the same directories, and jedi analyzes the document as if it lived in the
mirror. Locations jedi reports inside the mirror are mapped back to the real files.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import hashlib
import os
import re
import shutil
import sys
import tempfile
import threading

from coconut.lsp.symbols import COCONUT_EXTENSIONS

MAX_MODULES = 40
MAX_DEPTH = 2

IMPORT_RE = re.compile(r"^[ \t]*import[ \t]+([^\n#;]+)", re.MULTILINE)
FROM_IMPORT_RE = re.compile(r"^[ \t]*from[ \t]+(\.*[\w.]*)[ \t]+import[ \t]+\(?([^\n#;)]+)", re.MULTILINE)


def _private_dir_ok(path):
    """Whether path is a real (non-symlink) directory owned by us and not writable by others."""
    try:
        if os.path.islink(path) or not os.path.isdir(path):
            return False
        if hasattr(os, "getuid"):
            st = os.stat(path)
            if st.st_uid != os.getuid() or st.st_mode & 0o022:
                return False
        return True
    except OSError:
        return False


def default_base_dir():
    """A private per-user cache directory for the mirror (never a predictable shared /tmp path)."""
    home = os.path.expanduser("~")
    if os.name == "nt":
        cache = os.environ.get("LOCALAPPDATA") or os.path.join(home, "AppData", "Local")
    elif sys.platform == "darwin":
        cache = os.path.join(home, "Library", "Caches")
    else:
        cache = os.environ.get("XDG_CACHE_HOME") or os.path.join(home, ".cache")
    path = os.path.join(cache, "coconut-language-server", "mirror")
    try:
        os.makedirs(path, mode=0o700, exist_ok=True)
        if _private_dir_ok(path) and _private_dir_ok(os.path.dirname(path)):
            return path
    except OSError:
        pass
    return tempfile.mkdtemp(prefix="coconut-ls-")


def imported_modules(text):
    """Yield (module, names) for each import statement in Coconut/Python source."""
    for m in IMPORT_RE.finditer(text):
        for part in m.group(1).split(","):
            name = part.strip().split(" as ")[0].strip()
            if re.match(r"^[\w.]+$", name):
                yield name, ()
    for m in FROM_IMPORT_RE.finditer(text):
        names = tuple(p.strip().split(" as ")[0].strip() for p in m.group(2).split(",") if p.strip())
        yield m.group(1), names


def resolve_module(module, from_path, roots):
    """Find the source file (.coco or .py) for an import like '.mod' or 'pkg.mod' from from_path.

    Returns a path or None. Only searches the importing file's directory (for relative or
    script-local imports) and the workspace roots."""
    dots = len(module) - len(module.lstrip("."))
    parts = [p for p in module.lstrip(".").split(".") if p]
    if dots:
        base = os.path.dirname(os.path.abspath(from_path))
        for _ in range(dots - 1):
            base = os.path.dirname(base)
        bases = [base]
    else:
        bases = [os.path.dirname(os.path.abspath(from_path))] + list(roots)
    for base in bases:
        target = os.path.join(base, *parts) if parts else base
        for ext in COCONUT_EXTENSIONS + (".py",):
            if parts and os.path.isfile(target + ext):
                return target + ext
        for ext in COCONUT_EXTENSIONS + (".py",):
            init = os.path.join(target, "__init__" + ext)
            if os.path.isfile(init):
                return init
    return None


class Overlay(object):

    def __init__(self, compile_func, base_dir=None):
        """compile_func(text) -> compiled Python (with line-number comments) or None."""
        self.compile_func = compile_func
        self.base_dir = base_dir or default_base_dir()
        self.lock = threading.RLock()
        self.compiled = {}  # mirror .py path -> (real .coco path, source mtime)
        self.copied = {}  # mirror .py path -> (real .py path, mtime)

    # ------------------------------------------------------------------ paths

    @staticmethod
    def root_for(path, roots):
        apath = os.path.abspath(path)
        best = None
        for root in roots:
            aroot = os.path.abspath(root)
            if apath == aroot or apath.startswith(aroot.rstrip(os.sep) + os.sep):
                if best is None or len(aroot) > len(best):
                    best = aroot
        return best or os.path.dirname(apath)

    def mirror_root(self, root):
        digest = hashlib.sha1(os.path.abspath(root).encode("utf-8")).hexdigest()[:12]
        return os.path.join(self.base_dir, os.path.basename(root.rstrip(os.sep)) + "-" + digest)

    def mirror_path(self, real_path, roots):
        """The mirror location of a real file (Coconut files map to .py)."""
        root = self.root_for(real_path, roots)
        rel = os.path.relpath(os.path.abspath(real_path), root)
        base, ext = os.path.splitext(rel)
        if ext in COCONUT_EXTENSIONS:
            rel = base + ".py"
        return os.path.join(self.mirror_root(root), rel)

    def script_path(self, doc_path, roots):
        return self.mirror_path(doc_path, roots)

    def to_real(self, path):
        """Map a path in the mirror back to (real_path, from_coconut); (path, False) if not mirrored.

        Deliberately lock-free (single dict lookups are atomic), so requests never wait on prepare()."""
        apath = os.path.abspath(path)
        compiled = self.compiled.get(apath)
        if compiled is not None:
            return compiled[0], True
        copied = self.copied.get(apath)
        if copied is not None:
            return copied[0], False
        return path, False

    def is_mirror_path(self, path):
        return os.path.abspath(path).startswith(os.path.abspath(self.base_dir) + os.sep)

    # ------------------------------------------------------------------ building

    def prepare(self, doc_path, doc_text, roots):
        """Make the modules imported by a document (transitively) available in the mirror."""
        with self.lock:
            seen = set()
            queue = [(doc_path, doc_text, 0)]
            dirs = {os.path.dirname(os.path.abspath(doc_path))}
            while queue and len(seen) < MAX_MODULES:
                path, text, depth = queue.pop(0)
                for module, names in imported_modules(text):
                    candidates = [module] + [
                        (module + "." if module.strip(".") else module) + n for n in names if re.match(r"^\w+$", n)
                    ]
                    for cand in candidates:
                        target = resolve_module(cand, path, roots)
                        if target is None or target in seen or os.path.abspath(target) == os.path.abspath(doc_path):
                            continue
                        seen.add(target)
                        dirs.update(self._package_dirs(target, roots))
                        if target.endswith(COCONUT_EXTENSIONS):
                            self._compile_into_mirror(target, roots)
                            if depth + 1 < MAX_DEPTH:
                                try:
                                    with open(target, encoding="utf-8") as f:
                                        queue.append((target, f.read(), depth + 1))
                                except (OSError, UnicodeDecodeError):
                                    pass
            for d in dirs:
                self._mirror_directory(d, roots)

    def _package_dirs(self, target, roots):
        """The directory of target and its parent package directories within its root."""
        root = self.root_for(target, roots)
        d = os.path.dirname(os.path.abspath(target))
        out = []
        while True:
            out.append(d)
            if d == root or len(d) <= len(root):
                break
            d = os.path.dirname(d)
        return out

    def _compile_into_mirror(self, real, roots):
        mirror = self.mirror_path(real, roots)
        try:
            mtime = os.path.getmtime(real)
        except OSError:
            return
        cached = self.compiled.get(mirror)
        if cached is not None and cached[1] == mtime and os.path.exists(mirror):
            return
        try:
            with open(real, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            return
        try:
            compiled = self.compile_func(text)
        except Exception:
            compiled = None
        if compiled is None:
            # keep a stale version rather than nothing; otherwise expose at least the definitions
            if os.path.exists(mirror):
                return
            compiled = ""
        self._write(mirror, compiled)
        self.compiled[mirror] = (real, mtime)

    def _mirror_directory(self, real_dir, roots):
        """Copy the real .py files of a directory into the mirror (skipping compiled outputs of .coco files)."""
        try:
            names = os.listdir(real_dir)
        except OSError:
            return
        for name in names:
            base, ext = os.path.splitext(name)
            if ext != ".py":
                continue
            if any(os.path.exists(os.path.join(real_dir, base + e)) for e in COCONUT_EXTENSIONS):
                continue  # compiled from a .coco file; the mirror holds a fresh compile instead
            real = os.path.join(real_dir, name)
            mirror = self.mirror_path(real, roots)
            try:
                mtime = os.path.getmtime(real)
            except OSError:
                continue
            cached = self.copied.get(mirror)
            if cached is not None and cached[1] == mtime and os.path.exists(mirror):
                continue
            try:
                os.makedirs(os.path.dirname(mirror), exist_ok=True)
                shutil.copyfile(real, mirror)
            except OSError:
                continue
            self.copied[mirror] = (real, mtime)

    @staticmethod
    def _write(path, text):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
