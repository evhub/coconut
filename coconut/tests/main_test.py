#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Fred Buchanan, Claude
License: Apache 2.0
Description: Main Coconut tests.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import unittest
import sys
import os
import re
import shutil
import functools
import tempfile
from io import StringIO
from contextlib import contextmanager
if sys.version_info >= (2, 7):
    import importlib
else:
    import imp

import pytest

from coconut.util import noop_ctx, get_target_info, univ_open
from coconut.terminal import (
    logger,
    LoggingStringIO,
)
from coconut.command.util import (
    call_output,
    reload,
    run_cmd,
)
from coconut.compiler.util import (
    get_psf_target,
)
from coconut.constants import (
    ai_docs_file,
    LSP,
    WINDOWS,
    PYPY,
    IPY,
    XONSH,
    MYPY,
    PY26,
    PY35,
    PY36,
    PY38,
    PY39,
    PY310,
    PY312,
    CPYTHON,
    adaptive_any_of_env_var,
    reverse_any_of_env_var,
    supported_py2_vers,
    supported_py3_vers,
    icoconut_default_kernel_names,
    icoconut_custom_kernel_name,
    mypy_err_infixes,
    get_bool_env_var,
    coconut_cache_dir,
    default_use_cache_dir,
    base_dir,
    fixpath,
)

from coconut.api import (
    auto_compilation,
    setup,
)


# -----------------------------------------------------------------------------------------------------------------------
# SETUP:
# -----------------------------------------------------------------------------------------------------------------------


auto_compilation(False)

logger.verbose = property(lambda self: True, lambda self, value: print("WARNING: ignoring attempt to set logger.verbose = {value}".format(value=value)))

os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"

TEST_ALL = get_bool_env_var("COCONUT_TEST_ALL", (
    # run fewer tests on Windows so appveyor doesn't time out
    not WINDOWS
))


# -----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------


default_recursion_limit = "6144"
default_stack_size = "6144"
default_jobs = (
    # fix EOMs on GitHub actions
    "0" if PYPY
    else None
)


def pexpect(p, out):
    """p.expect(out) with timeout"""
    p.expect(out, timeout=120)


tests_dir = os.path.dirname(os.path.relpath(__file__))
src = os.path.join(tests_dir, "src")
dest = os.path.join(tests_dir, "dest")
additional_dest = os.path.join(tests_dir, "dest", "additional_dest")

src_cache_dir = os.path.join(src, coconut_cache_dir)
cocotest_dir = os.path.join(src, "cocotest")
agnostic_dir = os.path.join(cocotest_dir, "agnostic")

runnable_coco = os.path.join(src, "runnable.coco")
runnable_py = os.path.join(src, "runnable.py")
runnable_compiled_loc = src_cache_dir if default_use_cache_dir else runnable_py

importable_coco = os.path.join(src, "importable.coco")
importable_py = os.path.join(src, "importable.py")
importable_compiled_loc = src_cache_dir if default_use_cache_dir else importable_py

pyston = os.path.join(os.curdir, "pyston")
pyprover = os.path.join(os.curdir, "pyprover")
prelude = os.path.join(os.curdir, "coconut-prelude")
bbopt = os.path.join(os.curdir, "bbopt")
imp_issue_dir = os.path.join(os.curdir, "coconut-issue")

pyston_git = "https://github.com/evhub/pyston.git"
pyprover_git = "https://github.com/evhub/pyprover.git"
prelude_git = "https://github.com/evhub/coconut-prelude"
bbopt_git = "https://github.com/evhub/bbopt.git"
imp_issue_git = "https://github.com/evhub/coconut-issue.git"

coconut_snip = "msg = '<success>'; pmsg = print$(msg); `pmsg`"
pickle_main_snip = """
import pickle
class PickleMainC:
    pass
assert pickle.loads(pickle.dumps(PickleMainC())).__class__.__name__ == "PickleMainC"
def pickle_main_sq(x) = x * x
assert process_map(pickle_main_sq, range(3)) |> list == [0, 1, 4]
print("<success>")
"""
target_3_snip = "assert super is py_super; print('<success>')"

always_err_strs = (
    "CoconutInternalException",
    "<unprintable",
    "*** glibc detected ***",
    "INTERNAL ERROR",
)
ignore_error_lines_with = (
    # ignore SyntaxWarnings containing assert_raises or raise
    "raise",
    # ignore type checker errors (which are checked separately for MyPy with check_mypy),
    #  both in Pyright's own format and in the file:line: error: format Coconut reports them in
    " - error: ",
    ": error: ",
)

mypy_snip = "a: str = count()[0]"

repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
tutorial_file = os.path.join(repo_root, "HELP.md")
tutorial_exceptions = ("TypeError", "MatchError", "ValueError", "AttributeError", "NameError")


def tutorial_statements(block):
    """Split a tutorial code block into the statements one would enter into the interpreter."""
    out, cur = [], []
    for line in block.splitlines():
        if (
            line and not line[0].isspace() and cur
            and not cur[-1].rstrip().endswith(("=", "(", ",", "\\"))
            and not cur[-1].startswith("@")
            and not line.startswith((")", "else", "except", "elif", "finally"))
        ):
            out.append("\n".join(cur))
            cur = []
        cur.append(line)
    if cur:
        out.append("\n".join(cur))
    return [stmt for stmt in out if stmt.strip()]


def check_tutorial(tutorial):
    """Run the tutorial's examples in order, as if entered into the interpreter, checking that each
    line ending in "|> print  # <output>" prints that output and each "# <Exception>" line raises it.
    Returns a list of failures. Exercise tests (blocks followed by a solution) are rerun after later
    blocks until they pass, since they're meant to be run with the reader's solution."""
    from coconut.api import parse
    # (use the same examples as the interactive tutorial does)
    sys.path.insert(0, repo_root)
    try:
        from interactive_tutorial import is_example
    finally:
        sys.path.pop(0)
    fence = "`" * 3
    blocks = []
    exercise_tests = set()
    for match in re.finditer(fence + r"coconut\n(.*?)" + fence, tutorial, re.DOTALL):
        rest = tutorial[match.end():]
        next_block, next_solution = rest.find(fence + "coconut"), rest.find("<details>")
        if next_solution != -1 and (next_block == -1 or next_solution < next_block):
            exercise_tests.add(len(blocks))
        blocks.append(match.group(1))

    namespace = {}
    exec(parse("pass", "sys"), namespace)

    def run(stmt):
        first_line = stmt.splitlines()[0]
        comment_match = re.search(r"#\s*(.*)$", first_line) if "|> print" in first_line or any(exc in first_line for exc in tutorial_exceptions) else None
        comment = comment_match.group(1).strip() if comment_match else None
        expected_exc = next((exc for exc in tutorial_exceptions if comment and exc in comment), None)
        stdout = StringIO()
        old_stdout, sys.stdout = sys.stdout, stdout
        try:
            exec(parse(stmt, "block"), namespace)
        except Exception as err:
            if expected_exc and expected_exc in type(err).__name__:
                return None
            if isinstance(err, NameError):
                return "undefined"
            return "raised {exc}: {err}".format(exc=type(err).__name__, err=err)
        finally:
            sys.stdout = old_stdout
        if expected_exc:
            return "expected {exc}, but printed {out!r}".format(exc=expected_exc, out=stdout.getvalue())
        if comment is not None and "|> print" in first_line and "should be the same" not in comment:
            printed, expected = stdout.getvalue().strip(), comment.split(" (should")[0].strip()
            if printed != expected:
                return "printed {printed!r}, but the comment says {expected!r}".format(printed=printed, expected=expected)
        return None

    failures, pending = [], []
    for i, block in enumerate(blocks):
        if not is_example(block):
            continue
        to_run = [(i, stmt) for stmt in tutorial_statements(block)] + pending
        pending = []
        for j, stmt in to_run:
            failure = run(stmt)
            if failure is not None and (failure == "undefined" or j in exercise_tests):
                pending.append((j, stmt))
            elif failure is not None:
                failures.append((stmt.splitlines()[0], failure))
    failures += [(stmt.splitlines()[0], "never ran successfully") for _, stmt in pending]
    return failures


exhaustiveness_snip = """
from typing import assert_never

case data Shape:
    case Circle(r: float)
    case Square(side: float)

case data Tree:
    case Leaf(value: int)
    case Node(left: Tree, right: Tree)

def shape_missing(shape: Shape) -> None:
    match shape:  # ERR
        case Circle(r):
            pass

def shape_complete(shape: Shape) -> None:
    match shape:
        case Circle(r):
            pass
        case Square(s):
            pass

def shape_guarded(shape: Shape) -> None:
    match shape:  # ERR
        case Circle(r) if r > 0:
            pass
        case Square(s):
            pass

def shape_ignored(shape: Shape) -> None:
    match shape:  # type: ignore
        case Circle(r):
            pass

def tree_missing(t: Tree) -> None:
    match t:  # ERR
        case Leaf(_):
            pass
        case Node(Leaf(_), _):
            pass

def tree_complete(t: Tree) -> None:
    match t:
        case Leaf(_):
            pass
        case Node(Leaf(_), _) | Node(_, Leaf(_)):
            pass
        case Node(Node(_, _), _):
            pass

def int_partial(x: int | str) -> None:
    match x:  # PURE
        case int(_):
            pass

def int_total_missing(x: int | str) -> None:
    match x:  # ERR
        case int(_):
            pass
        case _:
            assert_never(x)

def int_total_complete(x: int | str) -> None:
    match x:
        case int(_):
            pass
        case str(_):
            pass
        case _:
            assert_never(x)

def sequence(x: Shape | list[int]) -> None:
    match x:
        case [_]:
            pass
        case Circle(_):
            pass

def one_line(x: int | str) -> None:
    match int(_) in x:
        pass

case def area_missing:  # ERR
    type(shape: Shape) -> float
    case(Circle(r)) = r

case def area_complete:
    type(shape: Shape) -> float
    case(Circle(r)) = r
    case(Square(s)) = s

case def area_ignored:  # type: ignore
    type(shape: Shape) -> float
    case(Circle(r)) = r

case def int_missing:  # PURE
    type(x: int) -> int
    type(x: str) -> int
    case(int(n)) = n

def area_expr_missing(shape: Shape) -> float = match shape:  # ERR
    case Circle(r): r

def area_expr_complete(shape: Shape) -> float = match shape:
    case Circle(r): r
    case Square(s): s

def area_expr_guarded(shape: Shape) -> float = match shape:  # ERR
    case Circle(r) if r > 0: r
    case Square(s): s

def area_expr_else(shape: Shape) -> float = match shape:
    case Circle(r): r
    else: 0.0

def assign_expr_missing(shape: Shape) -> float:
    area = match shape:  # ERR
        case Square(s): s
    return area

def assign_expr_complete(shape: Shape) -> float:
    area = match shape:
        case Circle(r):
            r_squared = r * r
            r_squared
        case Square(s): s
    return area

def return_expr_missing(t: Tree) -> int:
    return match t:  # ERR
        case Leaf(v): v
        case Node(Leaf(lv), _): lv

def int_expr_guarded(x: int) -> str = match x:  # PURE
    case pos if pos > 0: "positive"
    case nonpos if nonpos <= 0: "nonpositive"

def int_expr_total(x: int) -> str = match x:
    case pos if pos > 0: "positive"
    case _: "nonpositive"

def int_expr_partial(x: int | str) -> int = match x:  # PURE
    case int(n): n

def int_expr_total_missing(x: int | str) -> int = match x:  # ERR
    case int(n): n
    case _: assert_never(x)

def int_expr_total_complete(x: int | str) -> int:
    y = match x:
        case int(n): n
        case str(s): len(s)
        else: assert_never(x)
    return y
"""

addpattern_snip = '''
def factorial(0) = 1

addpattern def factorial(int() as n if n > 0) =
    """Compute n! where n is an integer >= 0."""
    n * factorial(n - 1)

match def typed_f(int(x)) -> int = x
addpattern def typed_f(str(s)) -> int = len(s)
addpattern def typed_f([]) -> int = 0
x: int = typed_f("abc")
y: str = typed_f(1)  # ERR

class A:
    def meth(self, 0) = 0
    addpattern def meth(self, n) = n

class B:
    def bmeth(self, 0) = 0
addpattern def B.bmeth(self, n) = n

def cc(0) = 0
copyclosure addpattern def cc(n) = n

def outer() -> None:
    def g(0) = 1
    addpattern def g(n) = n

def incompat(0) -> int = 0
addpattern def incompat(str(s)) -> str = s  # MYPY

# (this used to crash MyPy's overload merging)
def redefined(0) = 0
addpattern def redefined(n) = n
assert redefined(1) == 1
def redefined(0) = 1  # MYPY
addpattern def redefined(n) = n + 1
'''
mypy_snip_err = '''error: Incompatible types in assignment (expression has type'''

mypy_args = ["--follow-imports", "silent", "--ignore-missing-imports", "--allow-redefinition"]

ignore_mypy_errs_with = (
    "with error: MyPy error",
    "tutorial.py",
    "unused 'type: ignore' comment",
    "site-packages/numpy",
    ".py: error:"
)

ignore_atexit_errors_with = (
    "Traceback (most recent call last):",
    "sqlite3.ProgrammingError",
    "OSError: handle is closed",
)

ignore_last_lines_with = (
    "DeprecationWarning: The distutils package is deprecated",
    "from distutils.version import LooseVersion",
    ": CoconutWarning: Deprecated use of ",
    "Populating initial parsing cache",
    "_coconut.warnings.warn(",
    ": SyntaxWarning: ",
    "  assert_raises(",
    "  assert ",
    "  if x is 1:",
)

kernel_installation_msg = (
    "Coconut: Successfully installed Jupyter kernels: '"
    + "', '".join((icoconut_custom_kernel_name,) + icoconut_default_kernel_names) + "'"
)

always_sys_versions = (
    supported_py2_vers[-1],
    supported_py3_vers[-2],
    supported_py3_vers[-1],
)


# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------

def escape(inputstring):
    """Performs basic shell escaping.
    Not by any means complete, should only be used on coconut_snip."""
    if WINDOWS:
        return inputstring.replace("<", "^^^<").replace(">", "^^^>")
    else:
        return '"' + inputstring.replace("$", "\\$").replace("`", "\\`") + '"'


def call_with_import(module_name, extra_argv=[], assert_result=True):
    """Import module_name and run module.main() with given argv, capturing output."""
    pytest.register_assert_rewrite(py_str(module_name))
    print("import", module_name, "with extra_argv=" + repr(extra_argv))
    old_stdout, sys.stdout = sys.stdout, LoggingStringIO(sys.stdout)
    old_stderr, sys.stderr = sys.stderr, LoggingStringIO(sys.stderr)
    old_argv = sys.argv
    try:
        with using_coconut():
            if sys.version_info >= (2, 7):
                module = importlib.import_module(module_name)
            else:
                module = imp.load_module(module_name, *imp.find_module(module_name))
            sys.argv = [module.__file__] + extra_argv
            result = module.main()
            if assert_result:
                assert result
    except SystemExit as err:
        retcode = err.code or 0
    except BaseException:
        logger.print_exc()
        retcode = 1
    else:
        retcode = 0
    finally:
        sys.argv = old_argv
        stdout = sys.stdout.getvalue()
        stderr = sys.stderr.getvalue()
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    return stdout, stderr, retcode


def call(
    raw_cmd,
    assert_output=False,
    check_mypy=False,
    check_errors=True,
    stderr_first=False,
    expect_retcode=0,
    convert_to_import=False,
    assert_output_only_at_end=None,
    ignore_output=False,
    **kwargs
):
    """Execute a shell command and assert that no errors were encountered."""
    if isinstance(raw_cmd, str):
        cmd = raw_cmd.split()
    else:
        cmd = raw_cmd

    print()
    logger.log_cmd(cmd)

    if assert_output is False:
        assert_output = ("",)
    elif assert_output is True:
        assert_output = ("<success>",)
    elif isinstance(assert_output, str):
        if assert_output_only_at_end is None and "\n" in assert_output:
            assert_output_only_at_end = False
        assert_output = (assert_output,)
    else:
        assert_output = tuple(x if x is not True else "<success>" for x in assert_output)
    if assert_output_only_at_end is None:
        assert_output_only_at_end = True

    if convert_to_import is None:
        convert_to_import = (
            cmd[0] == sys.executable
            and cmd[1] != "-c"
            and cmd[1:3] != ["-m", "coconut"]
        )

    if convert_to_import:
        assert cmd[0] == sys.executable
        if cmd[1] == "-m":
            module_name = cmd[2]
            extra_argv = cmd[3:]
            stdout, stderr, retcode = call_with_import(module_name, extra_argv)
        else:
            module_path = cmd[1]
            extra_argv = cmd[2:]
            module_dir = os.path.dirname(module_path)
            module_name = os.path.splitext(os.path.basename(module_path))[0]
            if os.path.isdir(module_path):
                module_name += ".__main__"
            with using_sys_path(module_dir):
                stdout, stderr, retcode = call_with_import(module_name, extra_argv)
    elif ignore_output:
        retcode = run_cmd(raw_cmd, raise_errs=False, **kwargs)
        stdout = stderr = ""
    else:
        stdout, stderr, retcode = call_output(raw_cmd, color=False, **kwargs)

    if expect_retcode is not None:
        assert retcode == expect_retcode, "Return code not as expected ({retcode} != {expect_retcode}) in: {cmd!r}".format(
            retcode=retcode,
            expect_retcode=expect_retcode,
            cmd=raw_cmd,
        )
    if stderr_first:
        out = stderr + stdout
    else:
        out = stdout + stderr

    raw_lines = out.splitlines()
    lines = []
    i = 0
    while True:
        if i >= len(raw_lines):
            break
        line = raw_lines[i]

        # ignore https://bugs.python.org/issue39098 errors
        if sys.version_info < (3, 9) and (
            line == "Error in atexit._run_exitfuncs:"
            or (
                line == "Traceback (most recent call last):"
                and i + 1 < len(raw_lines)
                and "concurrent/futures/process.py" in raw_lines[i + 1]
                and "_python_exit" in raw_lines[i + 1]
            )
        ):
            while True:
                i += 1
                if i >= len(raw_lines):
                    break

                new_line = raw_lines[i]
                if not new_line.startswith(" ") and not any(test in new_line for test in ignore_atexit_errors_with):
                    i -= 1
                    break
            continue

        # combine mypy error lines
        if any(infix in line for infix in mypy_err_infixes) and i < len(raw_lines) - 1:
            # always add the next line, since it might be a continuation of the error message
            line += "\n" + raw_lines[i + 1]
            i += 1
            # then keep adding more lines if they start with whitespace, since they might be the referenced code
            for j in range(i + 2, len(raw_lines)):
                next_line = raw_lines[j]
                if next_line.lstrip() == next_line:
                    break
                line += "\n" + next_line
                i += 1

        lines.append(line)
        i += 1

    for line in lines:
        for errstr in always_err_strs:
            assert errstr not in line, "{errstr!r} in {line!r}".format(errstr=errstr, line=line)
        if check_errors and not any(ignore in line for ignore in ignore_error_lines_with):
            assert "Traceback (most recent call last):" not in line, "Traceback in " + repr(line)
            assert "Exception" not in line, "Exception in " + repr(line)
            assert "Error" not in line, "Error in " + repr(line)
        if check_mypy and all(test not in line for test in ignore_mypy_errs_with):
            assert "error:" not in line, "MyPy error in " + repr(line)

    if assert_output_only_at_end:
        last_line = ""
        for line in reversed(lines):
            if not any(ignore in line for ignore in ignore_last_lines_with):
                last_line = line
                break
        if assert_output is None:
            assert not last_line, "Expected nothing; got:\n" + "\n".join(repr(li) for li in raw_lines)
        else:
            assert any(x in last_line for x in assert_output), (
                "Expected " + ", ".join(repr(s) for s in assert_output)
                + " in " + repr(last_line)
                + "; got:\n" + "\n".join(repr(li) for li in raw_lines)
            )
    else:
        got_output = "\n".join(raw_lines) + "\n"
        assert any(x in got_output for x in assert_output), "Expected " + repr(assert_output) + "; got " + repr(got_output)


def call_python(args, **kwargs):
    """Calls the current Python."""
    if get_bool_env_var("COCONUT_TEST_DEBUG_PYTHON"):
        args = ["-X", "dev"] + args
    call([sys.executable] + args, **kwargs)


def call_coconut(args, **kwargs):
    """Calls Coconut."""
    if default_recursion_limit is not None and "--recursion-limit" not in args:
        args = ["--recursion-limit", default_recursion_limit] + args
    if default_stack_size is not None and "--stack-size" not in args:
        args = ["--stack-size", default_stack_size] + args
    if default_jobs is not None and "--jobs" not in args:
        args = ["--jobs", default_jobs] + args
    if "--mypy" in args and "check_mypy" not in kwargs:
        kwargs["check_mypy"] = True
    if PY26:
        call(["coconut"] + args, **kwargs)
    else:
        call_python(["-m", "coconut"] + args, **kwargs)


def comp(path=None, folder=None, file=None, args=[], **kwargs):
    """Compiles a test file or directory."""
    paths = []
    if path is not None:
        paths.append(path)
    compdest = os.path.join(dest, *paths)
    if folder is not None:
        paths.append(folder)
    if file is not None:
        paths.append(file)
    source = os.path.join(src, *paths)
    if "--and" in args:
        additional_compdest = os.path.join(additional_dest, *paths)
        args.remove("--and")
        args = ["--and", source, additional_compdest] + args
    call_coconut([source, compdest] + args, **kwargs)


def rm_path(path, allow_keep=False):
    """Delete a path."""
    path = os.path.abspath(fixpath(path))
    assert not base_dir.startswith(path), "refusing to delete Coconut itself: " + repr(path)
    if allow_keep and get_bool_env_var("COCONUT_KEEP_TEST_FILES"):
        return
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)
    except OSError:
        logger.print_exc()


@contextmanager
def using_paths(*paths):
    """Removes paths at the beginning and end."""
    for path in paths:
        rm_path(path)
    try:
        yield
    finally:
        for path in paths:
            rm_path(path, allow_keep=True)


@contextmanager
def using_dest(dest=dest, allow_existing=False):
    """Makes and removes the dest folder."""
    try:
        os.mkdir(dest)
    except Exception:
        if not allow_existing:
            rm_path(dest)
            os.mkdir(dest)
    try:
        yield
    finally:
        rm_path(dest, allow_keep=True)


def clean_caches():
    """Clean out all __coconut_cache__ dirs."""
    for dirpath, dirnames, filenames in os.walk(tests_dir):
        for name in dirnames:
            if name == coconut_cache_dir:
                rm_path(os.path.join(dirpath, name))


@contextmanager
def using_caches():
    """Cleans caches at start and end."""
    clean_caches()
    try:
        yield
    finally:
        clean_caches()


@contextmanager
def using_coconut(fresh_logger=True, fresh_api=False):
    """Decorator for ensuring that coconut.terminal.logger and coconut.api.* are reset."""
    saved_logger = logger.copy()
    if fresh_api:
        setup()
        auto_compilation(False)
    if fresh_logger:
        logger.reset()
    try:
        yield
    finally:
        setup()
        auto_compilation(False)
        logger.copy_from(saved_logger)


def remove_pys_in(dirpath):
    removed_pys = 0
    for fname in os.listdir(dirpath):
        if fname.endswith(".py"):
            rm_path(os.path.join(dirpath, fname))
            removed_pys += 1
    return removed_pys


@contextmanager
def using_pys_in(dirpath):
    """Remove *.py in dirpath at start and finish."""
    remove_pys_in(dirpath)
    try:
        yield
    finally:
        removed_pys = remove_pys_in(dirpath)
        assert removed_pys > 0, os.listdir(dirpath)


@contextmanager
def using_sys_path(path, prepend=False):
    """Adds a path to sys.path."""
    old_sys_path = sys.path[:]
    if prepend:
        sys.path.insert(0, path)
    else:
        sys.path.append(path)
    try:
        yield
    finally:
        sys.path[:] = old_sys_path


def add_test_func_name(test_func, cls):
    """Decorator for test functions."""
    @functools.wraps(test_func)
    def new_test_func(*args, **kwargs):
        print(
            """

===============================================================================
running {cls_name}.{name}...
===============================================================================""".format(
                cls_name=cls.__name__,
                name=test_func.__name__,
            ),
        )
        return test_func(*args, **kwargs)
    return new_test_func


def add_test_func_names(cls):
    """Decorator for test classes."""
    for name, attr in cls.__dict__.items():
        if name.startswith("test_") and callable(attr):
            setattr(cls, name, add_test_func_name(attr, cls))
    return cls


def spawn_cmd(cmd):
    """Version of pexpect.spawn that prints the command being run."""
    import pexpect  # hide import since not always available
    print("\n>", cmd)
    return pexpect.spawn(cmd)


@contextmanager
def using_env_vars(env_vars):
    """Run using the given environment variables."""
    old_env = os.environ.copy()
    os.environ.update(env_vars)
    try:
        yield
    finally:
        for k in env_vars:
            del os.environ[k]
        os.environ.update(old_env)


def list_kernel_names():
    """Get a list of installed jupyter kernels."""
    stdout, stderr, retcode = call_output(["jupyter", "kernelspec", "list"])
    if not stdout:
        stdout, stderr = stderr, ""
    assert not retcode and not stderr, stderr
    return stdout


# -----------------------------------------------------------------------------------------------------------------------
# RUNNERS:
# -----------------------------------------------------------------------------------------------------------------------

def comp_extras(args=[], **kwargs):
    """Compiles extras.coco."""
    comp(file="extras.coco", args=args, **kwargs)


def comp_runner(args=[], **kwargs):
    """Compiles runner.coco."""
    comp(file="runner.coco", args=args, **kwargs)


def comp_agnostic(args=[], **kwargs):
    """Compiles agnostic."""
    comp(path="cocotest", folder="agnostic", args=args, **kwargs)


def comp_2(args=[], always_sys=False, **kwargs):
    """Compiles target_2."""
    # remove --mypy checking for target_2 to avoid numpy errors
    try:
        mypy_ind = args.index("--mypy")
    except ValueError:
        pass
    else:
        args = args[:mypy_ind]
    comp(path="cocotest", folder="target_2", args=["--target", "2" if not always_sys else "sys"] + args, **kwargs)


def comp_3(args=[], always_sys=False, **kwargs):
    """Compiles target_3."""
    comp(path="cocotest", folder="target_3", args=["--target", "3" if not always_sys else "sys"] + args, **kwargs)


def comp_35(args=[], always_sys=False, **kwargs):
    """Compiles target_35."""
    comp(path="cocotest", folder="target_35", args=["--target", "35" if not always_sys else "sys"] + args, **kwargs)


def comp_36(args=[], always_sys=False, **kwargs):
    """Compiles target_36."""
    comp(path="cocotest", folder="target_36", args=["--target", "36" if not always_sys else "sys"] + args, **kwargs)


def comp_38(args=[], always_sys=False, **kwargs):
    """Compiles target_38."""
    comp(path="cocotest", folder="target_38", args=["--target", "38" if not always_sys else "sys"] + args, **kwargs)


def comp_311(args=[], always_sys=False, **kwargs):
    """Compiles target_311."""
    comp(path="cocotest", folder="target_311", args=["--target", "311" if not always_sys else "sys"] + args, **kwargs)


def comp_314(args=[], always_sys=False, **kwargs):
    """Compiles target_314."""
    # remove --mypy checking when running on Python 3.14 since MyPy can't parse t-strings
    if sys.version_info < (3, 14):
        try:
            mypy_ind = args.index("--mypy")
        except ValueError:
            pass
        else:
            args = args[:mypy_ind]
    comp(path="cocotest", folder="target_314", args=["--target", "314" if not always_sys else "sys"] + args, **kwargs)


def comp_sys(args=[], **kwargs):
    """Compiles target_sys."""
    comp(path="cocotest", folder="target_sys", args=["--target", "sys"] + args, **kwargs)


def comp_non_strict(args=[], **kwargs):
    """Compiles non_strict."""
    non_strict_args = [arg for arg in args if arg != "--strict"]
    comp(path="cocotest", folder="non_strict", args=non_strict_args, **kwargs)


def run_src(**kwargs):
    """Runs runner.py."""
    call_python([os.path.join(dest, "runner.py")], assert_output=True, **kwargs)


def run_extras(**kwargs):
    """Runs extras.py."""
    call_python([os.path.join(dest, "extras.py")], assert_output=True, check_errors=False, stderr_first=True, **kwargs)


def run(
    args=[],
    agnostic_target=None,
    use_run_arg=False,
    run_directory=False,
    convert_to_import=False,
    always_sys=False,
    manage_cache=True,
    **kwargs  # no comma for compat
):
    """Compiles and runs tests."""
    assert use_run_arg + run_directory < 2

    if manage_cache and "--no-cache" not in args:
        args = ["--no-cache"] + args

    if agnostic_target is None:
        agnostic_args = args
    else:
        agnostic_args = ["--target", str(agnostic_target)] + args

    with using_caches() if manage_cache else noop_ctx():
        with using_dest():
            with using_dest(additional_dest) if "--and" in args else noop_ctx():

                spec_kwargs = kwargs.copy()
                spec_kwargs["always_sys"] = always_sys
                if PY2:
                    comp_2(args, **spec_kwargs)
                else:
                    comp_3(args, **spec_kwargs)
                    if sys.version_info >= (3, 5):
                        comp_35(args, **spec_kwargs)
                    if sys.version_info >= (3, 6):
                        comp_36(args, **spec_kwargs)
                    if sys.version_info >= (3, 8):
                        comp_38(args, **spec_kwargs)
                    if sys.version_info >= (3, 11):
                        comp_311(args, **spec_kwargs)
                    if sys.version_info >= (3, 14):
                        comp_314(args, **spec_kwargs)

                if not run_directory:
                    comp_agnostic(agnostic_args, **kwargs)
                comp_sys(args, **kwargs)
                # do non-strict at the end so we get the non-strict header
                comp_non_strict(args, **kwargs)

                if run_directory:
                    _kwargs = kwargs.copy()
                    _kwargs["assert_output"] = True
                    _kwargs["stderr_first"] = True
                    comp_agnostic(
                        # remove --strict so that we run with the non-strict header
                        ["--run"] + [arg for arg in agnostic_args if arg != "--strict"],
                        **_kwargs
                    )
                elif use_run_arg:
                    _kwargs = kwargs.copy()
                    _kwargs["assert_output"] = True
                    comp_runner(["--run"] + agnostic_args, **_kwargs)
                else:
                    comp_runner(agnostic_args, **kwargs)
                    run_src(convert_to_import=convert_to_import)  # **kwargs are for comp, not run

                if use_run_arg:
                    _kwargs = kwargs.copy()
                    _kwargs["assert_output"] = True
                    _kwargs["check_errors"] = False
                    _kwargs["stderr_first"] = True
                    comp_extras(["--run"] + agnostic_args, **_kwargs)
                else:
                    comp_extras(agnostic_args, **kwargs)
                    run_extras(convert_to_import=convert_to_import)  # **kwargs are for comp, not run


def comp_all(args=[], agnostic_target=None, **kwargs):
    """Compile Coconut tests."""
    if agnostic_target is None:
        agnostic_args = args
    else:
        agnostic_args = ["--target", str(agnostic_target)] + args

    try:
        os.mkdir(dest)
    except Exception:
        pass

    comp_agnostic(agnostic_args, **kwargs)
    comp_runner(agnostic_args, **kwargs)
    comp_extras(agnostic_args, **kwargs)

    comp_2(args, **kwargs)
    comp_3(args, **kwargs)
    comp_35(args, **kwargs)
    comp_36(args, **kwargs)
    comp_38(args, **kwargs)
    comp_311(args, **kwargs)
    comp_314(args, **kwargs)
    comp_sys(args, **kwargs)
    # do non-strict at the end so we get the non-strict header
    comp_non_strict(args, **kwargs)


def comp_pyston(args=[], **kwargs):
    """Compiles evhub/pyston."""
    call(["git", "clone", pyston_git])
    call_coconut(["pyston", "--force"] + args, check_errors=False, **kwargs)


def run_pyston(**kwargs):
    """Runs pyston."""
    call_python([os.path.join(pyston, "runner.py")], assert_output=True, **kwargs)


def comp_pyprover(args=[], **kwargs):
    """Compiles evhub/pyprover."""
    call(["git", "clone", pyprover_git])
    call_coconut([os.path.join(pyprover, "setup.coco"), "--force"] + args, **kwargs)
    call_coconut([os.path.join(pyprover, "pyprover-source"), os.path.join(pyprover, "pyprover"), "--force"] + args, **kwargs)


def run_pyprover(**kwargs):
    """Runs pyprover."""
    call(["pip", "install", "-e", pyprover])
    call_python([os.path.join(pyprover, "pyprover", "tests.py")], assert_output=True, **kwargs)


def comp_prelude(args=[], **kwargs):
    """Compiles evhub/coconut-prelude."""
    call(["git", "clone", prelude_git])
    # disabled --mypy: was causing test_prelude to take ~5 hours due to
    # extremely slow mypy type-checking on the coconut-prelude package
    # if MYPY and not WINDOWS:
    #     args.extend(["--target", "3.5", "--mypy"])
    #     kwargs["check_errors"] = False
    call_coconut([os.path.join(prelude, "setup.coco"), "--force"] + args, **kwargs)
    call_coconut([os.path.join(prelude, "prelude-source"), os.path.join(prelude, "prelude"), "--force"] + args, **kwargs)


def run_prelude(**kwargs):
    """Runs coconut-prelude."""
    call(["make", "base-install"], cwd=prelude)
    call(["pytest", "--strict-markers", "-s", os.path.join(prelude, "prelude")], assert_output=" passed in ", assert_output_only_at_end=False, **kwargs)


def comp_bbopt(args=[], **kwargs):
    """Compiles evhub/bbopt."""
    call(["git", "clone", bbopt_git])
    call_coconut([os.path.join(bbopt, "setup.coco"), "--force"] + args, **kwargs)
    call_coconut([os.path.join(bbopt, "bbopt-source"), os.path.join(bbopt, "bbopt"), "--force"] + args, **kwargs)


def install_bbopt():
    """Runs bbopt."""
    call(["pip", "install", "-Ue", bbopt])


def run_runnable(args=[]):
    """Call coconut-run on runnable_coco."""
    paths_being_used = [importable_compiled_loc]
    if "--no-write" not in args and "-n" not in args:
        paths_being_used.append(runnable_compiled_loc)
    with using_paths(*paths_being_used):
        call(["coconut-run"] + args + [runnable_coco, "--arg"], assert_output=True)


def comp_runnable(args=[]):
    """Just compile runnable."""
    if "--target" not in args:
        args += ["--target", "sys"]
    call_coconut([runnable_coco, "--and", importable_coco] + args)
    call_coconut([runnable_coco, "--and", importable_coco] + args, assert_output="Left unchanged", assert_output_only_at_end=False)


# -----------------------------------------------------------------------------------------------------------------------
# TESTS:
# -----------------------------------------------------------------------------------------------------------------------

@add_test_func_names
class TestShell(unittest.TestCase):

    def test_version(self):
        call(["coconut", "--version"])

    def test_code(self):
        call(["coconut", "-s", "-c", coconut_snip], assert_output=True)

    # (on Python 2, Coconut's pickle is cPickle, which can't find the substitute __main__ module)
    if not PY2:
        def test_pickle_main(self):
            call(["coconut", "-c", pickle_main_snip], assert_output=True)

    if not PY2:
        def test_target_3_snip(self):
            call(["coconut", "-t3", "-c", target_3_snip], assert_output=True)

    if MYPY:
        def test_universal_mypy_snip(self):
            call(
                ["coconut", "-c", mypy_snip, "--mypy"],
                assert_output=mypy_snip_err,
                check_errors=False,
                check_mypy=False,
            )

        def test_sys_mypy_snip(self):
            call(
                ["coconut", "--target", "sys", "-c", mypy_snip, "--mypy"],
                assert_output=mypy_snip_err,
                check_errors=False,
                check_mypy=False,
            )

        def test_no_wrap_mypy_snip(self):
            call(
                ["coconut", "--target", "sys", "--no-wrap", "-c", mypy_snip, "--mypy"],
                assert_output=mypy_snip_err,
                check_errors=False,
                check_mypy=False,
            )

        def test_mypy_source_lines(self):
            mypy_dir = tempfile.mkdtemp()
            try:
                mypy_coco = os.path.join(mypy_dir, "mypy_lines_test.coco")
                with open(mypy_coco, "w") as mypy_file:
                    mypy_file.write("def f(x: int) -> int = x + 1\n\ny: str = f(1)\n")
                # errors should point to the Coconut source line rather than the compiled line
                call(
                    ["coconut", mypy_coco, "--force", "--mypy"],
                    assert_output=("mypy_lines_test.coco:3: error:",),
                    assert_output_only_at_end=False,
                    check_errors=False,
                    check_mypy=False,
                    expect_retcode=1,
                )
            finally:
                shutil.rmtree(mypy_dir)

        def test_exhaustiveness(self):
            exhaustiveness_dir = tempfile.mkdtemp()
            try:
                exhaustiveness_coco = os.path.join(exhaustiveness_dir, "exhaustiveness_test.coco")
                with open(exhaustiveness_coco, "w") as exhaustiveness_file:
                    exhaustiveness_file.write(exhaustiveness_snip)

                def get_error_lines(*extra_args, **kwargs):
                    pyright = kwargs.pop("pyright", False)
                    if pyright:
                        type_checking_args = ["--pyright"]
                        # (Pyright reports other issues with the compiled pattern-matching code, so only look at ours)
                        error_regex = r"exhaustiveness_test\.coco:([0-9]+): error: [^\n]*match_must"
                    else:
                        # (MyPy's cache can report stale errors for files of the same name in other directories)
                        type_checking_args = ["--mypy", "--cache-dir", os.path.join(exhaustiveness_dir, ".mypy_cache")]
                        error_regex = r"exhaustiveness_test\.coco:([0-9]+): error:"
                    stdout, stderr, retcode = call_output(
                        ["coconut", exhaustiveness_coco, "--force", "--no-cache", "--target", "sys"] + list(extra_args) + type_checking_args,
                        color=False,
                    )
                    output = "".join(stdout + stderr)
                    error_lines = set(int(ln) for ln in re.findall(error_regex, output))
                    return error_lines, output

                snip_lines = exhaustiveness_snip.splitlines()
                # lines marked "# ERR" should get exhaustiveness errors, and lines marked "# PURE" only under --pure
                expected_errors = set(i + 1 for i, line in enumerate(snip_lines) if "# ERR" in line)
                expected_pure_errors = expected_errors | set(i + 1 for i, line in enumerate(snip_lines) if "# PURE" in line)

                error_lines, output = get_error_lines()
                assert error_lines == expected_errors, (error_lines, expected_errors, output)
                pure_error_lines, pure_output = get_error_lines("--pure")
                assert pure_error_lines == expected_pure_errors, (pure_error_lines, expected_pure_errors, pure_output)
                pyright_error_lines, pyright_output = get_error_lines(pyright=True)
                assert pyright_error_lines == expected_errors, (pyright_error_lines, expected_errors, pyright_output)
            finally:
                shutil.rmtree(exhaustiveness_dir)

        def test_addpattern_redefinition(self):
            addpattern_dir = tempfile.mkdtemp()
            try:
                addpattern_coco = os.path.join(addpattern_dir, "addpattern_test.coco")
                with open(addpattern_coco, "w") as addpattern_file:
                    addpattern_file.write(addpattern_snip)

                def get_output(*extra_args):
                    stdout, stderr, retcode = call_output(
                        ["coconut", addpattern_coco, "--force", "--no-cache"] + list(extra_args),
                        color=False,
                    )
                    return "".join(stdout + stderr)

                # addpattern def shouldn't produce any redefinition errors; lines marked "# ERR" should get type errors
                #  (showing that the combined function keeps a real type), and lines marked "# MYPY" should get mypy errors
                #  (since mypy keeps the type of the first definition, so later cases have to be compatible with it)
                snip_lines = addpattern_snip.splitlines()
                expected_type_errors = set(i + 1 for i, line in enumerate(snip_lines) if "# ERR" in line)
                expected_mypy_errors = expected_type_errors | set(i + 1 for i, line in enumerate(snip_lines) if "# MYPY" in line)

                # (the universal target compiles annotations to type comments)
                for target_args in ([], ["--target", "sys"]):
                    # (MyPy's cache can report stale errors for files of the same name in other directories)
                    mypy_output = get_output(*(target_args + ["--mypy", "--cache-dir", os.path.join(addpattern_dir, ".mypy_cache")]))
                    mypy_error_lines = set(int(ln) for ln in re.findall(r"addpattern_test\.coco:([0-9]+): error:", mypy_output))
                    assert mypy_error_lines == expected_mypy_errors, (target_args, mypy_error_lines, expected_mypy_errors, mypy_output)
                    assert not re.search(r"addpattern_test\.py:[0-9]+: error:", mypy_output), (target_args, mypy_output)

                # (Pyright reports other issues with the compiled pattern-matching code, so only look at the relevant errors)
                pyright_output = get_output("--target", "sys", "--pyright")
                pyright_redef_lines = set(int(ln) for ln in re.findall(
                    r"addpattern_test\.coco:([0-9]+): error: (?:[^\n]*obscured by a declaration of the same name|Cannot assign to attribute)",
                    pyright_output,
                ))
                assert not pyright_redef_lines, (pyright_redef_lines, pyright_output)
                pyright_type_error_lines = set(int(ln) for ln in re.findall(
                    r"addpattern_test\.coco:([0-9]+): error: Type \"int\" is not assignable to declared type \"str\"",
                    pyright_output,
                ))
                assert pyright_type_error_lines == expected_type_errors, (pyright_type_error_lines, expected_type_errors, pyright_output)
            finally:
                shutil.rmtree(addpattern_dir)

        def test_pyright(self):
            pyright_dir = tempfile.mkdtemp()
            try:
                pyright_coco = os.path.join(pyright_dir, "pyright_test.coco")
                with open(pyright_coco, "w") as pyright_file:
                    pyright_file.write("def f(x: int) -> int = x + 1\n\ny: str = f(1)\n")
                # errors should point to the Coconut source line rather than the compiled line
                call(
                    ["coconut", pyright_coco, "--pyright"],
                    assert_output=("pyright_test.coco:3: error:", "y: str = f(1)"),
                    assert_output_only_at_end=False,
                    check_errors=False,
                    expect_retcode=1,
                )
            finally:
                shutil.rmtree(pyright_dir)

    def test_silence_warnings(self):
        warn_dir = tempfile.mkdtemp()
        try:
            warn_coco = os.path.join(warn_dir, "silence_warnings_test.coco")
            with open(warn_coco, "w") as warn_file:
                warn_file.write("class A(object):\n    pass\nf = getattr.\n")
            base_cmd = ["coconut", warn_coco, "--force", "--no-cache"]

            def get_output(*extra_args):
                stdout, stderr, retcode = call_output(base_cmd + list(extra_args), color=False)
                assert retcode == 0, (stdout, stderr)
                return "".join(stdout + stderr)

            unsilenced = get_output()
            assert "inheriting from object" in unsilenced, unsilenced
            assert "getattr" in unsilenced, unsilenced
            partly_silenced = get_output("--silence-warnings", "inheriting from")
            assert "inheriting from object" not in partly_silenced, partly_silenced
            assert "getattr" in partly_silenced, partly_silenced
            # only the warning message should be matched, not the code snippet that follows it
            snippet_silenced = get_output("--silence-warnings", "class A")
            assert "inheriting from object" in snippet_silenced, snippet_silenced
            fully_silenced = get_output("--silence-warnings", "object", "--silence-warnings", r"silence_warnings_test\.coco")
            assert "CoconutSyntaxWarning" not in fully_silenced, fully_silenced
        finally:
            shutil.rmtree(warn_dir)

    if sys.version_info >= (3, 5):
        def test_zipapp(self):
            zipapp_dir = tempfile.mkdtemp()
            try:
                src_dir = os.path.join(zipapp_dir, "src")
                build_dir = os.path.join(zipapp_dir, "build")
                os.makedirs(os.path.join(src_dir, "zipapp_pkg"))
                with open(os.path.join(src_dir, "zipapp_pkg", "__init__.coco"), "w") as init_file:
                    init_file.write("\n")
                with open(os.path.join(src_dir, "zipapp_pkg", "mod.coco"), "w") as mod_file:
                    mod_file.write("def run() = range(3) |> map$(.*2) |> list\n")
                with open(os.path.join(src_dir, "__main__.coco"), "w") as main_file:
                    main_file.write("from zipapp_pkg.mod import run\nprint(run())\n")
                call(["coconut", src_dir, build_dir, "--force"])
                app_path = os.path.join(zipapp_dir, "app.pyz")
                call([sys.executable, "-m", "zipapp", build_dir, "-o", app_path])
                call([sys.executable, app_path], assert_output="[0, 2, 4]", convert_to_import=False)
            finally:
                shutil.rmtree(zipapp_dir)

    def test_pipe(self):
        call('echo ' + escape(coconut_snip) + "| coconut -s", shell=True, assert_output=True)

    def test_code_interact(self):
        call(["coconut", "-s", "-c", coconut_snip, "--interact"], assert_output=True, assert_output_only_at_end=False)

    if not PY2 and int(pytest.__version__.split(".")[0]) >= 7:
        def test_pytest_plugin(self):
            plugin_dir = tempfile.mkdtemp()
            try:
                with open(os.path.join(plugin_dir, "plugin_helpers.coco"), "w") as helper_file:
                    helper_file.write("def double(x) = x * 2\n")
                with open(os.path.join(plugin_dir, "test_plugin_example.coco"), "w") as test_file:
                    test_file.write(
                        "from plugin_helpers import double\n"
                        "def test_double():\n"
                        "    assert range(3) |> map$(double) |> list == [0, 2, 4]\n"
                        "def test_fails():\n"
                        "    assert double(2) == 5\n"
                    )
                call(
                    [sys.executable, "-m", "pytest", "-p", "coconut.pytest_plugin", "-p", "no:cacheprovider", plugin_dir],
                    assert_output=("assert 4 == 5", "1 failed, 1 passed"),
                    assert_output_only_at_end=False,
                    check_errors=False,
                    expect_retcode=1,
                )
            finally:
                shutil.rmtree(plugin_dir)

    if LSP:
        def test_lsp(self):
            import json
            import subprocess
            import threading
            try:
                import queue
            except ImportError:
                import Queue as queue  # type: ignore

            # how long to wait for any single response from the server before failing
            lsp_timeout = 300

            proc = subprocess.Popen(["coconut", "--lsp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            next_id = [0]
            messages = queue.Queue()

            def send(msg):
                data = json.dumps(msg).encode("utf-8")
                proc.stdin.write(("Content-Length: %d\r\n\r\n" % len(data)).encode("ascii") + data)
                proc.stdin.flush()

            def read_messages():
                # read messages on a separate thread so that a server that stops
                #  responding fails the test rather than hanging it
                try:
                    while True:
                        headers = {}
                        while True:
                            line = proc.stdout.readline()
                            if not line:
                                return  # server exited
                            line = line.decode("ascii").strip()
                            if not line:
                                break
                            key, val = line.split(":", 1)
                            headers[key.strip().lower()] = val.strip()
                        messages.put(json.loads(proc.stdout.read(int(headers["content-length"]))))
                finally:
                    messages.put(None)
            reader = threading.Thread(target=read_messages)
            reader.daemon = True
            reader.start()

            def wait_for(pred):
                while True:
                    try:
                        msg = messages.get(timeout=lsp_timeout)
                    except queue.Empty:
                        raise AssertionError("timed out waiting for the language server to respond")
                    if msg is None:
                        raise AssertionError("language server exited unexpectedly:\n" + proc.stderr.read().decode("utf-8", "replace"))
                    if pred(msg):
                        return msg

            def request(method, params):
                next_id[0] += 1
                req_id = next_id[0]
                send({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params})
                return wait_for(lambda msg: msg.get("id") == req_id and "method" not in msg)["result"]

            def notify(method, params):
                send({"jsonrpc": "2.0", "method": method, "params": params})

            try:
                uri = "file:///lsp_test.coco"
                src = "import json\n\ndata Point(x, y)\n\ndef total(ps) =\n    ps |> map$(p => p.x + p.y) |> sum\n\nresult = total([Point(1, 2)])\nencoded = json.dumps(result)\n"
                capabilities = request("initialize", {"processId": None, "rootUri": None, "capabilities": {}})["capabilities"]
                for capability in ("hoverProvider", "definitionProvider", "completionProvider", "documentSymbolProvider", "referencesProvider", "documentHighlightProvider", "signatureHelpProvider", "renameProvider", "workspaceSymbolProvider", "typeDefinitionProvider", "codeActionProvider"):
                    assert capabilities.get(capability), capabilities
                notify("initialized", {})

                # diagnostics
                notify("textDocument/didOpen", {"textDocument": {"uri": uri, "languageId": "coconut", "version": 1, "text": src}})
                diagnostics = wait_for(lambda msg: msg.get("method") == "textDocument/publishDiagnostics")["params"]["diagnostics"]
                assert diagnostics == [], diagnostics

                # hover and go to definition
                hover = request("textDocument/hover", {"textDocument": {"uri": uri}, "position": {"line": 7, "character": 10}})
                assert "total(ps)" in hover["contents"]["value"], hover
                definition = request("textDocument/definition", {"textDocument": {"uri": uri}, "position": {"line": 7, "character": 17}})
                assert definition[0]["range"]["start"] == {"line": 2, "character": 5}, definition

                # references and highlights
                result_refs = [((7, 0), (7, 6)), ((8, 21), (8, 27))]
                references = request("textDocument/references", {"textDocument": {"uri": uri}, "position": {"line": 8, "character": 23}, "context": {"includeDeclaration": True}})
                assert [((ref["range"]["start"]["line"], ref["range"]["start"]["character"]), (ref["range"]["end"]["line"], ref["range"]["end"]["character"])) for ref in references] == result_refs, references
                highlights = request("textDocument/documentHighlight", {"textDocument": {"uri": uri}, "position": {"line": 7, "character": 2}})
                assert [((hl["range"]["start"]["line"], hl["range"]["start"]["character"]), (hl["range"]["end"]["line"], hl["range"]["end"]["character"])) for hl in highlights] == result_refs, highlights

                # error diagnostics
                bad_src = src.replace("json.dumps(result)", "json.dumps(result")
                notify("textDocument/didChange", {"textDocument": {"uri": uri, "version": 2}, "contentChanges": [{"text": bad_src}]})
                diagnostics = wait_for(lambda msg: msg.get("method") == "textDocument/publishDiagnostics" and msg["params"].get("version") == 2)["params"]["diagnostics"]
                assert len(diagnostics) == 1 and diagnostics[0]["range"]["start"]["line"] == 8, diagnostics

                # completion in the middle of typing
                typing_src = src.replace("json.dumps(result)", "json.du")
                notify("textDocument/didChange", {"textDocument": {"uri": uri, "version": 3}, "contentChanges": [{"text": typing_src}]})
                completions = request("textDocument/completion", {"textDocument": {"uri": uri}, "position": {"line": 8, "character": 17}})
                assert "dumps" in [item["label"] for item in completions["items"]], completions

                # signature help in the middle of typing
                sig_src = src.replace("json.dumps(result)", "total(")
                notify("textDocument/didChange", {"textDocument": {"uri": uri, "version": 4}, "contentChanges": [{"text": sig_src}]})
                sig_help = request("textDocument/signatureHelp", {"textDocument": {"uri": uri}, "position": {"line": 8, "character": len("encoded = total(")}})
                assert sig_help["signatures"][0]["label"].startswith("total(ps"), sig_help
                assert sig_help["activeParameter"] == 0, sig_help

                # document symbols
                symbols = request("textDocument/documentSymbol", {"textDocument": {"uri": uri}})
                # (the line being typed, 'encoded = total(', doesn't compile yet, so it isn't a symbol yet)
                assert [sym["name"] for sym in symbols] == ["Point", "total", "result"], symbols

                request("shutdown", None)
                notify("exit", None)
                assert proc.wait(timeout=30) == 0
            finally:
                if proc.poll() is None:
                    proc.kill()

    # (Counter reprs and dict ordering differ on older Pythons)
    if sys.version_info >= (3, 7) and os.path.exists(tutorial_file):
        def test_tutorial(self):
            # all the examples in the tutorial should work exactly as the tutorial says they do
            with univ_open(tutorial_file, "r") as tutorial:
                tutorial_text = tutorial.read()
            failures = check_tutorial(tutorial_text)
            assert not failures, failures

            # and the interactive tutorial should let you run all of them
            try:
                import markdown_it  # NOQA
            except ImportError:
                return
            sys.path.insert(0, repo_root)
            try:
                from interactive_tutorial import make_interactive_tutorial, is_example, pyodide_packages
            finally:
                sys.path.pop(0)
            page = make_interactive_tutorial(tutorial_text, ["pyparsing==2.4.7", "coconut"])
            num_examples = len([block for block in re.findall(r"```coconut\n(.*?)```", tutorial_text, re.DOTALL) if is_example(block)])
            assert page.count('<div class="example">') == num_examples, (page.count('<div class="example">'), num_examples)
            # Pyodide's setuptools depends on Pyodide's pyparsing, which is pyparsing 3
            assert "setuptools" not in pyodide_packages, pyodide_packages

    def test_ai_docs(self):
        # (the guide mentions exception names, so don't check for errors in its text)
        call(["coconut", "--ai-docs"], assert_output="Common pitfalls", assert_output_only_at_end=False, check_errors=False)
        # all the code examples in the AI guide should actually work
        with univ_open(ai_docs_file, "r") as ai_docs:
            guide = ai_docs.read()
        code_blocks = re.findall(r"```coconut\n(.*?)```", guide, re.DOTALL)
        assert code_blocks, guide
        guide_dir = tempfile.mkdtemp()
        try:
            guide_coco = os.path.join(guide_dir, "ai_guide_examples.coco")
            with univ_open(guide_coco, "w") as guide_file:
                guide_file.write("\n".join(code_blocks) + '\nprint("<success>")\n')
            # (run it separately, rather than with --run, since on Python 2, process_map can't
            #  pickle functions defined in code that Coconut runs itself)
            call_coconut([guide_coco, "--target", "sys", "--force"], check_errors=False)
            call_python([os.path.join(guide_dir, "ai_guide_examples.py")], assert_output=True, check_errors=False)
            # compiled files should point back to their source and the guide
            with univ_open(os.path.join(guide_dir, "ai_guide_examples.py"), "r") as compiled_file:
                compiled_header = compiled_file.read(1024)
            assert "compiled from ai_guide_examples.coco" in compiled_header, compiled_header
            assert "coconut --ai-docs" in compiled_header, compiled_header
        finally:
            shutil.rmtree(guide_dir)

    def test_no_write_package(self):
        pkg_dir = tempfile.mkdtemp()
        try:
            os.mkdir(os.path.join(pkg_dir, "pkg"))
            with univ_open(os.path.join(pkg_dir, "pkg", "mod.coco"), "w") as mod_file:
                mod_file.write("x = 1\n")
            # compiling a directory without writing used to fail with an invalid package level
            call_coconut([pkg_dir, "--no-write"])
            assert not os.path.exists(os.path.join(pkg_dir, "pkg", "mod.py"))
        finally:
            shutil.rmtree(pkg_dir)

    def test_module_arg(self):
        module_dir = tempfile.mkdtemp()
        try:
            pkg_dir = os.path.join(module_dir, "coconut_m_test_pkg")
            os.mkdir(pkg_dir)
            for name, contents in (
                ("__init__.coco", '"""A package to test coconut -m."""\n'),
                ("helper.coco", "def double(x) = x * 2\n"),
                ("main.coco", (
                    "import sys\n"
                    "from .helper import double\n"  # relative imports should work
                    "assert __name__ == '__main__' and __package__ == 'coconut_m_test_pkg'\n"
                    "assert double(sys.argv[1:]) == ['a', 'b'] * 2, sys.argv\n"
                    "assert sys.stdin.read() == 'stdin for the module', 'got the wrong stdin'\n"  # stdin should be left for the module
                    "print('<success>')\n"
                )),
                ("exits.coco", "import sys\nsys.exit(int(sys.argv[1]))\n"),
            ):
                with univ_open(os.path.join(pkg_dir, name), "w") as module_file:
                    module_file.write(contents)

            call_coconut(["--no-cache", "-m", "coconut_m_test_pkg.main", "--argv", "a", "b"], cwd=module_dir, stdin=b"stdin for the module", assert_output=True)
            # the whole package is compiled in place so that python -m can find it
            for name in ("__init__.py", "helper.py", "main.py", "exits.py"):
                assert os.path.isfile(os.path.join(pkg_dir, name)), os.listdir(pkg_dir)
            call_python(["-m", "coconut_m_test_pkg.main", "a", "b"], cwd=module_dir, stdin=b"stdin for the module", assert_output=True, convert_to_import=False)

            # coconut-run -m passes everything after the module to it
            call(["coconut-run", "--no-cache", "-m", "coconut_m_test_pkg.main", "a", "b"], cwd=module_dir, stdin=b"stdin for the module", assert_output=True)

            # the module's exit code is passed through
            call_coconut(["--no-cache", "-m", "coconut_m_test_pkg.exits", "--argv", "3"], cwd=module_dir, expect_retcode=3)
            call(["coconut-run", "--no-cache", "--module", "coconut_m_test_pkg.exits", "4"], cwd=module_dir, expect_retcode=4)

            # -m can't be combined with --run or a source, and the module has to exist
            for bad_args, err_msg in (
                (["-m", "coconut_m_test_pkg.main", "--run"], "cannot use -m/--module with --run"),
                (["-m", "coconut_m_test_pkg.main", pkg_dir], "cannot pass a source file/folder with -m/--module"),
                (["-m", "coconut_m_test_pkg.nonexistent"], "could not find module"),
            ):
                call_coconut(bad_args, cwd=module_dir, assert_output=err_msg, assert_output_only_at_end=False, check_errors=False, expect_retcode=1)
        finally:
            shutil.rmtree(module_dir)

    def test_project_config(self):
        from coconut.project_config import parse_table, _fallback_parse_table, find_project_config
        toml_text = (
            '[project]\nname = "pkg"\n\n'
            '[tool.coconut]  # comment\ntarget = "3.10"\npure = true\nno-tco = false\n\n'
            '[tool.other]\nstrict = true\n'
        )
        expected = {"target": "3.10", "pure": True, "no-tco": False}
        assert parse_table(toml_text, ("tool", "coconut")) == expected
        assert _fallback_parse_table(toml_text, ("tool", "coconut"), "<test>") == expected
        assert parse_table("[project]\n", ("tool", "coconut")) == {}

        proj_dir = tempfile.mkdtemp()
        try:
            src_dir = os.path.join(proj_dir, "src")
            os.mkdir(src_dir)
            with univ_open(os.path.join(proj_dir, "pyproject.toml"), "w") as config_file:
                config_file.write('[tool.coconut]\nstrict = true\npure = true\ntarget = "3.10"\n')
            assert find_project_config(src_dir) == {"strict": True, "pure": True, "target": "3.10"}
            impure_file = os.path.join(src_dir, "impure.coco")
            with univ_open(impure_file, "w") as impure:
                impure.write("x = 1\nx = 2\n")
            call_coconut(
                [impure_file, "--no-write"],
                assert_output="disallowed reassignment",
                assert_output_only_at_end=False,
                check_errors=False,
                expect_retcode=1,
            )
            # a pyproject.toml without a [tool.coconut] table means no configuration
            with univ_open(os.path.join(proj_dir, "pyproject.toml"), "w") as config_file:
                config_file.write('[project]\nname = "pkg"\n')
            call_coconut([impure_file, "--no-write"])
        finally:
            shutil.rmtree(proj_dir)

    if not WINDOWS:
        def test_import_hook_preserves_stdin(self):
            hook_dir = tempfile.mkdtemp()
            try:
                with open(os.path.join(hook_dir, "stdin_hook_mod.coco"), "w") as mod_file:
                    mod_file.write("x = 1 |> (.+1)\n")
                # importing a Coconut module shouldn't consume (and execute) the program's piped stdin
                call(
                    "cd " + hook_dir + " && echo 'print(\"HIJACKED\")' | " + sys.executable + ' -c "'
                    + "import sys, coconut.api; import stdin_hook_mod; "
                    + "assert stdin_hook_mod.x == 2; assert 'HIJACKED' in sys.stdin.read(); print('<success>')"
                    + '"',
                    shell=True,
                    assert_output=True,
                )
            finally:
                shutil.rmtree(hook_dir)

    def test_api(self):
        call_python(["-c", 'from coconut.api import parse; exec(parse("' + coconut_snip + '"))'], assert_output=True)

    def test_import_hook(self):
        with using_sys_path(src):
            with using_paths(runnable_compiled_loc, importable_compiled_loc):
                with using_coconut():
                    auto_compilation(True)
                    import runnable
                    if not PY2:  # triggers a weird metaclass conflict
                        reload(runnable)
        assert runnable.success == "<success>"

    def test_find_packages(self):
        with using_pys_in(agnostic_dir):
            with using_coconut():
                from coconut.api import find_packages, find_and_compile_packages
                assert find_packages(cocotest_dir) == ["agnostic"]
                assert find_and_compile_packages(cocotest_dir) == ["agnostic"]

    def test_runnable(self):
        run_runnable()

    def test_runnable_nowrite(self):
        run_runnable(["-n"])

    def test_compile_runnable(self):
        with using_paths(runnable_py, importable_py):
            comp_runnable()
            call_python([runnable_py, "--arg"], assert_output=True)

    def test_import_runnable(self):
        with using_paths(runnable_py, importable_py):
            comp_runnable()
            for _ in range(2):  # make sure we can import it twice
                call_python([runnable_py, "--arg"], assert_output=True, convert_to_import=True)

    if not WINDOWS and XONSH:
        def test_xontrib(self):
            # don't let xonsh history (from this or earlier sessions) affect the session, since
            #  history-based autosuggestions change how input is echoed
            with using_env_vars({"XONSH_HISTORY_BACKEND": "dummy"}):
                # xonsh generates its parser tables the first time it parses anything (which can take
                #  a very long time), so make sure that happens before the interactive session
                call(["xonsh", "-c", "echo xonsh_warmup"], assert_output="xonsh_warmup", check_errors=False)
                p = spawn_cmd("xonsh")
                pexpect(p, "$")
                p.sendline("xontrib load coconut")
                pexpect(p, "$")
                p.sendline("!(ls -la) |> bool")
                pexpect(p, "True")
                p.sendline("'1; 2' |> print")
                pexpect(p, "1; 2")
                p.sendline('$ENV_VAR = "ABC"')
                pexpect(p, "$")
                p.sendline('echo f"{$ENV_VAR}"; echo f"{$ENV_VAR}"')
                pexpect(p, "ABC")
                pexpect(p, "ABC")
                p.sendline('len("""1\n3\n5""")\n')
                pexpect(p, "5")
                if not PYPY or PY39:
                    if PY36:
                        p.sendline("echo 123;; 123")
                        # match the output rather than the echoed input: newer xonshes print 123; and 123 on separate
                        #  lines (possibly with color codes in between) while older ones print 123;; 123, but
                        #  either way the output starts right after a newline or escape code, unlike the echoed input
                        pexpect(p, r"(?:\n|\x1b\[[0-9;?>]*[A-Za-z])123;(?:; |\r?\n(?:\x1b\[[0-9;?>]*[A-Za-z])*)123")
                        p.sendline("echo abc; echo abc")
                        pexpect(p, "abc")
                        pexpect(p, "abc")
                        p.sendline("echo abc; print(1 |> (.+1))")
                        pexpect(p, "abc")
                        pexpect(p, "2")
                    p.sendline('execx("10 |> print")')
                    pexpect(p, ["subprocess mode", "IndexError"])
                p.sendline("xontrib unload coconut")
                pexpect(p, "$")
                if (not PYPY or PY39) and PY36:
                    p.sendline("1 |> print")
                    pexpect(p, ["subprocess mode", "IndexError"])
                p.sendeof()
                if p.isalive():
                    p.terminate()

    if IPY and (not WINDOWS or PY35):
        def test_ipython_extension(self):
            call(
                ["ipython", "--ext", "coconut", "-c", r'%coconut ' + coconut_snip],
                assert_output=(True,) + (("Jupyter error",) if WINDOWS else ()),
                stderr_first=WINDOWS,
                check_errors=not WINDOWS,
                expect_retcode=0 if not WINDOWS else None,
            )

        def test_kernel_run_cell_kwargs(self):
            # newer ipykernels pass extra kwargs (cell_id, cell_meta) that older IPythons don't accept (#908)
            call_python(
                ["-c", "\n".join((
                    "from coconut.icoconut.root import CoconutShell, filter_kwargs_for",
                    "def old_run_cell(self, raw_cell, store_history=False, silent=False, shell_futures=True, cell_id=None): pass",
                    "assert filter_kwargs_for(old_run_cell, dict(cell_id=1, cell_meta=2)) == dict(cell_id=1)",
                    "assert filter_kwargs_for(lambda **kwargs: None, dict(cell_id=1, cell_meta=2)) == dict(cell_id=1, cell_meta=2)",
                    "res = CoconutShell.instance().run_cell('x = 1 |> (.+1)', cell_id='abc', cell_meta=dict(cellId='abc'))",
                    "assert res.success, res",
                    "assert CoconutShell.instance().user_ns['x'] == 2",
                    "print('<success>')",
                ))],
                assert_output="<success>",
            )

        def test_kernel_installation(self):
            assert icoconut_custom_kernel_name in list_kernel_names()
            call(["coconut", "--jupyter"], assert_output=kernel_installation_msg)
            kernels = list_kernel_names()
            for kernel in (icoconut_custom_kernel_name,) + icoconut_default_kernel_names:
                assert kernel in kernels

        if not WINDOWS and not PYPY:
            def test_jupyter_console(self):
                p = spawn_cmd("coconut --jupyter console")
                pexpect(p, "In")
                p.sendline("%load_ext coconut")
                pexpect(p, "In")
                p.sendline("`exit`")
                if sys.version_info[:2] != (3, 6):
                    pexpect(p, "Shutting down kernel|shutting down")
                if p.isalive():
                    p.terminate()


@add_test_func_names
class TestCompilation(unittest.TestCase):

    def test_simple_no_line_numbers(self):
        run_runnable(["-n", "--no-line-numbers"])

    def test_simple_keep_lines(self):
        run_runnable(["-n", "--keep-lines"])

    def test_simple_no_line_numbers_keep_lines(self):
        run_runnable(["-n", "--no-line-numbers", "--keep-lines"])

    def test_simple_minify(self):
        run_runnable(["-n", "--minify"])

    if sys.version_info >= get_target_info(get_psf_target()):
        def test_simple_psf(self):
            run_runnable(["-n", "--target", "psf"])

    def test_normal(self):
        run()

    if MYPY:
        def test_mypy_sys(self):
            run(["--mypy"] + mypy_args, agnostic_target="sys", expect_retcode=None, check_errors=False)  # fails due to tutorial mypy errors

    if sys.version_info[:2] in always_sys_versions:
        def test_always_sys(self):
            run(agnostic_target="sys", always_sys=True)

    def test_target(self):
        run(agnostic_target=(2 if PY2 else 3))

    def test_no_tco(self):
        run(["--no-tco"])

    def test_package(self):
        run(["--package"])

    # TODO: re-allow these once we figure out what's causing the strange unreproducible errors with them on py3.12
    if not PY312:
        def test_standalone(self):
            run(["--standalone"])

        if PY35:
            def test_no_wrap(self):
                run(["--no-wrap"])

    if TEST_ALL:
        if CPYTHON:
            def test_any_of(self):
                with using_env_vars({
                    adaptive_any_of_env_var: "True",
                    reverse_any_of_env_var: "True",
                }):
                    run()

        def test_strict_keep_lines(self):
            run(["--strict", "--keep-lines"])

        def test_and(self):
            run(["--and"])  # src and dest built by comp

        def test_run_arg(self):
            run(use_run_arg=True)

        def test_run_dir(self):
            run(run_directory=True)

        if not PYPY and not PY26:
            def test_jobs_zero(self):
                run(["--jobs", "0"])

        if not PYPY:
            def test_incremental(self):
                with using_caches():
                    run(manage_cache=False)
                    run(["--force"], manage_cache=False)

    if get_bool_env_var("COCONUT_TEST_VERBOSE"):
        def test_verbose(self):
            run(["--jobs", "0", "--verbose"])

    if get_bool_env_var("COCONUT_TEST_TRACE"):
        def test_trace(self):
            run(["--jobs", "0", "--trace"], check_errors=False)


if TEST_ALL:
    @add_test_func_names
    class TestExternal(unittest.TestCase):

        if not PYPY or PY2:
            def test_prelude(self):
                with using_paths(prelude):
                    comp_prelude(["--strict", "--pure"], expect_retcode=None)
                    if MYPY and PY38:
                        run_prelude()

        # def test_pyprover(self):
        #     with using_paths(pyprover):
        #         comp_pyprover()
        #         if PY38:
        #             run_pyprover()

        if PY312:  # reduce test load

            def test_bbopt(self):
                with using_paths(bbopt):
                    comp_bbopt()
                    if not PYPY and PY38 and not PY310:
                        install_bbopt()

            def test_pyston(self):
                with using_paths(pyston):
                    comp_pyston(["--no-tco"])
                    if PYPY and PY2:
                        run_pyston()

        def test_imp_issue(self):
            with using_paths(imp_issue_dir):
                if not os.path.exists(imp_issue_dir):
                    call(["git", "clone", imp_issue_git])
                with using_env_vars({"PYTHONPATH": os.pathsep.join([imp_issue_dir, os.environ.get("PYTHONPATH", "")])}):
                    call_coconut(["-r", os.path.join(imp_issue_dir, "main.coco")])


# -----------------------------------------------------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
