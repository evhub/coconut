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
#   - Parser Handlers
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

from coconut.myparsing import (
    ParseBaseException,
    col,
    line as getline,
    lineno,
    nums,
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
    tre_check_var,
    py3_to_py2_stdlib,
    checksum,
    reserved_prefix,
    case_check_var,
    function_match_error_var,
    legal_indent_chars,
    format_var,
    match_val_repr_var,
    max_match_val_repr_len,
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
    split_leading_trailing_indent,
    match_in,
    transform,
    ignore_transform,
    parse,
    get_target_info_len2,
    split_leading_comment,
    compile_regex,
    keyword,
    append_it,
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
                openindent + mod_name + ' = _coconut.types.ModuleType("' + mod_name + '")',
                closeindent + "else:",
                openindent + "if not _coconut.isinstance(" + mod_name + ", _coconut.types.ModuleType):",
                openindent + mod_name + ' = _coconut.types.ModuleType("' + mod_name + '")' + closeindent * 2,
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
        elif not target:  # universal compatibility
            paths = (old_imp, imp, version_check)
        elif get_target_info_len2(target) >= version_check:  # if lowest is above, we can safely use new
            paths = (imp,)
        elif target.startswith("2"):  # "2" and "27" can safely use old
            paths = (old_imp,)
        elif get_target_info(target) < version_check:  # "3" should be compatible with all 3+
            paths = (old_imp, imp, version_check)
        else:  # "35" and above can safely use new
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


def imported_names(imports):
    """Yields all the names imported by imports = [[imp1], [imp2, as], ...]."""
    for imp in imports:
        yield imp[-1].split(".", 1)[0]


def split_args_list(tokens, loc):
    """Splits function definition arguments."""
    req_args, def_args, star_arg, kwd_args, dubstar_arg = [], [], None, [], None
    pos = 0
    for arg in tokens:
        if len(arg) == 1:
            if arg[0] == "*":
                # star sep (pos = 3)
                if pos >= 3:
                    raise CoconutDeferredSyntaxError("star separator at invalid position in function definition", loc)
                pos = 3
            else:
                # pos arg (pos = 0)
                if pos > 0:
                    raise CoconutDeferredSyntaxError("positional arguments must come first in function definition", loc)
                req_args.append(arg[0])
        elif len(arg) == 2:
            if arg[0] == "*":
                # star arg (pos = 2)
                if pos >= 2:
                    raise CoconutDeferredSyntaxError("star argument at invalid position in function definition", loc)
                pos = 2
                star_arg = arg[1]
            elif arg[0] == "**":
                # dub star arg (pos = 4)
                if pos == 4:
                    raise CoconutDeferredSyntaxError("double star argument at invalid position in function definition", loc)
                pos = 4
                dubstar_arg = arg[1]
            else:
                # def arg (pos = 1)
                if pos <= 1:
                    pos = 1
                    def_args.append((arg[0], arg[1]))
                # kwd arg (pos = 3)
                elif pos <= 3:
                    pos = 3
                    kwd_args.append((arg[0], arg[1]))
                else:
                    raise CoconutDeferredSyntaxError("invalid default argument in function definition", loc)
        else:
            raise CoconutInternalException("invalid function definition argument", arg)
    return req_args, def_args, star_arg, kwd_args, dubstar_arg


def match_case_tokens(loc, tokens, check_var, top):
    """Build code for matching the given case."""
    if len(tokens) == 2:
        matches, stmts = tokens
        cond = None
    elif len(tokens) == 3:
        matches, cond, stmts = tokens
    else:
        raise CoconutInternalException("invalid case match tokens", tokens)
    matching = Matcher(loc, check_var)
    matching.match(matches, match_to_var)
    if cond:
        matching.add_guard(cond)
    return matching.build(stmts, set_check_var=top)


# end: HANDLERS
# -----------------------------------------------------------------------------------------------------------------------
# COMPILER:
# -----------------------------------------------------------------------------------------------------------------------


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

    def genhash(self, code, package_level=-1):
        """Generate a hash from code."""
        reduce_args = self.__reduce__()[1]
        logger.log(
            "Hash args:", {
                "VERSION_STR": VERSION_STR,
                "reduce_args": reduce_args,
                "package_level": package_level,
            },
        )
        return hex(checksum(
            hash_sep.join(
                str(item) for item in (
                    (VERSION_STR,)
                    + reduce_args
                    + (package_level, code)
                )
            ).encode(default_encoding),
        ))

    def reset(self):
        """Resets references."""
        self.indchar = None
        self.comments = {}
        self.refs = []
        self.set_skips([])
        self.docstring = ""
        self.ichain_count = 0
        self.tre_store_count = 0
        self.case_check_count = 0
        self.stmt_lambdas = []
        if self.strict:
            self.unused_imports = set()
        self.bind()

    def bind(self):
        """Binds reference objects to the proper parse actions."""
        self.endline <<= attach(self.endline_ref, self.endline_handle)

        self.moduledoc_item <<= trace(attach(self.moduledoc, self.set_docstring))
        self.name <<= trace(attach(self.base_name, self.name_check))
        # comments are evaluated greedily because we need to know about them even if we're going to suppress them
        self.comment <<= trace(attach(self.comment_ref, self.comment_handle, greedy=True))
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
        self.typedef <<= trace(attach(self.typedef_ref, self.typedef_handle))
        self.typedef_default <<= trace(attach(self.typedef_default_ref, self.typedef_handle))
        self.unsafe_typedef_default <<= trace(attach(self.unsafe_typedef_default_ref, self.unsafe_typedef_handle))
        self.return_typedef <<= trace(attach(self.return_typedef_ref, self.typedef_handle))
        self.typed_assign_stmt <<= trace(attach(self.typed_assign_stmt_ref, self.typed_assign_stmt_handle))
        self.datadef <<= trace(attach(self.datadef_ref, self.data_handle))
        self.match_datadef <<= trace(attach(self.match_datadef_ref, self.match_data_handle))
        self.with_stmt <<= trace(attach(self.with_stmt_ref, self.with_stmt_handle))
        self.await_item <<= trace(attach(self.await_item_ref, self.await_item_handle))
        self.ellipsis <<= trace(attach(self.ellipsis_ref, self.ellipsis_handle))
        self.case_stmt <<= trace(attach(self.case_stmt_ref, self.case_stmt_handle))
        self.f_string <<= attach(self.f_string_ref, self.f_string_handle)

        self.decoratable_normal_funcdef_stmt <<= trace(attach(
            self.decoratable_normal_funcdef_stmt_ref,
            self.decoratable_funcdef_stmt_handle,
        ))
        self.decoratable_async_funcdef_stmt <<= trace(attach(
            self.decoratable_async_funcdef_stmt_ref,
            partial(self.decoratable_funcdef_stmt_handle, is_async=True),
        ))

        self.u_string <<= attach(self.u_string_ref, self.u_string_check)
        self.matrix_at <<= attach(self.matrix_at_ref, self.matrix_at_check)
        self.nonlocal_stmt <<= attach(self.nonlocal_stmt_ref, self.nonlocal_check)
        self.star_assign_item <<= attach(self.star_assign_item_ref, self.star_assign_item_check)
        self.classic_lambdef <<= attach(self.classic_lambdef_ref, self.lambdef_check)
        self.star_expr <<= attach(self.star_expr_ref, self.star_expr_check)
        self.dubstar_expr <<= attach(self.dubstar_expr_ref, self.star_expr_check)
        self.star_sep_arg <<= attach(self.star_sep_arg_ref, self.star_sep_check)
        self.star_sep_vararg <<= attach(self.star_sep_vararg_ref, self.star_sep_check)
        self.endline_semicolon <<= attach(self.endline_semicolon_ref, self.endline_semicolon_check)
        self.async_stmt <<= attach(self.async_stmt_ref, self.async_stmt_check)
        self.async_comp_for <<= attach(self.async_comp_for_ref, self.async_comp_check)
        self.namedexpr <<= attach(self.namedexpr_ref, self.namedexpr_check)

    def copy_skips(self):
        """Copy the line skips."""
        return self.skips[:]

    def set_skips(self, skips):
        """Set the line skips."""
        skips.sort()
        internal_assert(lambda: len(set(skips)) == len(skips), "duplicate line skip(s) in skips", skips)
        self.skips = skips

    def adjust(self, ln):
        """Converts a parsing line number into an original line number."""
        adj_ln = ln
        need_unskipped = 0
        for i in self.skips:
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
        if index is not None:
            return self.reformat(snip), len(self.reformat(snip[:index]))
        else:
            return self.repl_proc(snip, reformatting=True, log=False)

    def eval_now(self, code):
        """Reformat and evaluate a code snippet and return code for the result."""
        result = eval(self.reformat(code))
        if result is None or isinstance(result, (bool, int, float, complex)):
            return repr(result)
        elif isinstance(result, bytes):
            return "b" + self.wrap_str_of(result)
        elif isinstance(result, str):
            return self.wrap_str_of(result)
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

    def add_ref(self, reftype, data):
        """Add a reference and returns the identifier."""
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
            use_hash=use_hash,
            target=self.target,
            no_tco=self.no_tco,
            strict=self.strict,
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
        """Use the parser to parse the inputstring with appropriate setup and teardown."""
        self.reset()
        pre_procd = None
        with logger.gather_parsing_stats():
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
                if name != "*":
                    logger.warn("found unused import", name, extra="disable --strict to dismiss")
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

    def stmt_lambda_proc(self, inputstring, **kwargs):
        """Add statement lambda definitions."""
        regexes = []
        for i in range(len(self.stmt_lambdas)):
            name = self.stmt_lambda_name(i)
            regex = compile_regex(r"\b%s\b" % (name,))
            regexes.append(regex)
        out = []
        for line in inputstring.splitlines():
            for i, regex in enumerate(regexes):
                if regex.search(line):
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
                complain(CoconutInternalException(
                    "out of bounds line number", ln,
                    "not in range [1, " + str(len(self.original_lines) + 2) + "]",
                ))
            if ln >= len(self.original_lines) + 1:  # trim too large
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
            return ""
        return self.wrap_comment(comment, reformat=False)

    def endline_repl(self, inputstring, reformatting=False, **kwargs):
        """Add end of line comments."""
        out = []
        ln = 1  # line number
        for line in inputstring.splitlines():
            add_one_to_ln = False
            try:
                if line.endswith(lnwrapper):
                    line, index = line[:-1].rsplit("#", 1)
                    new_ln = self.get_ref("ln", index)
                    if new_ln < ln:
                        raise CoconutInternalException("line number decreased", (ln, new_ln))
                    ln = new_ln
                    line = line.rstrip()
                    add_one_to_ln = True
                if not reformatting or add_one_to_ln:  # add_one_to_ln here is a proxy for whether there was a ln comment or not
                    line += self.comments.get(ln, "")
                if not reformatting and line.rstrip() and not line.lstrip().startswith("#"):
                    line += self.ln_comment(ln)
            except CoconutInternalException as err:
                complain(err)
            out.append(line)
            if add_one_to_ln:
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
        internal_assert(lambda: ln not in self.comments, "multiple comments on line", ln)
        self.comments[ln] = tokens[0]
        return ""

    def augassign_handle(self, tokens):
        """Process assignments."""
        internal_assert(len(tokens) == 3, "invalid assignment tokens", tokens)
        name, op, item = tokens
        out = ""
        if op == "|>=":
            out += name + " = (" + item + ")(" + name + ")"
        elif op == "|*>=":
            out += name + " = (" + item + ")(*" + name + ")"
        elif op == "|**>=":
            out += name + " = (" + item + ")(**" + name + ")"
        elif op == "<|=":
            out += name + " = " + name + "((" + item + "))"
        elif op == "<*|=":
            out += name + " = " + name + "(*(" + item + "))"
        elif op == "<**|=":
            out += name + " = " + name + "(**(" + item + "))"
        elif op == "..=" or op == "<..=":
            out += name + " = _coconut_forward_compose((" + item + "), " + name + ")"
        elif op == "..>=":
            out += name + " = _coconut_forward_compose(" + name + ", (" + item + "))"
        elif op == "<*..=":
            out += name + " = _coconut_forward_star_compose((" + item + "), " + name + ")"
        elif op == "..*>=":
            out += name + " = _coconut_forward_star_compose(" + name + ", (" + item + "))"
        elif op == "<**..=":
            out += name + " = _coconut_forward_dubstar_compose((" + item + "), " + name + ")"
        elif op == "..**>=":
            out += name + " = _coconut_forward_dubstar_compose(" + name + ", (" + item + "))"
        elif op == "??=":
            out += name + " = " + item + " if " + name + " is None else " + name
        elif op == "::=":
            ichain_var = lazy_chain_var + "_" + str(self.ichain_count)
            self.ichain_count += 1
            # this is necessary to prevent a segfault caused by self-reference
            out += (
                ichain_var + " = " + name + "\n"
                + name + " = _coconut.itertools.chain.from_iterable(" + lazy_list_handle([ichain_var, "(" + item + ")"]) + ")"
            )
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
            if "tests" in tokens[0]:
                if self.strict and tokens[0][0] == "(object)":
                    raise self.make_err(CoconutStyleError, "unnecessary inheriting from object (Coconut does this automatically)", original, loc)
                return tokens[0][0]
            elif "args" in tokens[0]:
                if self.target.startswith("3"):
                    return tokens[0][0]
                else:
                    raise self.make_err(CoconutTargetError, "found Python 3 keyword class definition", original, loc, target="3")
            else:
                raise CoconutInternalException("invalid inner classlist token", tokens[0])
        else:
            raise CoconutInternalException("invalid classlist tokens", tokens)

    def match_data_handle(self, original, loc, tokens):
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

        matcher = Matcher(loc, match_check_var, name_list=[])

        req_args, def_args, star_arg, kwd_args, dubstar_arg = split_args_list(matches, loc)
        matcher.match_function(match_to_args_var, match_to_kwargs_var, req_args + def_args, star_arg, kwd_args, dubstar_arg)

        if cond is not None:
            matcher.add_guard(cond)

        arg_names = ", ".join(matcher.name_list)
        arg_tuple = arg_names + ("," if len(matcher.name_list) == 1 else "")

        extra_stmts = '''def __new__(_cls, *{match_to_args_var}, **{match_to_kwargs_var}):
            {oind}{match_check_var} = False
            {matching}
            {pattern_error}
            return _coconut.tuple.__new__(_cls, ({arg_tuple}))
        {cind}'''.format(
            oind=openindent,
            cind=closeindent,
            match_to_args_var=match_to_args_var,
            match_to_kwargs_var=match_to_kwargs_var,
            match_check_var=match_check_var,
            matching=matcher.out(),
            pattern_error=self.pattern_error(original, loc, match_to_args_var, match_check_var, function_match_error_var),
            arg_tuple=arg_tuple,
        )

        namedtuple_call = '_coconut.collections.namedtuple("' + name + '", "' + arg_names + '")'

        return self.assemble_data(name, namedtuple_call, inherit, extra_stmts, stmts)

    def data_handle(self, loc, tokens):
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

        attr_str = " ".join(base_args)
        extra_stmts = ""
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
                        {oind}raise _coconut.ValueError("Got unexpected field names: " + _coconut.repr(kwds.keys()))
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
                    all_args=", ".join(all_args),
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
                        {oind}raise _coconut.ValueError("Got unexpected field names: " + _coconut.repr(kwds.keys()))
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
                all_args=", ".join(all_args),
                args_tuple="(" + ", ".join(base_args) + ("," if len(base_args) == 1 else "") + ")",
            )

        if types:
            namedtuple_call = '_coconut.typing.NamedTuple("' + name + '", [' + ", ".join(
                '("' + argname + '", ' + self.wrap_typedef(types.get(i, "_coconut.typing.Any")) + ")"
                for i, argname in enumerate(base_args + ([starred_arg] if starred_arg is not None else []))
            ) + "])"
        else:
            namedtuple_call = '_coconut.collections.namedtuple("' + name + '", "' + attr_str + '")'

        return self.assemble_data(name, namedtuple_call, inherit, extra_stmts, stmts)

    def assemble_data(self, name, namedtuple_call, inherit, extra_stmts, stmts):
        # create class
        out = (
            "class " + name + "(" + namedtuple_call + (
                ", " + inherit if inherit is not None
                else ", _coconut.object" if not self.target.startswith("3")
                else ""
            ) + "):\n" + openindent
        )

        # add universal statements
        extra_stmts = '''__slots__ = ()
        __ne__ = _coconut.object.__ne__
        def __eq__(self, other):
            {oind}return self.__class__ is other.__class__ and _coconut.tuple.__eq__(self, other)
        {cind}def __hash__(self):
            {oind}return _coconut.tuple.__hash__(self) ^ hash(self.__class__)
        {cind}'''.format(
            oind=openindent,
            cind=closeindent,
        ) + extra_stmts

        # manage docstring
        rest = None
        if "simple" in stmts and len(stmts) == 1:
            out += extra_stmts
            rest = stmts[0]
        elif "docstring" in stmts and len(stmts) == 1:
            out += stmts[0] + extra_stmts
        elif "complex" in stmts and len(stmts) == 1:
            out += extra_stmts
            rest = "".join(stmts[0])
        elif "complex" in stmts and len(stmts) == 2:
            out += stmts[0] + extra_stmts
            rest = "".join(stmts[1])
        elif "empty" in stmts and len(stmts) == 1:
            out += extra_stmts.rstrip() + stmts[0]
        else:
            raise CoconutInternalException("invalid inner data tokens", stmts)

        # create full data definition
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
        if self.strict:
            self.unused_imports.update(imported_names(imports))
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

    def pattern_error(self, original, loc, value_var, check_var, match_error_class='_coconut_MatchError'):
        """Construct a pattern-matching error message."""
        base_line = clean(self.reformat(getline(loc, original)))
        line_wrap = self.wrap_str_of(base_line)
        repr_wrap = self.wrap_str_of(ascii(base_line))
        return (
            "if not " + check_var + ":\n" + openindent
            + match_val_repr_var + " = _coconut.repr(" + value_var + ")\n"
            + match_err_var + " = " + match_error_class + '("pattern-matching failed for " '
            + repr_wrap + ' " in " + (' + match_val_repr_var
            + " if _coconut.len(" + match_val_repr_var + ") <= " + str(max_match_val_repr_len)
            + " else " + match_val_repr_var + "[:" + str(max_match_val_repr_len) + '] + "..."))\n'
            + match_err_var + ".pattern = " + line_wrap + "\n"
            + match_err_var + ".value = " + value_var + "\n"
            + "raise " + match_err_var + "\n" + closeindent
        )

    def destructuring_stmt_handle(self, original, loc, tokens):
        """Process match assign blocks."""
        internal_assert(len(tokens) == 2, "invalid destructuring assignment tokens", tokens)
        matches, item = tokens
        out = match_handle(loc, [matches, "in", item, None])
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

        matcher = Matcher(loc, match_check_var)

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
            # we only include match_to_args_var here because match_to_kwargs_var is modified during matching
            + self.pattern_error(original, loc, match_to_args_var, match_check_var, function_match_error_var)
            + closeindent
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
            if "tests" in tokens:
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
            match_tokens = [name] + list(params)
            self.stmt_lambdas.append(
                "".join(self.name_match_funcdef_handle(original, loc, match_tokens))
                + body,
            )
        return name

    @contextmanager
    def complain_on_err(self):
        """Complain about any parsing-related errors raised inside."""
        try:
            yield
        except ParseBaseException as err:
            complain(self.make_parse_err(err, reformat=False, include_ln=False))
        except CoconutException as err:
            complain(err)

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

    def tre_return(self, func_name, func_args, func_store, use_mock=True):
        """Generate grammar element that matches a string which is just a TRE return statement."""
        def tre_return_handle(loc, tokens):
            internal_assert(len(tokens) == 1, "invalid tail recursion elimination tokens", tokens)
            args = tokens[0][1:-1]  # strip parens
            # check if there is anything in the arguments that will store a reference
            # to the current scope, and if so, abort TRE, since it can't handle that
            if match_in(self.stores_scope, args):
                return ignore_transform  # this is the only way to make the outer transform call return None
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
                "try:\n" + openindent
                + tre_check_var + " = " + func_name + " is " + func_store + "\n" + closeindent
                + "except _coconut.NameError:\n" + openindent
                + tre_check_var + " = False\n" + closeindent
                + "if " + tre_check_var + ":\n" + openindent
                + tre_recurse + "\n" + closeindent
                + "else:\n" + openindent
                + tco_recurse + "\n" + closeindent
            )
        return attach(
            self.start_marker + (keyword("return") + keyword(func_name)).suppress() + self.parens + self.end_marker,
            tre_return_handle,
        )

    yield_regex = compile_regex(r"\byield\b")
    def_regex = compile_regex(r"(async\s+)?def\b")
    tre_disable_regex = compile_regex(r"(try|(async\s+)?(with|for)|while)\b")
    return_regex = compile_regex(r"return\b")

    def transform_returns(self, raw_lines, tre_return_grammar=None, use_mock=None, is_async=False):
        """Apply TCO, TRE, or async universalization to the given function."""
        lines = []  # transformed lines
        tco = False  # whether tco was done
        tre = False  # whether tre was done
        level = 0  # indentation level
        disabled_until_level = None  # whether inside of a disabled block
        attempt_tre = tre_return_grammar is not None  # whether to even attempt tre
        attempt_tco = not is_async and not self.no_tco  # whether to even attempt tco

        if is_async:
            internal_assert(not attempt_tre and not attempt_tco, "cannot tail call optimize async functions")

        for line in raw_lines:
            indent, body, dedent = split_leading_trailing_indent(line)
            base, comment = split_comment(body)

            level += ind_change(indent)

            if disabled_until_level is not None:
                if level <= disabled_until_level:
                    disabled_until_level = None

            if disabled_until_level is None:

                # tco and tre don't support generators
                if not is_async and self.yield_regex.search(body):
                    lines = raw_lines  # reset lines
                    break

                # don't touch inner functions
                elif self.def_regex.match(body):
                    disabled_until_level = level

                # tco and tre shouldn't touch scopes that depend on actual return statements
                #  or scopes where we can't insert a continue
                elif not is_async and self.tre_disable_regex.match(body):
                    disabled_until_level = level

                else:

                    if is_async:
                        if self.return_regex.match(base):
                            to_return = base[len("return"):].strip()
                            if to_return:  # leave empty return statements alone
                                line = indent + "raise _coconut.asyncio.Return(" + to_return + ")" + comment + dedent

                    tre_base = None
                    if attempt_tre:
                        with self.complain_on_err():
                            tre_base = transform(tre_return_grammar, base)
                        if tre_base is not None:
                            line = indent + tre_base + comment + dedent
                            tre = True
                            # when tco is available, tre falls back on it if the function is changed
                            tco = not self.no_tco

                    if attempt_tco and tre_base is None:  # don't attempt tco if tre succeeded
                        tco_base = None
                        with self.complain_on_err():
                            tco_base = transform(self.tco_return, base)
                        if tco_base is not None:
                            line = indent + tco_base + comment + dedent
                            tco = True

            level += ind_change(dedent)
            lines.append(line)

        func_code = "".join(lines)
        if is_async:
            return func_code
        else:
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
        func_name, func_args, func_params = None, None, None
        with self.complain_on_err():
            func_name, func_args, func_params = parse(self.split_func, def_stmt)

        # handle addpattern functions
        if addpattern:
            if func_name is None:
                raise CoconutInternalException("could not find name in addpattern function definition", def_stmt)
            # binds most tightly, except for TCO
            decorators += "@_coconut_addpattern(" + func_name + ")\n"

        # handle dotted function definition
        undotted_name = None  # the function __name__ if func_name is a dotted name
        if func_name is not None:
            if "." in func_name:
                undotted_name = func_name.rsplit(".", 1)[-1]
                def_stmt_pre_lparen, def_stmt_post_lparen = def_stmt.split("(", 1)
                def_stmt_pre_lparen = def_stmt_pre_lparen.replace(func_name, undotted_name)
                def_stmt = def_stmt_pre_lparen + "(" + def_stmt_post_lparen

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

            # only Python 3.3+ supports returning values inside generators
            if self.target_info < (3, 3):
                func_code = self.transform_returns(raw_lines, is_async=True)
            else:
                func_code = "".join(raw_lines)

        # handle normal functions
        else:
            # tre does not work with decorators, though tco does
            attempt_tre = func_name is not None and not decorators
            if attempt_tre:
                use_mock = func_args and func_args != func_params[1:-1]
                func_store = tre_store_var + "_" + str(self.tre_store_count)
                self.tre_store_count += 1
                tre_return_grammar = self.tre_return(func_name, func_args, func_store, use_mock)
            else:
                use_mock = func_store = tre_return_grammar = None

            func_code, tco, tre = self.transform_returns(
                raw_lines,
                tre_return_grammar,
                use_mock,
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
                        "def " + tre_mock_var + func_params + ": return " + func_args + "\n"
                        if use_mock else ""
                    ) + "while True:\n"
                        + openindent + base + base_dedent
                        + ("\n" if "\n" not in base_dedent else "") + "return None"
                        + ("\n" if "\n" not in dedent else "") + closeindent + dedent
                    + func_store + " = " + (func_name if undotted_name is None else undotted_name) + "\n"
                )
            if tco:
                decorators += "@_coconut_tco\n"  # binds most tightly

        out = decorators + def_stmt + func_code
        if undotted_name is not None:
            out += func_name + " = " + undotted_name + "\n"
        return out

    def await_item_handle(self, original, loc, tokens):
        """Check for Python 3.5 await expression."""
        internal_assert(len(tokens) == 1, "invalid await statement tokens", tokens)
        if not self.target:
            self.make_err(
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

    def wrap_typedef(self, typedef):
        """Wrap a type definition in a string to defer it."""
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
                return tokens[0] + ": " + self.wrap_typedef(tokens[1])
            else:
                return tokens[0] + " = None" + self.wrap_comment(" type: " + tokens[1])
        elif len(tokens) == 3:
            if self.target_info >= (3, 6):
                return tokens[0] + ": " + self.wrap_typedef(tokens[1]) + " = " + tokens[2]
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

    def ellipsis_handle(self, tokens):
        internal_assert(len(tokens) == 1, "invalid ellipsis tokens", tokens)
        if self.target.startswith("3"):
            return "..."
        else:
            return "_coconut.Ellipsis"

    def case_stmt_handle(self, loc, tokens):
        """Process case blocks."""
        if len(tokens) == 2:
            item, cases = tokens
            default = None
        elif len(tokens) == 3:
            item, cases, default = tokens
        else:
            raise CoconutInternalException("invalid case tokens", tokens)
        check_var = case_check_var + "_" + str(self.case_check_count)
        self.case_check_count += 1
        out = (
            match_to_var + " = " + item + "\n"
            + match_case_tokens(loc, cases[0], check_var, True)
        )
        for case in cases[1:]:
            out += (
                "if not " + check_var + ":\n" + openindent
                + match_case_tokens(loc, case, check_var, False) + closeindent
            )
        if default is not None:
            out += "if not " + check_var + default
        return out

    def f_string_handle(self, original, loc, tokens):
        """Handle Python 3.6 format strings."""
        internal_assert(len(tokens) == 1, "invalid format string tokens", tokens)
        string = tokens[0]
        if self.target_info >= (3, 6):
            return "f" + string
        else:
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
            new_text = ""
            exprs = []
            saw_brace = False
            in_expr = False
            expr_level = 0
            for c in old_text:
                if saw_brace:
                    saw_brace = False
                    if c == "{":
                        new_text += c
                    elif c == "}":
                        raise self.make_err(CoconutSyntaxError, "empty expressing in format string", original, loc)
                    else:
                        in_expr = True
                        expr_level = paren_change(c)
                        exprs.append(c)
                elif in_expr:
                    if expr_level < 0:
                        expr_level += paren_change(c)
                        exprs[-1] += c
                    elif expr_level > 0:
                        raise self.make_err(CoconutSyntaxError, "imbalanced parentheses in format string expression", original, loc)
                    elif c in "!:}":  # these characters end the expr
                        in_expr = False
                        name = format_var + "_" + str(len(exprs) - 1)
                        new_text += name + c
                    else:
                        exprs[-1] += c
                elif c == "{":
                    saw_brace = True
                    new_text += c
                else:
                    new_text += c

            # handle dangling detections
            if saw_brace:
                raise self.make_err(CoconutSyntaxError, "format string ends with unescaped brace (escape by doubling to '{{')", original, loc)
            if in_expr:
                raise self.make_err(CoconutSyntaxError, "imbalanced braces in format string (escape braces by doubling to '{{' and '}}')", original, loc)

            # generate format call
            return ("r" if raw else "") + strchar + new_text + strchar + ".format(" + ", ".join(
                format_var + "_" + str(i) + "=(" + expr + ")"
                for i, expr in enumerate(exprs)
            ) + ")"

# end: COMPILER HANDLERS
# -----------------------------------------------------------------------------------------------------------------------
# CHECKING HANDLERS:
# -----------------------------------------------------------------------------------------------------------------------

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
        """Check the given base name."""
        internal_assert(len(tokens) == 1, "invalid name tokens", tokens)
        if self.strict:
            self.unused_imports.discard(tokens[0])
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
        return self.check_py("3", "starred assignment (use 'match' to produce universal code)", original, loc, tokens)

    def star_expr_check(self, original, loc, tokens):
        """Check for Python 3.5 star unpacking."""
        return self.check_py("35", "star unpacking (use 'match' to produce universal code)", original, loc, tokens)

    def star_sep_check(self, original, loc, tokens):
        """Check for Python 3 keyword-only arguments."""
        return self.check_py("3", "keyword-only argument separator (use 'match' to produce universal code)", original, loc, tokens)

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
        """Parse module code."""
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
