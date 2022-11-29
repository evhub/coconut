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
#   - Utilities
#   - Compiler
#   - Processors
#   - Handlers
#   - Checking Handlers
#   - Endpoints
#   - Binding

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
import re
from contextlib import contextmanager
from functools import partial, wraps
from collections import defaultdict
from threading import Lock

from coconut._pyparsing import (
    USE_COMPUTATION_GRAPH,
    ParseBaseException,
    ParseResults,
    col as getcol,
    lineno,
    nums,
    _trim_arity,
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
    errwrapper,
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
    none_coalesce_var,
    is_data_var,
    funcwrapper,
    non_syntactic_newline,
    indchars,
    default_whitespace_chars,
    early_passthrough_wrapper,
    super_names,
    custom_op_var,
    all_keywords,
    reserved_compiler_symbols,
    delimiter_symbols,
    reserved_command_symbols,
    streamline_grammar_for_len,
    all_builtins,
)
from coconut.util import (
    pickleable_obj,
    checksum,
    clip,
    logical_lines,
    clean,
    get_target_info,
    get_clock_time,
)
from coconut.exceptions import (
    CoconutException,
    CoconutSyntaxError,
    CoconutParseError,
    CoconutStyleError,
    CoconutTargetError,
    CoconutInternalException,
    CoconutSyntaxWarning,
    CoconutDeferredSyntaxError,
    CoconutInternalSyntaxError,
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
    partial_op_item_handle,
)
from coconut.compiler.util import (
    sys_target,
    getline,
    addskip,
    count_end,
    paren_change,
    ind_change,
    rem_comment,
    split_comment,
    attach,
    trace_attach,
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
    parse_where,
    get_highest_parse_loc,
    literal_eval,
    should_trim_arity,
    rem_and_count_indents,
    normalize_indent_markers,
    try_parse,
    prep_grammar,
    split_leading_whitespace,
    ordered_items,
    tuple_str_of_str,
)
from coconut.compiler.header import (
    minify_header,
    getheader,
)

# end: IMPORTS
# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
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
    default_args = []
    star_arg = None
    kwd_only_args = []
    dubstar_arg = None
    pos = 0
    for arg in tokens:
        # only the first two components matter; if there's a third it's a typedef
        arg = arg[:2]

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
            internal_assert(arg[1] is not None, "invalid arg[1] in split_args_list", arg)

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
                    default_args.append((arg[0], arg[1]))
                # kwd only arg (pos = 2)
                elif pos <= 2:
                    pos = 2
                    kwd_only_args.append((arg[0], arg[1]))
                else:
                    raise CoconutDeferredSyntaxError("invalid default argument in function definition", loc)

    return pos_only_args, req_args, default_args, star_arg, kwd_only_args, dubstar_arg


def reconstitute_paramdef(pos_only_args, req_args, default_args, star_arg, kwd_only_args, dubstar_arg):
    """Convert the results of split_args_list back into a parameter defintion string."""
    args_list = []
    if pos_only_args:
        args_list += pos_only_args
        args_list.append("/")
    args_list += req_args
    for name, default in default_args:
        args_list.append(name + "=" + default)
    if star_arg is not None:
        args_list.append("*" + star_arg)
    elif kwd_only_args:
        args_list.append("*")
    for name, default in kwd_only_args:
        if default is None:
            args_list.append(name)
        else:
            args_list.append(name + "=" + default)
    if dubstar_arg is not None:
        args_list.append("**" + dubstar_arg)
    return ", ".join(args_list)


# end: UTILITIES
# -----------------------------------------------------------------------------------------------------------------------
# COMPILER:
# -----------------------------------------------------------------------------------------------------------------------


class Compiler(Grammar, pickleable_obj):
    """The Coconut compiler."""
    lock = Lock()
    current_compiler = [None]  # list for mutability

    preprocs = [
        lambda self: self.prepare,
        lambda self: self.str_proc,
        lambda self: self.passthrough_proc,
        lambda self: self.operator_proc,
        lambda self: self.ind_proc,
    ]

    reformatprocs = [
        lambda self: self.deferred_code_proc,
        lambda self: self.reind_proc,
        lambda self: self.endline_repl,
        lambda self: partial(self.base_passthrough_repl, wrap_char="\\"),
        lambda self: self.str_repl,
    ]
    postprocs = reformatprocs + [
        lambda self: self.header_proc,
        lambda self: self.polish,
    ]

    def __init__(self, *args, **kwargs):
        """Creates a new compiler with the given parsing parameters."""
        self.setup(*args, **kwargs)

    # changes here should be reflected in the stub for coconut.convenience.setup
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

    temp_var_counts = None
    operators = None

    def reset(self, keep_state=False):
        """Resets references."""
        self.indchar = None
        self.comments = {}
        self.refs = []
        self.skips = []
        self.docstring = ""
        # need to keep temp_var_counts in interpreter to avoid overwriting typevars
        if self.temp_var_counts is None or not keep_state:
            self.temp_var_counts = defaultdict(int)
        self.parsing_context = defaultdict(list)
        self.add_code_before = {}
        self.add_code_before_regexes = {}
        self.add_code_before_replacements = {}
        self.unused_imports = defaultdict(list)
        self.kept_lines = []
        self.num_lines = 0
        self.disable_name_check = False
        if self.operators is None or not keep_state:
            self.operators = []
            self.operator_repl_table = []

    @contextmanager
    def inner_environment(self):
        """Set up compiler to evaluate inner expressions."""
        line_numbers, self.line_numbers = self.line_numbers, False
        keep_lines, self.keep_lines = self.keep_lines, False
        comments, self.comments = self.comments, {}
        skips, self.skips = self.skips, []
        docstring, self.docstring = self.docstring, ""
        parsing_context, self.parsing_context = self.parsing_context, defaultdict(list)
        kept_lines, self.kept_lines = self.kept_lines, []
        num_lines, self.num_lines = self.num_lines, 0
        try:
            yield
        finally:
            self.line_numbers = line_numbers
            self.keep_lines = keep_lines
            self.comments = comments
            self.skips = skips
            self.docstring = docstring
            self.parsing_context = parsing_context
            self.kept_lines = kept_lines
            self.num_lines = num_lines

    def current_parsing_context(self, name, default=None):
        """Get the current parsing context for the given name."""
        stack = self.parsing_context[name]
        if stack:
            return stack[-1]
        else:
            return default

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

    @classmethod
    def method(cls, method_name, is_action=None, **kwargs):
        """Get a function that always dispatches to getattr(current_compiler, method_name)$(**kwargs)."""
        cls_method = getattr(cls, method_name)
        if is_action is None:
            is_action = not method_name.endswith("_manage")
        trim_arity = should_trim_arity(cls_method) if is_action else False

        @wraps(cls_method)
        def method(original, loc, tokens):
            self_method = getattr(cls.current_compiler[0], method_name)
            if kwargs:
                self_method = partial(self_method, **kwargs)
            if trim_arity:
                self_method = _trim_arity(self_method)
            return self_method(original, loc, tokens)
        internal_assert(
            hasattr(cls_method, "ignore_tokens") is hasattr(method, "ignore_tokens")
            and hasattr(cls_method, "ignore_no_tokens") is hasattr(method, "ignore_no_tokens")
            and hasattr(cls_method, "ignore_one_token") is hasattr(method, "ignore_one_token"),
            "failed to properly wrap method",
            method_name,
        )
        method.trim_arity = False
        return method

    @classmethod
    def bind(cls):
        """Binds reference objects to the proper parse actions."""
        # handle parsing_context for class definitions
        new_classdef = trace_attach(cls.classdef_ref, cls.method("classdef_handle"))
        cls.classdef <<= Wrap(new_classdef, cls.method("class_manage"), greedy=True)

        new_datadef = trace_attach(cls.datadef_ref, cls.method("datadef_handle"))
        cls.datadef <<= Wrap(new_datadef, cls.method("class_manage"), greedy=True)

        new_match_datadef = trace_attach(cls.match_datadef_ref, cls.method("match_datadef_handle"))
        cls.match_datadef <<= Wrap(new_match_datadef, cls.method("class_manage"), greedy=True)

        # handle parsing_context for function definitions
        new_stmt_lambdef = trace_attach(cls.stmt_lambdef_ref, cls.method("stmt_lambdef_handle"))
        cls.stmt_lambdef <<= Wrap(new_stmt_lambdef, cls.method("func_manage"), greedy=True)

        new_decoratable_normal_funcdef_stmt = trace_attach(
            cls.decoratable_normal_funcdef_stmt_ref,
            cls.method("decoratable_funcdef_stmt_handle"),
        )
        cls.decoratable_normal_funcdef_stmt <<= Wrap(new_decoratable_normal_funcdef_stmt, cls.method("func_manage"), greedy=True)

        new_decoratable_async_funcdef_stmt = trace_attach(
            cls.decoratable_async_funcdef_stmt_ref,
            cls.method("decoratable_funcdef_stmt_handle", is_async=True),
        )
        cls.decoratable_async_funcdef_stmt <<= Wrap(new_decoratable_async_funcdef_stmt, cls.method("func_manage"), greedy=True)

        # handle parsing_context for type aliases
        new_type_alias_stmt = trace_attach(cls.type_alias_stmt_ref, cls.method("type_alias_stmt_handle"))
        cls.type_alias_stmt <<= Wrap(new_type_alias_stmt, cls.method("type_alias_stmt_manage"), greedy=True)

        # greedy handlers (we need to know about them even if suppressed and/or they use the parsing_context)
        cls.comment <<= trace_attach(cls.comment_tokens, cls.method("comment_handle"), greedy=True)
        cls.type_param <<= trace_attach(cls.type_param_ref, cls.method("type_param_handle"), greedy=True)

        # name handlers
        cls.refname <<= attach(cls.name_ref, cls.method("name_handle"))
        cls.setname <<= attach(cls.name_ref, cls.method("name_handle", assign=True))
        cls.classname <<= trace_attach(cls.name_ref, cls.method("name_handle", assign=True, classname=True), greedy=True)

        # abnormally named handlers
        cls.moduledoc_item <<= trace_attach(cls.moduledoc, cls.method("set_moduledoc"))
        cls.endline <<= attach(cls.endline_ref, cls.method("endline_handle"))
        cls.normal_pipe_expr <<= trace_attach(cls.normal_pipe_expr_tokens, cls.method("pipe_handle"))
        cls.return_typedef <<= trace_attach(cls.return_typedef_ref, cls.method("typedef_handle"))

        # handle all atom + trailers constructs with item_handle
        cls.trailer_atom <<= trace_attach(cls.trailer_atom_ref, cls.method("item_handle"))
        cls.no_partial_trailer_atom <<= trace_attach(cls.no_partial_trailer_atom_ref, cls.method("item_handle"))
        cls.simple_assign <<= trace_attach(cls.simple_assign_ref, cls.method("item_handle"))

        # handle all string atoms with string_atom_handle
        cls.string_atom <<= trace_attach(cls.string_atom_ref, cls.method("string_atom_handle"))
        cls.f_string_atom <<= trace_attach(cls.f_string_atom_ref, cls.method("string_atom_handle"))

        # standard handlers of the form name <<= trace_attach(name_tokens, method("name_handle")) (implies name_tokens is reused)
        cls.function_call <<= trace_attach(cls.function_call_tokens, cls.method("function_call_handle"))
        cls.testlist_star_namedexpr <<= trace_attach(cls.testlist_star_namedexpr_tokens, cls.method("testlist_star_expr_handle"))
        cls.ellipsis <<= trace_attach(cls.ellipsis_tokens, cls.method("ellipsis_handle"))
        cls.f_string <<= trace_attach(cls.f_string_tokens, cls.method("f_string_handle"))

        # standard handlers of the form name <<= trace_attach(name_ref, method("name_handle"))
        cls.term <<= trace_attach(cls.term_ref, cls.method("term_handle"))
        cls.set_literal <<= trace_attach(cls.set_literal_ref, cls.method("set_literal_handle"))
        cls.set_letter_literal <<= trace_attach(cls.set_letter_literal_ref, cls.method("set_letter_literal_handle"))
        cls.import_stmt <<= trace_attach(cls.import_stmt_ref, cls.method("import_handle"))
        cls.complex_raise_stmt <<= trace_attach(cls.complex_raise_stmt_ref, cls.method("complex_raise_stmt_handle"))
        cls.augassign_stmt <<= trace_attach(cls.augassign_stmt_ref, cls.method("augassign_stmt_handle"))
        cls.kwd_augassign <<= trace_attach(cls.kwd_augassign_ref, cls.method("kwd_augassign_handle"))
        cls.dict_comp <<= trace_attach(cls.dict_comp_ref, cls.method("dict_comp_handle"))
        cls.destructuring_stmt <<= trace_attach(cls.destructuring_stmt_ref, cls.method("destructuring_stmt_handle"))
        cls.full_match <<= trace_attach(cls.full_match_ref, cls.method("full_match_handle"))
        cls.name_match_funcdef <<= trace_attach(cls.name_match_funcdef_ref, cls.method("name_match_funcdef_handle"))
        cls.op_match_funcdef <<= trace_attach(cls.op_match_funcdef_ref, cls.method("op_match_funcdef_handle"))
        cls.yield_from <<= trace_attach(cls.yield_from_ref, cls.method("yield_from_handle"))
        cls.typedef <<= trace_attach(cls.typedef_ref, cls.method("typedef_handle"))
        cls.typedef_default <<= trace_attach(cls.typedef_default_ref, cls.method("typedef_handle"))
        cls.unsafe_typedef_default <<= trace_attach(cls.unsafe_typedef_default_ref, cls.method("unsafe_typedef_handle"))
        cls.typed_assign_stmt <<= trace_attach(cls.typed_assign_stmt_ref, cls.method("typed_assign_stmt_handle"))
        cls.with_stmt <<= trace_attach(cls.with_stmt_ref, cls.method("with_stmt_handle"))
        cls.await_expr <<= trace_attach(cls.await_expr_ref, cls.method("await_expr_handle"))
        cls.cases_stmt <<= trace_attach(cls.cases_stmt_ref, cls.method("cases_stmt_handle"))
        cls.decorators <<= trace_attach(cls.decorators_ref, cls.method("decorators_handle"))
        cls.unsafe_typedef_or_expr <<= trace_attach(cls.unsafe_typedef_or_expr_ref, cls.method("unsafe_typedef_or_expr_handle"))
        cls.testlist_star_expr <<= trace_attach(cls.testlist_star_expr_ref, cls.method("testlist_star_expr_handle"))
        cls.list_expr <<= trace_attach(cls.list_expr_ref, cls.method("list_expr_handle"))
        cls.dict_literal <<= trace_attach(cls.dict_literal_ref, cls.method("dict_literal_handle"))
        cls.new_testlist_star_expr <<= trace_attach(cls.new_testlist_star_expr_ref, cls.method("new_testlist_star_expr_handle"))
        cls.anon_namedtuple <<= trace_attach(cls.anon_namedtuple_ref, cls.method("anon_namedtuple_handle"))
        cls.base_match_for_stmt <<= trace_attach(cls.base_match_for_stmt_ref, cls.method("base_match_for_stmt_handle"))
        cls.unsafe_typedef_tuple <<= trace_attach(cls.unsafe_typedef_tuple_ref, cls.method("unsafe_typedef_tuple_handle"))
        cls.funcname_typeparams <<= trace_attach(cls.funcname_typeparams_ref, cls.method("funcname_typeparams_handle"))

        # these handlers just do strict/target checking
        cls.u_string <<= trace_attach(cls.u_string_ref, cls.method("u_string_check"))
        cls.nonlocal_stmt <<= trace_attach(cls.nonlocal_stmt_ref, cls.method("nonlocal_check"))
        cls.star_assign_item <<= trace_attach(cls.star_assign_item_ref, cls.method("star_assign_item_check"))
        cls.classic_lambdef <<= trace_attach(cls.classic_lambdef_ref, cls.method("lambdef_check"))
        cls.star_sep_arg <<= trace_attach(cls.star_sep_arg_ref, cls.method("star_sep_check"))
        cls.star_sep_setarg <<= trace_attach(cls.star_sep_setarg_ref, cls.method("star_sep_check"))
        cls.slash_sep_arg <<= trace_attach(cls.slash_sep_arg_ref, cls.method("slash_sep_check"))
        cls.slash_sep_setarg <<= trace_attach(cls.slash_sep_setarg_ref, cls.method("slash_sep_check"))
        cls.endline_semicolon <<= trace_attach(cls.endline_semicolon_ref, cls.method("endline_semicolon_check"))
        cls.async_stmt <<= trace_attach(cls.async_stmt_ref, cls.method("async_stmt_check"))
        cls.async_comp_for <<= trace_attach(cls.async_comp_for_ref, cls.method("async_comp_check"))
        cls.namedexpr <<= trace_attach(cls.namedexpr_ref, cls.method("namedexpr_check"))
        cls.new_namedexpr <<= trace_attach(cls.new_namedexpr_ref, cls.method("new_namedexpr_check"))
        cls.match_dotted_name_const <<= trace_attach(cls.match_dotted_name_const_ref, cls.method("match_dotted_name_const_check"))
        cls.except_star_clause <<= trace_attach(cls.except_star_clause_ref, cls.method("except_star_clause_check"))
        cls.subscript_star <<= trace_attach(cls.subscript_star_ref, cls.method("subscript_star_check"))

        # these checking handlers need to be greedy since they can be suppressed
        cls.match_check_equals <<= trace_attach(cls.match_check_equals_ref, cls.method("match_check_equals_check"), greedy=True)

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

    def reformat(self, snip, *indices, **kwargs):
        """Post process a preprocessed snippet."""
        internal_assert("ignore_errors" in kwargs, "reformat() missing required keyword argument: 'ignore_errors'")
        if not indices:
            with self.complain_on_err():
                return self.apply_procs(self.reformatprocs, snip, reformatting=True, log=False, **kwargs)
            return snip
        else:
            internal_assert(kwargs.get("ignore_errors", False), "cannot reformat with indices and ignore_errors=False")
            return (
                (self.reformat(snip, **kwargs),)
                + tuple(len(self.reformat(snip[:index], **kwargs)) for index in indices)
            )

    def literal_eval(self, code):
        """Version of ast.literal_eval that reformats first."""
        return literal_eval(self.reformat(code, ignore_errors=False))

    def eval_now(self, code):
        """Reformat and evaluate a code snippet and return code for the result."""
        try:
            result = self.literal_eval(code)
            if result is None or isinstance(result, (bool, int, float, complex)):
                return ascii(result)
            elif isinstance(result, bytes):
                return self.wrap_str_of(result, expect_bytes=True)
            elif isinstance(result, str):
                return self.wrap_str_of(result)
            else:
                raise CoconutInternalException("failed to eval_now", code, extra="got: " + repr(result))
        except CoconutInternalException as err:
            complain(err)
            return code

    def strict_err(self, *args, **kwargs):
        """Raise a CoconutStyleError if in strict mode."""
        internal_assert("extra" not in kwargs, "cannot pass extra=... to strict_err")
        if self.strict:
            raise self.make_err(CoconutStyleError, *args, **kwargs)

    def strict_err_or_warn(self, *args, **kwargs):
        """Raises an error if in strict mode, otherwise raises a warning."""
        internal_assert("extra" not in kwargs, "cannot pass extra=... to strict_err_or_warn")
        if self.strict:
            kwargs["extra"] = "remove --strict to downgrade to a warning"
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

    def get_matcher(self, original, loc, check_var, name_list=None):
        """Get a Matcher object."""
        return Matcher(self, original, loc, check_var, name_list=name_list)

    def add_ref(self, reftype, data):
        """Add a reference and return the identifier."""
        ref = (reftype, data)
        self.refs.append(ref)
        return str(len(self.refs) - 1)

    def get_ref(self, reftype, index):
        """Retrieve a reference."""
        try:
            got_reftype, data = self.refs[int(index)]
        except (IndexError, ValueError):
            raise CoconutInternalException(
                "no reference at invalid index",
                index,
                extra="max index: {max_index}; wanted reftype: {reftype}".format(max_index=len(self.refs) - 1, reftype=reftype),
            )
        internal_assert(
            got_reftype == reftype,
            "wanted {reftype} reference; got {got_reftype} reference".format(reftype=reftype, got_reftype=got_reftype),
            extra="index: {index}; data: {data!r}".format(index=index, data=data),
        )
        return data

    def wrap_str(self, text, strchar, multiline=False):
        """Wrap a string."""
        if multiline:
            strchar *= 3
        return strwrapper + self.add_ref("str", (text, strchar)) + unwrapper

    def wrap_str_of(self, text, expect_bytes=False):
        """Wrap a string of a string."""
        text_repr = ascii(text)
        if expect_bytes:
            internal_assert(text_repr[0] == "b", "expected bytes but got str", text)
            text_repr = text_repr[1:]
        internal_assert(text_repr[0] == text_repr[-1] and text_repr[0] in ("'", '"'), "cannot wrap str of", text)
        return ("b" if expect_bytes else "") + self.wrap_str(text_repr[1:-1], text_repr[-1])

    def wrap_passthrough(self, text, multiline=True, early=False):
        """Wrap a passthrough."""
        if not multiline:
            text = text.lstrip()
        if early:
            out = early_passthrough_wrapper
        elif multiline:
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
            whitespace, base_comment = split_leading_whitespace(text)
            text = whitespace + self.reformat(base_comment, ignore_errors=False)
        return "#" + self.add_ref("comment", text) + unwrapper

    def wrap_error(self, error):
        """Create a symbol that will raise the given error in postprocessing."""
        return errwrapper + self.add_ref("error", error) + unwrapper

    def raise_or_wrap_error(self, error):
        """Raise if USE_COMPUTATION_GRAPH else wrap."""
        if USE_COMPUTATION_GRAPH:
            raise error
        else:
            return self.wrap_error(error)

    def type_ignore_comment(self):
        return self.wrap_comment(" type: ignore", reformat=False)

    def wrap_line_number(self, ln):
        """Wrap a line number."""
        return lnwrapper + str(ln) + unwrapper

    def wrap_loc(self, original, loc):
        """Wrap a location."""
        ln = lineno(loc, original)
        return self.wrap_line_number(ln)

    def apply_procs(self, procs, inputstring, log=True, **kwargs):
        """Apply processors to inputstring."""
        for get_proc in procs:
            proc = get_proc(self)
            inputstring = proc(inputstring, **kwargs)
            if log:
                logger.log_tag(getattr(proc, "__name__", proc), inputstring, multiline=True)
        return inputstring

    def pre(self, inputstring, **kwargs):
        """Perform pre-processing."""
        out = self.apply_procs(self.preprocs, str(inputstring), **kwargs)
        logger.log_tag("skips", self.skips)
        return out

    def post(self, result, **kwargs):
        """Perform post-processing."""
        internal_assert(isinstance(result, str), "got non-string parse result", result)
        return self.apply_procs(self.postprocs, result, **kwargs)

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

    def make_err(self, errtype, message, original, loc=0, ln=None, extra=None, reformat=True, include_endpoint=False, include_causes=False, **kwargs):
        """Generate an error of the specified type."""
        # move loc back to end of most recent actual text
        while loc >= 2 and original[loc - 1:loc + 1].rstrip("".join(indchars) + default_whitespace_chars) == "":
            loc -= 1

        # get endpoint and line number
        endpoint = clip(get_highest_parse_loc() + 1, min=loc) if include_endpoint else loc
        if ln is None:
            ln = self.adjust(lineno(loc, original))

        # get line indices for the error locs
        original_lines = tuple(logical_lines(original, True))
        loc_line_ind = clip(lineno(loc, original) - 1, max=len(original_lines) - 1)

        # build the source snippet that the error is referring to
        endpt_line_ind = lineno(endpoint, original) - 1
        snippet = "".join(original_lines[loc_line_ind:endpt_line_ind + 1])

        # fix error locations to correspond to the snippet
        loc_in_snip = getcol(loc, original) - 1
        endpt_in_snip = endpoint - sum(len(line) for line in original_lines[:loc_line_ind])

        # determine possible causes
        if include_causes:
            self.internal_assert(extra is None, original, loc, "make_err cannot include causes with extra")
            causes = []
            for cause, _, _ in all_matches(self.parse_err_msg, snippet[loc_in_snip:]):
                causes.append(cause)
            for cause, _, _ in all_matches(self.parse_err_msg, snippet[endpt_in_snip:]):
                if cause not in causes:
                    causes.append(cause)
            if causes:
                extra = "possible cause{s}: {causes}".format(
                    s="s" if len(causes) > 1 else "",
                    causes=", ".join(causes),
                )
            else:
                extra = None

        # reformat the snippet and fix error locations to match
        if reformat:
            snippet, loc_in_snip, endpt_in_snip = self.reformat(snippet, loc_in_snip, endpt_in_snip, ignore_errors=True)

        if extra is not None:
            kwargs["extra"] = extra
        return errtype(message, snippet, loc_in_snip, ln, endpoint=endpt_in_snip, **kwargs)

    def make_syntax_err(self, err, original):
        """Make a CoconutSyntaxError from a CoconutDeferredSyntaxError."""
        msg, loc = err.args
        return self.make_err(CoconutSyntaxError, msg, original, loc, include_endpoint=True)

    def make_parse_err(self, err, msg=None, include_ln=True, **kwargs):
        """Make a CoconutParseError from a ParseBaseException."""
        original = err.pstr
        loc = err.loc
        ln = self.adjust(err.lineno) if include_ln else None

        return self.make_err(CoconutParseError, msg, original, loc, ln, include_endpoint=True, include_causes=True, **kwargs)

    def make_internal_syntax_err(self, original, loc, msg, item, extra):
        """Make a CoconutInternalSyntaxError."""
        message = msg + ": " + repr(item)
        return self.make_err(CoconutInternalSyntaxError, message, original, loc, extra=extra, include_endpoint=True)

    def internal_assert(self, cond, original, loc, msg=None, item=None):
        """Version of internal_assert that raises CoconutInternalSyntaxErrors."""
        if not cond or callable(cond):  # avoid the overhead of another call if we know the assert will pass
            internal_assert(cond, msg, item, exc_maker=partial(self.make_internal_syntax_err, original, loc))

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
            self.streamline(parser, inputstring)
            pre_procd = self.pre(inputstring, **preargs)
            parsed = parse(parser, pre_procd)
            return self.post(parsed, **postargs)

    @contextmanager
    def parsing(self, keep_state=False):
        """Acquire the lock and reset the parser."""
        with self.lock:
            self.reset(keep_state)
            self.current_compiler[0] = self
            yield

    def streamline(self, grammar, inputstring=""):
        """Streamline the given grammar for the given inputstring."""
        if streamline_grammar_for_len is not None and len(inputstring) >= streamline_grammar_for_len:
            start_time = get_clock_time()
            prep_grammar(grammar, streamline=True)
            logger.log_lambda(
                lambda: "Streamlined {grammar} in {time} seconds (streamlined due to receiving input of length {length}).".format(
                    grammar=grammar.name,
                    time=get_clock_time() - start_time,
                    length=len(inputstring),
                ),
            )
        else:
            logger.log("No streamlining done for input of length {length}.".format(length=len(inputstring)))

    def run_final_checks(self, original, keep_state=False):
        """Run post-parsing checks to raise any necessary errors/warnings."""
        # only check for unused imports if we're not keeping state accross parses
        if not keep_state:
            for name, locs in self.unused_imports.items():
                for loc in locs:
                    ln = self.adjust(lineno(loc, original))
                    comment = self.reformat(self.comments.get(ln, ""), ignore_errors=True)
                    if not self.noqa_regex.search(comment):
                        self.strict_err_or_warn(
                            "found unused import " + repr(self.reformat(name, ignore_errors=True)) + " (add '# NOQA' to suppress)",
                            original,
                            loc,
                        )

    def parse(self, inputstring, parser, preargs, postargs, streamline=True, keep_state=False):
        """Use the parser to parse the inputstring with appropriate setup and teardown."""
        with self.parsing(keep_state):
            if streamline:
                self.streamline(parser, inputstring)
            with logger.gather_parsing_stats():
                pre_procd = None
                try:
                    pre_procd = self.pre(inputstring, keep_state=keep_state, **preargs)
                    parsed = parse(parser, pre_procd, inner=False)
                    out = self.post(parsed, keep_state=keep_state, **postargs)
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
            self.run_final_checks(pre_procd, keep_state)
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
        kept_lines = inputstring.splitlines()
        self.num_lines = len(kept_lines)
        if self.keep_lines:
            self.kept_lines = kept_lines
        inputstring = "\n".join(kept_lines)
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
                internal_assert(x == len(inputstring), "invalid index in str_proc", (inputstring, x))
                c = "\n"

            if hold is not None:
                if len(hold) == 1:  # hold == [_comment]
                    if c == "\n":
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
                        raise self.make_err(CoconutSyntaxError, "invalid number of closing " + repr(hold[_start][0]) + "s", inputstring, x, reformat=False)
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
                if c == found[0] and len(found) < 3:
                    found += c
                elif len(found) == 1:  # found == "_"
                    hold = ["", found, None]  # [_contents, _start, _stop]
                    found = None
                    x -= 1
                elif len(found) == 2:  # found == "__"
                    out.append(self.wrap_str("", found[0], False))
                    found = None
                    x -= 1
                else:  # found == "___"
                    internal_assert(len(found) == 3, "invalid number of string starts", found)
                    hold = ["", found, None]  # [_contents, _start, _stop]
                    found = None
                    x -= 1
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

    def operator_proc(self, inputstring, keep_state=False, **kwargs):
        """Process custom operator definitions."""
        out = []
        skips = self.copy_skips()
        for i, raw_line in enumerate(logical_lines(inputstring, keep_newlines=True)):
            ln = i + 1
            base_line = rem_comment(raw_line)
            stripped_line = base_line.lstrip()

            imp_from = None
            op = try_parse(self.operator_stmt, stripped_line)
            if op is None:
                op_imp_toks = try_parse(self.from_import_operator, base_line)
                if op_imp_toks is not None:
                    imp_from, op = op_imp_toks
            if op is not None:
                op = op.strip()

            op_name = None
            # whitespace, just the word operator, or a backslash continuation means it's not
            #  an operator declaration (e.g. it's something like "operator = 1" instead)
            if op is not None and op and not op.endswith("\\") and not self.whitespace_regex.search(op):
                if stripped_line != base_line:
                    raise self.make_err(CoconutSyntaxError, "operator declaration statement only allowed at top level", raw_line, ln=self.adjust(ln))
                if op in all_keywords:
                    raise self.make_err(CoconutSyntaxError, "cannot redefine keyword " + repr(op), raw_line, ln=self.adjust(ln))
                if op.isdigit():
                    raise self.make_err(CoconutSyntaxError, "cannot redefine number " + repr(op), raw_line, ln=self.adjust(ln))
                if self.existing_operator_regex.match(op):
                    raise self.make_err(CoconutSyntaxError, "cannot redefine existing operator " + repr(op), raw_line, ln=self.adjust(ln))
                for sym in reserved_compiler_symbols + reserved_command_symbols:
                    if sym in op:
                        sym_repr = ascii(sym.replace(strwrapper, '"'))
                        raise self.make_err(CoconutSyntaxError, "invalid custom operator", raw_line, ln=self.adjust(ln), extra="cannot contain " + sym_repr)
                op_name = custom_op_var
                for c in op:
                    op_name += "_U" + hex(ord(c))[2:]
                # if we're keeping state, then we're at the interpreter, so to support reevaluation
                #  (which the interpreter often does), we need to allow repeated operator declarations
                if not keep_state and op_name in self.operators:
                    raise self.make_err(CoconutSyntaxError, "custom operator already declared", raw_line, ln=self.adjust(ln))
                self.operators.append(op_name)
                self.operator_repl_table.append((
                    compile_regex(r"\(\s*" + re.escape(op) + r"\s*\)"),
                    None,
                    "(" + op_name + ")",
                ))
                any_delimiter = r"|".join(re.escape(sym) for sym in delimiter_symbols)
                self.operator_repl_table.append((
                    compile_regex(r"(^|\s|(?<!\\)\b|" + any_delimiter + r")" + re.escape(op) + r"(?=\s|\b|$|" + any_delimiter + r")"),
                    1,
                    "`" + op_name + "`",
                ))

            if op_name is None:
                new_line = raw_line
                for repl, repl_type, repl_to in self.operator_repl_table:
                    if repl_type is None:
                        def sub_func(match):
                            return repl_to
                    elif repl_type == 1:
                        def sub_func(match):
                            return match.group(1) + repl_to
                    else:
                        raise CoconutInternalException("invalid operator_repl_table repl_type", repl_type)
                    new_line = repl.sub(sub_func, new_line)
                out.append(new_line)
            elif imp_from is not None:
                out.append("from " + imp_from + " import " + op_name + "\n")
            else:
                skips = addskip(skips, self.adjust(ln))

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
        lines = tuple(logical_lines(inputstring))
        new = []  # new lines
        opens = []  # (line, col, adjusted ln) at which open parens were seen, newest first
        current = None  # indentation level of previous line
        levels = []  # indentation levels of all previous blocks, newest at end
        skips = self.copy_skips()

        for ln in range(1, len(lines) + 1):  # ln is 1-indexed
            line = lines[ln - 1]  # lines is 0-indexed
            line_rstrip = line.rstrip()
            if line != line_rstrip:
                self.strict_err("found trailing whitespace", line, len(line), self.adjust(ln))
                line = line_rstrip
            last_line, last_comment = split_comment(new[-1]) if new else (None, None)

            if not line or line.lstrip().startswith("#"):  # blank line or comment
                if opens:  # inside parens
                    skips = addskip(skips, self.adjust(ln))
                else:
                    new.append(line)
            elif last_line is not None and last_line.endswith("\\"):  # backslash line continuation
                self.strict_err("found backslash continuation (use parenthetical continuation instead)", new[-1], len(last_line), self.adjust(ln - 1))
                skips = addskip(skips, self.adjust(ln))
                new[-1] = last_line[:-1] + non_syntactic_newline + line + last_comment
            elif opens:  # inside parens
                skips = addskip(skips, self.adjust(ln))
                new[-1] = last_line + non_syntactic_newline + line + last_comment
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
            last_line = rem_comment(new[-1])
            if last_line.endswith("\\"):
                raise self.make_err(CoconutSyntaxError, "illegal final backslash continuation", new[-1], len(last_line), self.adjust(len(new)))
            if opens:
                open_line, adj_ln = opens[0]
                raise self.make_err(CoconutSyntaxError, "unclosed open parenthesis", open_line, 0, adj_ln)
        new.append(closeindent * len(levels))
        return "\n".join(new)

    @property
    def tabideal(self):
        """Local tabideal."""
        return 1 if self.minify else tabideal

    def reind_proc(self, inputstring, ignore_errors=False, **kwargs):
        """Add back indentation."""
        out = []
        level = 0

        next_line_is_fake = False
        for line in inputstring.splitlines(True):
            is_fake = next_line_is_fake
            next_line_is_fake = line.endswith("\f") and line.rstrip("\f") == line.rstrip()

            line, comment = split_comment(line.strip())

            indent, line = split_leading_indent(line)
            level += ind_change(indent)

            if line:
                line = " " * self.tabideal * (level + int(is_fake)) + line

            line, indent = split_trailing_indent(line)
            level += ind_change(indent)

            # handle indentation markers interleaved with comment/endline markers
            comment, change_in_level = rem_and_count_indents(comment)
            level += change_in_level

            line = (line + comment).rstrip()
            out.append(line)

        if not ignore_errors and level != 0:
            logger.log_lambda(lambda: "failed to reindent:\n" + "\n".join(out))
            complain(CoconutInternalException("non-zero final indentation level ", level))
        return "\n".join(out)

    def ln_comment(self, ln):
        """Get an end line comment."""
        # CoconutInternalExceptions should always be caught and complained here
        if self.keep_lines:
            internal_assert(
                # keep this as a lambda to prevent it from breaking release builds
                lambda: 1 <= ln <= len(self.kept_lines) + 2,
                "out of bounds line number",
                ln,
                "not in range [1, " + str(len(self.kept_lines) + 2) + "]",
            )
            if ln >= len(self.kept_lines) + 1:  # trim too large
                lni = -1
            else:
                lni = ln - 1

        if self.line_numbers and self.keep_lines:
            if self.minify:
                comment = str(ln) + " " + self.kept_lines[lni]
            else:
                comment = str(ln) + ": " + self.kept_lines[lni]
        elif self.keep_lines:
            if self.minify:
                comment = self.kept_lines[lni]
            else:
                comment = " " + self.kept_lines[lni]
        elif self.line_numbers:
            if self.minify:
                comment = str(ln)
            else:
                comment = str(ln) + " (line in Coconut source)"
        else:
            return ""

        return self.wrap_comment(comment, reformat=False)

    def endline_repl(self, inputstring, reformatting=False, ignore_errors=False, **kwargs):
        """Add end of line comments."""
        out = []
        ln = 1  # line number in pre-processed original
        for line in logical_lines(inputstring):
            add_one_to_ln = False
            try:

                # extract line number information
                lnwrapper_split = line.split(lnwrapper)
                has_wrapped_ln = len(lnwrapper_split) > 1
                if has_wrapped_ln:
                    line = lnwrapper_split.pop(0).rstrip()
                    for ln_str in lnwrapper_split:
                        internal_assert(ln_str.endswith(unwrapper), "invalid wrapped line number in", line)
                        new_ln = int(ln_str[:-1])
                        # note that it is possible for this to decrease the line number,
                        #  since there are circumstances where the compiler will reorder lines
                        ln = new_ln
                        add_one_to_ln = True

                # add comments based on source line number
                src_ln = self.adjust(ln)
                if not reformatting or has_wrapped_ln:
                    line += self.comments.get(src_ln, "")
                if not reformatting and line.rstrip() and not line.lstrip().startswith("#"):
                    line += self.ln_comment(src_ln)

            except CoconutInternalException as err:
                if not ignore_errors:
                    complain(err)

            out.append(line)
            if add_one_to_ln and ln <= self.num_lines - 1:
                ln += 1
        return "\n".join(out)

    def base_passthrough_repl(self, inputstring, wrap_char, ignore_errors=False, **kwargs):
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
                    elif c != wrap_char or index:
                        out.append(wrap_char + index)
                        if c is not None:
                            out.append(c)
                        index = None
                elif c is not None:
                    if c == wrap_char:
                        index = ""
                    else:
                        out.append(c)

            except CoconutInternalException as err:
                if not ignore_errors:
                    complain(err)
                if index is not None:
                    out.append(wrap_char + index)
                    index = None
                if c is not None:
                    out.append(c)

        return "".join(out)

    def str_repl(self, inputstring, ignore_errors=False, **kwargs):
        """Add back strings and comments."""
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
                if not ignore_errors:
                    complain(err)
                if comment is not None:
                    internal_assert(string is None, "invalid detection of string and comment markers in", inputstring)
                    out.append("#" + comment)
                    comment = None
                if string is not None:
                    out.append(strwrapper + string)
                    string = None
                if c is not None:
                    out.append(c)

        return "".join(out)

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

            # we have to use func_name not func_store here since we use this when we fail to verify that func_name is func_store
            if self.no_tco:
                tco_recurse = "return " + func_name + "(" + args + ")"
            else:
                tco_recurse = "return _coconut_tail_call(" + func_name + (", " + args if args else "") + ")"

            if not func_args or func_args == args:
                tre_recurse = "continue"
            elif mock_var is None:
                tre_recurse = tuple_str_of_str(func_args) + " = " + tuple_str_of_str(args) + "\ncontinue"
            else:
                tre_recurse = tuple_str_of_str(func_args) + " = " + mock_var + "(" + args + ")" + "\ncontinue"

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

    def detect_is_gen(self, raw_lines):
        """Determine if the given function code is for a generator."""
        level = 0  # indentation level
        func_until_level = None  # whether inside of an inner function

        # normalize_indent_markers is required for func_until_level to work
        for line in normalize_indent_markers(raw_lines):
            indent, line, dedent = split_leading_trailing_indent(line)

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

            level += ind_change(dedent)

        return False

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
        self.internal_assert(not (not normal_func and (attempt_tre or attempt_tco)), original, loc, "cannot tail call optimize async/generator functions")

        if (
            not normal_func
            # don't transform generator returns if they're supported
            and (not is_gen or self.target_info >= (3, 3))
            # don't transform async returns if they're supported
            and (not is_async or self.target_info >= (3, 5))
        ):
            func_code = "".join(raw_lines)
            return func_code, tco, tre

        # normalize_indent_markers is required for ..._until_level to work
        for line in normalize_indent_markers(raw_lines):
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

    def proc_funcdef(self, original, loc, decorators, funcdef, is_async, in_method, is_stmt_lambda):
        """Determines if TCO or TRE can be done and if so does it,
        handles dotted function names, and universalizes async functions."""
        # process tokens
        raw_lines = list(logical_lines(funcdef, True))
        def_stmt = raw_lines.pop(0)

        # detect addpattern functions
        if def_stmt.startswith("addpattern def"):
            def_stmt = def_stmt[len("addpattern "):]
            addpattern = True
        elif def_stmt.startswith("def"):
            addpattern = False
        else:
            raise CoconutInternalException("invalid function definition statement", funcdef)

        # extract information about the function
        with self.complain_on_err():
            try:
                split_func_tokens = parse(self.split_func, def_stmt)

                self.internal_assert(len(split_func_tokens) == 2, original, loc, "invalid function definition splitting tokens", split_func_tokens)
                func_name, func_arg_tokens = split_func_tokens

                func_paramdef = ", ".join("".join(arg) for arg in func_arg_tokens)

                # arguments that should be used to call the function; must be in the order in which they're defined
                func_args = []
                for arg in func_arg_tokens:
                    if len(arg) > 1 and arg[0] in ("*", "**"):
                        func_args.append(arg[1])
                    elif arg[0] not in ("*", "/"):
                        func_args.append(arg[0])
                func_args = ", ".join(func_args)
            except BaseException:
                func_name = None
                raise

        # run target checks if func info extraction succeeded
        if func_name is not None:
            # raises DeferredSyntaxErrors which shouldn't be complained
            pos_only_args, req_args, default_args, star_arg, kwd_only_args, dubstar_arg = split_args_list(func_arg_tokens, loc)
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
        is_match_func = func_paramdef == "*{match_to_args_var}, **{match_to_kwargs_var}".format(
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

        # detect generators
        is_gen = self.detect_is_gen(raw_lines)

        # handle async functions
        if is_async:
            if not self.target:
                raise self.make_err(
                    CoconutTargetError,
                    "async function definition requires a specific target",
                    original, loc,
                    target="sys",
                )
            elif is_gen and self.target_info < (3, 6):
                raise self.make_err(
                    CoconutTargetError,
                    "found Python 3.6 async generator",
                    original, loc,
                    target="36",
                )
            elif self.target_info >= (3, 5):
                def_stmt = "async " + def_stmt
            else:
                decorators += "@_coconut.asyncio.coroutine\n"

            func_code, _, _ = self.transform_returns(original, loc, raw_lines, is_async=True, is_gen=is_gen)

        # handle normal functions
        else:
            attempt_tre = (
                func_name is not None
                and not is_gen
                and not in_method
                and not is_stmt_lambda
                and not decorators
            )
            if attempt_tre:
                if func_args and func_args != func_paramdef:
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
                # build mock to handle arg rebinding
                if mock_var is None:
                    mock_def = ""
                else:
                    # find defaults and replace them with sentinels
                    #  (note that we can't put the original defaults in the actual defaults here,
                    #  since we don't know if func_store will be available at mock definition)
                    names_with_defaults = []
                    mock_default_args = []
                    for name, default in default_args:
                        mock_default_args.append((name, "_coconut_sentinel"))
                        names_with_defaults.append(name)
                    mock_kwd_only_args = []
                    for name, default in kwd_only_args:
                        if default is None:
                            mock_kwd_only_args.append((name, None))
                        else:
                            mock_kwd_only_args.append((name, "_coconut_sentinel"))
                            names_with_defaults.append(name)

                    # create mock def that uses original function defaults
                    mock_paramdef = reconstitute_paramdef(pos_only_args, req_args, mock_default_args, star_arg, mock_kwd_only_args, dubstar_arg)
                    mock_body_lines = []
                    for i, name in enumerate(names_with_defaults):
                        mock_body_lines.append(
                            "if {name} is _coconut_sentinel: {name} = {orig_func}.__defaults__[{i}]".format(
                                name=name,
                                orig_func=func_store + ("._coconut_tco_func" if tco else ""),
                                i=i,
                            ),
                        )
                    mock_body_lines.append("return " + tuple_str_of_str(func_args))
                    mock_def = handle_indentation(
                        """
def {mock_var}({mock_paramdef}):
    {mock_body}
                        """,
                        add_newline=True,
                    ).format(
                        mock_var=mock_var,
                        mock_paramdef=mock_paramdef,
                        mock_body="\n".join(mock_body_lines),
                    )

                # assemble tre'd function
                comment, rest = split_leading_comment(func_code)
                indent, base, dedent = split_leading_trailing_indent(rest, 1)
                base, base_dedent = split_trailing_indent(base)
                docstring, base = self.split_docstring(base)
                func_code = (
                    comment + indent
                    + (docstring + "\n" if docstring is not None else "")
                    + mock_def
                    + "while True:\n"
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

    def deferred_code_proc(self, inputstring, add_code_at_start=False, ignore_names=(), **kwargs):
        """Process all forms of previously deferred code. All such deferred code needs to be handled here so we can properly handle nested deferred code."""
        # compile add_code_before regexes
        for name in self.add_code_before:
            if name not in self.add_code_before_regexes:
                self.add_code_before_regexes[name] = compile_regex(r"\b%s\b" % (name,))

        out = []
        for raw_line in inputstring.splitlines(True):
            bef_ind, line, aft_ind = split_leading_trailing_indent(raw_line)

            # handle early passthroughs
            line = self.base_passthrough_repl(line, wrap_char=early_passthrough_wrapper, **kwargs)

            # look for deferred errors
            if errwrapper in raw_line:
                err_ref = raw_line.split(errwrapper, 1)[1].split(unwrapper, 1)[0]
                raise self.get_ref("error", err_ref)

            # look for functions
            if line.startswith(funcwrapper):
                func_id = int(line[len(funcwrapper):])
                original, loc, decorators, funcdef, is_async, in_method, is_stmt_lambda = self.get_ref("func", func_id)

                # process inner code
                decorators = self.deferred_code_proc(decorators, add_code_at_start=True, ignore_names=ignore_names, **kwargs)
                funcdef = self.deferred_code_proc(funcdef, ignore_names=ignore_names, **kwargs)

                # handle any non-function code that was added before the funcdef
                pre_def_lines = []
                post_def_lines = []
                funcdef_lines = list(logical_lines(funcdef, True))
                for i, line in enumerate(funcdef_lines):
                    if self.def_regex.match(line):
                        pre_def_lines = funcdef_lines[:i]
                        post_def_lines = funcdef_lines[i:]
                        break
                internal_assert(post_def_lines, "no def statement found in funcdef", funcdef)

                out.append(bef_ind)
                out.extend(pre_def_lines)
                out.append(self.proc_funcdef(original, loc, decorators, "".join(post_def_lines), is_async, in_method, is_stmt_lambda))
                out.append(aft_ind)

            # look for add_code_before regexes
            else:
                for name, raw_code in ordered_items(self.add_code_before):
                    if name in ignore_names:
                        continue

                    regex = self.add_code_before_regexes[name]
                    replacement = self.add_code_before_replacements.get(name)

                    if replacement is None:
                        saw_name = regex.search(line)
                    else:
                        line, saw_name = regex.subn(lambda match: replacement, line)

                    if saw_name:
                        # process inner code
                        code_to_add = self.deferred_code_proc(raw_code, ignore_names=ignore_names + (name,), **kwargs)

                        # add code and update indents
                        if add_code_at_start:
                            out.insert(0, code_to_add + "\n")
                        else:
                            out.append(bef_ind)
                            out.append(code_to_add)
                            out.append("\n")
                            bef_ind = ""

                out.append(bef_ind)
                out.append(line)
                out.append(aft_ind)

        return "".join(out)

    def header_proc(self, inputstring, header="file", initial="initial", use_hash=None, **kwargs):
        """Add the header."""
        pre_header = self.getheader(initial, use_hash=use_hash, polish=False)
        main_header = self.getheader(header, polish=False)
        if self.minify:
            main_header = minify_header(main_header)
        return pre_header + self.docstring + main_header + inputstring

    def polish(self, inputstring, final_endline=True, **kwargs):
        """Does final polishing touches."""
        return inputstring.rstrip() + ("\n" if final_endline else "")

# end: PROCESSORS
# -----------------------------------------------------------------------------------------------------------------------
# HANDLERS:
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
                if star_args:
                    # if we've already seen a star arg, convert this pos arg to a star arg
                    star_args.append("*(" + argstr + ",)")
                elif kwd_args or dubstar_args:
                    raise CoconutDeferredSyntaxError("positional arguments must come before keyword arguments", loc)
                else:
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

        Return (type, split) where split is:
            - (expr,) for expression
            - (func, pos_args, kwd_args) for partial
            - (name, args) for attr/method
            - (op, args)+ for itemgetter
            - (op, arg) for right op partial
        """
        # list implies artificial tokens, which must be expr
        if isinstance(tokens, list) or "expr" in tokens:
            internal_assert(len(tokens) == 1, "invalid pipe item", tokens)
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
        elif "op partial" in tokens:
            inner_toks, = tokens
            if "left partial" in inner_toks:
                arg, op = inner_toks
                return "partial", (op, arg, "")
            elif "right partial" in inner_toks:
                op, arg = inner_toks
                return "right op partial", (op, arg)
            else:
                raise CoconutInternalException("invalid op partial tokens in pipe_item", inner_toks)
        else:
            raise CoconutInternalException("invalid pipe item tokens", tokens)

    def pipe_handle(self, original, loc, tokens, **kwargs):
        """Process pipe calls."""
        self.internal_assert(set(kwargs) <= set(("top",)), original, loc, "unknown pipe_handle keyword arguments", kwargs)
        top = kwargs.get("top", True)
        if len(tokens) == 1:
            item = tokens.pop()
            if not top:  # defer to other pipe_handle call
                return item

            # we've only been given one operand, so we can't do any optimization, so just produce the standard object
            name, split_item = self.pipe_item_split(item, loc)
            if name == "expr":
                expr, = split_item
                return expr
            elif name == "partial":
                self.internal_assert(len(split_item) == 3, original, loc)
                return "_coconut.functools.partial(" + join_args(split_item) + ")"
            elif name == "attrgetter":
                return attrgetter_atom_handle(loc, item)
            elif name == "itemgetter":
                return itemgetter_handle(item)
            elif name == "right op partial":
                return partial_op_item_handle(item)
            else:
                raise CoconutInternalException("invalid split pipe item", split_item)

        else:
            item, op = tokens.pop(), tokens.pop()
            direction, stars, none_aware = pipe_info(op)
            star_str = "*" * stars

            if direction == "backwards":
                # for backwards pipes, we just reuse the machinery for forwards pipes
                inner_item = self.pipe_handle(original, loc, tokens, top=False)
                if isinstance(inner_item, str):
                    inner_item = [inner_item]  # artificial pipe item
                return self.pipe_handle(original, loc, [item, "|" + ("?" if none_aware else "") + star_str + ">", inner_item])

            elif none_aware:
                # for none_aware forward pipes, we wrap the normal forward pipe in a lambda
                pipe_expr = self.pipe_handle(original, loc, [[none_coalesce_var], "|" + star_str + ">", item])
                # := changes meaning inside lambdas, so we must disallow it when wrapping
                #  user expressions in lambdas (and naive string analysis is safe here)
                if ":=" in pipe_expr:
                    raise CoconutDeferredSyntaxError("illegal assignment expression in a None-coalescing pipe", loc)
                return "(lambda {x}: None if {x} is None else {pipe})({subexpr})".format(
                    x=none_coalesce_var,
                    pipe=pipe_expr,
                    subexpr=self.pipe_handle(original, loc, tokens),
                )

            elif direction == "forwards":
                # if this is an implicit partial, we have something to apply it to, so optimize it
                name, split_item = self.pipe_item_split(item, loc)
                subexpr = self.pipe_handle(original, loc, tokens)

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
                    self.internal_assert(len(split_item) % 2 == 0, original, loc, "invalid itemgetter pipe tokens", split_item)
                    out = subexpr
                    for i in range(0, len(split_item), 2):
                        op, args = split_item[i:i + 2]
                        if op == "[":
                            fmtstr = "({x})[{args}]"
                        elif op == "$[":
                            fmtstr = "_coconut_iter_getitem({x}, ({args}))"
                        else:
                            raise CoconutInternalException("pipe into invalid implicit itemgetter operation", op)
                        out = fmtstr.format(x=out, args=args)
                    return out
                elif name == "right op partial":
                    if stars:
                        raise CoconutDeferredSyntaxError("cannot star pipe into operator partial", loc)
                    op, arg = split_item
                    return "({op})({x}, {arg})".format(op=op, x=subexpr, arg=arg)
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
                    out = "_coconut.functools.partial(_coconut_iter_getitem, " + out + ")"
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
                    out = "_coconut_iter_getitem(" + out + ", " + trailer[1] + ")"
                elif trailer[0] == "$(":
                    args = trailer[1][1:-1]
                    if not args:
                        raise CoconutDeferredSyntaxError("a partial application argument is required", loc)
                    out = "_coconut.functools.partial(" + out + ", " + args + ")"
                elif trailer[0] == "$[":
                    out = "_coconut_iter_getitem(" + out + ", " + trailer[1] + ")"
                elif trailer[0] == "$(?":
                    pos_args, star_args, base_kwd_args, dubstar_args = self.split_function_call(trailer[1], loc)
                    has_question_mark = False

                    argdict_pairs = []
                    for i, arg in enumerate(pos_args):
                        if arg == "?":
                            has_question_mark = True
                        else:
                            argdict_pairs.append(str(i) + ": " + arg)

                    pos_kwargs = []
                    kwd_args = []
                    for i, arg in enumerate(base_kwd_args):
                        if arg.endswith("=?"):
                            has_question_mark = True
                            pos_kwargs.append(arg[:-2])
                        else:
                            kwd_args.append(arg)

                    extra_args_str = join_args(star_args, kwd_args, dubstar_args)
                    if not has_question_mark:
                        raise CoconutInternalException("no question mark in question mark partial", trailer[1])
                    elif argdict_pairs or pos_kwargs or extra_args_str:
                        out = (
                            "_coconut_partial("
                            + out
                            + ", {" + ", ".join(argdict_pairs) + "}"
                            + ", " + str(len(pos_args))
                            + ", " + tuple_str_of(pos_kwargs, add_quotes=True)
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
        moduledoc, endline = tokens
        self.docstring = self.reformat(moduledoc, ignore_errors=False) + "\n\n"
        return endline

    def yield_from_handle(self, tokens):
        """Process Python 3.3 yield from."""
        expr, = tokens
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
                expr=expr,
                yield_from_var=self.get_temp_var("yield_from"),
                yield_err_var=self.get_temp_var("yield_err"),
                ret_val_name=ret_val_name,
            )
            return ret_val_name
        else:
            return "yield from " + expr

    def endline_handle(self, original, loc, tokens):
        """Add line number information to end of line."""
        endline, = tokens
        lines = endline.splitlines(True)
        if self.minify:
            lines = lines[0]
        out = []
        ln = lineno(loc, original)
        for endline in lines:
            out.append(self.wrap_line_number(ln) + endline)
            ln += 1
        return "".join(out)

    def comment_handle(self, original, loc, tokens):
        """Store comment in comments."""
        comment_marker, = tokens
        ln = self.adjust(lineno(loc, original))
        if ln in self.comments:
            self.comments[ln] += " " + comment_marker
        else:
            self.comments[ln] = comment_marker
        return ""

    def kwd_augassign_handle(self, original, loc, tokens):
        """Process global/nonlocal augmented assignments."""
        name, _ = tokens
        return name + "\n" + self.augassign_stmt_handle(original, loc, tokens)

    def augassign_stmt_handle(self, original, loc, tokens):
        """Process augmented assignments."""
        name, augassign = tokens

        if "pipe" in augassign:
            pipe_op, partial_item = augassign
            pipe_tokens = [ParseResults([name], name="expr"), pipe_op, partial_item]
            return name + " = " + self.pipe_handle(original, loc, pipe_tokens)

        self.internal_assert("simple" in augassign, original, loc, "invalid augmented assignment rhs tokens", augassign)
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
        decorators, name, paramdefs, classlist_toks, body = tokens

        out = "".join(paramdefs) + decorators + "class " + name

        # handle classlist
        base_classes = []
        if classlist_toks:
            pos_args, star_args, kwd_args, dubstar_args = self.split_function_call(classlist_toks, loc)

            # check for just inheriting from object
            if (
                len(pos_args) == 1
                and pos_args[0] == "object"
                and not star_args
                and not kwd_args
                and not dubstar_args
            ):
                self.strict_err_or_warn("unnecessary inheriting from object (Coconut does this automatically)", original, loc)

            # universalize if not Python 3
            if not self.target.startswith("3"):

                if star_args:
                    pos_args += ["_coconut_handle_cls_stargs(" + join_args(star_args) + ")"]
                    star_args = ()

                if kwd_args or dubstar_args:
                    out = "@_coconut_handle_cls_kwargs(" + join_args(kwd_args, dubstar_args) + ")\n" + out
                    kwd_args = dubstar_args = ()

            base_classes.append(join_args(pos_args, star_args, kwd_args, dubstar_args))

        if paramdefs:
            base_classes.append(self.get_generic_for_typevars())

        if not classlist_toks and not self.target.startswith("3"):
            base_classes.append("_coconut.object")

        out += "(" + ", ".join(base_classes) + ")" + body

        # add override detection
        if self.target_info < (3, 6):
            out += "_coconut_call_set_names(" + name + ")\n"

        return out

    def match_datadef_handle(self, original, loc, tokens):
        """Process pattern-matching data blocks."""
        if len(tokens) == 4:
            decorators, name, match_tokens, stmts = tokens
            inherit = None
        elif len(tokens) == 5:
            decorators, name, match_tokens, inherit, stmts = tokens
        else:
            raise CoconutInternalException("invalid match_datadef tokens", tokens)

        if len(match_tokens) == 1:
            matches, = match_tokens
            cond = None
        elif len(match_tokens) == 2:
            matches, cond = match_tokens
        else:
            raise CoconutInternalException("invalid pattern-matching tokens in data", match_tokens)

        check_var = self.get_temp_var("match_check")
        matcher = self.get_matcher(original, loc, check_var, name_list=[])

        pos_only_args, req_args, default_args, star_arg, kwd_only_args, dubstar_arg = split_args_list(matches, loc)
        matcher.match_function(match_to_args_var, match_to_kwargs_var, pos_only_args, req_args + default_args, star_arg, kwd_only_args, dubstar_arg)

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

        namedtuple_call = self.make_namedtuple_call(name, matcher.name_list)
        return self.assemble_data(decorators, name, namedtuple_call, inherit, extra_stmts, stmts, matcher.name_list)

    def datadef_handle(self, loc, tokens):
        """Process data blocks."""
        if len(tokens) == 5:
            decorators, name, paramdefs, original_args, stmts = tokens
            inherit = None
        elif len(tokens) == 6:
            decorators, name, paramdefs, original_args, inherit, stmts = tokens
        else:
            raise CoconutInternalException("invalid datadef tokens", tokens)

        all_args = []  # string definitions for all args
        base_args = []  # names of all the non-starred args
        req_args = 0  # number of required arguments
        starred_arg = None  # starred arg if there is one else None
        saw_defaults = False  # whether there have been any default args so far
        types = {}  # arg position to typedef for arg
        for i, arg in enumerate(original_args):

            star, default, typedef = False, None, None
            if "name" in arg:
                argname, = arg
            elif "default" in arg:
                argname, default = arg
            elif "star" in arg:
                argname, = arg
                star = True
            elif "type" in arg:
                argname, typedef = arg
            elif "type default" in arg:
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
    result = _self._make(kwds.pop("{arg}", _self))
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
        namedtuple_call = self.make_namedtuple_call(name, namedtuple_args, types)

        return self.assemble_data(decorators, name, namedtuple_call, inherit, extra_stmts, stmts, namedtuple_args, paramdefs)

    def make_namedtuple_call(self, name, namedtuple_args, types=None):
        """Construct a namedtuple call."""
        if types:
            wrapped_types = [
                self.wrap_typedef(types.get(i, "_coconut.typing.Any"), for_py_typedef=False)
                for i in range(len(namedtuple_args))
            ]
            if name is None:
                return "_coconut_mk_anon_namedtuple(" + tuple_str_of(namedtuple_args, add_quotes=True) + ", " + tuple_str_of(wrapped_types) + ")"
            else:
                return '_coconut.typing.NamedTuple("' + name + '", [' + ", ".join(
                    '("' + argname + '", ' + wrapped_type + ")"
                    for argname, wrapped_type in zip(namedtuple_args, wrapped_types)
                ) + "])"
        else:
            if name is None:
                return "_coconut_mk_anon_namedtuple(" + tuple_str_of(namedtuple_args, add_quotes=True) + ")"
            else:
                return '_coconut.collections.namedtuple("' + name + '", ' + tuple_str_of(namedtuple_args, add_quotes=True) + ')'

    def assemble_data(self, decorators, name, namedtuple_call, inherit, extra_stmts, stmts, match_args, paramdefs=()):
        """Create a data class definition from the given components."""
        # create class
        out = (
            "".join(paramdefs)
            + decorators
            + "class " + name + "("
            + namedtuple_call
            + (", " + inherit if inherit is not None else "")
            + (", " + self.get_generic_for_typevars() if paramdefs else "")
            + (", _coconut.object" if not self.target.startswith("3") else "")
            + "):\n"
            + openindent
        )

        # add universal statements
        all_extra_stmts = handle_indentation(
            """
{is_data_var} = True
__slots__ = ()
def __add__(self, other): return _coconut.NotImplemented
def __mul__(self, other): return _coconut.NotImplemented
def __rmul__(self, other): return _coconut.NotImplemented
__ne__ = _coconut.object.__ne__
def __eq__(self, other):
    return self.__class__ is other.__class__ and _coconut.tuple.__eq__(self, other)
def __hash__(self):
    return _coconut.tuple.__hash__(self) ^ hash(self.__class__)
            """,
            add_newline=True,
        ).format(
            is_data_var=is_data_var,
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

    def anon_namedtuple_handle(self, tokens):
        """Handle anonymous named tuples."""
        names = []
        types = {}
        items = []
        for i, tok in enumerate(tokens):
            if len(tok) == 2:
                name, item = tok
            elif len(tok) == 3:
                name, typedef, item = tok
                types[i] = typedef
            else:
                raise CoconutInternalException("invalid anonymous named item", tok)
            names.append(name)
            items.append(item)

        namedtuple_call = self.make_namedtuple_call(None, names, types)
        return namedtuple_call + "(" + ", ".join(items) + ")"

    def single_import(self, path, imp_as, type_ignore=False):
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

        if type_ignore:
            for i, line in enumerate(out):
                out[i] = line + self.type_ignore_comment()

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
            type_ignore = False
            path = imp.split(".")
            for i in reversed(range(1, len(path) + 1)):
                base, exts = ".".join(path[:i]), path[i:]
                clean_base = base.replace("/", "")
                if clean_base in py3_to_py2_stdlib:
                    old_imp, version_check = py3_to_py2_stdlib[clean_base]
                    if old_imp.endswith("#"):
                        type_ignore = True
                        old_imp = old_imp[:-1]
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
            importmap.append((paths, imp_as, type_ignore))

        stmts = []
        for paths, imp_as, type_ignore in importmap:
            if len(paths) == 1:
                more_stmts = self.single_import(paths[0], imp_as)
                stmts.extend(more_stmts)
            else:
                old_imp, new_imp, version_check = paths
                # we have to do this craziness to get mypy to statically handle the version check
                stmts.append(
                    handle_indentation("""
try:
    {store_var} = sys
except _coconut.NameError:
    {store_var} = _coconut_sentinel
sys = _coconut_sys
if sys.version_info >= {version_check}:
    {new_imp}
else:
    {old_imp}
if {store_var} is not _coconut_sentinel:
    sys = {store_var}
                """).format(
                        store_var=self.get_temp_var("sys"),
                        version_check=version_check,
                        new_imp="\n".join(self.single_import(new_imp, imp_as)),
                        # should only type: ignore the old import
                        old_imp="\n".join(self.single_import(old_imp, imp_as, type_ignore=type_ignore)),
                    ),
                )
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
        for imp_name in imported_names(imports):
            self.unused_imports[imp_name].append(loc)
        return self.universal_import(imports, imp_from=imp_from)

    def complex_raise_stmt_handle(self, tokens):
        """Process Python 3 raise from statement."""
        raise_expr, from_expr = tokens
        if self.target.startswith("3"):
            return "raise " + raise_expr + " from " + from_expr
        else:
            raise_from_var = self.get_temp_var("raise_from")
            return (
                raise_from_var + " = " + raise_expr + "\n"
                + raise_from_var + ".__cause__ = " + from_expr + "\n"
                + "raise " + raise_from_var
            )

    def dict_comp_handle(self, loc, tokens):
        """Process Python 2.7 dictionary comprehension."""
        key, val, comp = tokens
        if self.target.startswith("3"):
            return "{" + key + ": " + val + " " + comp + "}"
        else:
            return "dict(((" + key + "), (" + val + ")) " + comp + ")"

    def pattern_error(self, original, loc, value_var, check_var, match_error_class='_coconut_MatchError'):
        """Construct a pattern-matching error message."""
        base_line = clean(self.reformat(getline(loc, original), ignore_errors=True)).strip()
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

    def full_match_handle(self, original, loc, tokens, match_to_var=None, match_check_var=None):
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

        matching = self.get_matcher(original, loc, match_check_var)
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

        pos_only_args, req_args, default_args, star_arg, kwd_only_args, dubstar_arg = split_args_list(matches, loc)
        matcher.match_function(match_to_args_var, match_to_kwargs_var, pos_only_args, req_args + default_args, star_arg, kwd_only_args, dubstar_arg)

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

    def stmt_lambdef_handle(self, original, loc, tokens):
        """Process multi-line lambdef statements."""
        kwds, params, stmts_toks = tokens

        is_async = False
        for kwd in kwds:
            if kwd == "async":
                self.internal_assert(not is_async, original, loc, "duplicate stmt_lambdef async keyword", kwd)
                is_async = True
            else:
                raise CoconutInternalException("invalid stmt_lambdef keyword", kwd)

        if len(stmts_toks) == 1:
            stmts, = stmts_toks
        elif len(stmts_toks) == 2:
            stmts, last = stmts_toks
            if "tests" in stmts_toks:
                stmts = stmts.asList() + ["return " + last]
            else:
                stmts = stmts.asList() + [last]
        else:
            raise CoconutInternalException("invalid statement lambda body tokens", stmts_toks)

        name = self.get_temp_var("lambda")
        body = openindent + "\n".join(stmts) + closeindent

        if isinstance(params, str):
            decorators = ""
            funcdef = "def " + name + params + ":\n" + body
        else:
            match_tokens = [name] + list(params)
            before_colon, after_docstring = self.name_match_funcdef_handle(original, loc, match_tokens)
            decorators = "@_coconut_mark_as_match\n"
            funcdef = (
                before_colon
                + ":\n"
                + after_docstring
                + body
            )

        self.add_code_before[name] = self.decoratable_funcdef_stmt_handle(original, loc, [decorators, funcdef], is_async, is_stmt_lambda=True)

        return name

    def decoratable_funcdef_stmt_handle(self, original, loc, tokens, is_async=False, is_stmt_lambda=False):
        """Wraps the given function for later processing"""
        if len(tokens) == 1:
            funcdef, = tokens
            decorators = ""
        elif len(tokens) == 2:
            decorators, funcdef = tokens
        else:
            raise CoconutInternalException("invalid function definition tokens", tokens)
        return funcwrapper + self.add_ref("func", (original, loc, decorators, funcdef, is_async, self.in_method, is_stmt_lambda)) + "\n"

    def await_expr_handle(self, original, loc, tokens):
        """Check for Python 3.5 await expression."""
        await_expr, = tokens
        if not self.target:
            raise self.make_err(
                CoconutTargetError,
                "await requires a specific target",
                original, loc,
                target="sys",
            )
        elif self.target_info >= (3, 5):
            return "await " + await_expr
        elif self.target_info >= (3, 3):
            # we have to wrap the yield here so it doesn't cause the function to be detected as an async generator
            return self.wrap_passthrough("(yield from " + await_expr + ")", early=True)
        else:
            # this yield is fine because we can detect the _coconut.asyncio.From
            return "(yield _coconut.asyncio.From(" + await_expr + "))"

    def unsafe_typedef_handle(self, tokens):
        """Process type annotations without a comma after them."""
        return self.typedef_handle(tokens.asList() + [","])

    def wrap_typedef(self, typedef, for_py_typedef):
        """Wrap a type definition in a string to defer it unless --no-wrap or __future__.annotations."""
        if self.no_wrap or for_py_typedef and self.target_info >= (3, 7):
            return typedef
        else:
            return self.wrap_str_of(self.reformat(typedef, ignore_errors=False))

    def typedef_handle(self, tokens):
        """Process Python 3 type annotations."""
        if len(tokens) == 1:  # return typedef
            if self.target.startswith("3"):
                return " -> " + self.wrap_typedef(tokens[0], for_py_typedef=True) + ":"
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
                return varname + ": " + self.wrap_typedef(typedef, for_py_typedef=True) + default + comma
            else:
                return varname + default + comma + self.wrap_passthrough(self.wrap_comment(" type: " + typedef) + non_syntactic_newline, early=True)

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
            return name + ": " + self.wrap_typedef(typedef, for_py_typedef=True) + ("" if value is None else " = " + value)
        else:
            return handle_indentation('''
{name} = {value}{comment}
if "__annotations__" not in _coconut.locals():
    __annotations__ = {{}}
__annotations__["{name}"] = {annotation}
            ''').format(
                name=name,
                value=(
                    value if value is not None
                    else "_coconut.typing.cast(_coconut.typing.Any, {ellipsis})".format(ellipsis=self.ellipsis_handle())
                ),
                comment=self.wrap_comment(" type: " + typedef),
                annotation=self.wrap_typedef(typedef, for_py_typedef=False),
            )

    def funcname_typeparams_handle(self, tokens):
        """Handle function names with type parameters."""
        if len(tokens) == 1:
            name, = tokens
            return name
        else:
            name, paramdefs = tokens
            # temp_marker will be set back later, but needs to be a unique name until then for add_code_before
            temp_marker = self.get_temp_var("type_param_func")
            self.add_code_before[temp_marker] = "".join(paramdefs)
            self.add_code_before_replacements[temp_marker] = name
            return temp_marker

    funcname_typeparams_handle.ignore_one_token = True

    def type_param_handle(self, original, loc, tokens):
        """Compile a type param into an assignment."""
        bounds = ""
        if "TypeVar" in tokens:
            TypeVarFunc = "TypeVar"
            if len(tokens) == 1:
                name, = tokens
            else:
                name, bound_op, bound = tokens
                if bound_op == "<=":
                    self.strict_err_or_warn(
                        "use of " + repr(bound_op) + " as a type parameter bound declaration operator is deprecated (Coconut style is to use '<:' operator)",
                        original,
                        loc,
                    )
                elif bound_op == ":":
                    self.strict_err(
                        "found use of " + repr(bound_op) + " as a type parameter bound declaration operator (Coconut style is to use '<:' operator)",
                        original,
                        loc,
                    )
                else:
                    self.internal_assert(bound_op == "<:", original, loc, "invalid type_param bound_op", bound_op)
                bounds = ", bound=" + self.wrap_typedef(bound, for_py_typedef=False)
        elif "TypeVarTuple" in tokens:
            TypeVarFunc = "TypeVarTuple"
            name, = tokens
        elif "ParamSpec" in tokens:
            TypeVarFunc = "ParamSpec"
            name, = tokens
        else:
            raise CoconutInternalException("invalid type_param tokens", tokens)

        typevar_info = self.current_parsing_context("typevars")
        if typevar_info is not None:
            if name in typevar_info["all_typevars"]:
                raise CoconutDeferredSyntaxError("type variable {name!r} already defined", loc)
            temp_name = self.get_temp_var("typevar_" + name)
            typevar_info["all_typevars"][name] = temp_name
            typevar_info["new_typevars"].append((TypeVarFunc, temp_name))
            name = temp_name

        return '{name} = _coconut.typing.{TypeVarFunc}("{name}"{bounds})\n'.format(
            name=name,
            TypeVarFunc=TypeVarFunc,
            bounds=bounds,
        )

    def get_generic_for_typevars(self):
        """Get the Generic instances for the current typevars."""
        typevar_info = self.current_parsing_context("typevars")
        internal_assert(typevar_info is not None, "get_generic_for_typevars called with no typevars")
        generics = []
        for TypeVarFunc, name in typevar_info["new_typevars"]:
            if TypeVarFunc in ("TypeVar", "ParamSpec"):
                generics.append(name)
            elif TypeVarFunc == "TypeVarTuple":
                if self.target_info >= (3, 11):
                    generics.append("*" + name)
                else:
                    generics.append("_coconut.typing.Unpack[" + name + "]")
            else:
                raise CoconutInternalException("invalid TypeVarFunc", TypeVarFunc)
        return "_coconut.typing.Generic[" + ", ".join(generics) + "]"

    @contextmanager
    def type_alias_stmt_manage(self, item=None, original=None, loc=None):
        """Manage the typevars parsing context."""
        typevars_stack = self.parsing_context["typevars"]
        prev_typevar_info = self.current_parsing_context("typevars")
        typevars_stack.append({
            "all_typevars": {} if prev_typevar_info is None else prev_typevar_info["all_typevars"].copy(),
            "new_typevars": [],
        })
        try:
            yield
        finally:
            typevars_stack.pop()

    def type_alias_stmt_handle(self, tokens):
        """Handle type alias statements."""
        if len(tokens) == 2:
            name, typedef = tokens
            paramdefs = ()
        else:
            name, paramdefs, typedef = tokens
        return "".join(paramdefs) + self.typed_assign_stmt_handle([
            name,
            "_coconut.typing.TypeAlias",
            self.wrap_typedef(typedef, for_py_typedef=False),
        ])

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

    def ellipsis_handle(self, tokens=None):
        if self.target.startswith("3"):
            return "..."
        else:
            return "_coconut.Ellipsis"

    ellipsis_handle.ignore_tokens = True

    def match_case_tokens(self, match_var, check_var, original, tokens, top):
        """Build code for matching the given case."""
        if len(tokens) == 3:
            loc, matches, stmts = tokens
            cond = None
        elif len(tokens) == 4:
            loc, matches, cond, stmts = tokens
        else:
            raise CoconutInternalException("invalid case match tokens", tokens)
        loc = int(loc)
        matching = self.get_matcher(original, loc, check_var)
        matching.match(matches, match_var)
        if cond:
            matching.add_guard(cond)
        return matching.build(stmts, set_check_var=top)

    def cases_stmt_handle(self, original, loc, tokens):
        """Process case blocks."""
        if len(tokens) == 3:
            block_kwd, item, cases = tokens
            default = None
        elif len(tokens) == 4:
            block_kwd, item, cases, default = tokens
        else:
            raise CoconutInternalException("invalid case tokens", tokens)

        self.internal_assert(block_kwd in ("cases", "case", "match"), original, loc, "invalid case statement keyword", block_kwd)
        if block_kwd == "case":
            self.strict_err_or_warn("deprecated case keyword at top level in case ...: match ...: block (use Python 3.10 match ...: case ...: syntax instead)", original, loc)

        check_var = self.get_temp_var("case_match_check")
        match_var = self.get_temp_var("case_match_to")

        out = (
            match_var + " = " + item + "\n"
            + self.match_case_tokens(match_var, check_var, original, cases[0], True)
        )
        for case in cases[1:]:
            out += (
                "if not " + check_var + ":\n" + openindent
                + self.match_case_tokens(match_var, check_var, original, case, False) + closeindent
            )
        if default is not None:
            out += "if not " + check_var + default
        return out

    def f_string_handle(self, loc, tokens):
        """Process Python 3.6 format strings."""
        string, = tokens

        # strip raw r
        raw = string.startswith("r")
        if raw:
            string = string[1:]

        # strip wrappers
        internal_assert(string.startswith(strwrapper) and string.endswith(unwrapper), "invalid f string item", string)
        string = string[1:-1]

        # get text
        old_text, strchar = self.get_ref("str", string)

        # separate expressions
        string_parts = [""]
        exprs = []
        saw_brace = False
        in_expr = False
        paren_level = 0
        i = 0
        while i < len(old_text):
            c = old_text[i]
            if saw_brace:
                saw_brace = False
                if c == "{":
                    string_parts[-1] += c
                elif c == "}":
                    raise CoconutDeferredSyntaxError("empty expression in format string", loc)
                else:
                    in_expr = True
                    exprs.append("")
                    i -= 1
            elif in_expr:
                remaining_text = old_text[i:]
                str_start, str_stop = parse_where(self.string_start, remaining_text)
                if str_start is not None:  # str_start >= 0; if > 0 means there is whitespace before the string
                    exprs[-1] += remaining_text[:str_stop]
                    i += str_stop - 1
                elif paren_level < 0:
                    paren_level += paren_change(c)
                    exprs[-1] += c
                elif paren_level > 0:
                    raise CoconutDeferredSyntaxError("imbalanced parentheses in format string expression", loc)
                elif match_in(self.end_f_str_expr, remaining_text):
                    in_expr = False
                    string_parts.append(c)
                else:
                    paren_level += paren_change(c)
                    exprs[-1] += c
            elif c == "{":
                saw_brace = True
                string_parts[-1] += c
            else:
                string_parts[-1] += c
            i += 1

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
                    decorators.append("@" + varname + "\n")
            else:
                raise CoconutInternalException("invalid decorator tokens", tok)
        return "".join(defs + decorators)

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

    def testlist_star_expr_handle(self, original, loc, tokens, is_list=False):
        """Handle naked a, *b."""
        groups, has_star, has_comma = self.split_star_expr_tokens(tokens)
        is_sequence = has_comma or is_list

        if not is_sequence:
            if has_star:
                raise CoconutDeferredSyntaxError("can't use starred expression here", loc)
            self.internal_assert(len(groups) == 1 and len(groups[0]) == 1, original, loc, "invalid single-item testlist_star_expr tokens", tokens)
            out = groups[0][0]

        elif not has_star:
            self.internal_assert(len(groups) == 1, original, loc, "testlist_star_expr group splitting failed on", tokens)
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
                    if g:
                        to_chain.append(tuple_str_of(g))
                else:
                    to_chain.append(g)
            self.internal_assert(to_chain, original, loc, "invalid naked a, *b expression", tokens)

            # return immediately, since we handle is_list here
            if is_list:
                return "_coconut.list(_coconut.itertools.chain(" + ", ".join(to_chain) + "))"
            else:
                return "_coconut.tuple(_coconut.itertools.chain(" + ", ".join(to_chain) + "))"

        if is_list:
            return "[" + out + "]"
        else:
            return out  # the grammar wraps this in parens as needed

    def list_expr_handle(self, original, loc, tokens):
        """Handle non-comprehension list literals."""
        return self.testlist_star_expr_handle(original, loc, tokens, is_list=True)

    def dict_literal_handle(self, tokens):
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

    def new_testlist_star_expr_handle(self, tokens):
        """Handles new starred expressions that only started being allowed
        outside of parentheses in Python 3.9."""
        item, = tokens
        if (3, 5) <= self.target_info <= (3, 8):
            return "(" + item + ")"
        else:
            return item

    def base_match_for_stmt_handle(self, original, loc, tokens):
        """Handle match for loops."""
        matches, item, body = tokens

        match_to_var = self.get_temp_var("match_to")
        match_check_var = self.get_temp_var("match_check")

        matcher = self.get_matcher(original, loc, match_check_var)
        matcher.match(matches, match_to_var)

        match_code = matcher.build()
        match_error = self.pattern_error(original, loc, match_to_var, match_check_var)

        return handle_indentation(
            """
for {match_to_var} in {item}:
    {match_code}
    {match_error}
{body}
            """,
            add_newline=True,
        ).format(
            match_to_var=match_to_var,
            item=item,
            match_code=match_code,
            match_error=match_error,
            body=body,
        )

    def string_atom_handle(self, tokens):
        """Handle concatenation of string literals."""
        internal_assert(len(tokens) >= 1, "invalid string literal tokens", tokens)
        if any(s.endswith(")") for s in tokens):  # has .format() calls
            return "(" + " + ".join(tokens) + ")"
        elif any(s.startswith(("f", "rf")) for s in tokens):  # has f-strings
            return " ".join(tokens)
        else:
            return self.eval_now(" ".join(tokens))

    string_atom_handle.ignore_one_token = True

    def unsafe_typedef_tuple_handle(self, original, loc, tokens):
        """Handle Tuples in typedefs."""
        tuple_items = self.testlist_star_expr_handle(original, loc, tokens)
        return "_coconut.typing.Tuple[" + tuple_items + "]"

    def term_handle(self, tokens):
        """Handle terms seperated by mul-like operators."""
        out = [tokens[0]]
        for i in range(1, len(tokens), 2):
            op, term = tokens[i:i + 2]
            if op == "@" and self.target_info < (3, 5):
                out = ["_coconut_matmul(" + " ".join(out) + ", " + term + ")"]
            else:
                out += [op, term]
        return " ".join(out)

# end: HANDLERS
# -----------------------------------------------------------------------------------------------------------------------
# CHECKING HANDLERS:
# -----------------------------------------------------------------------------------------------------------------------

    def check_strict(self, name, original, loc, tokens, only_warn=False, always_warn=False):
        """Check that syntax meets --strict requirements."""
        self.internal_assert(len(tokens) == 1, original, loc, "invalid " + name + " tokens", tokens)
        message = "found " + name
        if self.strict:
            kwargs = {}
            if only_warn:
                if not always_warn:
                    kwargs["extra"] = "remove --strict to dismiss"
                logger.warn_err(self.make_err(CoconutSyntaxWarning, message, original, loc, **kwargs))
            else:
                if always_warn:
                    kwargs["extra"] = "remove --strict to downgrade to a warning"
                raise self.make_err(CoconutStyleError, message, original, loc, **kwargs)
        elif always_warn:
            logger.warn_err(self.make_err(CoconutSyntaxWarning, message, original, loc))
        return tokens[0]

    def lambdef_check(self, original, loc, tokens):
        """Check for Python-style lambdas."""
        return self.check_strict("Python-style lambda", original, loc, tokens)

    def endline_semicolon_check(self, original, loc, tokens):
        """Check for semicolons at the end of lines."""
        return self.check_strict("semicolon at end of line", original, loc, tokens, always_warn=True)

    def u_string_check(self, original, loc, tokens):
        """Check for Python-2-style unicode strings."""
        return self.check_strict("Python-2-style unicode string (all Coconut strings are unicode strings)", original, loc, tokens, always_warn=True)

    def match_dotted_name_const_check(self, original, loc, tokens):
        """Check for Python-3.10-style implicit dotted name match check."""
        return self.check_strict("Python-3.10-style dotted name in pattern-matching (Coconut style is to use '=={name}' not '{name}')".format(name=tokens[0]), original, loc, tokens)

    def match_check_equals_check(self, original, loc, tokens):
        """Check for old-style =item in pattern-matching."""
        return self.check_strict("deprecated equality-checking '=...' pattern; use '==...' instead", original, loc, tokens, always_warn=True)

    def check_py(self, version, name, original, loc, tokens):
        """Check for Python-version-specific syntax."""
        self.internal_assert(len(tokens) == 1, original, loc, "invalid " + name + " tokens", tokens)
        version_info = get_target_info(version)
        if self.target_info < version_info:
            raise self.make_err(CoconutTargetError, "found Python " + ".".join(str(v) for v in version_info) + " " + name, original, loc, target=version)
        else:
            return tokens[0]

    @contextmanager
    def class_manage(self, item, original, loc):
        """Manage the class parsing context."""
        cls_stack = self.parsing_context["class"]
        if cls_stack:
            cls_context = cls_stack[-1]
            if cls_context["name"] is None:  # this should only happen when the managed class item will fail to fully parse
                name_prefix = cls_context["name_prefix"]
            elif cls_context["in_method"]:  # if we're in a function, we shouldn't use the prefix to look up the class
                name_prefix = ""
            else:
                name_prefix = cls_context["name_prefix"] + cls_context["name"] + "."
        else:
            name_prefix = ""
        cls_stack.append({
            "name_prefix": name_prefix,
            "name": None,
            "in_method": False,
        })
        try:
            # handles support for class type variables
            with self.type_alias_stmt_manage():
                yield
        finally:
            cls_stack.pop()

    @contextmanager
    def func_manage(self, item, original, loc):
        """Manage the function parsing context."""
        cls_context = self.current_parsing_context("class")
        if cls_context is not None:
            in_method, cls_context["in_method"] = cls_context["in_method"], True
        try:
            # handles support for function type variables
            with self.type_alias_stmt_manage():
                yield
        finally:
            if cls_context is not None:
                cls_context["in_method"] = in_method

    @property
    def in_method(self):
        """Determine if currently in a method."""
        cls_context = self.current_parsing_context("class")
        return cls_context is not None and cls_context["name"] is not None and cls_context["in_method"]

    def name_handle(self, original, loc, tokens, assign=False, classname=False):
        """Handle the given base name."""
        name, = tokens
        if name.startswith("\\"):
            name = name[1:]
            escaped = True
        else:
            escaped = False

        if classname:
            cls_context = self.current_parsing_context("class")
            self.internal_assert(cls_context is not None, original, loc, "found classname outside of class", tokens)
            cls_context["name"] = name

        if self.disable_name_check:
            return name

        # raise_or_wrap_error for all errors here to make sure we don't
        #  raise spurious errors if not using the computation graph

        if not escaped:
            typevar_info = self.current_parsing_context("typevars")
            if typevar_info is not None:
                typevars = typevar_info["all_typevars"]
                if name in typevars:
                    if assign:
                        return self.raise_or_wrap_error(
                            self.make_err(
                                CoconutSyntaxError,
                                "cannot reassign type variable '{name}'".format(name=name),
                                original,
                                loc,
                                extra="use explicit '\\{name}' syntax if intended".format(name=name),
                            ),
                        )
                    return typevars[name]

        if not assign:
            self.unused_imports.pop(name, None)

        if (
            assign
            and not escaped
            # if we're not using the computation graph, then name is handled
            #  greedily, which means this might be an invalid parse, in which
            #  case we can't be sure this is actually shadowing a builtin
            and USE_COMPUTATION_GRAPH
            # classnames are handled greedily, so ditto the above
            and not classname
            and name in all_builtins
        ):
            self.strict_err_or_warn(
                "assignment shadows builtin '{name}' (use explicit '\\{name}' syntax when purposefully assigning to builtin names)".format(name=name),
                original,
                loc,
            )

        if name == "exec":
            if self.target.startswith("3"):
                return name
            elif assign:
                return self.raise_or_wrap_error(
                    self.make_err(
                        CoconutTargetError,
                        "found Python-3-only assignment to 'exec' as a variable name",
                        original,
                        loc,
                        target="3",
                    ),
                )
            else:
                return "_coconut_exec"
        elif not assign and name in super_names and not self.target.startswith("3"):
            if self.in_method:
                cls_context = self.current_parsing_context("class")
                enclosing_cls = cls_context["name_prefix"] + cls_context["name"]
                # temp_marker will be set back later, but needs to be a unique name until then for add_code_before
                temp_marker = self.get_temp_var("super")
                self.add_code_before[temp_marker] = "__class__ = " + enclosing_cls + "\n"
                self.add_code_before_replacements[temp_marker] = name
                return temp_marker
            else:
                return name
        elif not escaped and name.startswith(reserved_prefix) and name not in self.operators:
            return self.raise_or_wrap_error(
                self.make_err(
                    CoconutSyntaxError,
                    "variable names cannot start with reserved prefix '{prefix}' (use explicit '\\{name}' syntax if intending to access Coconut internals)".format(prefix=reserved_prefix, name=name),
                    original,
                    loc,
                ),
            )
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
        """Check for Python 3.10 assignment expressions."""
        return self.check_py("310", "assignment expression in set literal or indexing", original, loc, tokens)

    def except_star_clause_check(self, original, loc, tokens):
        """Check for Python 3.11 except* statements."""
        return self.check_py("311", "except* statement", original, loc, tokens)

    def subscript_star_check(self, original, loc, tokens):
        """Check for Python 3.11 starred expressions in subscripts."""
        return self.check_py("311", "starred expression in indexing", original, loc, tokens)

# end: CHECKING HANDLERS
# -----------------------------------------------------------------------------------------------------------------------
# ENDPOINTS:
# -----------------------------------------------------------------------------------------------------------------------

    def parse_single(self, inputstring, **kwargs):
        """Parse line code."""
        return self.parse(inputstring, self.single_parser, {}, {"header": "none", "initial": "none"}, streamline=False, **kwargs)

    def parse_file(self, inputstring, addhash=True, **kwargs):
        """Parse file code."""
        if addhash:
            use_hash = self.genhash(inputstring)
        else:
            use_hash = None
        return self.parse(inputstring, self.file_parser, {"nl_at_eof_check": True}, {"header": "file", "use_hash": use_hash}, **kwargs)

    def parse_exec(self, inputstring, **kwargs):
        """Parse exec code."""
        return self.parse(inputstring, self.file_parser, {}, {"header": "file", "initial": "none"}, **kwargs)

    def parse_package(self, inputstring, package_level=0, addhash=True, **kwargs):
        """Parse package code."""
        internal_assert(package_level >= 0, "invalid package level", package_level)
        if addhash:
            use_hash = self.genhash(inputstring, package_level)
        else:
            use_hash = None
        return self.parse(inputstring, self.file_parser, {"nl_at_eof_check": True}, {"header": "package:" + str(package_level), "use_hash": use_hash}, **kwargs)

    def parse_block(self, inputstring, **kwargs):
        """Parse block code."""
        return self.parse(inputstring, self.file_parser, {}, {"header": "none", "initial": "none"}, **kwargs)

    def parse_sys(self, inputstring, **kwargs):
        """Parse code to use the Coconut module."""
        return self.parse(inputstring, self.file_parser, {}, {"header": "sys", "initial": "none"}, **kwargs)

    def parse_eval(self, inputstring, **kwargs):
        """Parse eval code."""
        return self.parse(inputstring, self.eval_parser, {"strip": True}, {"header": "none", "initial": "none", "final_endline": False}, **kwargs)

    def parse_lenient(self, inputstring, **kwargs):
        """Parse any code."""
        return self.parse(inputstring, self.file_parser, {"strip": True}, {"header": "none", "initial": "none", "final_endline": False}, **kwargs)

    def parse_xonsh(self, inputstring, **kwargs):
        """Parse xonsh code."""
        return self.parse(inputstring, self.xonsh_parser, {"strip": True}, {"header": "none", "initial": "none"}, streamline=False, **kwargs)

    def warm_up(self):
        """Warm up the compiler by streamlining the file_parser."""
        self.streamline(self.file_parser)
        self.streamline(self.eval_parser)


# end: ENDPOINTS
# -----------------------------------------------------------------------------------------------------------------------
# BINDING:
# -----------------------------------------------------------------------------------------------------------------------

Compiler.bind()

# end: BINDING
