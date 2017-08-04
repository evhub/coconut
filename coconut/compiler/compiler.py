#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

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
#   - Parser Handlers
#   - Checking Handlers
#   - Endpoints

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
from contextlib import contextmanager

from coconut.pyparsing import (
    ParseBaseException,
    col,
    line as getline,
    lineno,
    nums,
    Keyword,
)

from coconut.constants import (
    get_target_info,
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
    tabworth,
    match_to_var,
    match_to_args_var,
    match_to_kwargs_var,
    match_check_var,
    match_err_var,
    lazy_chain_var,
    import_as_var,
    yield_from_var,
    yield_item_var,
    raise_from_var,
    stmt_lambda_var,
    tre_mock_var,
    tre_store_var,
    py3_to_py2_stdlib,
    checksum,
    reserved_prefix,
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
    clean,
    internal_assert,
)
from coconut.terminal import logger, trace, complain
from coconut.compiler.matching import Matcher
from coconut.compiler.grammar import (
    Grammar,
    lazy_list_handle,
    get_infix_items,
    match_handle,
)
from coconut.compiler.util import (
    addskip,
    count_end,
    paren_change,
    ind_change,
    rem_comment,
    split_comment,
    attach,
    split_leading_indent,
    split_trailing_indent,
    match_in,
    transform,
    ignore_transform,
    parse,
)
from coconut.compiler.header import (
    minify,
    getheader,
)

# end: IMPORTS
#-----------------------------------------------------------------------------------------------------------------------
# HANDLERS:
#-----------------------------------------------------------------------------------------------------------------------


def set_to_tuple(tokens):
    """Converts set literal tokens to tuples."""
    internal_assert(len(tokens) == 1, "invalid set maker tokens", tokens)
    if "comp" in tokens.keys() or "list" in tokens.keys():
        return "(" + tokens[0] + ")"
    elif "test" in tokens.keys():
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


def single_import(path, imp_as):
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
        fake_mods = imp_as.split(".")
        out.append(import_stmt(imp_from, imp, import_as_var))
        for i in range(1, len(fake_mods)):
            mod_name = ".".join(fake_mods[:i])
            out.extend((
                "try:",
                openindent + mod_name,
                closeindent + "except:",
                openindent + mod_name + ' = _coconut.imp.new_module("' + mod_name + '")',
                closeindent + "else:",
                openindent + "if not _coconut.isinstance(" + mod_name + ", _coconut.types.ModuleType):",
                openindent + mod_name + ' = _coconut.imp.new_module("' + mod_name + '")' + closeindent * 2,
            ))
        out.append(".".join(fake_mods) + " = " + import_as_var)
    else:
        out.append(import_stmt(imp_from, imp, imp_as))

    return out


def universal_import(imports, imp_from=None, target=""):
    """Generate code for a universal import of imports from imp_from on target.
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
        elif target.startswith("2"):
            paths = (old_imp,)
        elif not target or get_target_info(target) < version_check:
            paths = (old_imp, imp, version_check)
        else:
            paths = (imp,)
        importmap.append((paths, imp_as))

    stmts = []
    for paths, imp_as in importmap:
        if len(paths) == 1:
            more_stmts = single_import(paths[0], imp_as)
            stmts.extend(more_stmts)
        else:
            first, second, version_check = paths
            stmts.append("if _coconut_sys.version_info < " + str(version_check) + ":")
            first_stmts = single_import(first, imp_as)
            first_stmts[0] = openindent + first_stmts[0]
            first_stmts[-1] += closeindent
            stmts.extend(first_stmts)
            stmts.append("else:")
            second_stmts = single_import(second, imp_as)
            second_stmts[0] = openindent + second_stmts[0]
            second_stmts[-1] += closeindent
            stmts.extend(second_stmts)
    return "\n".join(stmts)


def split_args_list(tokens, loc):
    """Splits function definition arguments."""
    req_args, def_args, star_arg, kwd_args, dubstar_arg = [], [], None, [], None
    pos = 0
    for arg in tokens:
        if len(arg) == 1:
            if arg[0] == "*":
                # star sep (pos = 3)
                if pos >= 3:
                    raise CoconutDeferredSyntaxError("invalid star separator in function definition", loc)
                pos = 3
            else:
                # pos arg (pos = 0)
                if pos > 0:
                    raise CoconutDeferredSyntaxError("invalid positional argument in function definition", loc)
                req_args.append(arg[0])
        elif len(arg) == 2:
            if arg[0] == "*":
                # star arg (pos = 2)
                if pos >= 2:
                    raise CoconutDeferredSyntaxError("invalid star argument in function definition", loc)
                pos = 2
                star_arg = arg[1]
            elif arg[0] == "**":
                # dub star arg (pos = 4)
                if pos == 4:
                    raise CoconutDeferredSyntaxError("invalid double star argument in function definition", loc)
                pos = 4
                dubstar_arg = arg[1]
            else:
                # kwd arg (pos = 1 or 3)
                if pos <= 1:
                    pos = 1
                    def_args.append((arg[0], arg[1]))
                elif pos <= 3:
                    pos = 3
                    kwd_args.append((arg[0], arg[1]))
                else:
                    raise CoconutDeferredSyntaxError("invalid default argument in function definition", loc)
        else:
            raise CoconutInternalException("invalid function definition argument", arg)
    return req_args, def_args, star_arg, kwd_args, dubstar_arg


# end: HANDLERS
#-----------------------------------------------------------------------------------------------------------------------
# COMPILER:
#-----------------------------------------------------------------------------------------------------------------------


class Compiler(Grammar):
    """The Coconut compiler."""
    preprocs = [
        lambda self: self.prepare,
        lambda self: self.str_proc,
        lambda self: self.passthrough_proc,
        lambda self: self.ind_proc,
    ]
    postprocs = [
        lambda self: self.stmt_lambda_proc,
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

    def setup(self, target=None, strict=False, minify=False, line_numbers=False, keep_lines=False, no_tco=False):
        """Initializes parsing parameters."""
        if target is None:
            target = ""
        else:
            target = str(target).replace(".", "")
        if target in pseudo_targets:
            target = pseudo_targets[target]
        if target not in targets:
            raise CoconutException(
                "unsupported target Python version " + ascii(target),
                extra="supported targets are " + ', '.join(ascii(t) for t in specific_targets) + ", or leave blank for universal",
            )
        logger.log_vars("Compiler args:", locals())
        self.target, self.strict, self.minify, self.line_numbers, self.keep_lines, self.no_tco = (
            target, strict, minify, line_numbers, keep_lines, no_tco,
        )

    def __reduce__(self):
        """Return pickling information."""
        return (Compiler, (self.target, self.strict, self.minify, self.line_numbers, self.keep_lines, self.no_tco))

    def genhash(self, package, code):
        """Generate a hash from code."""
        return hex(
            checksum(
                hash_sep.join(
                    str(item) for item in
                    (VERSION_STR,)
                    + self.__reduce__()[1]
                    + (package, code)
                ).encode(default_encoding),
            ) & 0xffffffff,
        )  # necessary for cross-compatibility

    def reset(self):
        """Resets references."""
        self.indchar = None
        self.refs = []
        self.skips = set()
        self.docstring = ""
        self.ichain_count = 0
        self.tre_store_count = 0
        self.stmt_lambdas = []
        self.bind()

    def bind(self):
        """Binds reference objects to the proper parse actions."""
        self.endline <<= attach(self.endline_ref, self.endline_handle)
        self.moduledoc_item <<= trace(attach(self.moduledoc, self.set_docstring))
        self.name <<= trace(attach(self.base_name, self.name_check))

        self.set_literal <<= trace(attach(self.set_literal_ref, self.set_literal_handle))
        self.set_letter_literal <<= trace(attach(self.set_letter_literal_ref, self.set_letter_literal_handle))
        self.classlist <<= trace(attach(self.classlist_ref, self.classlist_handle))
        self.import_stmt <<= trace(attach(self.import_stmt_ref, self.import_handle))
        self.complex_raise_stmt <<= trace(attach(self.complex_raise_stmt_ref, self.complex_raise_stmt_handle))
        self.augassign_stmt <<= trace(attach(self.augassign_stmt_ref, self.augassign_handle))
        self.dict_comp <<= trace(attach(self.dict_comp_ref, self.dict_comp_handle))
        self.destructuring_stmt <<= trace(attach(self.destructuring_stmt_ref, self.destructuring_stmt_handle))
        self.name_match_funcdef <<= trace(attach(self.name_match_funcdef_ref, self.name_match_funcdef_handle))
        self.op_match_funcdef <<= trace(attach(self.op_match_funcdef_ref, self.op_match_funcdef_handle))
        self.yield_from <<= trace(attach(self.yield_from_ref, self.yield_from_handle))
        self.exec_stmt <<= trace(attach(self.exec_stmt_ref, self.exec_stmt_handle))
        self.stmt_lambdef <<= trace(attach(self.stmt_lambdef_ref, self.stmt_lambdef_handle))
        self.decoratable_normal_funcdef_stmt <<= trace(attach(self.decoratable_normal_funcdef_stmt_ref, self.decoratable_normal_funcdef_stmt_handle))
        self.typedef <<= trace(attach(self.typedef_ref, self.typedef_handle))
        self.typedef_default <<= trace(attach(self.typedef_default_ref, self.typedef_handle))
        self.unsafe_typedef_default <<= trace(attach(self.unsafe_typedef_default_ref, self.unsafe_typedef_handle))
        self.return_typedef <<= trace(attach(self.return_typedef_ref, self.typedef_handle))
        self.typed_assign_stmt <<= trace(attach(self.typed_assign_stmt_ref, self.typed_assign_stmt_handle))
        self.datadef <<= trace(attach(self.datadef_ref, self.data_handle))
        self.with_stmt <<= trace(attach(self.with_stmt_ref, self.with_stmt_handle))

        self.u_string <<= attach(self.u_string_ref, self.u_string_check)
        self.f_string <<= attach(self.f_string_ref, self.f_string_check)
        self.matrix_at <<= attach(self.matrix_at_ref, self.matrix_at_check)
        self.nonlocal_stmt <<= attach(self.nonlocal_stmt_ref, self.nonlocal_check)
        self.star_assign_item <<= attach(self.star_assign_item_ref, self.star_assign_item_check)
        self.classic_lambdef <<= attach(self.classic_lambdef_ref, self.lambdef_check)
        self.async_keyword <<= attach(self.async_keyword_ref, self.async_keyword_check)
        self.await_keyword <<= attach(self.await_keyword_ref, self.await_keyword_check)
        self.star_expr <<= attach(self.star_expr_ref, self.star_expr_check)
        self.dubstar_expr <<= attach(self.dubstar_expr_ref, self.star_expr_check)
        self.endline_semicolon <<= attach(self.endline_semicolon_ref, self.endline_semicolon_check)
        self.async_comp_for <<= attach(self.async_comp_for_ref, self.async_comp_check)

    def adjust(self, ln):
        """Adjusts a line number."""
        adj_ln = 0
        i = 0
        while i < ln:
            adj_ln += 1
            if adj_ln not in self.skips:
                i += 1
        return adj_ln

    def reformat(self, snip, index=None):
        """Post process a preprocessed snippet."""
        if index is not None:
            return self.reformat(snip), len(self.reformat(snip[:index]))
        else:
            return self.repl_proc(snip, log=False, add_to_line=False)

    def eval_now(self, code):
        """Reformat and evaluates a code snippet and returns code for the result."""
        result = eval(self.reformat(code))
        if result is True or result is False or result is None or isinstance(result, int):
            return repr(result)
        elif isinstance(result, (bytes, str)):
            return ("b" if isinstance(result, bytes) else "") + self.wrap_str_of(result)
        else:
            return None

    def make_err(self, errtype, message, original, loc, ln=None, reformat=True, *args, **kwargs):
        """Generate an error of the specified type."""
        if ln is None:
            ln = self.adjust(lineno(loc, original))
        errstr, index = getline(loc, original), col(loc, original) - 1
        if reformat:
            errstr, index = self.reformat(errstr, index)
        return errtype(message, errstr, index, ln, *args, **kwargs)

    def strict_err_or_warn(self, *args, **kwargs):
        """Raises an error if in strict mode, otherwise raises a warning."""
        if self.strict:
            raise self.make_err(CoconutStyleError, *args, **kwargs)
        else:
            logger.warn_err(self.make_err(CoconutSyntaxWarning, *args, **kwargs))

    def add_ref(self, ref):
        """Add a reference and returns the identifier."""
        try:
            index = self.refs.index(ref)
        except ValueError:
            self.refs.append(ref)
            index = len(self.refs) - 1
        return str(index)

    def get_ref(self, index):
        """Retrieve a reference."""
        try:
            return self.refs[int(index)]
        except (IndexError, ValueError):
            raise CoconutInternalException("invalid reference", index)

    def wrap_str(self, text, strchar, multiline=False):
        """Wrap a string."""
        return strwrapper + self.add_ref((text, strchar, multiline)) + unwrapper

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
        out += self.add_ref(text) + unwrapper
        if not multiline:
            out += "\n"
        return out

    def wrap_comment(self, text, reformat=True):
        """Wrap a comment."""
        if reformat:
            text = self.reformat(text)
        return "#" + self.add_ref(text) + unwrapper

    def wrap_line_number(self, ln):
        """Wrap a line number."""
        return "#" + self.add_ref(ln) + lnwrapper

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
        if self.line_numbers or self.keep_lines:
            logger.log_tag("skips", list(sorted(self.skips)))
        return out

    def post(self, tokens, **kwargs):
        """Perform post-processing."""
        internal_assert(len(tokens) == 1, "multiple tokens leftover", tokens)
        return self.apply_procs(self.postprocs, kwargs, tokens[0])

    def getheader(self, which, use_hash=None, polish=True):
        """Get a formatted header."""
        header = getheader(which, target=self.target, use_hash=use_hash, no_tco=self.no_tco)
        if polish:
            header = self.polish(header)
        return header

    @property
    def target_info(self):
        """Return information on the current target as a version tuple."""
        return get_target_info(self.target)

    @property
    def target_info_len2(self):
        """Return target_info as a length 2 tuple."""
        info = self.target_info
        if not info:
            return (2, 7)
        elif len(info) == 1:
            if info == (2,):
                return (2, 7)
            elif info == (3,):
                return (3, 4)
            else:
                raise CoconutInternalException("invalid target info", info)
        elif len(info) == 2:
            return info
        else:
            return info[:2]

    def make_syntax_err(self, err, original):
        """Make a CoconutSyntaxError from a CoconutDeferredSyntaxError."""
        msg, loc = err.args
        return self.make_err(CoconutSyntaxError, msg, original, loc)

    def make_parse_err(self, err, reformat=True, include_ln=True):
        """Make a CoconutParseError from a ParseBaseException."""
        err_line = err.line
        err_index = err.col - 1
        err_lineno = err.lineno if include_ln else None
        if reformat:
            err_line, err_index = self.reformat(err_line, err_index)
            if err_lineno is not None:
                err_lineno = self.adjust(err_lineno)
        return CoconutParseError(None, err_line, err_index, err_lineno)

    def parse(self, inputstring, parser, preargs, postargs):
        """Use the parser to parse the inputstring."""
        self.reset()
        with logger.gather_parsing_stats():
            try:
                pre_procd = self.pre(inputstring, **preargs)
                parsed = parse(parser, pre_procd)
                out = self.post(parsed, **postargs)
            except ParseBaseException as err:
                raise self.make_parse_err(err)
            except CoconutDeferredSyntaxError as err:
                raise self.make_syntax_err(err, pre_procd)
            except RuntimeError as err:
                raise CoconutException(
                    str(err), extra="try again with --recursion-limit greater than the current "
                    + str(sys.getrecursionlimit()),
                )
        return out

# end: COMPILER
#-----------------------------------------------------------------------------------------------------------------------
# PROCESSORS:
#-----------------------------------------------------------------------------------------------------------------------

    def prepare(self, inputstring, strip=False, nl_at_eof_check=False, **kwargs):
        """Prepare a string for processing."""
        if self.strict and nl_at_eof_check and not inputstring.endswith("\n"):
            end_index = len(inputstring) - 1 if inputstring else 0
            raise self.make_err(CoconutStyleError, "missing new line at end of file", inputstring, end_index)
        original_lines = inputstring.splitlines()
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
        x = 0
        skips = self.skips.copy()

        while x <= len(inputstring):
            if x == len(inputstring):
                c = "\n"
            else:
                c = inputstring[x]

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
                            else:
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
                        else:
                            skips = addskip(skips, self.adjust(lineno(x, inputstring)))
                    hold[_contents] += c
            elif found is not None:
                if c == found[0]:
                    found += c
                elif len(found) == 1:  # found == "_"
                    if c == "\n":
                        raise self.make_err(CoconutSyntaxError, "linebreak in non-multiline string", inputstring, x, reformat=False)
                    else:
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
            self.skips = skips
            return "".join(out)

    def passthrough_proc(self, inputstring, **kwargs):
        """Process python passthroughs."""
        out = []
        found = None  # store of characters that might be the start of a passthrough
        hold = None  # the contents of the passthrough so far
        count = None  # current parenthetical level (num closes - num opens)
        multiline = None  # if in a passthrough, is it a multiline passthrough
        skips = self.skips.copy()

        for x in range(len(inputstring) + 1):
            if x == len(inputstring):
                c = "\n"
            else:
                c = inputstring[x]

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
                        skips = addskip(skips, self.adjust(lineno(x, inputstring)))
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
            raise self.make_err(CoconutSyntaxError, "unclosed passthrough", inputstring, x)

        self.skips = skips
        return "".join(out)

    def leading_whitespace(self, inputstring):
        """Count leading whitespace."""
        count = 0
        for i, c in enumerate(inputstring):
            if c == " ":
                count += 1
            elif c == "\t":
                count += tabworth - (i % tabworth)
            else:
                break
            if self.indchar is None:
                self.indchar = c
            elif c != self.indchar:
                self.strict_err_or_warn("found mixing of tabs and spaces", inputstring, i)
        return count

    def ind_proc(self, inputstring, **kwargs):
        """Process indentation."""
        lines = inputstring.splitlines()
        new = []  # new lines
        opens = []  # (line, col, adjusted ln) at which open parens were seen, newest first
        current = None  # indentation level of previous line
        levels = []  # indentation levels of all previous blocks, newest at end
        skips = self.skips.copy()  # todo

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
                        current = 0
                elif check > current:
                    levels.append(current)
                    current = check
                    line = openindent + line
                elif check in levels:
                    point = levels.index(check) + 1
                    line = closeindent * (len(levels[point:]) + 1) + line
                    levels = levels[:point]
                    current = levels.pop()
                elif current != check:
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

        self.skips = skips
        if new:
            last = rem_comment(new[-1])
            if last.endswith("\\"):
                raise self.make_err(CoconutSyntaxError, "illegal final backslash continuation", new[-1], len(new[-1]), self.adjust(len(new)))
            if opens:
                line, adj_ln = opens[0]
                raise self.make_err(CoconutSyntaxError, "unclosed open parenthesis", line, 0, adj_ln)
        new.append(closeindent * len(levels))
        return "\n".join(new)

    def stmt_lambda_proc(self, inputstring, **kwargs):
        """Add statement lambda definitions."""
        out = []
        for line in inputstring.splitlines():
            for i in range(len(self.stmt_lambdas)):
                name = self.stmt_lambda_name(i)
                if match_in(Keyword(name), line):
                    indent, line = split_leading_indent(line)
                    out.append(indent + self.stmt_lambdas[i])
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

            out.append(line + comment)

        if level != 0:
            complain(CoconutInternalException("non-zero final indentation level", level))
        return "\n".join(out)

    def endline_comment(self, ln):
        """Get an end line comment. CoconutInternalExceptions should always be caught and complained."""
        if self.keep_lines:
            if ln < 1 or ln - 1 > len(self.original_lines):
                raise CoconutInternalException("out of bounds line number", ln)
            elif ln - 1 == len(self.original_lines):  # trim too large
                lni = -1
            else:
                lni = ln - 1
        if self.line_numbers and self.keep_lines:
            if self.minify:
                comment = str(ln) + " " + self.original_lines[lni]
            else:
                comment = " line " + str(ln) + ": " + self.original_lines[lni]
        elif self.keep_lines:
            if self.minify:
                comment = self.original_lines[lni]
            else:
                comment = " " + self.original_lines[lni]
        elif self.line_numbers:
            if self.minify:
                comment = str(ln)
            else:
                comment = " line " + str(ln)
        else:
            raise CoconutInternalException("attempted to add line number comment without --line-numbers or --keep-lines")
        return self.wrap_comment(comment, reformat=False)

    def endline_repl(self, inputstring, add_to_line=True, **kwargs):
        """Add in end line comments."""
        if self.line_numbers or self.keep_lines:
            out = []
            ln = 1
            fix = False
            for line in inputstring.splitlines():
                try:
                    if line.endswith(lnwrapper):
                        line, index = line[:-1].rsplit("#", 1)
                        ln = self.get_ref(index)
                        if not isinstance(ln, int):
                            raise CoconutInternalException("invalid reference for a line number", ln)
                        line = line.rstrip()
                        fix = True
                    elif fix:
                        ln += 1
                        fix = False
                    if add_to_line and line and not line.lstrip().startswith("#"):
                        line += self.endline_comment(ln)
                except CoconutInternalException as err:
                    complain(err)
                    fix = False
                out.append(line)
            return "\n".join(out)
        else:
            return inputstring

    def passthrough_repl(self, inputstring, **kwargs):
        """Add back passthroughs."""
        out = []
        index = None
        for x in range(len(inputstring) + 1):
            c = inputstring[x] if x != len(inputstring) else None
            try:
                if index is not None:
                    if c is not None and c in nums:
                        index += c
                    elif c == unwrapper and index:
                        ref = self.get_ref(index)
                        if not isinstance(ref, str):
                            raise CoconutInternalException("invalid reference for a passthrough", ref)
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

        for x in range(len(inputstring) + 1):
            c = inputstring[x] if x != len(inputstring) else None
            try:

                if comment is not None:
                    if c is not None and c in nums:
                        comment += c
                    elif c == unwrapper and comment:
                        ref = self.get_ref(comment)
                        if not isinstance(ref, str):
                            raise CoconutInternalException("invalid reference for a comment", ref)
                        if out and not out[-1].endswith("\n"):
                            out[-1] = out[-1].rstrip(" ")
                            if not self.minify:
                                out[-1] += "  "  # put two spaces before comment
                        out.append("#" + ref)
                        comment = None
                    else:
                        raise CoconutInternalException("invalid comment marker in", getline(x, inputstring))
                elif string is not None:
                    if c is not None and c in nums:
                        string += c
                    elif c == unwrapper and string:
                        ref = self.get_ref(string)
                        if not isinstance(ref, tuple):
                            raise CoconutInternalException("invalid reference for a str", ref)
                        text, strchar, multiline = ref
                        if multiline:
                            out.append(strchar * 3 + text + strchar * 3)
                        else:
                            out.append(strchar + text + strchar)
                        string = None
                    else:
                        raise CoconutInternalException("invalid string marker in", getline(x, inputstring))
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
#-----------------------------------------------------------------------------------------------------------------------
# COMPILER HANDLERS:
#-----------------------------------------------------------------------------------------------------------------------

    def set_docstring(self, loc, tokens):
        """Set the docstring."""
        internal_assert(len(tokens) == 2, "invalid docstring tokens", tokens)
        self.docstring = self.reformat(tokens[0]) + "\n\n"
        return tokens[1]

    def yield_from_handle(self, tokens):
        """Process Python 3.3 yield from."""
        internal_assert(len(tokens) == 1, "invalid yield from tokens", tokens)
        if self.target_info < (3, 3):
            return (
                yield_from_var + " = " + tokens[0]
                + "\nfor " + yield_item_var + " in " + yield_from_var + ":\n"
                + openindent + "yield " + yield_item_var + "\n" + closeindent
            )
        else:
            return "yield from " + tokens[0]

    def endline_handle(self, original, loc, tokens):
        """Insert line number comments when in line_numbers mode."""
        internal_assert(len(tokens) == 1, "invalid endline tokens", tokens)
        out = tokens[0]
        if self.minify:
            out = out.splitlines(True)[0]  # if there are multiple new lines, take only the first one
        if self.line_numbers or self.keep_lines:
            out = self.wrap_line_number(self.adjust(lineno(loc, original))) + out
        return out

    def augassign_handle(self, tokens):
        """Process assignments."""
        internal_assert(len(tokens) == 3, "invalid assignment tokens", tokens)
        name, op, item = tokens
        out = ""
        if op == "|>=":
            out += name + " = (" + item + ")(" + name + ")"
        elif op == "|*>=":
            out += name + " = (" + item + ")(*" + name + ")"
        elif op == "<|=":
            out += name + " = " + name + "((" + item + "))"
        elif op == "<*|=":
            out += name + " = " + name + "(*(" + item + "))"
        elif op == "..=":  # also <..=
            out += name + " = _coconut_compose((" + item + "), " + name + ")"
        elif op == "..>=":
            out += name + " = _coconut_compose(" + name + ", (" + item + "))"
        elif op == "??=":
            out += name + " = " + item + " if " + name + " is None else " + name
        elif op == "::=":
            # this is necessary to prevent a segfault caused by self-reference
            ichain_var = lazy_chain_var + "_" + str(self.ichain_count)
            out += ichain_var + " = " + name + "\n"
            out += name + " = _coconut.itertools.chain.from_iterable(" + lazy_list_handle([ichain_var, "(" + item + ")"]) + ")"
            self.ichain_count += 1
        else:
            out += name + " " + op + " " + item
        return out

    def classlist_handle(self, original, loc, tokens):
        """Process class inheritance lists."""
        if len(tokens) == 0:
            if self.target.startswith("3"):
                return ""
            else:
                return "(_coconut.object)"
        elif len(tokens) == 1 and len(tokens[0]) == 1:
            if "tests" in tokens[0].keys():
                if self.strict and tokens[0][0] == "(object)":
                    raise self.make_err(CoconutStyleError, "unnecessary inheriting from object (Coconut does this automatically)", original, loc)
                return tokens[0][0]
            elif "args" in tokens[0].keys():
                if self.target.startswith("3"):
                    return tokens[0][0]
                else:
                    raise self.make_err(CoconutTargetError, "found Python 3 keyword class definition", original, loc, target="3")
            else:
                raise CoconutInternalException("invalid inner classlist token", tokens[0])
        else:
            raise CoconutInternalException("invalid classlist tokens", tokens)

    def data_handle(self, loc, tokens):
        """Process data blocks."""
        if len(tokens) == 3:
            name, args, stmts = tokens
            inherit = None
        elif len(tokens) == 4:
            name, args, inherit, stmts = tokens
        else:
            raise CoconutInternalException("invalid data tokens", tokens)

        base_args = []  # names of all the non-starred args
        req_args = 0  # number of required arguments
        starred_arg = None  # starred arg if there is one else None
        saw_defaults = False  # whether there have been any default args so far
        for i, arg in enumerate(args):
            if arg.startswith("_"):
                raise CoconutDeferredSyntaxError("data fields cannot start with an underscore", loc)
            elif arg.startswith("*"):
                if i != len(args) - 1:
                    raise CoconutDeferredSyntaxError("starred data field must come last", loc)
                starred_arg = arg[1:]
            else:
                if "=" in arg:
                    arg = arg.split("=", 1)[0]
                    saw_defaults = True
                elif saw_defaults:
                    raise CoconutDeferredSyntaxError("data fields with defaults must come after data fields without", loc)
                else:
                    req_args += 1
                base_args.append(arg)

        attr_str = " ".join(base_args)
        extra_stmts = (
            '__slots__ = ()\n'
            '__ne__ = _coconut.object.__ne__\n'
        )
        if starred_arg is not None:
            attr_str += (" " if attr_str else "") + starred_arg
            if base_args:
                extra_stmts += '''def __new__(_cls, {all_args}):
                    {oind}return _coconut.tuple.__new__(_cls, {base_args_tuple} + {starred_arg})
                {cind}@_coconut.classmethod
                def _make(cls, iterable, {kwd_only}new=_coconut.tuple.__new__, len=_coconut.len):
                    {oind}result = new(cls, iterable)
                    if len(result) < {req_args}:
                        {oind}raise _coconut.TypeError("Expected at least {req_args} argument(s), got %d" % len(result))
                    {cind}return result
                {cind}def _asdict(self):
                    {oind}return _coconut.OrderedDict((f, _coconut.getattr(self, f)) for f in self._fields)
                {cind}def __repr__(self):
                    {oind}return "{name}({args_for_repr})".format(**self._asdict())
                {cind}def _replace(_self, **kwds):
                    {oind}result = _self._make(_coconut.tuple(_coconut.map(kwds.pop, {quoted_base_args_tuple}, _self)) + kwds.pop("{starred_arg}", self.{starred_arg}))
                    if kwds:
                        {oind}raise _coconut.ValueError("Got unexpected field names: %r" % kwds.keys())
                    {cind}return result
                {cind}@_coconut.property
                def {starred_arg}(self):
                    {oind}return self[{num_base_args}:]
                {cind}'''.format(
                    oind=openindent,
                    cind=closeindent,
                    name=name,
                    args_for_repr=", ".join(arg + "={" + arg.lstrip("*") + "!r}" for arg in base_args + ["*" + starred_arg]),
                    starred_arg=starred_arg,
                    all_args=", ".join(args),
                    req_args=req_args,
                    num_base_args=str(len(base_args)),
                    base_args_tuple="(" + ", ".join(base_args) + ("," if len(base_args) == 1 else "") + ")",
                    quoted_base_args_tuple='("' + '", "'.join(base_args) + '"' + ("," if len(base_args) == 1 else "") + ")",
                    kwd_only=("*, " if self.target.startswith("3") else ""),
                )
            else:
                extra_stmts += '''def __new__(_cls, *{arg}):
                    {oind}return _coconut.tuple.__new__(_cls, {arg})
                {cind}@_coconut.classmethod
                def _make(cls, iterable, {kwd_only}new=_coconut.tuple.__new__, len=None):
                    {oind}return new(cls, iterable)
                {cind}def _asdict(self):
                    {oind}return _coconut.OrderedDict([("{arg}", self[:])])
                {cind}def __repr__(self):
                    {oind}return "{name}(*{arg}=%r)" % (self[:],)
                {cind}def _replace(_self, **kwds):
                    {oind}result = self._make(kwds.pop("{arg}", _self))
                    if kwds:
                        {oind}raise _coconut.ValueError("Got unexpected field names: %r" % kwds.keys())
                    {cind}return result
                {cind}@_coconut.property
                def {arg}(self):
                    {oind}return self[:]
                {cind}'''.format(
                    oind=openindent,
                    cind=closeindent,
                    name=name,
                    arg=starred_arg,
                    kwd_only=("*, " if self.target.startswith("3") else ""),
                )
        elif saw_defaults:
            extra_stmts += '''def __new__(_cls, {all_args}):
                {oind}return _coconut.tuple.__new__(_cls, {args_tuple})
            {cind}'''.format(
                oind=openindent,
                cind=closeindent,
                all_args=", ".join(args),
                args_tuple="(" + ", ".join(base_args) + ("," if len(base_args) == 1 else "") + ")",
            )

        out = (
            "class " + name + "("
            '_coconut.collections.namedtuple("' + name + '", "' + attr_str + '")'
            + (
                ", " + inherit if inherit is not None
                else ", _coconut.object" if not self.target.startswith("3")
                else ""
            ) + "):\n" + openindent
        )
        rest = None
        if "simple" in stmts.keys() and len(stmts) == 1:
            out += extra_stmts
            rest = stmts[0]
        elif "docstring" in stmts.keys() and len(stmts) == 1:
            out += stmts[0] + extra_stmts
        elif "complex" in stmts.keys() and len(stmts) == 1:
            out += extra_stmts
            rest = "".join(stmts[0])
        elif "complex" in stmts.keys() and len(stmts) == 2:
            out += stmts[0] + extra_stmts
            rest = "".join(stmts[1])
        elif "empty" in stmts.keys() and len(stmts) == 1:
            out += extra_stmts.rstrip() + stmts[0]
        else:
            raise CoconutInternalException("invalid inner data tokens", stmts)
        if rest is not None and rest != "pass\n":
            out += rest
        out += closeindent
        return out

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
        return universal_import(imports, imp_from=imp_from, target=self.target)

    def complex_raise_stmt_handle(self, tokens):
        """Process Python 3 raise from statement."""
        internal_assert(len(tokens) == 2, "invalid raise from tokens", tokens)
        if self.target.startswith("3"):
            return "raise " + tokens[0] + " from " + tokens[1]
        else:
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

    def pattern_error(self, original, loc, value_var):
        """Construct a pattern-matching error message."""
        base_line = clean(self.reformat(getline(loc, original)))
        line_wrap = self.wrap_str_of(base_line)
        repr_wrap = self.wrap_str_of(ascii(base_line))
        return (
            "if not " + match_check_var + ":\n" + openindent
            + match_err_var + ' = _coconut_MatchError("pattern-matching failed for " '
            + repr_wrap + ' " in " + _coconut.repr(_coconut.repr(' + value_var + ")))\n"
            + match_err_var + ".pattern = " + line_wrap + "\n"
            + match_err_var + ".value = " + value_var
            + "\nraise " + match_err_var + "\n" + closeindent
        )

    def destructuring_stmt_handle(self, original, loc, tokens):
        """Process match assign blocks."""
        internal_assert(len(tokens) == 2, "invalid destructuring assignment tokens", tokens)
        matches, item = tokens
        out = match_handle(loc, [matches, item, None])
        out += self.pattern_error(original, loc, match_to_var)
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
        matcher = Matcher(loc)

        req_args, def_args, star_arg, kwd_args, dubstar_arg = split_args_list(matches, loc)
        matcher.match_function(match_to_args_var, match_to_kwargs_var, req_args + def_args, star_arg, kwd_args, dubstar_arg)

        if cond is not None:
            matcher.add_guard(cond)

        before_docstring = (
            "def " + func
            + "(*" + match_to_args_var + ", **" + match_to_kwargs_var + "):\n"
            + openindent
        )
        after_docstring = (
            match_check_var + " = False\n"
            + matcher.out()
            + self.pattern_error(original, loc, match_to_args_var) + closeindent
        )
        return before_docstring, after_docstring

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

    def stmt_lambda_name(self, index=None):
        """Return the next (or specified) statement lambda name."""
        if index is None:
            index = len(self.stmt_lambdas)
        return stmt_lambda_var + "_" + str(index)

    def stmt_lambdef_handle(self, original, loc, tokens):
        """Process multi-line lambdef statements."""
        if len(tokens) == 2:
            params, stmts = tokens
        elif len(tokens) == 3:
            params, stmts, last = tokens
            if "tests" in tokens.keys():
                stmts = stmts.asList() + ["return " + last]
            else:
                stmts = stmts.asList() + [last]
        else:
            raise CoconutInternalException("invalid statement lambda tokens", tokens)
        name = self.stmt_lambda_name()
        body = openindent + self.stmt_lambda_proc("\n".join(stmts)) + closeindent
        if isinstance(params, str):
            self.stmt_lambdas.append(
                "def " + name + params + ":\n" + body,
            )
        else:
            params.insert(0, name)  # construct match tokens
            self.stmt_lambdas.append(
                "".join(self.name_match_funcdef_handle(original, loc, params))
                + body,
            )
        return name

    def tre_return(self, func_name, func_args, func_store, use_mock=True):
        """Generate a tail recursion elimination grammar element."""
        def tre_return_handle(loc, tokens):
            internal_assert(len(tokens) == 1, "invalid tail recursion elimination tokens", tokens)
            args = tokens[0][1:-1]  # strip parens
            # check if there is anything in the arguments that will store a reference
            # to the current scope, and if so, abort TRE, since it can't handle that
            if match_in(self.stores_scope, args):
                return ignore_transform
            if self.no_tco:
                tco_recurse = "return " + func_name + "(" + args + ")"
            else:
                tco_recurse = "return _coconut_tail_call(" + func_name + (", " + args if args else "") + ")"
            if not func_args or func_args == args:
                tre_recurse = "continue"
            elif use_mock:
                tre_recurse = func_args + " = " + tre_mock_var + "(" + args + ")" + "\ncontinue"
            else:
                tre_recurse = func_args + " = " + args + "\ncontinue"
            return (
                "if " + func_name + " is " + func_store + ":\n" + openindent
                + tre_recurse + "\n" + closeindent
                + "else:\n" + openindent
                + tco_recurse + closeindent
            )
        return attach(
            (Keyword("return") + Keyword(func_name)).suppress() + self.parens + self.end_marker.suppress(),
            tre_return_handle,
        )

    @contextmanager
    def complain_on_err(self):
        """Complain about any parsing-related errors raised inside."""
        try:
            yield
        except ParseBaseException as err:
            complain(self.make_parse_err(err, reformat=False, include_ln=False))
        except CoconutException as err:
            complain(err)

    def decoratable_normal_funcdef_stmt_handle(self, tokens):
        """Determines if TCO or TRE can be done and if so does it.
        Also handles dotted function names."""
        if len(tokens) == 1:
            decorators, funcdef = None, tokens[0]
        elif len(tokens) == 2:
            decorators, funcdef = tokens
        else:
            raise CoconutInternalException("invalid function definition tokens", tokens)

        lines = []  # transformed
        tco = False  # whether tco was done
        tre = False  # wether tre was done
        level = 0  # indentation level
        disabled_until_level = None  # whether inside of a def/try/with
        attempt_tre = False  # whether to attempt tre at all
        func_name = None  # the name of the function, None if attempt_tre == False
        undotted_name = None  # the function __name__ if func_name is a dotted name

        raw_lines = funcdef.splitlines(True)
        def_stmt, raw_lines = raw_lines[0], raw_lines[1:]
        with self.complain_on_err():
            func_name, func_args, func_params = parse(self.split_func_name_args_params, def_stmt)
        if func_name is not None:
            if "." in func_name:
                undotted_name = func_name.rsplit(".", 1)[-1]
                def_stmt = def_stmt.replace(func_name, undotted_name)
            use_mock = func_args and func_args != func_params[1:-1]
            func_store = tre_store_var + "_" + str(self.tre_store_count)
            self.tre_store_count += 1
            attempt_tre = True

        for line in raw_lines:
            body, indent = split_trailing_indent(line)
            level += ind_change(body)
            if disabled_until_level is not None:
                if level <= disabled_until_level:
                    disabled_until_level = None
            if disabled_until_level is None:
                if match_in(Keyword("yield"), body):
                    # we can't tco or tre generators
                    lines = raw_lines
                    break
                elif match_in(Keyword("def") | Keyword("try") | Keyword("with"), body):
                    disabled_until_level = level
                else:
                    base, comment = split_comment(body)
                    tre_base = None
                    # tre does not work with decorators, though tco does
                    if not decorators and attempt_tre:
                        # attempt tre
                        with self.complain_on_err():
                            tre_base = transform(self.tre_return(func_name, func_args, func_store, use_mock=use_mock), base)
                        if tre_base is not None:
                            line = tre_base + comment + indent
                            tre = True
                            # when tco is available, tre falls back on it if the function is changed
                            tco = not self.no_tco
                    if tre_base is None and not self.no_tco:
                        # attempt tco
                        tco_base = None
                        with self.complain_on_err():
                            tco_base = transform(self.tco_return, base)
                        if tco_base is not None:
                            line = tco_base + comment + indent
                            tco = True
            lines.append(line)
            level += ind_change(indent)

        out = "".join(lines)
        if tre:
            indent, base = split_leading_indent(out, 1)
            base, dedent = split_trailing_indent(base, 1)
            base, base_dedent = split_trailing_indent(base)
            out = (
                indent + (
                    "def " + tre_mock_var + func_params + ": return " + func_args + "\n"
                    if use_mock else ""
                ) + "while True:\n"
                    + openindent + base + base_dedent
                    + ("\n" if "\n" not in base_dedent else "") + "return None"
                    + ("\n" if "\n" not in dedent else "") + closeindent + dedent
                + func_store + " = " + (func_name if undotted_name is None else undotted_name) + "\n"
            )
        out = def_stmt + out
        if tco:
            out = "@_coconut_tco\n" + out
        if decorators:
            out = decorators + out
        if undotted_name is not None:
            out += func_name + " = " + undotted_name + "\n"
        return out

    def unsafe_typedef_handle(self, tokens):
        """Process type annotations without a comma after them."""
        return self.typedef_handle(tokens.asList() + [","])

    def wrap_typedef(self, typedef):
        """Wrap a type definition in a string to defer it.
        Used for function type annotations on Python 3, the only ones evaluated at runtime."""
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
            if self.target_info >= (3, 6):
                return tokens[0] + ": " + tokens[1]
            else:
                return tokens[0] + " = None" + self.wrap_comment(" type: " + tokens[1])
        elif len(tokens) == 3:
            if self.target_info >= (3, 6):
                return tokens[0] + ": " + tokens[1] + " = " + tokens[2]
            else:
                return tokens[0] + " = " + tokens[2] + self.wrap_comment(" type: " + tokens[1])
        else:
            raise CoconutInternalException("invalid variable type annotation tokens", tokens)

    def with_stmt_handle(self, tokens):
        """Process with statements."""
        internal_assert(len(tokens) == 2, "invalid with statement tokens", tokens)
        withs, body = tokens
        if len(withs) == 1 or self.target_info >= (2, 7):
            return "with " + ", ".join(withs) + body
        else:
            return (
                "".join("with " + expr + ":\n" + openindent for expr in withs[:-1])
                + "with " + withs[-1] + body
                + closeindent * (len(withs) - 1)
            )

# end: COMPILER HANDLERS
#-----------------------------------------------------------------------------------------------------------------------
# CHECKING HANDLERS:
#-----------------------------------------------------------------------------------------------------------------------

    def check_strict(self, name, original, loc, tokens):
        """Check that syntax meets --strict requirements."""
        internal_assert(len(tokens) == 1, "invalid " + name + " tokens", tokens)
        if self.strict:
            raise self.make_err(CoconutStyleError, "found " + name, original, loc)
        else:
            return tokens[0]

    def lambdef_check(self, original, loc, tokens):
        """Check for Python-style lambdas."""
        return self.check_strict("Python-style lambda", original, loc, tokens)

    def endline_semicolon_check(self, original, loc, tokens):
        """Check for semicolons at the end of lines."""
        return self.check_strict("semicolon at end of line", original, loc, tokens)

    def u_string_check(self, original, loc, tokens):
        """Check for Python2-style unicode strings."""
        return self.check_strict("Python-2-style unicode string", original, loc, tokens)

    def check_py(self, version, name, original, loc, tokens):
        """Check for Python-version-specific syntax."""
        internal_assert(len(tokens) == 1, "invalid " + name + " tokens", tokens)
        if self.target_info < get_target_info(version):
            raise self.make_err(CoconutTargetError, "found Python " + ".".join(version) + " " + name, original, loc, target=version)
        else:
            return tokens[0]

    def name_check(self, original, loc, tokens):
        """Check for Python 3 exec function."""
        internal_assert(len(tokens) == 1, "invalid name tokens", tokens)
        if tokens[0] == "exec":
            return self.check_py("3", "exec function", original, loc, tokens)
        elif tokens[0].startswith(reserved_prefix):
            raise self.make_err(CoconutSyntaxError, "variable names cannot start with reserved prefix " + reserved_prefix, original, loc)
        else:
            return tokens[0]

    def nonlocal_check(self, original, loc, tokens):
        """Check for Python 3 nonlocal statement."""
        return self.check_py("3", "nonlocal statement", original, loc, tokens)

    def star_assign_item_check(self, original, loc, tokens):
        """Check for Python 3 starred assignment."""
        return self.check_py("3", "starred assignment (add 'match' to front to produce universal code)", original, loc, tokens)

    def star_expr_check(self, original, loc, tokens):
        """Check for Python 3.5 star unpacking."""
        return self.check_py("35", "star unpacking (add 'match' to front to produce universal code)", original, loc, tokens)

    def matrix_at_check(self, original, loc, tokens):
        """Check for Python 3.5 matrix multiplication."""
        return self.check_py("35", "matrix multiplication", original, loc, tokens)

    def async_keyword_check(self, original, loc, tokens):
        """Check for Python 3.5 async statement."""
        return self.check_py("35", "async statement", original, loc, tokens)

    def async_comp_check(self, original, loc, tokens):
        """Check for Python 3.6 async comprehension."""
        return self.check_py("36", "async comprehension", original, loc, tokens)

    def await_keyword_check(self, original, loc, tokens):
        """Check for Python 3.5 await expression."""
        return self.check_py("35", "await expression", original, loc, tokens)

    def f_string_check(self, original, loc, tokens):
        """Check for Python 3.6 format strings."""
        return self.check_py("36", "format string", original, loc, tokens)

# end: CHECKING HANDLERS
#-----------------------------------------------------------------------------------------------------------------------
# ENDPOINTS:
#-----------------------------------------------------------------------------------------------------------------------

    def parse_single(self, inputstring):
        """Parse line code."""
        return self.parse(inputstring, self.single_parser, {}, {"header": "none", "initial": "none"})

    def parse_file(self, inputstring, addhash=True):
        """Parse file code."""
        if addhash:
            use_hash = self.genhash(False, inputstring)
        else:
            use_hash = None
        return self.parse(inputstring, self.file_parser, {"nl_at_eof_check": True}, {"header": "file", "use_hash": use_hash})

    def parse_exec(self, inputstring):
        """Parse exec code."""
        return self.parse(inputstring, self.file_parser, {}, {"header": "file", "initial": "none"})

    def parse_package(self, inputstring, addhash=True):
        """Parse package code."""
        if addhash:
            use_hash = self.genhash(True, inputstring)
        else:
            use_hash = None
        return self.parse(inputstring, self.file_parser, {"nl_at_eof_check": True}, {"header": "package", "use_hash": use_hash})

    def parse_block(self, inputstring):
        """Parse block code."""
        return self.parse(inputstring, self.file_parser, {}, {"header": "none", "initial": "none"})

    def parse_sys(self, inputstring):
        """Parse module code."""
        return self.parse(inputstring, self.file_parser, {}, {"header": "sys", "initial": "none"})

    def parse_eval(self, inputstring):
        """Parse eval code."""
        return self.parse(inputstring, self.eval_parser, {"strip": True}, {"header": "none", "initial": "none"})

    def parse_debug(self, inputstring):
        """Parse debug code."""
        return self.parse(inputstring, self.file_parser, {"strip": True}, {"header": "none", "initial": "none", "final_endline": False})

    def warm_up(self):
        """Warm up the compiler by running something through it."""
        result = self.parse_debug("")
        internal_assert(result == "", "compiler warm-up should produce no code; instead got", result)

# end: ENDPOINTS
