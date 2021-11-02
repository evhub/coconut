#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Compiles Coconut code into Python code.
"""

# Table of Contents:
#   - Imports
#   - Handlers
#   - Compiler
#   - Processors
#   - Compiler Handlers
#   - Checking Handlers
#   - Endpoints

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
from contextlib import contextmanager
from functools import partial
from collections import defaultdict
from threading import Lock

from coconut._pyparsing import (
    ParseBaseException,
    ParseResults,
    col as getcol,
    line as getline,
    lineno,
    nums,
)

from coconut.constants import (
    specific_targets,
    targets,
    pseudo_targets,
    default_encoding,
    hash_sep,
    openindent,
    closeindent,
    strwrapper,
    lnwrapper,
    unwrapper,
    holds,
    tabideal,
    match_to_args_var,
    match_to_kwargs_var,
    py3_to_py2_stdlib,
    reserved_prefix,
    function_match_error_var,
    legal_indent_chars,
    format_var,
    replwrapper,
    none_coalesce_var,
)
from coconut.util import checksum
from coconut.exceptions import (
    CoconutException,
    CoconutSyntaxError,
    CoconutParseError,
    CoconutStyleError,
    CoconutTargetError,
    CoconutInternalException,
    CoconutSyntaxWarning,
    CoconutDeferredSyntaxError,
    clean,
)
from coconut.terminal import (
    logger,
    complain,
    internal_assert,
)
from coconut.compiler.matching import Matcher
from coconut.compiler.grammar import (
    Grammar,
    lazy_list_handle,
    get_infix_items,
    pipe_info,
    attrgetter_atom_split,
    attrgetter_atom_handle,
    itemgetter_handle,
)
from coconut.compiler.util import (
    get_target_info,
    sys_target,
    addskip,
    count_end,
    paren_change,
    ind_change,
    rem_comment,
    split_comment,
    attach,
    split_leading_indent,
    split_trailing_indent,
    split_leading_trailing_indent,
    match_in,
    transform,
    parse,
    all_matches,
    get_target_info_smart,
    split_leading_comment,
    compile_regex,
    append_it,
    interleaved_join,
    handle_indentation,
    Wrap,
    tuple_str_of,
    join_args,
)
from coconut.compiler.header import (
    minify,
    getheader,
)

# end: IMPORTS
# -----------------------------------------------------------------------------------------------------------------------
# HANDLERS:
# -----------------------------------------------------------------------------------------------------------------------


def set_to_tuple(tokens):
    """Converts set literal tokens to tuples."""
    internal_assert(len(tokens) == 1, "invalid set maker tokens", tokens)
    if "comp" in tokens or "list" in tokens:
        return "(" + tokens[0] + ")"
    elif "test" in tokens:
        return "(" + tokens[0] + ",)"
    else:
        raise CoconutInternalException("invalid set maker item", tokens[0])


def import_stmt(imp_from, imp, imp_as):
    """Generate an import statement."""
    return (
        ("from " + imp_from + " " if imp_from is not None else "")
        + "import " + imp
        + (" as " + imp_as if imp_as is not None else "")
    )


def imported_names(imports):
    """Yields all the names imported by imports = [[imp1], [imp2, as], ...]."""
    for imp in imports:
        imp_name = imp[-1].split(".", 1)[0]
        if imp_name != "*":
            yield imp_name


def special_starred_import_handle(imp_all=False):
    """Handles the [from *] import * Coconut Easter egg."""
    out = handle_indentation(
        """
import imp as _coconut_imp
try:
    _coconut_norm_file = _coconut.os.path.normpath(_coconut.os.path.realpath(__file__))
    _coconut_norm_dir = _coconut.os.path.normpath(_coconut.os.path.realpath(_coconut.os.path.dirname(__file__)))
except _coconut.NameError:
    _coconut_norm_file = _coconut_norm_dir = ""
_coconut_seen_imports = set()
for _coconut_base_path in _coconut_sys.path:
    for _coconut_dirpath, _coconut_dirnames, _coconut_filenames in _coconut.os.walk(_coconut_base_path):
        _coconut_paths_to_imp = []
        for _coconut_fname in _coconut_filenames:
            if _coconut.os.path.splitext(_coconut_fname)[-1] == ".py":
                _coconut_fpath = _coconut.os.path.normpath(_coconut.os.path.realpath(_coconut.os.path.join(_coconut_dirpath, _coconut_fname)))
                if _coconut_fpath != _coconut_norm_file:
                    _coconut_paths_to_imp.append(_coconut_fpath)
        for _coconut_dname in _coconut_dirnames:
            _coconut_dpath = _coconut.os.path.normpath(_coconut.os.path.realpath(_coconut.os.path.join(_coconut_dirpath, _coconut_dname)))
            if "__init__.py" in _coconut.os.listdir(_coconut_dpath) and _coconut_dpath != _coconut_norm_dir:
                _coconut_paths_to_imp.append(_coconut_dpath)
        for _coconut_imp_path in _coconut_paths_to_imp:
            _coconut_imp_name = _coconut.os.path.splitext(_coconut.os.path.basename(_coconut_imp_path))[0]
            if _coconut_imp_name in _coconut_seen_imports:
                continue
            _coconut_seen_imports.add(_coconut_imp_name)
            _coconut.print("Importing {}...".format(_coconut_imp_name), end="", flush=True)
            try:
                descr = _coconut_imp.find_module(_coconut_imp_name, [_coconut.os.path.dirname(_coconut_imp_path)])
                _coconut_imp.load_module(_coconut_imp_name, *descr)
            except:
                _coconut.print(" Failed.")
            else:
                _coconut.print(" Imported.")
        _coconut_dirnames[:] = []
        """,
    )
    if imp_all:
        out += "\n" + handle_indentation(
            """
for _coconut_m in _coconut.tuple(_coconut_sys.modules.values()):
    _coconut_d = _coconut.getattr(_coconut_m, "__dict__", None)
    if _coconut_d is not None:
        for _coconut_k, _coconut_v in _coconut_d.items():
            if not _coconut_k.startswith("_"):
                _coconut.locals()[_coconut_k] = _coconut_v
            """,
        )
    else:
        out += "\n" + handle_indentation(
            """
for _coconut_n, _coconut_m in _coconut.tuple(_coconut_sys.modules.items()):
    _coconut.locals()[_coconut_n] = _coconut_m
            """,
        )
    return out


def split_args_list(tokens, loc):
    """Splits function definition arguments."""
    pos_only_args = []
    req_args = []
    def_args = []
    star_arg = None
    kwd_only_args = []
    dubstar_arg = None
    pos = 0
    for arg in tokens:
        if len(arg) == 1:
            if arg[0] == "*":
                # star sep (pos = 2)
                if pos >= 2:
                    raise CoconutDeferredSyntaxError("star separator at invalid position in function definition", loc)
                pos = 2
            elif arg[0] == "/":
                # slash sep (pos = 0)
                if pos > 0:
                    raise CoconutDeferredSyntaxError("slash separator at invalid position in function definition", loc)
                if pos_only_args:
                    raise CoconutDeferredSyntaxError("only one slash separator allowed in function definition", loc)
                if not req_args:
                    raise CoconutDeferredSyntaxError("slash separator must come after arguments to mark as positional-only", loc)
                pos_only_args = req_args
                req_args = []
            else:
                # pos arg (pos = 0)
                if pos == 0:
                    req_args.append(arg[0])
                # kwd only arg (pos = 2)
                elif pos == 2:
                    kwd_only_args.append((arg[0], None))
                else:
                    raise CoconutDeferredSyntaxError("non-default arguments must come first or after star argument/separator", loc)
        else:
            # only the first two components matter; if there's a third it's a typedef
            if arg[0] == "*":
                # star arg (pos = 2)
                if pos >= 2:
                    raise CoconutDeferredSyntaxError("star argument at invalid position in function definition", loc)
                pos = 2
                star_arg = arg[1]
            elif arg[0] == "**":
                # dub star arg (pos = 3)
                if pos == 3:
                    raise CoconutDeferredSyntaxError("double star argument at invalid position in function definition", loc)
                pos = 3
                dubstar_arg = arg[1]
            else:
                # def arg (pos = 1)
                if pos <= 1:
                    pos = 1
                    def_args.append((arg[0], arg[1]))
                # kwd only arg (pos = 2)
                elif pos <= 2:
                    pos = 2
                    kwd_only_args.append((arg[0], arg[1]))
                else:
                    raise CoconutDeferredSyntaxError("invalid default argument in function definition", loc)
    return pos_only_args, req_args, def_args, star_arg, kwd_only_args, dubstar_arg


# end: HANDLERS
# -----------------------------------------------------------------------------------------------------------------------
# COMPILER:
# -----------------------------------------------------------------------------------------------------------------------


class Compiler(Grammar):
    """The Coconut compiler."""
    lock = Lock()

    preprocs = [
        lambda self: self.prepare,
        lambda self: self.str_proc,
        lambda self: self.passthrough_proc,
        lambda self: self.ind_proc,
    ]
    postprocs = [
        lambda self: self.add_code_before_proc,
        lambda self: self.reind_proc,
        lambda self: self.repl_proc,
        lambda self: self.header_proc,
        lambda self: self.polish,
    ]
    replprocs = [
        lambda self: self.endline_repl,
        lambda self: self.passthrough_repl,
        lambda self: self.str_repl,
    ]

    def __init__(self, *args, **kwargs):
        """Creates a new compiler with the given parsing parameters."""
        self.setup(*args, **kwargs)

    def setup(self, target=None, strict=False, minify=False, line_numbers=False, keep_lines=False, no_tco=False, no_wrap=False):
        """Initializes parsing parameters."""
        if target is None:
            target = ""
        else:
            target = str(target).replace(".", "")
        if target == "sys":
            target = sys_target
        if target in pseudo_targets:
            target = pseudo_targets[target]
        if target not in targets:
            raise CoconutException(
                "unsupported target Python version " + repr(target),
                extra="supported targets are: " + ", ".join(repr(t) for t in specific_targets + tuple(pseudo_targets)) + ", and 'sys'",
            )
        logger.log_vars("Compiler args:", locals())
        self.target = target
        self.strict = strict
        self.minify = minify
        self.line_numbers = line_numbers
        self.keep_lines = keep_lines
        self.no_tco = no_tco
        self.no_wrap = no_wrap

    def __reduce__(self):
        """Return pickling information."""
        return (self.__class__, (self.target, self.strict, self.minify, self.line_numbers, self.keep_lines, self.no_tco, self.no_wrap))

    def __copy__(self):
        """Create a new, blank copy of the compiler."""
        cls, args = self.__reduce__()
        return cls(*args)

    copy = __copy__

    def genhash(self, code, package_level=-1):
        """Generate a hash from code."""
        reduce_args = self.__reduce__()[1]
        logger.log(
            "Hash args:", {
                "VERSION": VERSION,
                "reduce_args": reduce_args,
                "package_level": package_level,
            },
        )
        return hex(
            checksum(
                hash_sep.join(
                    str(item) for item in (
                        reduce_args
                        + (VERSION, package_level, code)
                    )
                ).encode(default_encoding),
            ),
        )

    def reset(self):
        """Resets references."""
        self.indchar = None
        self.comments = {}
        self.refs = []
        self.skips = []
        self.docstring = ""
        self.temp_var_counts = defaultdict(int)
        self.stored_matches_of = defaultdict(list)
        self.add_code_before = {}
        self.unused_imports = set()
        self.original_lines = []
        self.num_lines = 0
        self.disable_name_check = False
        self.bind()

    @contextmanager
    def inner_environment(self):
        """Set up compiler to evaluate inner expressions."""
        comments, self.comments = self.comments, {}
        skips, self.skips = self.skips, []
        docstring, self.docstring = self.docstring, ""
        original_lines, self.original_lines = self.original_lines, []
        line_numbers, self.line_numbers = self.line_numbers, False
        keep_lines, self.keep_lines = self.keep_lines, False
        num_lines, self.num_lines = self.num_lines, 0
        try:
            yield
        finally:
            self.comments = comments
            self.skips = skips
            self.docstring = docstring
            self.original_lines = original_lines
            self.line_numbers = line_numbers
            self.keep_lines = keep_lines
            self.num_lines = num_lines

    @contextmanager
    def disable_checks(self):
        """Run the block without checking names or strict errors."""
        disable_name_check, self.disable_name_check = self.disable_name_check, True
        strict, self.strict = self.strict, False
        try:
            yield
        finally:
            self.disable_name_check = disable_name_check
            self.strict = strict

    def post_transform(self, grammar, text):
        """Version of transform for post-processing."""
        with self.complain_on_err():
            with self.disable_checks():
                return transform(grammar, text)
        return None

    def get_temp_var(self, base_name="temp"):
        """Get a unique temporary variable name."""
        if self.minify:
            base_name = ""
        var_name = reserved_prefix + "_" + base_name + "_" + str(self.temp_var_counts[base_name])
        self.temp_var_counts[base_name] += 1
        return var_name

    def bind(self):
        """Binds reference objects to the proper parse actions."""
        # handle endlines, docstrings, names
        self.endline <<= attach(self.endline_ref, self.endline_handle)
        self.moduledoc_item <<= attach(self.moduledoc, self.set_moduledoc)
        self.name <<= attach(self.base_name, self.name_check)

        # comments are evaluated greedily because we need to know about them even if we're going to suppress them
        self.comment <<= attach(self.comment_ref, self.comment_handle, greedy=True)

        # handle all atom + trailers constructs with item_handle
        self.trailer_atom <<= attach(self.trailer_atom_ref, self.item_handle)
        self.no_partial_trailer_atom <<= attach(self.no_partial_trailer_atom_ref, self.item_handle)
        self.simple_assign <<= attach(self.simple_assign_ref, self.item_handle)

        # abnormally named handlers
        self.normal_pipe_expr <<= attach(self.normal_pipe_expr_tokens, self.pipe_handle)
        self.return_typedef <<= attach(self.return_typedef_ref, self.typedef_handle)

        # standard handlers of the form name <<= attach(name_tokens, name_handle) (implies name_tokens is reused)
        self.function_call <<= attach(self.function_call_tokens, self.function_call_handle)
        self.testlist_star_namedexpr <<= attach(self.testlist_star_namedexpr_tokens, self.testlist_star_expr_handle)

        # standard handlers of the form name <<= attach(name_ref, name_handle)
        self.set_literal <<= attach(self.set_literal_ref, self.set_literal_handle)
        self.set_letter_literal <<= attach(self.set_letter_literal_ref, self.set_letter_literal_handle)
        self.classdef <<= attach(self.classdef_ref, self.classdef_handle)
        self.import_stmt <<= attach(self.import_stmt_ref, self.import_handle)
        self.complex_raise_stmt <<= attach(self.complex_raise_stmt_ref, self.complex_raise_stmt_handle)
        self.augassign_stmt <<= attach(self.augassign_stmt_ref, self.augassign_stmt_handle)
        self.kwd_augassign <<= attach(self.kwd_augassign_ref, self.kwd_augassign_handle)
        self.dict_comp <<= attach(self.dict_comp_ref, self.dict_comp_handle)
        self.destructuring_stmt <<= attach(self.destructuring_stmt_ref, self.destructuring_stmt_handle)
        self.full_match <<= attach(self.full_match_ref, self.full_match_handle)
        self.name_match_funcdef <<= attach(self.name_match_funcdef_ref, self.name_match_funcdef_handle)
        self.op_match_funcdef <<= attach(self.op_match_funcdef_ref, self.op_match_funcdef_handle)
        self.yield_from <<= attach(self.yield_from_ref, self.yield_from_handle)
        self.exec_stmt <<= attach(self.exec_stmt_ref, self.exec_stmt_handle)
        self.stmt_lambdef <<= attach(self.stmt_lambdef_ref, self.stmt_lambdef_handle)
        self.typedef <<= attach(self.typedef_ref, self.typedef_handle)
        self.typedef_default <<= attach(self.typedef_default_ref, self.typedef_handle)
        self.unsafe_typedef_default <<= attach(self.unsafe_typedef_default_ref, self.unsafe_typedef_handle)
        self.typed_assign_stmt <<= attach(self.typed_assign_stmt_ref, self.typed_assign_stmt_handle)
        self.datadef <<= attach(self.datadef_ref, self.datadef_handle)
        self.match_datadef <<= attach(self.match_datadef_ref, self.match_datadef_handle)
        self.with_stmt <<= attach(self.with_stmt_ref, self.with_stmt_handle)
        self.await_item <<= attach(self.await_item_ref, self.await_item_handle)
        self.ellipsis <<= attach(self.ellipsis_ref, self.ellipsis_handle)
        self.case_stmt <<= attach(self.case_stmt_ref, self.case_stmt_handle)
        self.f_string <<= attach(self.f_string_ref, self.f_string_handle)
        self.decorators <<= attach(self.decorators_ref, self.decorators_handle)
        self.unsafe_typedef_or_expr <<= attach(self.unsafe_typedef_or_expr_ref, self.unsafe_typedef_or_expr_handle)
        self.testlist_star_expr <<= attach(self.testlist_star_expr_ref, self.testlist_star_expr_handle)
        self.list_literal <<= attach(self.list_literal_ref, self.list_literal_handle)
        self.dict_literal <<= attach(self.dict_literal_ref, self.dict_literal_handle)

        # handle normal and async function definitions
        self.decoratable_normal_funcdef_stmt <<= attach(
            self.decoratable_normal_funcdef_stmt_ref,
            self.decoratable_funcdef_stmt_handle,
        )
        self.decoratable_async_funcdef_stmt <<= attach(
            self.decoratable_async_funcdef_stmt_ref,
            partial(self.decoratable_funcdef_stmt_handle, is_async=True),
        )

        # these handlers just do strict/target checking
        self.u_string <<= attach(self.u_string_ref, self.u_string_check)
        self.matrix_at <<= attach(self.matrix_at_ref, self.matrix_at_check)
        self.nonlocal_stmt <<= attach(self.nonlocal_stmt_ref, self.nonlocal_check)
        self.star_assign_item <<= attach(self.star_assign_item_ref, self.star_assign_item_check)
        self.classic_lambdef <<= attach(self.classic_lambdef_ref, self.lambdef_check)
        self.star_sep_arg <<= attach(self.star_sep_arg_ref, self.star_sep_check)
        self.star_sep_vararg <<= attach(self.star_sep_vararg_ref, self.star_sep_check)
        self.slash_sep_arg <<= attach(self.slash_sep_arg_ref, self.slash_sep_check)
        self.slash_sep_vararg <<= attach(self.slash_sep_vararg_ref, self.slash_sep_check)
        self.endline_semicolon <<= attach(self.endline_semicolon_ref, self.endline_semicolon_check)
        self.async_stmt <<= attach(self.async_stmt_ref, self.async_stmt_check)
        self.async_comp_for <<= attach(self.async_comp_for_ref, self.async_comp_check)
        self.namedexpr <<= attach(self.namedexpr_ref, self.namedexpr_check)
        self.new_namedexpr <<= attach(self.new_namedexpr_ref, self.new_namedexpr_check)
        self.match_dotted_name_const <<= attach(self.match_dotted_name_const_ref, self.match_dotted_name_const_check)
        self.except_star_clause <<= attach(self.except_star_clause_ref, self.except_star_clause_check)
        self.match_check_equals <<= attach(self.match_check_equals_ref, self.match_check_equals_check)

    def copy_skips(self):
        """Copy the line skips."""
        return self.skips[:]

    def set_skips(self, skips):
        """Set the line skips."""
        skips.sort()
        internal_assert(lambda: len(set(skips)) == len(skips), "duplicate line skip(s) in skips", skips)
        self.skips = skips

    def adjust(self, ln, skips=None):
        """Converts a parsing line number into an original line number."""
        if skips is None:
            skips = self.skips
        adj_ln = ln
        need_unskipped = 0
        for i in skips:
            if i <= ln:
                need_unskipped += 1
            elif adj_ln + need_unskipped < i:
                break
            else:
                need_unskipped -= i - adj_ln - 1
                adj_ln = i
        return adj_ln + need_unskipped

    def reformat(self, snip, index=None):
        """Post process a preprocessed snippet."""
        if index is None:
            with self.complain_on_err():
                return self.repl_proc(snip, reformatting=True, log=False)
            return snip
        else:
            return self.reformat(snip), len(self.reformat(snip[:index]))

    def eval_now(self, code):
        """Reformat and evaluate a code snippet and return code for the result."""
        result = eval(self.reformat(code), {})
        if result is None or isinstance(result, (bool, int, float, complex)):
            return ascii(result)
        elif isinstance(result, bytes):
            return "b" + self.wrap_str_of(result)
        elif isinstance(result, str):
            return self.wrap_str_of(result)
        else:
            return None

    def make_err(self, errtype, message, original, loc, ln=None, line=None, col=None, reformat=True, *args, **kwargs):
        """Generate an error of the specified type."""
        if ln is None:
            ln = self.adjust(lineno(loc, original))
        if line is None:
            line = getline(loc, original)
        if col is None:
            col = getcol(loc, original)
        errstr, index = line, col - 1
        if reformat:
            errstr, index = self.reformat(errstr, index)
        return errtype(message, errstr, index, ln, *args, **kwargs)

    def strict_err_or_warn(self, *args, **kwargs):
        """Raises an error if in strict mode, otherwise raises a warning."""
        if self.strict:
            raise self.make_err(CoconutStyleError, *args, **kwargs)
        else:
            logger.warn_err(self.make_err(CoconutSyntaxWarning, *args, **kwargs))

    @contextmanager
    def complain_on_err(self):
        """Complain about any parsing-related errors raised inside."""
        try:
            yield
        except ParseBaseException as err:
            complain(self.make_parse_err(err, reformat=False, include_ln=False))
        except CoconutException as err:
            complain(err)

    def remove_strs(self, inputstring):
        """Remove strings/comments from the given input."""
        with self.complain_on_err():
            return self.str_proc(inputstring)
        return inputstring

    def get_matcher(self, original, loc, check_var, style=None, name_list=None):
        """Get a Matcher object."""
        if style is None:
            style = "coconut"
        return Matcher(self, original, loc, check_var, style=style, name_list=name_list)

    def add_ref(self, reftype, data):
        """Add a reference and return the identifier."""
        ref = (reftype, data)
        try:
            index = self.refs.index(ref)
        except ValueError:
            self.refs.append(ref)
            index = len(self.refs) - 1
        return str(index)

    def get_ref(self, reftype, index):
        """Retrieve a reference."""
        try:
            got_reftype, data = self.refs[int(index)]
        except (IndexError, ValueError):
            raise CoconutInternalException("no reference at invalid index", index)
        internal_assert(got_reftype == reftype, "wanted " + reftype + " reference; got " + got_reftype + " reference")
        return data

    def wrap_str(self, text, strchar, multiline=False):
        """Wrap a string."""
        if multiline:
            strchar *= 3
        return strwrapper + self.add_ref("str", (text, strchar)) + unwrapper

    def wrap_str_of(self, text):
        """Wrap a string of a string."""
        text_repr = ascii(text)
        internal_assert(text_repr[0] == text_repr[-1] and text_repr[0] in ("'", '"'), "cannot wrap str of", text)
        return self.wrap_str(text_repr[1:-1], text_repr[-1])

    def wrap_passthrough(self, text, multiline=True):
        """Wrap a passthrough."""
        if not multiline:
            text = text.lstrip()
        if multiline:
            out = "\\"
        else:
            out = "\\\\"
        out += self.add_ref("passthrough", text) + unwrapper
        if not multiline:
            out += "\n"
        return out

    def wrap_comment(self, text, reformat=True):
        """Wrap a comment."""
        if reformat:
            text = self.reformat(text)
        return "#" + self.add_ref("comment", text) + unwrapper

    def wrap_line_number(self, ln):
        """Wrap a line number."""
        return "#" + self.add_ref("ln", ln) + lnwrapper

    def apply_procs(self, procs, kwargs, inputstring, log=True):
        """Apply processors to inputstring."""
        for get_proc in procs:
            proc = get_proc(self)
            inputstring = proc(inputstring, **kwargs)
            if log:
                logger.log_tag(proc.__name__, inputstring, multiline=True)
        return inputstring

    def pre(self, inputstring, **kwargs):
        """Perform pre-processing."""
        out = self.apply_procs(self.preprocs, kwargs, str(inputstring))
        logger.log_tag("skips", self.skips)
        return out

    def post(self, result, **kwargs):
        """Perform post-processing."""
        internal_assert(isinstance(result, str), "got non-string parse result", result)
        return self.apply_procs(self.postprocs, kwargs, result)

    def getheader(self, which, use_hash=None, polish=True):
        """Get a formatted header."""
        header = getheader(
            which,
            target=self.target,
            use_hash=use_hash,
            no_tco=self.no_tco,
            strict=self.strict,
            no_wrap=self.no_wrap,
        )
        if polish:
            header = self.polish(header)
        return header

    @property
    def target_info(self):
        """Return information on the current target as a version tuple."""
        return get_target_info(self.target)

    def make_syntax_err(self, err, original):
        """Make a CoconutSyntaxError from a CoconutDeferredSyntaxError."""
        msg, loc = err.args
        return self.make_err(CoconutSyntaxError, msg, original, loc)

    def make_parse_err(self, err, reformat=True, include_ln=True, msg=None):
        """Make a CoconutParseError from a ParseBaseException."""
        err_line = err.line
        err_index = err.col - 1
        err_lineno = err.lineno if include_ln else None

        causes = []
        for cause, _, _ in all_matches(self.parse_err_msg, err_line[err_index:]):
            causes.append(cause)
        if causes:
            extra = "possible cause{s}: {causes}".format(
                s="s" if len(causes) > 1 else "",
                causes=", ".join(causes),
            )
        else:
            extra = None

        if reformat:
            err_line, err_index = self.reformat(err_line, err_index)
            if err_lineno is not None:
                err_lineno = self.adjust(err_lineno)

        return CoconutParseError(msg, err_line, err_index, err_lineno, extra)

    def inner_parse_eval(
        self,
        inputstring,
        parser=None,
        preargs={"strip": True},
        postargs={"header": "none", "initial": "none", "final_endline": False},
    ):
        """Parse eval code in an inner environment."""
        if parser is None:
            parser = self.eval_parser
        with self.inner_environment():
            pre_procd = self.pre(inputstring, **preargs)
            parsed = parse(parser, pre_procd)
            return self.post(parsed, **postargs)

    @contextmanager
    def parsing(self):
        """Acquire the lock and reset the parser."""
        with self.lock:
            self.reset()
            yield

    def parse(self, inputstring, parser, preargs, postargs):
        """Use the parser to parse the inputstring with appropriate setup and teardown."""
        with self.parsing():
            with logger.gather_parsing_stats():
                pre_procd = None
                try:
                    pre_procd = self.pre(inputstring, **preargs)
                    parsed = parse(parser, pre_procd)
                    out = self.post(parsed, **postargs)
                except ParseBaseException as err:
                    raise self.make_parse_err(err)
                except CoconutDeferredSyntaxError as err:
                    internal_assert(pre_procd is not None, "invalid deferred syntax error in pre-processing", err)
                    raise self.make_syntax_err(err, pre_procd)
                except RuntimeError as err:
                    raise CoconutException(
                        str(err), extra="try again with --recursion-limit greater than the current "
                        + str(sys.getrecursionlimit()),
                    )
        if self.strict:
            for name in self.unused_imports:
                logger.warn("found unused import", name, extra="remove --strict to dismiss")
        return out

    def replace_matches_of_inside(self, name, elem, *items):
        """Replace all matches of elem inside of items and include the
        replacements in the resulting matches of items. Requires elem
        to only match a single string.

        Returns (new version of elem, *modified items)."""
        @contextmanager
        def manage_item(wrapper, instring, loc):
            self.stored_matches_of[name].append([])
            try:
                yield
            finally:
                self.stored_matches_of[name].pop()

        def handle_item(tokens):
            if isinstance(tokens, ParseResults) and len(tokens) == 1:
                tokens = tokens[0]
            return (self.stored_matches_of[name][-1], tokens)

        handle_item.__name__ = "handle_wrapping_" + name

        def handle_elem(tokens):
            internal_assert(len(tokens) == 1, "invalid elem tokens in replace_matches_of_inside", tokens)
            if self.stored_matches_of[name]:
                ref = self.add_ref("repl", tokens[0])
                self.stored_matches_of[name][-1].append(ref)
                return replwrapper + ref + unwrapper
            else:
                return tokens[0]

        handle_elem.__name__ = "handle_" + name

        yield attach(elem, handle_elem)

        for item in items:
            yield Wrap(attach(item, handle_item, greedy=True), manage_item)

    def replace_replaced_matches(self, to_repl_str, ref_to_replacement):
        """Replace refs in str generated by replace_matches_of_inside."""
        out = to_repl_str
        for ref, repl in ref_to_replacement.items():
            out = out.replace(replwrapper + ref + unwrapper, repl)
        return out

# end: COMPILER
# -----------------------------------------------------------------------------------------------------------------------
# PROCESSORS:
# -----------------------------------------------------------------------------------------------------------------------

    def prepare(self, inputstring, strip=False, nl_at_eof_check=False, **kwargs):
        """Prepare a string for processing."""
        if self.strict and nl_at_eof_check and inputstring and not inputstring.endswith("\n"):
            end_index = len(inputstring) - 1 if inputstring else 0
            raise self.make_err(CoconutStyleError, "missing new line at end of file", inputstring, end_index)
        original_lines = inputstring.splitlines()
        self.num_lines = len(original_lines)
        if self.keep_lines:
            self.original_lines = original_lines
        inputstring = "\n".join(original_lines)
        if strip:
            inputstring = inputstring.strip()
        return inputstring

    def str_proc(self, inputstring, **kwargs):
        """Process strings and comments."""
        out = []
        found = None  # store of characters that might be the start of a string
        hold = None
        # hold = [_comment]:
        _comment = 0  # the contents of the comment so far
        # hold = [_contents, _start, _stop]:
        _contents = 0  # the contents of the string so far
        _start = 1  # the string of characters that started the string
        _stop = 2  # store of characters that might be the end of the string
        skips = self.copy_skips()

        x = 0
        while x <= len(inputstring):
            try:
                c = inputstring[x]
            except IndexError:
                internal_assert(x == len(inputstring), "invalid index in str_proc", x)
                c = "\n"

            if hold is not None:
                if len(hold) == 1:  # hold == [_comment]
                    if c == "\n":
                        if self.minify:
                            if out:
                                lines = "".join(out).splitlines()
                                lines[-1] = lines[-1].rstrip()
                                out = ["\n".join(lines)]
                            out.append(c)
                        else:
                            out.append(self.wrap_comment(hold[_comment], reformat=False) + c)
                        hold = None
                    else:
                        hold[_comment] += c
                elif hold[_stop] is not None:
                    if c == "\\":
                        hold[_contents] += hold[_stop] + c
                        hold[_stop] = None
                    elif c == hold[_start][0]:
                        hold[_stop] += c
                    elif len(hold[_stop]) > len(hold[_start]):
                        raise self.make_err(CoconutSyntaxError, "invalid number of string closes", inputstring, x, reformat=False)
                    elif hold[_stop] == hold[_start]:
                        out.append(self.wrap_str(hold[_contents], hold[_start][0], True))
                        hold = None
                        x -= 1
                    else:
                        if c == "\n":
                            if len(hold[_start]) == 1:
                                raise self.make_err(CoconutSyntaxError, "linebreak in non-multiline string", inputstring, x, reformat=False)
                            skips = addskip(skips, self.adjust(lineno(x, inputstring)))
                        hold[_contents] += hold[_stop] + c
                        hold[_stop] = None
                elif count_end(hold[_contents], "\\") % 2 == 1:
                    if c == "\n":
                        skips = addskip(skips, self.adjust(lineno(x, inputstring)))
                    hold[_contents] += c
                elif c == hold[_start]:
                    out.append(self.wrap_str(hold[_contents], hold[_start], False))
                    hold = None
                elif c == hold[_start][0]:
                    hold[_stop] = c
                else:
                    if c == "\n":
                        if len(hold[_start]) == 1:
                            raise self.make_err(CoconutSyntaxError, "linebreak in non-multiline string", inputstring, x, reformat=False)
                        skips = addskip(skips, self.adjust(lineno(x, inputstring)))
                    hold[_contents] += c
            elif found is not None:
                if c == found[0]:
                    found += c
                elif len(found) == 1:  # found == "_"
                    if c == "\n":
                        raise self.make_err(CoconutSyntaxError, "linebreak in non-multiline string", inputstring, x, reformat=False)
                    hold = [c, found, None]  # [_contents, _start, _stop]
                    found = None
                elif len(found) == 2:  # found == "__"
                    out.append(self.wrap_str("", found[0], False))
                    found = None
                    x -= 1
                elif len(found) == 3:  # found == "___"
                    if c == "\n":
                        skips = addskip(skips, self.adjust(lineno(x, inputstring)))
                    hold = [c, found, None]  # [_contents, _start, _stop]
                    found = None
                else:
                    raise self.make_err(CoconutSyntaxError, "invalid number of string starts", inputstring, x, reformat=False)
            elif c == "#":
                hold = [""]  # [_comment]
            elif c in holds:
                found = c
            else:
                out.append(c)
            x += 1

        if hold is not None or found is not None:
            raise self.make_err(CoconutSyntaxError, "unclosed string", inputstring, x, reformat=False)
        else:
            self.set_skips(skips)
            return "".join(out)

    def passthrough_proc(self, inputstring, **kwargs):
        """Process python passthroughs."""
        out = []
        found = None  # store of characters that might be the start of a passthrough
        hold = None  # the contents of the passthrough so far
        count = None  # current parenthetical level (num closes - num opens)
        multiline = None  # if in a passthrough, is it a multiline passthrough
        skips = self.copy_skips()

        for i, c in enumerate(append_it(inputstring, "\n")):
            if hold is not None:
                # we specify that we only care about parens, not brackets or braces
                count += paren_change(c, opens="(", closes=")")
                if count >= 0 and c == hold:
                    out.append(self.wrap_passthrough(found, multiline))
                    found = None
                    hold = None
                    count = None
                    multiline = None
                else:
                    if c == "\n":
                        skips = addskip(skips, self.adjust(lineno(i, inputstring)))
                    found += c
            elif found:
                if c == "\\":
                    found = ""
                    hold = "\n"
                    count = 0
                    multiline = False
                elif c == "(":
                    found = ""
                    hold = ")"
                    count = -1
                    multiline = True
                else:
                    out.append("\\" + c)
                    found = None
            elif c == "\\":
                found = True
            else:
                out.append(c)

        if hold is not None or found is not None:
            raise self.make_err(CoconutSyntaxError, "unclosed passthrough", inputstring, i)

        self.set_skips(skips)
        return "".join(out)

    def leading_whitespace(self, inputstring):
        """Get leading whitespace."""
        leading_ws = []
        for i, c in enumerate(inputstring):
            if c in legal_indent_chars:
                leading_ws.append(c)
            else:
                break
            if self.indchar is None:
                self.indchar = c
            elif c != self.indchar:
                self.strict_err_or_warn("found mixing of tabs and spaces", inputstring, i)
        return "".join(leading_ws)

    def ind_proc(self, inputstring, **kwargs):
        """Process indentation."""
        lines = inputstring.splitlines()
        new = []  # new lines
        opens = []  # (line, col, adjusted ln) at which open parens were seen, newest first
        current = None  # indentation level of previous line
        levels = []  # indentation levels of all previous blocks, newest at end
        skips = self.copy_skips()

        for ln in range(1, len(lines) + 1):  # ln is 1-indexed
            line = lines[ln - 1]  # lines is 0-indexed
            line_rstrip = line.rstrip()
            if line != line_rstrip:
                if self.strict:
                    raise self.make_err(CoconutStyleError, "found trailing whitespace", line, len(line), self.adjust(ln))
                line = line_rstrip
            last = rem_comment(new[-1]) if new else None

            if not line or line.lstrip().startswith("#"):  # blank line or comment
                if opens:  # inside parens
                    skips = addskip(skips, self.adjust(ln))
                else:
                    new.append(line)
            elif last is not None and last.endswith("\\"):  # backslash line continuation
                if self.strict:
                    raise self.make_err(CoconutStyleError, "found backslash continuation", last, len(last), self.adjust(ln - 1))
                skips = addskip(skips, self.adjust(ln))
                new[-1] = last[:-1] + " " + line
            elif opens:  # inside parens
                skips = addskip(skips, self.adjust(ln))
                new[-1] = last + " " + line
            else:
                check = self.leading_whitespace(line)
                if current is None:
                    if check:
                        raise self.make_err(CoconutSyntaxError, "illegal initial indent", line, 0, self.adjust(ln))
                    else:
                        current = ""
                elif current == check:
                    pass
                elif check in levels:  # dedent
                    point = levels.index(check) + 1
                    line = closeindent * (len(levels[point:]) + 1) + line
                    levels = levels[:point]
                    current = levels.pop()
                elif check.startswith(current):  # indent, since current != check
                    levels.append(current)
                    current = check
                    line = openindent + line
                else:
                    raise self.make_err(CoconutSyntaxError, "illegal dedent to unused indentation level", line, 0, self.adjust(ln))
                new.append(line)

            count = paren_change(line)  # num closes - num opens
            if count > len(opens):
                raise self.make_err(CoconutSyntaxError, "unmatched close parenthesis", new[-1], 0, self.adjust(len(new)))
            elif count > 0:  # closes > opens
                for _ in range(count):
                    opens.pop()
            elif count < 0:  # opens > closes
                opens += [(new[-1], self.adjust(len(new)))] * (-count)

        self.set_skips(skips)
        if new:
            last = rem_comment(new[-1])
            if last.endswith("\\"):
                raise self.make_err(CoconutSyntaxError, "illegal final backslash continuation", new[-1], len(new[-1]), self.adjust(len(new)))
            if opens:
                line, adj_ln = opens[0]
                raise self.make_err(CoconutSyntaxError, "unclosed open parenthesis", line, 0, adj_ln)
        new.append(closeindent * len(levels))
        return "\n".join(new)

    def add_code_before_proc(self, inputstring, **kwargs):
        """Add definitions for names in self.add_code_before."""
        regexes = {}
        for name in self.add_code_before:
            regexes[name] = compile_regex(r"\b%s\b" % (name,))
        out = []
        for line in inputstring.splitlines():
            for name, regex in regexes.items():
                if regex.search(line):
                    indent, line = split_leading_indent(line)
                    out.append(indent + self.add_code_before[name])
            out.append(line)
        return "\n".join(out)

    @property
    def tabideal(self):
        """Local tabideal."""
        return 1 if self.minify else tabideal

    def reind_proc(self, inputstring, **kwargs):
        """Add back indentation."""
        out = []
        level = 0

        for line in inputstring.splitlines():
            line, comment = split_comment(line.strip())

            indent, line = split_leading_indent(line)
            level += ind_change(indent)

            if line:
                line = " " * self.tabideal * level + line

            line, indent = split_trailing_indent(line)
            level += ind_change(indent)

            line = (line + comment).rstrip()
            out.append(line)

        if level != 0:
            complain(CoconutInternalException("non-zero final indentation level", level))
        return "\n".join(out)

    def ln_comment(self, ln):
        """Get an end line comment."""
        # CoconutInternalExceptions should always be caught and complained here
        if self.keep_lines:
            if not 1 <= ln <= len(self.original_lines) + 2:
                complain(
                    CoconutInternalException(
                        "out of bounds line number", ln,
                        "not in range [1, " + str(len(self.original_lines) + 2) + "]",
                    ),
                )
            if ln >= len(self.original_lines) + 1:  # trim too large
                lni = -1
            else:
                lni = ln - 1
        if self.line_numbers and self.keep_lines:
            if self.minify:
                comment = str(ln) + " " + self.original_lines[lni]
            else:
                comment = str(ln) + ": " + self.original_lines[lni]
        elif self.keep_lines:
            if self.minify:
                comment = self.original_lines[lni]
            else:
                comment = " " + self.original_lines[lni]
        elif self.line_numbers:
            if self.minify:
                comment = str(ln)
            else:
                comment = str(ln) + " (line num in coconut source)"
        else:
            return ""
        return self.wrap_comment(comment, reformat=False)

    def endline_repl(self, inputstring, reformatting=False, **kwargs):
        """Add end of line comments."""
        out = []
        ln = 1  # line number
        for line in inputstring.splitlines():
            add_one_to_ln = False
            try:
                has_ln_comment = line.endswith(lnwrapper)
                if has_ln_comment:
                    line, index = line[:-1].rsplit("#", 1)
                    new_ln = self.get_ref("ln", index)
                    if new_ln < ln:
                        raise CoconutInternalException("line number decreased", (ln, new_ln))
                    ln = new_ln
                    line = line.rstrip()
                    add_one_to_ln = True
                if not reformatting or has_ln_comment:
                    line += self.comments.get(ln, "")
                if not reformatting and line.rstrip() and not line.lstrip().startswith("#"):
                    line += self.ln_comment(ln)
            except CoconutInternalException as err:
                complain(err)
            out.append(line)
            if add_one_to_ln and ln <= self.num_lines - 1:
                ln += 1
        return "\n".join(out)

    def passthrough_repl(self, inputstring, **kwargs):
        """Add back passthroughs."""
        out = []
        index = None
        for c in append_it(inputstring, None):
            try:

                if index is not None:
                    if c is not None and c in nums:
                        index += c
                    elif c == unwrapper and index:
                        ref = self.get_ref("passthrough", index)
                        out.append(ref)
                        index = None
                    elif c != "\\" or index:
                        out.append("\\" + index)
                        if c is not None:
                            out.append(c)
                        index = None
                elif c is not None:
                    if c == "\\":
                        index = ""
                    else:
                        out.append(c)

            except CoconutInternalException as err:
                complain(err)
                if index is not None:
                    out.append(index)
                    index = None
                out.append(c)

        return "".join(out)

    def str_repl(self, inputstring, **kwargs):
        """Add back strings."""
        out = []
        comment = None
        string = None

        for i, c in enumerate(append_it(inputstring, None)):
            try:

                if comment is not None:
                    if c is not None and c in nums:
                        comment += c
                    elif c == unwrapper and comment:
                        ref = self.get_ref("comment", comment)
                        if out and not out[-1].endswith("\n"):
                            out[-1] = out[-1].rstrip(" ")
                            if not self.minify:
                                out[-1] += "  "  # put two spaces before comment
                        out.append("#" + ref)
                        comment = None
                    else:
                        raise CoconutInternalException("invalid comment marker in", getline(i, inputstring))
                elif string is not None:
                    if c is not None and c in nums:
                        string += c
                    elif c == unwrapper and string:
                        text, strchar = self.get_ref("str", string)
                        out.append(strchar + text + strchar)
                        string = None
                    else:
                        raise CoconutInternalException("invalid string marker in", getline(i, inputstring))
                elif c is not None:
                    if c == "#":
                        comment = ""
                    elif c == strwrapper:
                        string = ""
                    else:
                        out.append(c)

            except CoconutInternalException as err:
                complain(err)
                if comment is not None:
                    out.append(comment)
                    comment = None
                if string is not None:
                    out.append(string)
                    string = None
                out.append(c)

        return "".join(out)

    def repl_proc(self, inputstring, log=True, **kwargs):
        """Process using replprocs."""
        return self.apply_procs(self.replprocs, kwargs, inputstring, log=log)

    def header_proc(self, inputstring, header="file", initial="initial", use_hash=None, **kwargs):
        """Add the header."""
        pre_header = self.getheader(initial, use_hash=use_hash, polish=False)
        main_header = self.getheader(header, polish=False)
        if self.minify:
            main_header = minify(main_header)
        return pre_header + self.docstring + main_header + inputstring

    def polish(self, inputstring, final_endline=True, **kwargs):
        """Does final polishing touches."""
        return inputstring.rstrip() + ("\n" if final_endline else "")

# end: PROCESSORS
# -----------------------------------------------------------------------------------------------------------------------
# COMPILER HANDLERS:
# -----------------------------------------------------------------------------------------------------------------------

    def split_function_call(self, tokens, loc):
        """Split into positional arguments and keyword arguments."""
        pos_args = []
        star_args = []
        kwd_args = []
        dubstar_args = []
        for arg in tokens:
            argstr = "".join(arg)
            if len(arg) == 1:
                if star_args or kwd_args or dubstar_args:
                    raise CoconutDeferredSyntaxError("positional arguments must come first", loc)
                pos_args.append(argstr)
            elif len(arg) == 2:
                if arg[0] == "*":
                    if kwd_args or dubstar_args:
                        raise CoconutDeferredSyntaxError("star unpacking must come before keyword arguments", loc)
                    star_args.append(argstr)
                elif arg[0] == "**":
                    dubstar_args.append(argstr)
                else:
                    kwd_args.append(argstr)
            else:
                raise CoconutInternalException("invalid function call argument", arg)

        # universalize multiple unpackings
        if self.target_info < (3, 5):
            if len(star_args) > 1:
                star_args = ["*_coconut.itertools.chain(" + ", ".join(arg.lstrip("*") for arg in star_args) + ")"]
            if len(dubstar_args) > 1:
                dubstar_args = ["**_coconut_dict_merge(" + ", ".join(arg.lstrip("*") for arg in dubstar_args) + ", for_func=True)"]

        return pos_args, star_args, kwd_args, dubstar_args

    def function_call_handle(self, loc, tokens):
        """Enforce properly ordered function parameters."""
        return "(" + join_args(*self.split_function_call(tokens, loc)) + ")"

    def pipe_item_split(self, tokens, loc):
        """Process a pipe item, which could be a partial, an attribute access, a method call, or an expression.
        Return (type, split) where split is
            - (expr,) for expression,
            - (func, pos_args, kwd_args) for partial,
            - (name, args) for attr/method, and
            - (op, args)+ for itemgetter."""
        # list implies artificial tokens, which must be expr
        if isinstance(tokens, list) or "expr" in tokens:
            internal_assert(len(tokens) == 1, "invalid expr pipe item tokens", tokens)
            return "expr", tokens
        elif "partial" in tokens:
            func, args = tokens
            pos_args, star_args, kwd_args, dubstar_args = self.split_function_call(args, loc)
            return "partial", (func, join_args(pos_args, star_args), join_args(kwd_args, dubstar_args))
        elif "attrgetter" in tokens:
            name, args = attrgetter_atom_split(tokens)
            return "attrgetter", (name, args)
        elif "itemgetter" in tokens:
            internal_assert(len(tokens) >= 2, "invalid itemgetter pipe item tokens", tokens)
            return "itemgetter", tokens
        else:
            raise CoconutInternalException("invalid pipe item tokens", tokens)

    def pipe_handle(self, loc, tokens, **kwargs):
        """Process pipe calls."""
        internal_assert(set(kwargs) <= set(("top",)), "unknown pipe_handle keyword arguments", kwargs)
        top = kwargs.get("top", True)
        if len(tokens) == 1:
            item = tokens.pop()
            if not top:  # defer to other pipe_handle call
                return item

            # we've only been given one operand, so we can't do any optimization, so just produce the standard object
            name, split_item = self.pipe_item_split(item, loc)
            if name == "expr":
                internal_assert(len(split_item) == 1)
                return split_item[0]
            elif name == "partial":
                internal_assert(len(split_item) == 3)
                return "_coconut.functools.partial(" + join_args(split_item) + ")"
            elif name == "attrgetter":
                return attrgetter_atom_handle(loc, item)
            elif name == "itemgetter":
                return itemgetter_handle(item)
            else:
                raise CoconutInternalException("invalid split pipe item", split_item)

        else:
            item, op = tokens.pop(), tokens.pop()
            direction, stars, none_aware = pipe_info(op)
            star_str = "*" * stars

            if direction == "backwards":
                # for backwards pipes, we just reuse the machinery for forwards pipes
                inner_item = self.pipe_handle(loc, tokens, top=False)
                if isinstance(inner_item, str):
                    inner_item = [inner_item]  # artificial pipe item
                return self.pipe_handle(loc, [item, "|" + ("?" if none_aware else "") + star_str + ">", inner_item])

            elif none_aware:
                # for none_aware forward pipes, we wrap the normal forward pipe in a lambda
                pipe_expr = self.pipe_handle(loc, [[none_coalesce_var], "|" + star_str + ">", item])
                # := changes meaning inside lambdas, so we must disallow it when wrapping
                #  user expressions in lambdas (and naive string analysis is safe here)
                if ":=" in pipe_expr:
                    raise CoconutDeferredSyntaxError("illegal assignment expression in a None-coalescing pipe", loc)
                return "(lambda {x}: None if {x} is None else {pipe})({subexpr})".format(
                    x=none_coalesce_var,
                    pipe=pipe_expr,
                    subexpr=self.pipe_handle(loc, tokens),
                )

            elif direction == "forwards":
                # if this is an implicit partial, we have something to apply it to, so optimize it
                name, split_item = self.pipe_item_split(item, loc)
                subexpr = self.pipe_handle(loc, tokens)

                if name == "expr":
                    func, = split_item
                    return "({f})({stars}{x})".format(f=func, stars=star_str, x=subexpr)
                elif name == "partial":
                    func, partial_args, partial_kwargs = split_item
                    return "({f})({args})".format(f=func, args=join_args((partial_args, star_str + subexpr, partial_kwargs)))
                elif name == "attrgetter":
                    attr, method_args = split_item
                    call = "(" + method_args + ")" if method_args is not None else ""
                    if stars:
                        raise CoconutDeferredSyntaxError("cannot star pipe into attribute access or method call", loc)
                    return "({x}).{attr}{call}".format(x=subexpr, attr=attr, call=call)
                elif name == "itemgetter":
                    if stars:
                        raise CoconutDeferredSyntaxError("cannot star pipe into item getting", loc)
                    internal_assert(len(split_item) % 2 == 0, "invalid itemgetter pipe tokens", split_item)
                    out = subexpr
                    for i in range(0, len(split_item), 2):
                        op, args = split_item[i:i + 2]
                        if op == "[":
                            fmtstr = "({x})[{args}]"
                        elif op == "$[":
                            fmtstr = "_coconut_igetitem({x}, ({args}))"
                        else:
                            raise CoconutInternalException("pipe into invalid implicit itemgetter operation", op)
                        out = fmtstr.format(x=out, args=args)
                    return out
                else:
                    raise CoconutInternalException("invalid split pipe item", split_item)

            else:
                raise CoconutInternalException("invalid pipe operator direction", direction)

    def item_handle(self, loc, tokens):
        """Process trailers."""
        out = tokens.pop(0)
        for i, trailer in enumerate(tokens):
            if isinstance(trailer, str):
                out += trailer
            elif len(trailer) == 1:
                if trailer[0] == "$[]":
                    out = "_coconut.functools.partial(_coconut_igetitem, " + out + ")"
                elif trailer[0] == "$":
                    out = "_coconut.functools.partial(_coconut.functools.partial, " + out + ")"
                elif trailer[0] == "[]":
                    out = "_coconut.functools.partial(_coconut.operator.getitem, " + out + ")"
                elif trailer[0] == ".":
                    out = "_coconut.functools.partial(_coconut.getattr, " + out + ")"
                elif trailer[0] == "type:[]":
                    out = "_coconut.typing.Sequence[" + out + "]"
                elif trailer[0] == "type:$[]":
                    out = "_coconut.typing.Iterable[" + out + "]"
                elif trailer[0] == "type:?":
                    out = "_coconut.typing.Optional[" + out + "]"
                elif trailer[0] == "?":
                    # short-circuit the rest of the evaluation
                    rest_of_trailers = tokens[i + 1:]
                    if len(rest_of_trailers) == 0:
                        raise CoconutDeferredSyntaxError("None-coalescing '?' must have something after it", loc)
                    not_none_tokens = [none_coalesce_var]
                    not_none_tokens.extend(rest_of_trailers)
                    not_none_expr = self.item_handle(loc, not_none_tokens)
                    # := changes meaning inside lambdas, so we must disallow it when wrapping
                    #  user expressions in lambdas (and naive string analysis is safe here)
                    if ":=" in not_none_expr:
                        raise CoconutDeferredSyntaxError("illegal assignment expression after a None-coalescing '?'", loc)
                    return "(lambda {x}: None if {x} is None else {rest})({inp})".format(
                        x=none_coalesce_var,
                        rest=not_none_expr,
                        inp=out,
                    )
                else:
                    raise CoconutInternalException("invalid trailer symbol", trailer[0])
            elif len(trailer) == 2:
                if trailer[0] == "$[":
                    out = "_coconut_igetitem(" + out + ", " + trailer[1] + ")"
                elif trailer[0] == "$(":
                    args = trailer[1][1:-1]
                    if not args:
                        raise CoconutDeferredSyntaxError("a partial application argument is required", loc)
                    out = "_coconut.functools.partial(" + out + ", " + args + ")"
                elif trailer[0] == "$[":
                    out = "_coconut_igetitem(" + out + ", " + trailer[1] + ")"
                elif trailer[0] == "$(?":
                    pos_args, star_args, kwd_args, dubstar_args = self.split_function_call(trailer[1], loc)
                    extra_args_str = join_args(star_args, kwd_args, dubstar_args)
                    argdict_pairs = []
                    has_question_mark = False
                    for i, arg in enumerate(pos_args):
                        if arg == "?":
                            has_question_mark = True
                        else:
                            argdict_pairs.append(str(i) + ": " + arg)
                    if not has_question_mark:
                        raise CoconutInternalException("no question mark in question mark partial", trailer[1])
                    elif argdict_pairs or extra_args_str:
                        out = (
                            "_coconut_partial("
                            + out
                            + ", {" + ", ".join(argdict_pairs) + "}"
                            + ", " + str(len(pos_args))
                            + (", " if extra_args_str else "") + extra_args_str
                            + ")"
                        )
                    else:
                        raise CoconutDeferredSyntaxError("a non-? partial application argument is required", loc)
                else:
                    raise CoconutInternalException("invalid special trailer", trailer[0])
            else:
                raise CoconutInternalException("invalid trailer tokens", trailer)
        return out

    item_handle.ignore_one_token = True

    def set_moduledoc(self, tokens):
        """Set the docstring."""
        internal_assert(len(tokens) == 2, "invalid moduledoc tokens", tokens)
        self.docstring = self.reformat(tokens[0]) + "\n\n"
        return tokens[1]

    def yield_from_handle(self, tokens):
        """Process Python 3.3 yield from."""
        internal_assert(len(tokens) == 1, "invalid yield from tokens", tokens)
        if self.target_info < (3, 3):
            ret_val_name = self.get_temp_var("yield_from")
            self.add_code_before[ret_val_name] = handle_indentation(
                '''
{yield_from_var} = _coconut.iter({expr})
while True:
    try:
        yield _coconut.next({yield_from_var})
    except _coconut.StopIteration as {yield_err_var}:
        {ret_val_name} = {yield_err_var}.args[0] if _coconut.len({yield_err_var}.args) > 0 else None
        break
                ''',
                add_newline=True,
            ).format(
                expr=tokens[0],
                yield_from_var=self.get_temp_var("yield_from"),
                yield_err_var=self.get_temp_var("yield_err"),
                ret_val_name=ret_val_name,
            )
            return ret_val_name
        else:
            return "yield from " + tokens[0]

    def endline_handle(self, original, loc, tokens):
        """Add line number information to end of line."""
        internal_assert(len(tokens) == 1, "invalid endline tokens", tokens)
        lines = tokens[0].splitlines(True)
        if self.minify:
            lines = lines[0]
        out = []
        ln = lineno(loc, original)
        for endline in lines:
            out.append(self.wrap_line_number(self.adjust(ln)) + endline)
            ln += 1
        return "".join(out)

    def comment_handle(self, original, loc, tokens):
        """Store comment in comments."""
        internal_assert(len(tokens) == 1, "invalid comment tokens", tokens)
        ln = self.adjust(lineno(loc, original))
        internal_assert(
            lambda: ln not in self.comments or self.comments[ln] == tokens[0],
            "multiple comments on line", ln,
            extra=lambda: repr(self.comments[ln]) + " and " + repr(tokens[0]),
        )
        self.comments[ln] = tokens[0]
        return ""

    def kwd_augassign_handle(self, loc, tokens):
        """Process global/nonlocal augmented assignments."""
        name, _ = tokens
        return name + "\n" + self.augassign_stmt_handle(loc, tokens)

    def augassign_stmt_handle(self, loc, tokens):
        """Process augmented assignments."""
        name, augassign = tokens

        if "pipe" in augassign:
            pipe_op, partial_item = augassign
            pipe_tokens = [ParseResults([name], name="expr"), pipe_op, partial_item]
            return name + " = " + self.pipe_handle(loc, pipe_tokens)

        internal_assert("simple" in augassign, "invalid augmented assignment rhs tokens", augassign)
        op, item = augassign

        if op == "|>=":
            return name + " = (" + item + ")(" + name + ")"
        elif op == "|*>=":
            return name + " = (" + item + ")(*" + name + ")"
        elif op == "|**>=":
            return name + " = (" + item + ")(**" + name + ")"
        elif op == "<|=":
            return name + " = " + name + "((" + item + "))"
        elif op == "<*|=":
            return name + " = " + name + "(*(" + item + "))"
        elif op == "<**|=":
            return name + " = " + name + "(**(" + item + "))"
        elif op == "|?>=":
            return name + " = _coconut_none_pipe(" + name + ", (" + item + "))"
        elif op == "|?*>=":
            return name + " = _coconut_none_star_pipe(" + name + ", (" + item + "))"
        elif op == "|?**>=":
            return name + " = _coconut_none_dubstar_pipe(" + name + ", (" + item + "))"
        elif op == "..=" or op == "<..=":
            return name + " = _coconut_forward_compose((" + item + "), " + name + ")"
        elif op == "..>=":
            return name + " = _coconut_forward_compose(" + name + ", (" + item + "))"
        elif op == "<*..=":
            return name + " = _coconut_forward_star_compose((" + item + "), " + name + ")"
        elif op == "..*>=":
            return name + " = _coconut_forward_star_compose(" + name + ", (" + item + "))"
        elif op == "<**..=":
            return name + " = _coconut_forward_dubstar_compose((" + item + "), " + name + ")"
        elif op == "..**>=":
            return name + " = _coconut_forward_dubstar_compose(" + name + ", (" + item + "))"
        elif op == "??=":
            return name + " = " + item + " if " + name + " is None else " + name
        elif op == "::=":
            ichain_var = self.get_temp_var("lazy_chain")
            # this is necessary to prevent a segfault caused by self-reference
            return (
                ichain_var + " = " + name + "\n"
                + name + " = _coconut.itertools.chain.from_iterable(" + lazy_list_handle(loc, [ichain_var, "(" + item + ")"]) + ")"
            )
        else:
            return name + " " + op + " " + item

    def classdef_handle(self, original, loc, tokens):
        """Process class definitions."""
        name, classlist_toks, body = tokens

        out = "class " + name

        # handle classlist
        if len(classlist_toks) == 0:
            if self.target.startswith("3"):
                out += ""
            else:
                out += "(_coconut.object)"

        else:
            pos_args, star_args, kwd_args, dubstar_args = self.split_function_call(classlist_toks, loc)

            # check for just inheriting from object
            if (
                self.strict
                and len(pos_args) == 1
                and pos_args[0] == "object"
                and not star_args
                and not kwd_args
                and not dubstar_args
            ):
                raise self.make_err(CoconutStyleError, "unnecessary inheriting from object (Coconut does this automatically)", original, loc)

            # universalize if not Python 3
            if not self.target.startswith("3"):

                if star_args:
                    pos_args += ["_coconut_handle_cls_stargs(" + join_args(star_args) + ")"]
                    star_args = ()

                if kwd_args or dubstar_args:
                    out = "@_coconut_handle_cls_kwargs(" + join_args(kwd_args, dubstar_args) + ")\n" + out
                    kwd_args = dubstar_args = ()

            out += "(" + join_args(pos_args, star_args, kwd_args, dubstar_args) + ")"

        out += body

        # add override detection
        if self.target_info < (3, 6):
            out += "_coconut_call_set_names(" + name + ")\n"

        return out

    def match_datadef_handle(self, original, loc, tokens):
        """Process pattern-matching data blocks."""
        if len(tokens) == 3:
            name, match_tokens, stmts = tokens
            inherit = None
        elif len(tokens) == 4:
            name, match_tokens, inherit, stmts = tokens
        else:
            raise CoconutInternalException("invalid pattern-matching data tokens", tokens)

        if len(match_tokens) == 1:
            matches, = match_tokens
            cond = None
        elif len(match_tokens) == 2:
            matches, cond = match_tokens
        else:
            raise CoconutInternalException("invalid pattern-matching tokens in data", match_tokens)

        check_var = self.get_temp_var("match_check")
        matcher = self.get_matcher(original, loc, check_var, name_list=[])

        pos_only_args, req_args, def_args, star_arg, kwd_only_args, dubstar_arg = split_args_list(matches, loc)
        matcher.match_function(match_to_args_var, match_to_kwargs_var, pos_only_args, req_args + def_args, star_arg, kwd_only_args, dubstar_arg)

        if cond is not None:
            matcher.add_guard(cond)

        extra_stmts = handle_indentation(
            '''
def __new__(_coconut_cls, *{match_to_args_var}, **{match_to_kwargs_var}):
    {check_var} = False
    {matching}
    {pattern_error}
    return _coconut.tuple.__new__(_coconut_cls, {arg_tuple})
            ''',
            add_newline=True,
        ).format(
            match_to_args_var=match_to_args_var,
            match_to_kwargs_var=match_to_kwargs_var,
            check_var=check_var,
            matching=matcher.out(),
            pattern_error=self.pattern_error(original, loc, match_to_args_var, check_var, function_match_error_var),
            arg_tuple=tuple_str_of(matcher.name_list),
        )

        namedtuple_args = tuple_str_of(matcher.name_list, add_quotes=True)
        namedtuple_call = '_coconut.collections.namedtuple("' + name + '", ' + namedtuple_args + ')'

        return self.assemble_data(name, namedtuple_call, inherit, extra_stmts, stmts, matcher.name_list)

    def datadef_handle(self, loc, tokens):
        """Process data blocks."""
        if len(tokens) == 3:
            name, original_args, stmts = tokens
            inherit = None
        elif len(tokens) == 4:
            name, original_args, inherit, stmts = tokens
        else:
            raise CoconutInternalException("invalid data tokens", tokens)

        all_args = []  # string definitions for all args
        base_args = []  # names of all the non-starred args
        req_args = 0  # number of required arguments
        starred_arg = None  # starred arg if there is one else None
        saw_defaults = False  # whether there have been any default args so far
        types = {}  # arg position to typedef for arg
        for i, arg in enumerate(original_args):

            star, default, typedef = False, None, None
            if "name" in arg:
                internal_assert(len(arg) == 1)
                argname = arg[0]
            elif "default" in arg:
                internal_assert(len(arg) == 2)
                argname, default = arg
            elif "star" in arg:
                internal_assert(len(arg) == 1)
                star, argname = True, arg[0]
            elif "type" in arg:
                internal_assert(len(arg) == 2)
                argname, typedef = arg
            elif "type default" in arg:
                internal_assert(len(arg) == 3)
                argname, typedef, default = arg
            else:
                raise CoconutInternalException("invalid data arg tokens", arg)

            if argname.startswith("_"):
                raise CoconutDeferredSyntaxError("data fields cannot start with an underscore", loc)
            if star:
                if i != len(original_args) - 1:
                    raise CoconutDeferredSyntaxError("starred data field must come last", loc)
                starred_arg = argname
            else:
                if default:
                    saw_defaults = True
                elif saw_defaults:
                    raise CoconutDeferredSyntaxError("data fields with defaults must come after data fields without", loc)
                else:
                    req_args += 1
                base_args.append(argname)
            if typedef:
                internal_assert(not star, "invalid typedef in starred data field", typedef)
                types[i] = typedef
            arg_str = ("*" if star else "") + argname + ("=" + default if default else "")
            all_args.append(arg_str)

        extra_stmts = ""
        if starred_arg is not None:
            if base_args:
                extra_stmts += handle_indentation(
                    '''
def __new__(_coconut_cls, {all_args}):
    return _coconut.tuple.__new__(_coconut_cls, {base_args_tuple} + {starred_arg})
@_coconut.classmethod
def _make(cls, iterable, {kwd_only}new=_coconut.tuple.__new__, len=_coconut.len):
    result = new(cls, iterable)
    if len(result) < {req_args}:
        raise _coconut.TypeError("Expected at least {req_args} argument(s), got %d" % len(result))
    return result
def _asdict(self):
    return _coconut.OrderedDict((f, _coconut.getattr(self, f)) for f in self._fields)
def __repr__(self):
    return "{name}({args_for_repr})".format(**self._asdict())
def _replace(_self, **kwds):
    result = _self._make(_coconut.tuple(_coconut.map(kwds.pop, {quoted_base_args_tuple}, _self)) + kwds.pop("{starred_arg}", self.{starred_arg}))
    if kwds:
        raise _coconut.ValueError("Got unexpected field names: " + _coconut.repr(kwds.keys()))
    return result
@_coconut.property
def {starred_arg}(self):
    return self[{num_base_args}:]
                    ''',
                    add_newline=True,
                ).format(
                    name=name,
                    args_for_repr=", ".join(arg + "={" + arg.lstrip("*") + "!r}" for arg in base_args + ["*" + starred_arg]),
                    starred_arg=starred_arg,
                    all_args=", ".join(all_args),
                    req_args=req_args,
                    num_base_args=str(len(base_args)),
                    base_args_tuple=tuple_str_of(base_args),
                    quoted_base_args_tuple=tuple_str_of(base_args, add_quotes=True),
                    kwd_only=("*, " if self.target.startswith("3") else ""),
                )
            else:
                extra_stmts += handle_indentation(
                    '''
def __new__(_coconut_cls, *{arg}):
    return _coconut.tuple.__new__(_coconut_cls, {arg})
@_coconut.classmethod
def _make(cls, iterable, {kwd_only}new=_coconut.tuple.__new__, len=None):
    return new(cls, iterable)
def _asdict(self):
    return _coconut.OrderedDict([("{arg}", self[:])])
def __repr__(self):
    return "{name}(*{arg}=%r)" % (self[:],)
def _replace(_self, **kwds):
    result = self._make(kwds.pop("{arg}", _self))
    if kwds:
        raise _coconut.ValueError("Got unexpected field names: " + _coconut.repr(kwds.keys()))
    return result
@_coconut.property
def {arg}(self):
    return self[:]
                    ''',
                    add_newline=True,
                ).format(
                    name=name,
                    arg=starred_arg,
                    kwd_only=("*, " if self.target.startswith("3") else ""),
                )
        elif saw_defaults:
            extra_stmts += handle_indentation(
                '''
def __new__(_coconut_cls, {all_args}):
    return _coconut.tuple.__new__(_coconut_cls, {base_args_tuple})
                ''',
                add_newline=True,
            ).format(
                all_args=", ".join(all_args),
                base_args_tuple=tuple_str_of(base_args),
            )

        namedtuple_args = base_args + ([] if starred_arg is None else [starred_arg])
        if types:
            namedtuple_call = '_coconut.typing.NamedTuple("' + name + '", [' + ", ".join(
                '("' + argname + '", ' + self.wrap_typedef(types.get(i, "_coconut.typing.Any")) + ")"
                for i, argname in enumerate(namedtuple_args)
            ) + "])"
        else:
            namedtuple_call = '_coconut.collections.namedtuple("' + name + '", ' + tuple_str_of(namedtuple_args, add_quotes=True) + ')'

        return self.assemble_data(name, namedtuple_call, inherit, extra_stmts, stmts, namedtuple_args)

    def assemble_data(self, name, namedtuple_call, inherit, extra_stmts, stmts, match_args):
        # create class
        out = (
            "class " + name + "(" + namedtuple_call + (
                ", " + inherit if inherit is not None
                else ", _coconut.object" if not self.target.startswith("3")
                else ""
            ) + "):\n" + openindent
        )

        # add universal statements
        all_extra_stmts = handle_indentation(
            '''
__slots__ = ()
__ne__ = _coconut.object.__ne__
            ''',
            add_newline=True,
        )

        if not inherit:
            all_extra_stmts += handle_indentation(
                '''
def __eq__(self, other):
    return self.__class__ is other.__class__ and _coconut.tuple.__eq__(self, other)
def __hash__(self):
    return _coconut.tuple.__hash__(self) ^ hash(self.__class__)
                ''',
                add_newline=True,
            )

        if self.target_info < (3, 10):
            all_extra_stmts += "__match_args__ = " + tuple_str_of(match_args, add_quotes=True) + "\n"
        all_extra_stmts += extra_stmts

        # manage docstring
        rest = None
        if "simple" in stmts and len(stmts) == 1:
            out += all_extra_stmts
            rest = stmts[0]
        elif "docstring" in stmts and len(stmts) == 1:
            out += stmts[0] + all_extra_stmts
        elif "complex" in stmts and len(stmts) == 1:
            out += all_extra_stmts
            rest = "".join(stmts[0])
        elif "complex" in stmts and len(stmts) == 2:
            out += stmts[0] + all_extra_stmts
            rest = "".join(stmts[1])
        elif "empty" in stmts and len(stmts) == 1:
            out += all_extra_stmts.rstrip() + stmts[0]
        else:
            raise CoconutInternalException("invalid inner data tokens", stmts)

        # create full data definition
        if rest is not None and rest != "pass\n":
            out += rest
        out += closeindent

        # add override detection
        if self.target_info < (3, 6):
            out += "_coconut_call_set_names(" + name + ")\n"

        return out

    def single_import(self, path, imp_as):
        """Generate import statements from a fully qualified import and the name to bind it to."""
        out = []

        parts = path.split("./")  # denotes from ... import ...
        if len(parts) == 1:
            imp_from, imp = None, parts[0]
        else:
            imp_from, imp = parts

        if imp == imp_as:
            imp_as = None
        elif imp.endswith("." + imp_as):
            if imp_from is None:
                imp_from = ""
            imp_from += imp.rsplit("." + imp_as, 1)[0]
            imp, imp_as = imp_as, None

        if imp_from is None and imp == "sys":
            out.append((imp_as if imp_as is not None else imp) + " = _coconut_sys")
        elif imp_as is not None and "." in imp_as:
            import_as_var = self.get_temp_var("import")
            out.append(import_stmt(imp_from, imp, import_as_var))
            fake_mods = imp_as.split(".")
            for i in range(1, len(fake_mods)):
                mod_name = ".".join(fake_mods[:i])
                out.extend((
                    "try:",
                    openindent + mod_name,
                    closeindent + "except:",
                    openindent + mod_name + ' = _coconut.types.ModuleType("' + mod_name + '")',
                    closeindent + "else:",
                    openindent + "if not _coconut.isinstance(" + mod_name + ", _coconut.types.ModuleType):",
                    openindent + mod_name + ' = _coconut.types.ModuleType("' + mod_name + '")' + closeindent * 2,
                ))
            out.append(".".join(fake_mods) + " = " + import_as_var)
        else:
            out.append(import_stmt(imp_from, imp, imp_as))

        return out

    def universal_import(self, imports, imp_from=None):
        """Generate code for a universal import of imports from imp_from.
        imports = [[imp1], [imp2, as], ...]"""
        importmap = []  # [((imp | old_imp, imp, version_check), imp_as), ...]
        for imps in imports:
            if len(imps) == 1:
                imp, imp_as = imps[0], imps[0]
            else:
                imp, imp_as = imps
            if imp_from is not None:
                imp = imp_from + "./" + imp  # marker for from ... import ...
            old_imp = None
            path = imp.split(".")
            for i in reversed(range(1, len(path) + 1)):
                base, exts = ".".join(path[:i]), path[i:]
                clean_base = base.replace("/", "")
                if clean_base in py3_to_py2_stdlib:
                    old_imp, version_check = py3_to_py2_stdlib[clean_base]
                    if exts:
                        old_imp += "."
                        if "/" in base and "/" not in old_imp:
                            old_imp += "/"  # marker for from ... import ...
                        old_imp += ".".join(exts)
                    break
            if old_imp is None:
                paths = (imp,)
            elif not self.target:  # universal compatibility
                paths = (old_imp, imp, version_check)
            elif get_target_info_smart(self.target, mode="lowest") >= version_check:  # if lowest is above, we can safely use new
                paths = (imp,)
            elif self.target.startswith("2"):  # "2" and "27" can safely use old
                paths = (old_imp,)
            elif self.target_info < version_check:  # "3" should be compatible with all 3+
                paths = (old_imp, imp, version_check)
            else:  # "35" and above can safely use new
                paths = (imp,)
            importmap.append((paths, imp_as))

        stmts = []
        for paths, imp_as in importmap:
            if len(paths) == 1:
                more_stmts = self.single_import(paths[0], imp_as)
                stmts.extend(more_stmts)
            else:
                first, second, version_check = paths
                stmts.append("if _coconut_sys.version_info < " + str(version_check) + ":")
                first_stmts = self.single_import(first, imp_as)
                first_stmts[0] = openindent + first_stmts[0]
                first_stmts[-1] += closeindent
                stmts.extend(first_stmts)
                stmts.append("else:")
                second_stmts = self.single_import(second, imp_as)
                second_stmts[0] = openindent + second_stmts[0]
                second_stmts[-1] += closeindent
                stmts.extend(second_stmts)
        return "\n".join(stmts)

    def import_handle(self, original, loc, tokens):
        """Universalizes imports."""
        if len(tokens) == 1:
            imp_from, imports = None, tokens[0]
        elif len(tokens) == 2:
            imp_from, imports = tokens
            if imp_from == "__future__":
                self.strict_err_or_warn("unnecessary from __future__ import (Coconut does these automatically)", original, loc)
                return ""
        else:
            raise CoconutInternalException("invalid import tokens", tokens)
        imports = list(imports)
        if imp_from == "*" or imp_from is None and "*" in imports:
            if not (len(imports) == 1 and imports[0] == "*"):
                raise self.make_err(CoconutSyntaxError, "only [from *] import * allowed, not from * import name", original, loc)
            logger.warn_err(self.make_err(CoconutSyntaxWarning, "[from *] import * is a Coconut Easter egg and should not be used in production code", original, loc))
            return special_starred_import_handle(imp_all=bool(imp_from))
        if self.strict:
            self.unused_imports.update(imported_names(imports))
        return self.universal_import(imports, imp_from=imp_from)

    def complex_raise_stmt_handle(self, tokens):
        """Process Python 3 raise from statement."""
        internal_assert(len(tokens) == 2, "invalid raise from tokens", tokens)
        if self.target.startswith("3"):
            return "raise " + tokens[0] + " from " + tokens[1]
        else:
            raise_from_var = self.get_temp_var("raise_from")
            return (
                raise_from_var + " = " + tokens[0] + "\n"
                + raise_from_var + ".__cause__ = " + tokens[1] + "\n"
                + "raise " + raise_from_var
            )

    def dict_comp_handle(self, loc, tokens):
        """Process Python 2.7 dictionary comprehension."""
        internal_assert(len(tokens) == 3, "invalid dictionary comprehension tokens", tokens)
        if self.target.startswith("3"):
            key, val, comp = tokens
            return "{" + key + ": " + val + " " + comp + "}"
        else:
            key, val, comp = tokens
            return "dict(((" + key + "), (" + val + ")) " + comp + ")"

    def pattern_error(self, original, loc, value_var, check_var, match_error_class='_coconut_MatchError'):
        """Construct a pattern-matching error message."""
        base_line = clean(self.reformat(getline(loc, original)))
        line_wrap = self.wrap_str_of(base_line)
        return handle_indentation(
            """
if not {check_var}:
    raise {match_error_class}({line_wrap}, {value_var})
            """,
            add_newline=True,
        ).format(
            check_var=check_var,
            value_var=value_var,
            match_error_class=match_error_class,
            line_wrap=line_wrap,
        )

    def full_match_handle(self, original, loc, tokens, match_to_var=None, match_check_var=None, style=None):
        """Process match blocks."""
        if len(tokens) == 4:
            matches, match_type, item, stmts = tokens
            cond = None
        elif len(tokens) == 5:
            matches, match_type, item, cond, stmts = tokens
        else:
            raise CoconutInternalException("invalid match statement tokens", tokens)

        if match_type == "in":
            invert = False
        elif match_type == "not in":
            invert = True
        else:
            raise CoconutInternalException("invalid match type", match_type)

        if match_to_var is None:
            match_to_var = self.get_temp_var("match_to")
        if match_check_var is None:
            match_check_var = self.get_temp_var("match_check")

        matching = self.get_matcher(original, loc, match_check_var, style)
        matching.match(matches, match_to_var)
        if cond:
            matching.add_guard(cond)
        return (
            match_to_var + " = " + item + "\n"
            + matching.build(stmts, invert=invert)
        )

    def destructuring_stmt_handle(self, original, loc, tokens):
        """Process match assign blocks."""
        matches, item = tokens
        match_to_var = self.get_temp_var("match_to")
        match_check_var = self.get_temp_var("match_check")
        out = self.full_match_handle(original, loc, [matches, "in", item, None], match_to_var, match_check_var)
        out += self.pattern_error(original, loc, match_to_var, match_check_var)
        return out

    def name_match_funcdef_handle(self, original, loc, tokens):
        """Process match defs. Result must be passed to insert_docstring_handle."""
        if len(tokens) == 2:
            func, matches = tokens
            cond = None
        elif len(tokens) == 3:
            func, matches, cond = tokens
        else:
            raise CoconutInternalException("invalid match function definition tokens", tokens)

        check_var = self.get_temp_var("match_check")
        matcher = self.get_matcher(original, loc, check_var)

        pos_only_args, req_args, def_args, star_arg, kwd_only_args, dubstar_arg = split_args_list(matches, loc)
        matcher.match_function(match_to_args_var, match_to_kwargs_var, pos_only_args, req_args + def_args, star_arg, kwd_only_args, dubstar_arg)

        if cond is not None:
            matcher.add_guard(cond)

        before_colon = (
            "def " + func
            + "(*" + match_to_args_var + ", **" + match_to_kwargs_var + ")"
        )
        after_docstring = (
            openindent
            + check_var + " = False\n"
            + matcher.out()
            # we only include match_to_args_var here because match_to_kwargs_var is modified during matching
            + self.pattern_error(original, loc, match_to_args_var, check_var, function_match_error_var)
            # closeindent because the suite will have its own openindent/closeindent
            + closeindent
        )
        return before_colon, after_docstring

    def op_match_funcdef_handle(self, original, loc, tokens):
        """Process infix match defs. Result must be passed to insert_docstring_handle."""
        if len(tokens) == 3:
            func, args = get_infix_items(tokens)
            cond = None
        elif len(tokens) == 4:
            func, args = get_infix_items(tokens[:-1])
            cond = tokens[-1]
        else:
            raise CoconutInternalException("invalid infix match function definition tokens", tokens)
        name_tokens = [func, args]
        if cond is not None:
            name_tokens.append(cond)
        return self.name_match_funcdef_handle(original, loc, name_tokens)

    def set_literal_handle(self, tokens):
        """Converts set literals to the right form for the target Python."""
        internal_assert(len(tokens) == 1 and len(tokens[0]) == 1, "invalid set literal tokens", tokens)
        if self.target_info < (2, 7):
            return "_coconut.set(" + set_to_tuple(tokens[0]) + ")"
        else:
            return "{" + tokens[0][0] + "}"

    def set_letter_literal_handle(self, tokens):
        """Process set literals."""
        if len(tokens) == 1:
            set_type = tokens[0]
            if set_type == "s":
                return "_coconut.set()"
            elif set_type == "f":
                return "_coconut.frozenset()"
            else:
                raise CoconutInternalException("invalid set type", set_type)
        elif len(tokens) == 2:
            set_type, set_items = tokens
            internal_assert(len(set_items) == 1, "invalid set literal item", tokens[0])
            if set_type == "s":
                return self.set_literal_handle([set_items])
            elif set_type == "f":
                return "_coconut.frozenset(" + set_to_tuple(set_items) + ")"
            else:
                raise CoconutInternalException("invalid set type", set_type)
        else:
            raise CoconutInternalException("invalid set literal tokens", tokens)

    def exec_stmt_handle(self, tokens):
        """Process Python-3-style exec statements."""
        internal_assert(1 <= len(tokens) <= 3, "invalid exec statement tokens", tokens)
        if self.target.startswith("2"):
            out = "exec " + tokens[0]
            if len(tokens) > 1:
                out += " in " + ", ".join(tokens[1:])
            return out
        else:
            return "exec(" + ", ".join(tokens) + ")"

    def stmt_lambdef_handle(self, original, loc, tokens):
        """Process multi-line lambdef statements."""
        if len(tokens) == 2:
            params, stmts = tokens
        elif len(tokens) == 3:
            params, stmts, last = tokens
            if "tests" in tokens:
                stmts = stmts.asList() + ["return " + last]
            else:
                stmts = stmts.asList() + [last]
        else:
            raise CoconutInternalException("invalid statement lambda tokens", tokens)
        name = self.get_temp_var("lambda")
        body = openindent + self.add_code_before_proc("\n".join(stmts)) + closeindent
        if isinstance(params, str):
            self.add_code_before[name] = "def " + name + params + ":\n" + body
        else:
            match_tokens = [name] + list(params)
            before_colon, after_docstring = self.name_match_funcdef_handle(original, loc, match_tokens)
            self.add_code_before[name] = (
                "@_coconut_mark_as_match\n"
                + before_colon
                + ":\n"
                + after_docstring
                + body
            )
        return name

    def split_docstring(self, block):
        """Split a code block into a docstring and a body."""
        try:
            first_line, rest_of_lines = block.split("\n", 1)
        except ValueError:
            pass
        else:
            raw_first_line = split_leading_trailing_indent(rem_comment(first_line))[1]
            if match_in(self.just_a_string, raw_first_line):
                return first_line, rest_of_lines
        return None, block

    def tre_return(self, func_name, func_args, func_store, mock_var=None):
        """Generate grammar element that matches a string which is just a TRE return statement."""
        def tre_return_handle(loc, tokens):
            args = ", ".join(tokens)
            if self.no_tco:
                tco_recurse = "return " + func_name + "(" + args + ")"
            else:
                tco_recurse = "return _coconut_tail_call(" + func_name + (", " + args if args else "") + ")"
            if not func_args or func_args == args:
                tre_recurse = "continue"
            elif mock_var is None:
                tre_recurse = func_args + " = " + args + "\ncontinue"
            else:
                tre_recurse = func_args + " = " + mock_var + "(" + args + ")" + "\ncontinue"
            tre_check_var = self.get_temp_var("tre_check")
            return handle_indentation(
                """
try:
    {tre_check_var} = {func_name} is {func_store}
except _coconut.NameError:
    {tre_check_var} = False
if {tre_check_var}:
    {tre_recurse}
else:
    {tco_recurse}
                """,
                add_newline=True,
            ).format(
                tre_check_var=tre_check_var,
                func_name=func_name,
                func_store=func_store,
                tre_recurse=tre_recurse,
                tco_recurse=tco_recurse,
            )
        return attach(
            self.get_tre_return_grammar(func_name),
            tre_return_handle,
            greedy=True,
        )

    def_regex = compile_regex(r"(async\s+)?def\b")
    yield_regex = compile_regex(r"\byield\b")

    def detect_is_gen(self, raw_lines):
        """Determine if the given function code is for a generator."""
        level = 0  # indentation level
        func_until_level = None  # whether inside of an inner function

        for line in raw_lines:
            indent, line = split_leading_indent(line)

            level += ind_change(indent)

            # update func_until_level
            if func_until_level is not None and level <= func_until_level:
                func_until_level = None

            # detect inner functions
            if func_until_level is None and self.def_regex.match(line):
                func_until_level = level

            # search for yields if not in an inner function
            if func_until_level is None and self.yield_regex.search(line):
                return True

        return False

    tco_disable_regex = compile_regex(r"(try|(async\s+)?(with|for)|while)\b")
    return_regex = compile_regex(r"return\b")
    no_tco_funcs_regex = compile_regex(r"\b(locals|globals)\b")

    def transform_returns(self, original, loc, raw_lines, tre_return_grammar=None, is_async=False, is_gen=False):
        """Apply TCO, TRE, async, and generator return universalization to the given function."""
        lines = []  # transformed lines
        tco = False  # whether tco was done
        tre = False  # whether tre was done
        level = 0  # indentation level
        disabled_until_level = None  # whether inside of a disabled block
        func_until_level = None  # whether inside of an inner function
        attempt_tre = tre_return_grammar is not None  # whether to even attempt tre
        normal_func = not (is_async or is_gen)  # whether this is a normal function
        attempt_tco = normal_func and not self.no_tco  # whether to even attempt tco

        # sanity checks
        internal_assert(not (is_async and is_gen), "cannot mark as async and generator")
        internal_assert(not (not normal_func and (attempt_tre or attempt_tco)), "cannot tail call optimize async/generator functions")

        if (
            # don't transform generator returns if they're supported
            is_gen and self.target_info >= (3, 3)
            # don't transform async returns if they're supported
            or is_async and self.target_info >= (3, 5)
        ):
            func_code = "".join(raw_lines)
            return func_code, tco, tre

        for line in raw_lines:
            indent, _body, dedent = split_leading_trailing_indent(line)
            base, comment = split_comment(_body)

            level += ind_change(indent)

            # update disabled_until_level and func_until_level
            if disabled_until_level is not None and level <= disabled_until_level:
                disabled_until_level = None
            if func_until_level is not None and level <= func_until_level:
                func_until_level = None

            # detect inner functions
            if func_until_level is None and self.def_regex.match(base):
                func_until_level = level
                if disabled_until_level is None:
                    disabled_until_level = level
                # functions store scope so no TRE anywhere
                attempt_tre = False

            # tco and tre shouldn't touch scopes that depend on actual return statements
            #  or scopes where we can't insert a continue
            if normal_func and disabled_until_level is None and self.tco_disable_regex.match(base):
                disabled_until_level = level

            # check if there is anything that stores a scope reference, and if so,
            #  disable TRE, since it can't handle that
            if attempt_tre and match_in(self.stores_scope, line):
                attempt_tre = False

            # attempt tco/tre/async universalization
            if disabled_until_level is None:

                # handle generator/async returns
                if not normal_func and self.return_regex.match(base):
                    to_return = base[len("return"):].strip()
                    if to_return:
                        to_return = "(" + to_return + ")"
                    # only use trollius Return when trollius is imported
                    if is_async and self.target_info < (3, 4):
                        ret_err = "_coconut.asyncio.Return"
                    else:
                        ret_err = "_coconut.StopIteration"
                        # warn about Python 3.7 incompatibility on any target with Python 3 support
                        if not self.target.startswith("2"):
                            logger.warn_err(
                                self.make_err(
                                    CoconutSyntaxWarning,
                                    "compiled generator return to StopIteration error; this will break on Python >= 3.7 (pass --target sys to fix)",
                                    original, loc,
                                ),
                            )
                    line = indent + "raise " + ret_err + "(" + to_return + ")" + comment + dedent

                # TRE
                tre_base = None
                if attempt_tre:
                    tre_base = self.post_transform(tre_return_grammar, base)
                    if tre_base is not None:
                        line = indent + tre_base + comment + dedent
                        tre = True
                        # when tco is available, tre falls back on it if the function is changed
                        tco = not self.no_tco

                # TCO
                if (
                    attempt_tco
                    # don't attempt tco if tre succeeded
                    and tre_base is None
                    # don't tco scope-dependent functions
                    and not self.no_tco_funcs_regex.search(base)
                ):
                    tco_base = None
                    tco_base = self.post_transform(self.tco_return, base)
                    if tco_base is not None:
                        line = indent + tco_base + comment + dedent
                        tco = True

            level += ind_change(dedent)
            lines.append(line)

        func_code = "".join(lines)
        return func_code, tco, tre

    def decoratable_funcdef_stmt_handle(self, original, loc, tokens, is_async=False):
        """Determines if TCO or TRE can be done and if so does it,
        handles dotted function names, and universalizes async functions."""
        if len(tokens) == 1:
            decorators, funcdef = "", tokens[0]
        elif len(tokens) == 2:
            decorators, funcdef = tokens
        else:
            raise CoconutInternalException("invalid function definition tokens", tokens)

        # process tokens
        raw_lines = funcdef.splitlines(True)
        def_stmt = raw_lines.pop(0)

        # detect addpattern functions
        if def_stmt.startswith("addpattern def"):
            def_stmt = def_stmt[len("addpattern "):]
            addpattern = True
        elif def_stmt.startswith("def"):
            addpattern = False
        else:
            raise CoconutInternalException("invalid function definition statement", def_stmt)

        # extract information about the function
        with self.complain_on_err():
            try:
                split_func_tokens = parse(self.split_func, def_stmt)

                internal_assert(len(split_func_tokens) == 2, "invalid function definition splitting tokens", split_func_tokens)
                func_name, func_arg_tokens = split_func_tokens

                func_params = "(" + ", ".join("".join(arg) for arg in func_arg_tokens) + ")"

                # arguments that should be used to call the function; must be in the order in which they're defined
                func_args = []
                for arg in func_arg_tokens:
                    if len(arg) > 1 and arg[0] in ("*", "**"):
                        func_args.append(arg[1])
                    elif arg[0] != "*":
                        func_args.append(arg[0])
                func_args = ", ".join(func_args)
            except BaseException:
                func_name = None
                raise

        # run target checks if func info extraction succeeded
        if func_name is not None:
            # raises DeferredSyntaxErrors which shouldn't be complained
            pos_only_args, req_args, def_args, star_arg, kwd_only_args, dubstar_arg = split_args_list(func_arg_tokens, loc)
            if pos_only_args and self.target_info < (3, 8):
                raise self.make_err(
                    CoconutTargetError,
                    "found Python 3.8 keyword-only argument{s} (use 'match def' to produce universal code)".format(
                        s="s" if len(pos_only_args) > 1 else "",
                    ),
                    original,
                    loc,
                    target="38",
                )
            if kwd_only_args and self.target_info < (3,):
                raise self.make_err(
                    CoconutTargetError,
                    "found Python 3 keyword-only argument{s} (use 'match def' to produce universal code)".format(
                        s="s" if len(pos_only_args) > 1 else "",
                    ),
                    original,
                    loc,
                    target="3",
                )

        def_name = func_name  # the name used when defining the function

        # handle dotted function definition
        is_dotted = func_name is not None and "." in func_name
        if is_dotted:
            def_name = func_name.rsplit(".", 1)[-1]

        # detect pattern-matching functions
        is_match_func = func_params == "(*{match_to_args_var}, **{match_to_kwargs_var})".format(
            match_to_args_var=match_to_args_var,
            match_to_kwargs_var=match_to_kwargs_var,
        )

        # handle addpattern functions
        if addpattern:
            if func_name is None:
                raise CoconutInternalException("could not find name in addpattern function definition", def_stmt)
            # binds most tightly, except for TCO
            decorators += "@_coconut_addpattern(" + func_name + ")\n"

        # modify function definition to use def_name
        if def_name != func_name:
            def_stmt_pre_lparen, def_stmt_post_lparen = def_stmt.split("(", 1)
            def_stmt_def, def_stmt_name = def_stmt_pre_lparen.rsplit(" ", 1)
            def_stmt_name = def_stmt_name.replace(func_name, def_name)
            def_stmt = def_stmt_def + " " + def_stmt_name + "(" + def_stmt_post_lparen

        # handle async functions
        if is_async:
            if not self.target:
                raise self.make_err(
                    CoconutTargetError,
                    "async function definition requires a specific target",
                    original, loc,
                    target="sys",
                )
            elif self.target_info >= (3, 5):
                def_stmt = "async " + def_stmt
            else:
                decorators += "@_coconut.asyncio.coroutine\n"

            func_code, _, _ = self.transform_returns(original, loc, raw_lines, is_async=True)

        # handle normal functions
        else:
            # detect generators
            is_gen = self.detect_is_gen(raw_lines)

            attempt_tre = (
                func_name is not None
                and not is_gen
                # tre does not work with decorators, though tco does
                and not decorators
            )
            if attempt_tre:
                if func_args and func_args != func_params[1:-1]:
                    mock_var = self.get_temp_var("mock")
                else:
                    mock_var = None
                func_store = self.get_temp_var("recursive_func")
                tre_return_grammar = self.tre_return(func_name, func_args, func_store, mock_var)
            else:
                mock_var = func_store = tre_return_grammar = None

            func_code, tco, tre = self.transform_returns(
                original,
                loc,
                raw_lines,
                tre_return_grammar,
                is_gen=is_gen,
            )

            if tre:
                comment, rest = split_leading_comment(func_code)
                indent, base, dedent = split_leading_trailing_indent(rest, 1)
                base, base_dedent = split_trailing_indent(base)
                docstring, base = self.split_docstring(base)
                func_code = (
                    comment + indent
                    + (docstring + "\n" if docstring is not None else "")
                    + (
                        "def " + mock_var + func_params + ": return " + func_args + "\n"
                        if mock_var is not None else ""
                    ) + "while True:\n"
                        + openindent + base + base_dedent
                        + ("\n" if "\n" not in base_dedent else "") + "return None"
                        + ("\n" if "\n" not in dedent else "") + closeindent + dedent
                    + func_store + " = " + def_name + "\n"
                )
            if tco:
                decorators += "@_coconut_tco\n"  # binds most tightly (aside from below)

        # add attribute to mark pattern-matching functions
        if is_match_func:
            decorators += "@_coconut_mark_as_match\n"  # binds most tightly

        # handle dotted function definition
        if is_dotted:
            store_var = self.get_temp_var("name_store")
            out = handle_indentation(
                '''
try:
    {store_var} = {def_name}
except _coconut.NameError:
    {store_var} = _coconut_sentinel
{decorators}{def_stmt}{func_code}{func_name} = {def_name}
if {store_var} is not _coconut_sentinel:
    {def_name} = {store_var}
                ''',
                add_newline=True,
            ).format(
                store_var=store_var,
                def_name=def_name,
                decorators=decorators,
                def_stmt=def_stmt,
                func_code=func_code,
                func_name=func_name,
            )
        else:
            out = decorators + def_stmt + func_code

        return out

    def await_item_handle(self, original, loc, tokens):
        """Check for Python 3.5 await expression."""
        internal_assert(len(tokens) == 1, "invalid await statement tokens", tokens)
        if not self.target:
            raise self.make_err(
                CoconutTargetError,
                "await requires a specific target",
                original, loc,
                target="sys",
            )
        elif self.target_info >= (3, 5):
            return "await " + tokens[0]
        elif self.target_info >= (3, 3):
            return "(yield from " + tokens[0] + ")"
        else:
            return "(yield _coconut.asyncio.From(" + tokens[0] + "))"

    def unsafe_typedef_handle(self, tokens):
        """Process type annotations without a comma after them."""
        return self.typedef_handle(tokens.asList() + [","])

    def wrap_typedef(self, typedef, ignore_target=False):
        """Wrap a type definition in a string to defer it unless --no-wrap."""
        if self.no_wrap or not ignore_target and self.target_info >= (3, 7):
            return typedef
        else:
            return self.wrap_str_of(self.reformat(typedef))

    def typedef_handle(self, tokens):
        """Process Python 3 type annotations."""
        if len(tokens) == 1:  # return typedef
            if self.target.startswith("3"):
                return " -> " + self.wrap_typedef(tokens[0]) + ":"
            else:
                return ":\n" + self.wrap_comment(" type: (...) -> " + tokens[0])
        else:  # argument typedef
            if len(tokens) == 3:
                varname, typedef, comma = tokens
                default = ""
            elif len(tokens) == 4:
                varname, typedef, default, comma = tokens
            else:
                raise CoconutInternalException("invalid type annotation tokens", tokens)
            if self.target.startswith("3"):
                return varname + ": " + self.wrap_typedef(typedef) + default + comma
            else:
                return varname + default + comma + self.wrap_passthrough(self.wrap_comment(" type: " + typedef) + "\n" + " " * self.tabideal)

    def typed_assign_stmt_handle(self, tokens):
        """Process Python 3.6 variable type annotations."""
        if len(tokens) == 2:
            name, typedef = tokens
            value = None
        elif len(tokens) == 3:
            name, typedef, value = tokens
        else:
            raise CoconutInternalException("invalid variable type annotation tokens", tokens)

        if self.target_info >= (3, 6):
            return name + ": " + self.wrap_typedef(typedef) + ("" if value is None else " = " + value)
        else:
            return handle_indentation('''
{name} = {value}{comment}
if "__annotations__" not in _coconut.locals():
    __annotations__ = {{}}
__annotations__["{name}"] = {annotation}
            ''').format(
                name=name,
                value="None" if value is None else value,
                comment=self.wrap_comment(" type: " + typedef),
                # ignore target since this annotation isn't going inside an actual typedef
                annotation=self.wrap_typedef(typedef, ignore_target=True),
            )

    def with_stmt_handle(self, tokens):
        """Process with statements."""
        withs, body = tokens
        if len(withs) == 1 or self.target_info >= (2, 7):
            return "with " + ", ".join(withs) + body
        else:
            return (
                "".join("with " + expr + ":\n" + openindent for expr in withs[:-1])
                + "with " + withs[-1] + body
                + closeindent * (len(withs) - 1)
            )

    def ellipsis_handle(self, tokens):
        internal_assert(len(tokens) == 1, "invalid ellipsis tokens", tokens)
        if self.target.startswith("3"):
            return "..."
        else:
            return "_coconut.Ellipsis"

    def match_case_tokens(self, match_var, check_var, style, original, tokens, top):
        """Build code for matching the given case."""
        if len(tokens) == 3:
            loc, matches, stmts = tokens
            cond = None
        elif len(tokens) == 4:
            loc, matches, cond, stmts = tokens
        else:
            raise CoconutInternalException("invalid case match tokens", tokens)
        loc = int(loc)
        matching = self.get_matcher(original, loc, check_var, style)
        matching.match(matches, match_var)
        if cond:
            matching.add_guard(cond)
        return matching.build(stmts, set_check_var=top)

    def case_stmt_handle(self, original, loc, tokens):
        """Process case blocks."""
        if len(tokens) == 3:
            block_kwd, item, cases = tokens
            default = None
        elif len(tokens) == 4:
            block_kwd, item, cases, default = tokens
        else:
            raise CoconutInternalException("invalid case tokens", tokens)

        if block_kwd == "cases":
            if self.strict:
                style = "coconut"
            else:
                style = "coconut warn"
        elif block_kwd == "match":
            if self.strict:
                raise self.make_err(CoconutStyleError, "found Python-style 'match: case' syntax (use Coconut-style 'case: match' syntax instead)", original, loc)
            style = "python warn"
        else:
            raise CoconutInternalException("invalid case block keyword", block_kwd)

        check_var = self.get_temp_var("case_match_check")
        match_var = self.get_temp_var("case_match_to")

        out = (
            match_var + " = " + item + "\n"
            + self.match_case_tokens(match_var, check_var, style, original, cases[0], True)
        )
        for case in cases[1:]:
            out += (
                "if not " + check_var + ":\n" + openindent
                + self.match_case_tokens(match_var, check_var, style, original, case, False) + closeindent
            )
        if default is not None:
            out += "if not " + check_var + default
        return out

    def f_string_handle(self, loc, tokens):
        """Process Python 3.6 format strings."""
        internal_assert(len(tokens) == 1, "invalid format string tokens", tokens)
        string = tokens[0]

        # strip raw r
        raw = string.startswith("r")
        if raw:
            string = string[1:]

        # strip wrappers
        internal_assert(string.startswith(strwrapper) and string.endswith(unwrapper))
        string = string[1:-1]

        # get text
        old_text, strchar = self.get_ref("str", string)

        # separate expressions
        string_parts = [""]
        exprs = []
        saw_brace = False
        in_expr = False
        expr_level = 0
        for c in old_text:
            if saw_brace:
                saw_brace = False
                if c == "{":
                    string_parts[-1] += c
                elif c == "}":
                    raise CoconutDeferredSyntaxError("empty expression in format string", loc)
                else:
                    in_expr = True
                    expr_level = paren_change(c)
                    exprs.append(c)
            elif in_expr:
                if expr_level < 0:
                    expr_level += paren_change(c)
                    exprs[-1] += c
                elif expr_level > 0:
                    raise CoconutDeferredSyntaxError("imbalanced parentheses in format string expression", loc)
                elif c in "!:}":  # these characters end the expr
                    in_expr = False
                    string_parts.append(c)
                else:
                    expr_level += paren_change(c)
                    exprs[-1] += c
            elif c == "{":
                saw_brace = True
                string_parts[-1] += c
            else:
                string_parts[-1] += c

        # handle dangling detections
        if saw_brace:
            raise CoconutDeferredSyntaxError("format string ends with unescaped brace (escape by doubling to '{{')", loc)
        if in_expr:
            raise CoconutDeferredSyntaxError("imbalanced braces in format string (escape braces by doubling to '{{' and '}}')", loc)

        # handle Python 3.8 f string = specifier
        for i, expr in enumerate(exprs):
            if expr.endswith("="):
                before = string_parts[i]
                internal_assert(before[-1] == "{", "invalid format string split", (string_parts, exprs))
                string_parts[i] = before[:-1] + expr + "{"
                exprs[i] = expr[:-1]

        # compile Coconut expressions
        compiled_exprs = []
        for co_expr in exprs:
            try:
                py_expr = self.inner_parse_eval(co_expr)
            except ParseBaseException:
                raise CoconutDeferredSyntaxError("parsing failed for format string expression: " + co_expr, loc)
            if "\n" in py_expr:
                raise CoconutDeferredSyntaxError("invalid expression in format string: " + co_expr, loc)
            compiled_exprs.append(py_expr)

        # reconstitute string
        if self.target_info >= (3, 6):
            new_text = interleaved_join(string_parts, compiled_exprs)

            return "f" + ("r" if raw else "") + self.wrap_str(new_text, strchar)
        else:
            names = [format_var + "_" + str(i) for i in range(len(compiled_exprs))]
            new_text = interleaved_join(string_parts, names)

            # generate format call
            return ("r" if raw else "") + self.wrap_str(new_text, strchar) + ".format(" + ", ".join(
                name + "=(" + expr + ")"
                for name, expr in zip(names, compiled_exprs)
            ) + ")"

    def decorators_handle(self, tokens):
        """Process decorators."""
        defs = []
        decorators = []
        for tok in tokens:
            if "simple" in tok and len(tok) == 1:
                decorators.append("@" + tok[0])
            elif "complex" in tok and len(tok) == 1:
                if self.target_info >= (3, 9):
                    decorators.append("@" + tok[0])
                else:
                    varname = self.get_temp_var("decorator")
                    defs.append(varname + " = " + tok[0])
                    decorators.append("@" + varname)
            else:
                raise CoconutInternalException("invalid decorator tokens", tok)
        return "\n".join(defs + decorators) + "\n"

    def unsafe_typedef_or_expr_handle(self, tokens):
        """Handle Type | Type typedefs."""
        internal_assert(len(tokens) >= 2, "invalid union typedef tokens", tokens)
        if self.target_info >= (3, 10):
            return " | ".join(tokens)
        else:
            return "_coconut.typing.Union[" + ", ".join(tokens) + "]"

    def split_star_expr_tokens(self, tokens):
        """Split testlist_star_expr or dict_literal tokens."""
        groups = [[]]
        has_star = False
        has_comma = False
        for tok_grp in tokens:
            if tok_grp == ",":
                has_comma = True
            elif len(tok_grp) == 1:
                groups[-1].append(tok_grp[0])
            elif len(tok_grp) == 2:
                internal_assert(not tok_grp[0].lstrip("*"), "invalid star expr item signifier", tok_grp[0])
                has_star = True
                groups.append(tok_grp[1])
                groups.append([])
            else:
                raise CoconutInternalException("invalid testlist_star_expr tokens", tokens)
        if not groups[-1]:
            groups.pop()
        return groups, has_star, has_comma

    def testlist_star_expr_handle(self, original, loc, tokens, list_literal=False):
        """Handle naked a, *b."""
        groups, has_star, has_comma = self.split_star_expr_tokens(tokens)
        is_sequence = has_comma or list_literal

        if not is_sequence:
            if has_star:
                raise CoconutDeferredSyntaxError("can't use starred expression here", loc)
            internal_assert(len(groups) == 1 and len(groups[0]) == 1, "invalid single-item testlist_star_expr tokens", tokens)
            out = groups[0][0]

        elif not has_star:
            internal_assert(len(groups) == 1, "testlist_star_expr group splitting failed on", tokens)
            out = tuple_str_of(groups[0], add_parens=False)

        # naturally supported on 3.5+
        elif self.target_info >= (3, 5):
            to_literal = []
            for g in groups:
                if isinstance(g, list):
                    to_literal.extend(g)
                else:
                    to_literal.append("*" + g)
            out = tuple_str_of(to_literal, add_parens=False)

        # otherwise universalize
        else:
            to_chain = []
            for g in groups:
                if isinstance(g, list):
                    to_chain.append(tuple_str_of(g))
                else:
                    to_chain.append(g)

            # return immediately, since we handle list_literal here
            if list_literal:
                return "_coconut.list(_coconut.itertools.chain(" + ", ".join(to_chain) + "))"
            else:
                return "_coconut.tuple(_coconut.itertools.chain(" + ", ".join(to_chain) + "))"

        if list_literal:
            return "[" + out + "]"
        else:
            return out  # the grammar wraps this in parens as needed

    def list_literal_handle(self, original, loc, tokens):
        """Handle non-comprehension list literals."""
        return self.testlist_star_expr_handle(original, loc, tokens, list_literal=True)

    def dict_literal_handle(self, original, loc, tokens):
        """Handle {**d1, **d2}."""
        if not tokens:
            return "{}"

        groups, has_star, _ = self.split_star_expr_tokens(tokens)

        if not has_star:
            internal_assert(len(groups) == 1, "dict_literal group splitting failed on", tokens)
            return "{" + ", ".join(groups[0]) + "}"

        # naturally supported on 3.5+
        elif self.target_info >= (3, 5):
            to_literal = []
            for g in groups:
                if isinstance(g, list):
                    to_literal.extend(g)
                else:
                    to_literal.append("**" + g)
            return "{" + ", ".join(to_literal) + "}"

        # otherwise universalize
        else:
            to_merge = []
            for g in groups:
                if isinstance(g, list):
                    to_merge.append("{" + ", ".join(g) + "}")
                else:
                    to_merge.append(g)
            return "_coconut_dict_merge(" + ", ".join(to_merge) + ")"

# end: COMPILER HANDLERS
# -----------------------------------------------------------------------------------------------------------------------
# CHECKING HANDLERS:
# -----------------------------------------------------------------------------------------------------------------------

    def check_strict(self, name, original, loc, tokens, only_warn=False):
        """Check that syntax meets --strict requirements."""
        internal_assert(len(tokens) == 1, "invalid " + name + " tokens", tokens)
        if self.strict:
            if only_warn:
                logger.warn_err(self.make_err(CoconutSyntaxWarning, "found " + name, original, loc, extra="remove --strict to dismiss"))
            else:
                raise self.make_err(CoconutStyleError, "found " + name, original, loc)
        return tokens[0]

    def lambdef_check(self, original, loc, tokens):
        """Check for Python-style lambdas."""
        return self.check_strict("Python-style lambda", original, loc, tokens)

    def endline_semicolon_check(self, original, loc, tokens):
        """Check for semicolons at the end of lines."""
        return self.check_strict("semicolon at end of line", original, loc, tokens)

    def u_string_check(self, original, loc, tokens):
        """Check for Python-2-style unicode strings."""
        return self.check_strict("Python-2-style unicode string (all Coconut strings are unicode strings)", original, loc, tokens)

    def match_dotted_name_const_check(self, original, loc, tokens):
        """Check for Python-3.10-style implicit dotted name match check."""
        return self.check_strict("Python-3.10-style dotted name in pattern-matching (Coconut style is to use '={name}' not '{name}')".format(name=tokens[0]), original, loc, tokens)

    def match_check_equals_check(self, original, loc, tokens):
        """Check for old-style =item in pattern-matching."""
        return self.check_strict("old-style =<expr> instead of new-style ==<expr> in pattern-matching", original, loc, tokens, only_warn=True)

    def check_py(self, version, name, original, loc, tokens):
        """Check for Python-version-specific syntax."""
        internal_assert(len(tokens) == 1, "invalid " + name + " tokens", tokens)
        version_info = get_target_info(version)
        if self.target_info < version_info:
            raise self.make_err(CoconutTargetError, "found Python " + ".".join(str(v) for v in version_info) + " " + name, original, loc, target=version)
        else:
            return tokens[0]

    def name_check(self, original, loc, tokens):
        """Check the given base name."""
        name, = tokens  # avoid the overhead of an internal_assert call here

        if self.disable_name_check:
            return name
        if self.strict:
            self.unused_imports.discard(name)

        if name == "exec":
            if self.target.startswith("3"):
                return name
            else:
                return "_coconut_exec"
        elif name.startswith(reserved_prefix):
            raise self.make_err(CoconutSyntaxError, "variable names cannot start with reserved prefix " + reserved_prefix, original, loc)
        else:
            return name

    def nonlocal_check(self, original, loc, tokens):
        """Check for Python 3 nonlocal statement."""
        return self.check_py("3", "nonlocal statement", original, loc, tokens)

    def star_assign_item_check(self, original, loc, tokens):
        """Check for Python 3 starred assignment."""
        return self.check_py("3", "starred assignment (use 'match' to produce universal code)", original, loc, tokens)

    def star_sep_check(self, original, loc, tokens):
        """Check for Python 3 keyword-only argument separator."""
        return self.check_py("3", "keyword-only argument separator (use 'match' to produce universal code)", original, loc, tokens)

    def slash_sep_check(self, original, loc, tokens):
        """Check for Python 3.8 positional-only arguments."""
        return self.check_py("38", "positional-only argument separator (use 'match' to produce universal code)", original, loc, tokens)

    def matrix_at_check(self, original, loc, tokens):
        """Check for Python 3.5 matrix multiplication."""
        return self.check_py("35", "matrix multiplication", original, loc, tokens)

    def async_stmt_check(self, original, loc, tokens):
        """Check for Python 3.5 async for/with."""
        return self.check_py("35", "async for/with", original, loc, tokens)

    def async_comp_check(self, original, loc, tokens):
        """Check for Python 3.6 async comprehension."""
        return self.check_py("36", "async comprehension", original, loc, tokens)

    def namedexpr_check(self, original, loc, tokens):
        """Check for Python 3.8 assignment expressions."""
        return self.check_py("38", "assignment expression", original, loc, tokens)

    def new_namedexpr_check(self, original, loc, tokens):
        """Check for Python-3.10-only assignment expressions."""
        return self.check_py("310", "assignment expression in index or set literal", original, loc, tokens)

    def except_star_clause_check(self, original, loc, tokens):
        """Check for Python-3.11-only except* statements."""
        return self.check_py("311", "except* statement", original, loc, tokens)

# end: CHECKING HANDLERS
# -----------------------------------------------------------------------------------------------------------------------
# ENDPOINTS:
# -----------------------------------------------------------------------------------------------------------------------

    def parse_single(self, inputstring):
        """Parse line code."""
        return self.parse(inputstring, self.single_parser, {}, {"header": "none", "initial": "none"})

    def parse_file(self, inputstring, addhash=True):
        """Parse file code."""
        if addhash:
            use_hash = self.genhash(inputstring)
        else:
            use_hash = None
        return self.parse(inputstring, self.file_parser, {"nl_at_eof_check": True}, {"header": "file", "use_hash": use_hash})

    def parse_exec(self, inputstring):
        """Parse exec code."""
        return self.parse(inputstring, self.file_parser, {}, {"header": "file", "initial": "none"})

    def parse_package(self, inputstring, package_level=0, addhash=True):
        """Parse package code."""
        internal_assert(package_level >= 0, "invalid package level", package_level)
        if addhash:
            use_hash = self.genhash(inputstring, package_level)
        else:
            use_hash = None
        return self.parse(inputstring, self.file_parser, {"nl_at_eof_check": True}, {"header": "package:" + str(package_level), "use_hash": use_hash})

    def parse_block(self, inputstring):
        """Parse block code."""
        return self.parse(inputstring, self.file_parser, {}, {"header": "none", "initial": "none"})

    def parse_sys(self, inputstring):
        """Parse code to use the Coconut module."""
        return self.parse(inputstring, self.file_parser, {}, {"header": "sys", "initial": "none"})

    def parse_eval(self, inputstring):
        """Parse eval code."""
        return self.parse(inputstring, self.eval_parser, {"strip": True}, {"header": "none", "initial": "none", "final_endline": False})

    def parse_any(self, inputstring):
        """Parse any code."""
        return self.parse(inputstring, self.file_parser, {"strip": True}, {"header": "none", "initial": "none", "final_endline": False})

    def warm_up(self):
        """Warm up the compiler by running something through it."""
        result = self.parse_any("")
        internal_assert(result == "", "compiler warm-up should produce no code; instead got", result)

# end: ENDPOINTS
