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
#   - Setup
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

from pyparsing import (
    ParseBaseException,
    col,
    line as getline,
    lineno,
    nums,
    Keyword,
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
    tabworth,
    match_to_var,
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
    new_to_old_stdlib,
    default_recursion_limit,
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
    CoconutStyleWarning,
    clean,
)
from coconut.logging import logger, trace, complain
from coconut.compiler.grammar import (
    Grammar,
    lazy_list_handle,
    get_infix_items,
    Matcher,
    match_handle,
)
from coconut.compiler.util import (
    get_target_info,
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
    join_args,
    parse,
)
from coconut.compiler.header import (
    minify,
    getheader,
)

# end: IMPORTS
#-----------------------------------------------------------------------------------------------------------------------
# SETUP:
#-----------------------------------------------------------------------------------------------------------------------

if sys.getrecursionlimit() < default_recursion_limit:
    sys.setrecursionlimit(default_recursion_limit)

# end: SETUP
#-----------------------------------------------------------------------------------------------------------------------
# HANDLERS:
#-----------------------------------------------------------------------------------------------------------------------


def set_to_tuple(tokens):
    """Converts set literal tokens to tuples."""
    if len(tokens) != 1:
        raise CoconutInternalException("invalid set maker tokens", tokens)
    elif "comp" in tokens.keys() or "list" in tokens.keys():
        return "(" + tokens[0] + ")"
    elif "test" in tokens.keys():
        return "(" + tokens[0] + ",)"
    else:
        raise CoconutInternalException("invalid set maker item", tokens[0])


def gen_imports(path, impas):
    """Generates import statements."""
    out = []
    parts = path.split("./")  # denotes from ... import ...
    if len(parts) == 1:
        imp, = parts
        if impas == imp:
            out.append("import " + imp)
        elif "." not in impas:
            out.append("import " + imp + " as " + impas)
        else:
            fake_mods = impas.split(".")
            out.append("import " + imp + " as " + import_as_var)
            for i in range(1, len(fake_mods)):
                mod_name = ".".join(fake_mods[:i])
                out.extend((
                    "try:",
                    openindent + mod_name,
                    closeindent + "except:",
                    openindent + mod_name + ' = _coconut.imp.new_module("' + mod_name + '")',
                    closeindent + "else:",
                    openindent + "if not _coconut.isinstance(" + mod_name + ", _coconut.types.ModuleType):",
                    openindent + mod_name + ' = _coconut.imp.new_module("' + mod_name + '")' + closeindent * 2
                ))
            out.append(".".join(fake_mods) + " = " + import_as_var)
    else:
        imp_from, imp = parts
        if impas == imp:
            out.append("from " + imp_from + " import " + imp)
        else:
            out.append("from " + imp_from + " import " + imp + " as " + impas)
    return out

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

    def setup(self, target=None, strict=False, minify=False, line_numbers=False, keep_lines=False):
        """Initializes parsing parameters."""
        if target is None:
            target = ""
        else:
            target = str(target).replace(".", "")
        if target in pseudo_targets:
            target = pseudo_targets[target]
        if target not in targets:
            raise CoconutException('unsupported target Python version "' + target
                                   + '" (supported targets are "' + '", "'.join(specific_targets) + '", or leave blank for universal)')
        self.target, self.strict, self.minify, self.line_numbers, self.keep_lines = target, strict, minify, line_numbers, keep_lines

    def __reduce__(self):
        """Return pickling information."""
        return (Compiler, (self.target, self.strict, self.minify, self.line_numbers, self.keep_lines))

    def genhash(self, package, code):
        """Generates a hash from code."""
        return hex(checksum(
            hash_sep.join(
                str(item) for item in
                (VERSION_STR,)
                + self.__reduce__()[1]
                + (package, code)
            ).encode(default_encoding)
        ) & 0xffffffff)  # necessary for cross-compatibility

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
        self.moduledoc_item <<= trace(attach(self.moduledoc, self.set_docstring), "moduledoc")
        self.name <<= trace(attach(self.base_name, self.name_check), "name")
        self.atom_item <<= trace(attach(self.atom_item_ref, self.item_handle), "atom_item")
        self.no_partial_atom_item <<= trace(attach(self.no_partial_atom_item_ref, self.item_handle), "no_partial_atom_item")
        self.simple_assign <<= trace(attach(self.simple_assign_ref, self.item_handle), "simple_assign")
        self.set_literal <<= trace(attach(self.set_literal_ref, self.set_literal_handle), "set_literal")
        self.set_letter_literal <<= trace(attach(self.set_letter_literal_ref, self.set_letter_literal_handle), "set_letter_literal")
        self.classlist <<= trace(attach(self.classlist_ref, self.classlist_handle), "classlist")
        self.import_stmt <<= trace(attach(self.import_stmt_ref, self.import_handle), "import_stmt")
        self.complex_raise_stmt <<= trace(attach(self.complex_raise_stmt_ref, self.complex_raise_stmt_handle), "complex_raise_stmt")
        self.augassign_stmt <<= trace(attach(self.augassign_stmt_ref, self.augassign_handle), "augassign_stmt")
        self.dict_comp <<= trace(attach(self.dict_comp_ref, self.dict_comp_handle), "dict_comp")
        self.destructuring_stmt <<= trace(attach(self.destructuring_stmt_ref, self.destructuring_stmt_handle), "destructuring_stmt")
        self.name_match_funcdef <<= trace(attach(self.name_match_funcdef_ref, self.name_match_funcdef_handle), "name_match_funcdef")
        self.op_match_funcdef <<= trace(attach(self.op_match_funcdef_ref, self.op_match_funcdef_handle), "op_match_funcdef")
        self.yield_from <<= trace(attach(self.yield_from_ref, self.yield_from_handle), "yield_from")
        self.exec_stmt <<= trace(attach(self.exec_stmt_ref, self.exec_stmt_handle), "exec_stmt")
        self.stmt_lambdef <<= trace(attach(self.stmt_lambdef_ref, self.stmt_lambdef_handle), "stmt_lambdef")
        self.decoratable_normal_funcdef_stmt <<= trace(attach(self.decoratable_normal_funcdef_stmt_ref, self.decoratable_normal_funcdef_stmt_handle), "decoratable_normal_funcdef_stmt")
        self.function_call <<= trace(attach(self.function_call_tokens, self.function_call_handle), "function_call")
        self.pipe_expr <<= trace(attach(self.pipe_expr_ref, self.pipe_handle), "pipe_expr")
        self.no_chain_pipe_expr <<= trace(attach(self.no_chain_pipe_expr_ref, self.pipe_handle), "no_chain_pipe_expr")
        self.typedef <<= trace(attach(self.typedef_ref, self.typedef_handle), "typedef")
        self.typedef_default <<= trace(attach(self.typedef_default_ref, self.typedef_handle), "typedef")
        self.return_typedef <<= trace(attach(self.return_typedef_ref, self.typedef_handle), "return_typedef")
        self.u_string <<= attach(self.u_string_ref, self.u_string_check)
        self.f_string <<= attach(self.f_string_ref, self.f_string_check)
        self.matrix_at <<= attach(self.matrix_at_ref, self.matrix_at_check)
        self.nonlocal_stmt <<= attach(self.nonlocal_stmt_ref, self.nonlocal_check)
        self.star_assign_item <<= attach(self.star_assign_item_ref, self.star_assign_item_check)
        self.classic_lambdef <<= attach(self.classic_lambdef_ref, self.lambdef_check)
        self.async_funcdef <<= attach(self.async_funcdef_ref, self.async_stmt_check)
        self.async_match_funcdef <<= attach(self.async_match_funcdef_ref, self.async_stmt_check)
        self.async_stmt <<= attach(self.async_stmt_ref, self.async_stmt_check)
        self.await_keyword <<= attach(self.await_keyword_ref, self.await_keyword_check)
        self.star_expr <<= attach(self.star_expr_ref, self.star_expr_check)
        self.dubstar_expr <<= attach(self.dubstar_expr_ref, self.star_expr_check)
        self.endline_semicolon <<= attach(self.endline_semicolon_ref, self.endline_semicolon_check)

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
        """Post processes a preprocessed snippet."""
        if index is not None:
            return self.reformat(snip), len(self.reformat(snip[:index]))
        else:
            return self.repl_proc(snip, log=False, add_to_line=False)

    def make_err(self, errtype, message, original, loc, ln=None, reformat=True, *args, **kwargs):
        """Generates an error of the specified type."""
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
            logger.warn_err(self.make_err(CoconutStyleWarning, *args, **kwargs))

    def add_ref(self, ref):
        """Adds a reference and returns the identifier."""
        try:
            index = self.refs.index(ref)
        except ValueError:
            self.refs.append(ref)
            index = len(self.refs) - 1
        return str(index)

    def get_ref(self, index):
        """Retrieves a reference."""
        try:
            return self.refs[int(index)]
        except (IndexError, ValueError):
            raise CoconutInternalException("invalid reference", index)

    def wrap_str(self, text, strchar, multiline=False):
        """Wraps a string."""
        return strwrapper + self.add_ref((text, strchar, multiline)) + unwrapper

    def wrap_str_of(self, text):
        """Wraps a string of a string."""
        text_repr = ascii(text)
        return self.wrap_str(text_repr[1:-1], text_repr[-1])

    def wrap_passthrough(self, text, multiline=True):
        """Wraps a passthrough."""
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

    def wrap_comment(self, text):
        """Wraps a comment."""
        return "#" + self.add_ref(text) + unwrapper

    def wrap_line_number(self, ln):
        """Wraps a line number."""
        return "#" + self.add_ref(ln) + lnwrapper

    def apply_procs(self, procs, kwargs, inputstring, log=True):
        """Applies processors to inputstring."""
        for get_proc in procs:
            proc = get_proc(self)
            inputstring = proc(inputstring, **kwargs)
            if log:
                logger.log_tag(proc.__name__, inputstring, multiline=True)
        return inputstring

    def pre(self, inputstring, **kwargs):
        """Performs pre-processing."""
        out = self.apply_procs(self.preprocs, kwargs, str(inputstring))
        if self.line_numbers or self.keep_lines:
            logger.log_tag("skips", list(sorted(self.skips)))
        return out

    def post(self, tokens, **kwargs):
        """Performs post-processing."""
        if len(tokens) == 1:
            return self.apply_procs(self.postprocs, kwargs, tokens[0])
        else:
            raise CoconutInternalException("multiple tokens leftover", tokens)

    def headers(self, which, usehash=None):
        """Gets a formatted header."""
        return self.polish(getheader(which, self.target, usehash))

    @property
    def target_info(self):
        """Returns information on the current target as a version tuple."""
        return get_target_info(self.target)

    @property
    def target_info_len2(self):
        """Returns target_info as a length 2 tuple."""
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

    def should_indent(self, code):
        """Determines whether the next line should be indented."""
        last = rem_comment(code.splitlines()[-1])
        return last.endswith(":") or last.endswith("\\") or paren_change(last) < 0

    def parse(self, inputstring, parser, preargs, postargs):
        """Uses the parser to parse the inputstring."""
        self.reset()
        try:
            pre_procd = self.pre(inputstring, **preargs)
            parsed = parse(parser, pre_procd)
            out = self.post(parsed, **postargs)
        except ParseBaseException as err:
            err_line, err_index = self.reformat(err.line, err.col - 1)
            raise CoconutParseError(None, err_line, err_index, self.adjust(err.lineno))
        except RuntimeError as err:
            raise CoconutException(str(err),
                                   extra="try again with --recursion-limit greater than the current " + str(sys.getrecursionlimit()))
        return out

# end: COMPILER
#-----------------------------------------------------------------------------------------------------------------------
# PROCESSORS:
#-----------------------------------------------------------------------------------------------------------------------

    def prepare(self, inputstring, strip=False, nl_at_eof_check=False, **kwargs):
        """Prepares a string for processing."""
        if nl_at_eof_check and not inputstring.endswith("\n"):
            end_index = len(inputstring) - 1 if inputstring else 0
            self.strict_err_or_warn("missing new line at end of file", inputstring, end_index)
        original_lines = inputstring.splitlines()
        if self.keep_lines:
            self.original_lines = original_lines
        inputstring = "\n".join(original_lines)
        if strip:
            inputstring = inputstring.strip()
        return inputstring

    def str_proc(self, inputstring, **kwargs):
        """Processes strings and comments."""
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
                            out.append(self.wrap_comment(hold[_comment]) + c)
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
        """Processes python passthroughs."""
        out = []
        found = None  # store of characters that might be the start of a passthrough
        hold = None  # the contents of the passthrough so far
        count = None  # current parenthetical level
        multiline = None
        skips = self.skips.copy()

        for x in range(len(inputstring) + 1):
            if x == len(inputstring):
                c = "\n"
            else:
                c = inputstring[x]

            if hold is not None:
                count += paren_change(c)
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
        else:
            self.skips = skips
            return "".join(out)

    def leading(self, inputstring):
        """Counts leading whitespace."""
        count = 0
        for x in range(len(inputstring)):
            if inputstring[x] == " ":
                if self.indchar is None:
                    self.indchar = " "
                count += 1
            elif inputstring[x] == "\t":
                if self.indchar is None:
                    self.indchar = "\t"
                count += tabworth - (x % tabworth)
            else:
                break
            if self.indchar != inputstring[x]:
                self.strict_err_or_warn("found mixing of tabs and spaces", inputstring, x)
        return count

    def ind_proc(self, inputstring, **kwargs):
        """Processes indentation."""
        lines = inputstring.splitlines()
        new = []
        levels = []
        count = 0
        current = None
        skips = self.skips.copy()

        for ln in range(len(lines)):
            line = lines[ln]
            ln += 1
            line_rstrip = line.rstrip()
            if line != line_rstrip:
                if self.strict:
                    raise self.make_err(CoconutStyleError, "found trailing whitespace", line, len(line), self.adjust(ln))
                else:
                    line = line_rstrip
            if new:
                last = rem_comment(new[-1])
            else:
                last = None
            if not line or line.lstrip().startswith("#"):
                if count >= 0:
                    new.append(line)
                else:
                    skips = addskip(skips, self.adjust(ln))
            elif last is not None and last.endswith("\\"):
                if self.strict:
                    raise self.make_err(CoconutStyleError, "found backslash continuation", last, len(last), self.adjust(ln - 1))
                else:
                    skips = addskip(skips, self.adjust(ln))
                    new[-1] = last[:-1] + " " + line
            elif count < 0:
                skips = addskip(skips, self.adjust(ln))
                new[-1] = last + " " + line
            else:
                check = self.leading(line)
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
            count += paren_change(line)
            if count > 0:
                raise self.make_err(CoconutSyntaxError, "unmatched close parentheses", new[-1], len(new[-1]), self.adjust(len(new)))

        self.skips = skips
        if new:
            last = rem_comment(new[-1])
            if last.endswith("\\"):
                raise self.make_err(CoconutSyntaxError, "illegal final backslash continuation", last, len(last), self.adjust(len(new)))
            if count != 0:
                raise self.make_err(CoconutSyntaxError, "unclosed open parentheses", new[-1], len(new[-1]), self.adjust(len(new)))
        new.append(closeindent * len(levels))
        return "\n".join(new)

    def stmt_lambda_proc(self, inputstring, **kwargs):
        """Adds statement lambda definitions."""
        out = []
        for line in inputstring.splitlines():
            for i in range(len(self.stmt_lambdas)):
                name = self.stmt_lambda_name(i)
                if name in line:
                    indent, line = split_leading_indent(line)
                    out.append(indent + self.stmt_lambdas[i])
            out.append(line)
        return "\n".join(out)

    @property
    def tabideal(self):
        """Local tabideal."""
        return 1 if self.minify else tabideal

    def reind_proc(self, inputstring, **kwargs):
        """Adds back indentation."""
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
        """Gets an end line comment."""
        if self.keep_lines:
            if ln < 0 or ln - 1 > len(self.original_lines):
                raise CoconutInternalException("out of bounds line number", ln)
            elif ln - 1 == len(self.original_lines):
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
        return self.wrap_comment(comment)

    def endline_repl(self, inputstring, add_to_line=True, **kwargs):
        """Adds in end line comments."""
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
        """Adds back passthroughs."""
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
        """Adds back strings."""
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
                                out[-1] += "  "  # enforce two spaces before comment
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
        """Processes using replprocs."""
        return self.apply_procs(self.replprocs, kwargs, inputstring, log=log)

    def header_proc(self, inputstring, header="file", initial="initial", usehash=None, **kwargs):
        """Adds the header."""
        pre_header = getheader(initial, self.target, usehash)
        main_header = getheader(header, self.target)
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

    def set_docstring(self, original, loc, tokens):
        """Sets the docstring."""
        if len(tokens) == 2:
            self.docstring = self.reformat(tokens[0]) + "\n\n"
            return tokens[1]
        else:
            raise CoconutInternalException("invalid docstring tokens", tokens)

    def yield_from_handle(self, tokens):
        """Processes Python 3.3 yield from."""
        if len(tokens) != 1:
            raise CoconutInternalException("invalid yield from tokens", tokens)
        elif self.target_info < (3, 3):
            return (yield_from_var + " = " + tokens[0]
                    + "\nfor " + yield_item_var + " in " + yield_from_var + ":\n"
                    + openindent + "yield " + yield_item_var + "\n" + closeindent)
        else:
            return "yield from " + tokens[0]

    def endline_handle(self, original, loc, tokens):
        """Inserts line number comments when in line_numbers mode."""
        if len(tokens) != 1:
            raise CoconutInternalException("invalid endline tokens", tokens)
        out = tokens[0]
        if self.minify:
            out = out.splitlines(True)[0]  # if there are multiple new lines, take only the first one
        if self.line_numbers or self.keep_lines:
            out = self.wrap_line_number(self.adjust(lineno(loc, original))) + out
        return out

    def item_handle(self, original, loc, tokens):
        """Processes items."""
        out = tokens.pop(0)
        for trailer in tokens:
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
                elif trailer[0] == "$(":
                    raise self.make_err(CoconutSyntaxError, "a partial application argument is required", original, loc)
                else:
                    raise CoconutInternalException("invalid trailer symbol", trailer[0])
            elif len(trailer) == 2:
                if trailer[0] == "$(":
                    out = "_coconut.functools.partial(" + out + ", " + trailer[1] + ")"
                elif trailer[0] == "$[":
                    out = "_coconut_igetitem(" + out + ", " + trailer[1] + ")"
                else:
                    raise CoconutInternalException("invalid special trailer", trailer[0])
            else:
                raise CoconutInternalException("invalid trailer tokens", trailer)
        return out

    def augassign_handle(self, tokens):
        """Processes assignments."""
        if len(tokens) == 3:
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
            elif op == "..=":
                out += name + " = (lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs)))(" + name + ", (" + item + "))"
            elif op == "::=":
                ichain_var = lazy_chain_var + "_" + str(self.ichain_count)  # necessary to prevent a segfault caused by self-reference
                out += ichain_var + " = " + name + "\n"
                out += name + " = _coconut.itertools.chain.from_iterable(" + lazy_list_handle([ichain_var, "(" + item + ")"]) + ")"
                self.ichain_count += 1
            else:
                out += name + " " + op + " " + item
            return out
        else:
            raise CoconutInternalException("invalid assignment tokens", tokens)

    def classlist_handle(self, original, loc, tokens):
        """Processes class inheritance lists."""
        if len(tokens) == 0:
            if self.target.startswith("3"):
                return ""
            else:
                return "(_coconut.object)"
        elif len(tokens) == 1 and len(tokens[0]) == 1:
            if "tests" in tokens[0].keys():
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
        importmap = []  # [((imp | old_imp, imp, version_check), impas), ...]
        for imps in imports:
            if len(imps) == 1:
                imp, impas = imps[0], imps[0]
            else:
                imp, impas = imps
            if imp_from is not None:
                imp = imp_from + "./" + imp  # marker for from ... import ...
            old_imp = None
            path = imp.split(".")
            for i in reversed(range(1, len(path) + 1)):
                base, exts = ".".join(path[:i]), path[i:]
                clean_base = base.replace("/", "")
                if clean_base in new_to_old_stdlib:
                    old_imp, version_check = new_to_old_stdlib[clean_base]
                    if exts:
                        if "/" in base:
                            old_imp += "./"
                        else:
                            old_imp += "."
                        old_imp += ".".join(exts)
                    break
            if old_imp is None:
                paths = (imp,)
            elif self.target.startswith("2"):
                paths = (old_imp,)
            elif not self.target or self.target_info < version_check:
                paths = (old_imp, imp, version_check)
            else:
                paths = (imp,)
            importmap.append((paths, impas))
        stmts = []
        for paths, impas in importmap:
            if len(paths) == 1:
                more_stmts = gen_imports(paths[0], impas)
                stmts.extend(more_stmts)
            else:
                first, second, version_check = paths
                stmts.append("if _coconut_sys.version_info < " + str(version_check) + ":")
                first_stmts = gen_imports(first, impas)
                first_stmts[0] = openindent + first_stmts[0]
                first_stmts[-1] += closeindent
                stmts.extend(first_stmts)
                stmts.append("else:")
                second_stmts = gen_imports(second, impas)
                second_stmts[0] = openindent + second_stmts[0]
                second_stmts[-1] += closeindent
                stmts.extend(second_stmts)
        return "\n".join(stmts)

    def complex_raise_stmt_handle(self, tokens):
        """Processes Python 3 raise from statement."""
        if len(tokens) != 2:
            raise CoconutInternalException("invalid raise from tokens", tokens)
        elif self.target.startswith("3"):
            return "raise " + tokens[0] + " from " + tokens[1]
        else:
            return (raise_from_var + " = " + tokens[0] + "\n"
                    + raise_from_var + ".__cause__ = " + tokens[1] + "\n"
                    + "raise " + raise_from_var)

    def dict_comp_handle(self, original, loc, tokens):
        """Processes Python 2.7 dictionary comprehension."""
        if len(tokens) != 3:
            raise CoconutInternalException("invalid dictionary comprehension tokens", tokens)
        elif self.target.startswith("3"):
            key, val, comp = tokens
            return "{" + key + ": " + val + " " + comp + "}"
        else:
            key, val, comp = tokens
            return "dict(((" + key + "), (" + val + ")) " + comp + ")"

    def pattern_error(self, original, loc):
        """Constructs a pattern-matching error message."""
        base_line = clean(self.reformat(getline(loc, original)))
        line_wrap = self.wrap_str_of(base_line)
        repr_wrap = self.wrap_str_of(ascii(base_line))
        return ("if not " + match_check_var + ":\n" + openindent
                + match_err_var + ' = _coconut_MatchError("pattern-matching failed for " '
                + repr_wrap + ' " in " + _coconut.repr(_coconut.repr(' + match_to_var + ")))\n"
                + match_err_var + ".pattern = " + line_wrap + "\n"
                + match_err_var + ".value = " + match_to_var
                + "\nraise " + match_err_var + "\n" + closeindent)

    def destructuring_stmt_handle(self, original, loc, tokens):
        """Processes match assign blocks."""
        if len(tokens) == 2:
            matches, item = tokens
            out = match_handle(original, loc, (matches, item, None))
            out += self.pattern_error(original, loc)
            return out
        else:
            raise CoconutInternalException("invalid destructuring assignment tokens", tokens)

    def name_match_funcdef_handle(self, original, loc, tokens):
        """Processes match defs."""
        if len(tokens) == 2:
            func, matches = tokens
            cond = None
        elif len(tokens) == 3:
            func, matches, cond = tokens
        else:
            raise CoconutInternalException("invalid match function definition tokens", tokens)
        matching = Matcher()
        matching.match_sequence(("(", matches), match_to_var, typecheck=False)
        if cond is not None:
            matching.add_guard(cond)
        out = "def " + func + "(*" + match_to_var + "):\n" + openindent
        out += match_check_var + " = False\n"
        out += matching.out()
        out += self.pattern_error(original, loc) + closeindent
        return out

    def op_match_funcdef_handle(self, original, loc, tokens):
        """Processes infix match defs."""
        if len(tokens) == 3:
            name_tokens = get_infix_items(tokens)
        elif len(tokens) == 4:
            name_tokens = get_infix_items(tokens[:-1]) + tuple(tokens[-1:])
        else:
            raise CoconutInternalException("invalid infix match function definition tokens", tokens)
        return self.name_match_funcdef_handle(original, loc, name_tokens)

    def set_literal_handle(self, tokens):
        """Converts set literals to the right form for the target Python."""
        if len(tokens) != 1:
            raise CoconutInternalException("invalid set literal tokens", tokens)
        elif len(tokens[0]) != 1:
            raise CoconutInternalException("invalid set literal item", tokens[0])
        elif self.target_info < (2, 7):
            return "_coconut.set(" + set_to_tuple(tokens[0]) + ")"
        else:
            return "{" + tokens[0][0] + "}"

    def set_letter_literal_handle(self, tokens):
        """Processes set literals."""
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
            if len(set_items) != 1:
                raise CoconutInternalException("invalid set literal item", tokens[0])
            elif set_type == "s":
                return self.set_literal_handle([set_items])
            elif set_type == "f":
                return "_coconut.frozenset(" + set_to_tuple(set_items) + ")"
            else:
                raise CoconutInternalException("invalid set type", set_type)
        else:
            raise CoconutInternalException("invalid set literal tokens", tokens)

    def exec_stmt_handle(self, tokens):
        """Handles Python-3-style exec statements."""
        if len(tokens) < 1 or len(tokens) > 3:
            raise CoconutInternalException("invalid exec statement tokens", tokens)
        elif self.target.startswith("2"):
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
        """Handles multi-line lambdef statements."""
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
                "def " + name + params + ":\n" + body
            )
        else:
            params.insert(0, name)
            self.stmt_lambdas.append(
                self.name_match_funcdef_handle(original, loc, params) + body
            )
        return name

    def tre_return(self, func_name, func_args, func_store, use_mock=True):
        """Generates a tail recursion elimination grammar element."""
        def tre_return_handle(original, loc, tokens):
            if len(tokens) != 1:
                raise CoconutInternalException("invalid tail recursion elimination tokens", tokens)
            else:
                tco_recurse = "raise _coconut_tail_call(" + func_name + ", " + tokens[0][1:]  # strip initial paren, include final paren
                if not func_args:
                    tre_recurse = "continue"
                elif use_mock:
                    tre_recurse = func_args + " = " + tre_mock_var + tokens[0] + "\ncontinue"
                else:
                    tre_recurse = func_args + " = " + tokens[0][1:-1] + "\ncontinue"
                return (
                    "if " + func_name + " is " + func_store + ":\n" + openindent
                    + tre_recurse + "\n" + closeindent
                    + "else:\n" + openindent
                    + tco_recurse + "\n" + closeindent
                )
        return attach(
            (Keyword("return") + Keyword(func_name)).suppress() + self.function_call + self.end_marker.suppress(),
            tre_return_handle)

    def decoratable_normal_funcdef_stmt_handle(self, tokens):
        """Determines if tail call optimization can be done and if so does it."""
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

        raw_lines = funcdef.splitlines(True)
        def_stmt, raw_lines = raw_lines[0], raw_lines[1:]
        func_name, func_args, func_params = parse(self.split_func_name_args_params, def_stmt)
        use_mock = func_args and func_args != func_params[1:-1]
        func_store = tre_store_var + "_" + str(int(self.tre_store_count))
        self.tre_store_count += 1

        for line in raw_lines:
            body, indent = split_trailing_indent(line)
            level += ind_change(body)
            if disabled_until_level is not None:
                if level <= disabled_until_level:
                    disabled_until_level = None
            if disabled_until_level is None:
                if match_in(Keyword("yield"), body):
                    # we can't tco generators
                    return tokens[0]
                elif match_in(Keyword("def") | Keyword("try") | Keyword("with"), body):
                    disabled_until_level = level
                else:
                    base, comment = split_comment(body)
                    if decorators:
                        # tco works with decorators, but not tre
                        tre_base = None
                    else:
                        # attempt tre
                        tre_base = transform(self.tre_return(func_name, func_args, func_store, use_mock=use_mock), base)
                        if tre_base is not None:
                            line = tre_base + comment + indent
                            tre = True
                            tco = True  # tre falls back on tco if the function is changed
                    if tre_base is None:
                        # attempt tco
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
                + func_store + " = " + func_name + "\n"
            )
        out = def_stmt + out
        if tco:
            out = "@_coconut_tco\n" + out
        if decorators:
            out = decorators + out
        return out

    def function_call_tokens_split(self, original, loc, tokens):
        """Split into positional arguments and keyword arguments."""
        pos_args = []
        star_args = []
        kwd_args = []
        dubstar_args = []
        for arg in tokens:
            argstr = "".join(arg)
            if len(arg) == 1:
                if kwd_args or dubstar_args:
                    raise self.make_err(CoconutSyntaxError, "positional argument after keyword argument", original, loc)
                if arg[0] == "*":
                    kwd_args.insert(0, self.check_py("3", "star seperator", original, loc, [argstr]))
                else:
                    pos_args.append(argstr)
            elif len(arg) == 2:
                if arg[0] == "*":
                    if dubstar_args:
                        raise self.make_err(CoconutSyntaxError, "star unpacking after double star unpacking", original, loc)
                    star_args.append(argstr)
                elif arg[0] == "**":
                    dubstar_args.append(argstr)
                else:
                    kwd_args.append(argstr)
            else:
                raise CoconutInternalException("invalid function call argument", arg)
        return pos_args + star_args, kwd_args + dubstar_args

    def function_call_handle(self, original, loc, tokens):
        """Properly order call arguments."""
        pos_args, kwd_args = self.function_call_tokens_split(original, loc, tokens)
        return "(" + join_args(pos_args + kwd_args) + ")"

    def pipe_item_split(self, original, loc, tokens):
        """Split a partial trailer."""
        if len(tokens) == 1:
            return tokens[0]
        elif len(tokens) == 2:
            func, args = tokens
            pos_args, kwd_args = self.function_call_tokens_split(original, loc, args)
            return func, join_args(pos_args), join_args(kwd_args)
        else:
            raise CoconutInternalException("invalid partial trailer", tokens)

    def pipe_handle(self, original, loc, tokens, **kwargs):
        """Processes pipe calls."""
        if set(kwargs) > set(("top",)):
            complain(CoconutInternalException("unknown pipe_handle keyword arguments", kwargs))
        top = kwargs.get("top", True)
        if len(tokens) == 1:
            func = self.pipe_item_split(original, loc, tokens.pop())
            if top and isinstance(func, tuple):
                return "_coconut.functools.partial(" + join_args(func) + ")"
            else:
                return func
        else:
            func = self.pipe_item_split(original, loc, tokens.pop())
            op = tokens.pop()
            if op == "|>" or op == "|*>":
                star = "*" if op == "|*>" else ""
                if isinstance(func, tuple):
                    return func[0] + "(" + join_args((func[1], star + self.pipe_handle(original, loc, tokens), func[2])) + ")"
                else:
                    return "(" + func + ")(" + star + self.pipe_handle(original, loc, tokens) + ")"
            elif op == "<|" or op == "<*|":
                star = "*" if op == "<*|" else ""
                return self.pipe_handle(original, loc, [[func], "|" + star + ">", [self.pipe_handle(original, loc, tokens, top=False)]])
            else:
                raise CoconutInternalException("invalid pipe operator", op)

    def typedef_handle(self, tokens):
        """Checks for Python 3 type defs."""
        if len(tokens) == 1:  # return typedef
            if self.target.startswith("3"):
                return tokens[0] + ":"
            else:
                return ":\n" + self.wrap_comment(" type: (...) " + tokens[0])
        else:  # argument typedef
            if len(tokens) == 2:
                varname, typedef = tokens
                default = ""
            elif len(tokens) == 3:
                varname, typedef, default = tokens
            else:
                raise CoconutInternalException("invalid typedef tokens", tokens)
            if self.target.startswith("3"):
                return varname + ": " + typedef + default + ","
            else:
                return varname + default + "," + self.wrap_passthrough(self.wrap_comment(" type: " + typedef) + "\n" + " " * self.tabideal)

# end: COMPILER HANDLERS
#-----------------------------------------------------------------------------------------------------------------------
# CHECKING HANDLERS:
#-----------------------------------------------------------------------------------------------------------------------

    def check_strict(self, name, original, loc, tokens):
        """Checks that syntax meets --strict requirements."""
        if len(tokens) != 1:
            raise CoconutInternalException("invalid " + name + " tokens", tokens)
        elif self.strict:
            raise self.make_err(CoconutStyleError, "found " + name, original, loc)
        else:
            return tokens[0]

    def lambdef_check(self, original, loc, tokens):
        """Checks for Python-style lambdas."""
        return self.check_strict("Python-style lambda", original, loc, tokens)

    def endline_semicolon_check(self, original, loc, tokens):
        """Checks for semicolons at the end of lines."""
        return self.check_strict("semicolon at end of line", original, loc, tokens)

    def u_string_check(self, original, loc, tokens):
        """Checks for Python2-style unicode strings."""
        return self.check_strict("Python-2-style unicode string", original, loc, tokens)

    def check_py(self, version, name, original, loc, tokens):
        """Checks for Python-version-specific syntax."""
        if len(tokens) != 1:
            raise CoconutInternalException("invalid " + name + " tokens", tokens)
        elif self.target_info < get_target_info(version):
            raise self.make_err(CoconutTargetError, "found Python " + version + " " + name, original, loc, target=version)
        else:
            return tokens[0]

    def name_check(self, original, loc, tokens):
        """Checks for Python 3 exec function."""
        if len(tokens) != 1:
            raise CoconutInternalException("invalid name tokens", tokens)
        elif tokens[0] == "exec":
            return self.check_py("3", "exec function", original, loc, tokens)
        elif tokens[0].startswith(reserved_prefix):
            raise self.make_err(CoconutSyntaxError, "variable names cannot start with reserved prefix " + reserved_prefix, original, loc)
        else:
            return tokens[0]

    def nonlocal_check(self, original, loc, tokens):
        """Checks for Python 3 nonlocal statement."""
        return self.check_py("3", "nonlocal statement", original, loc, tokens)

    def star_assign_item_check(self, original, loc, tokens):
        """Checks for Python 3 starred assignment."""
        return self.check_py("3", "starred assignment (use pattern-matching version to produce universal code)", original, loc, tokens)

    def matrix_at_check(self, original, loc, tokens):
        """Checks for Python 3.5 matrix multiplication."""
        return self.check_py("35", "matrix multiplication", original, loc, tokens)

    def async_stmt_check(self, original, loc, tokens):
        """Checks for Python 3.5 async statement."""
        return self.check_py("35", "async statement", original, loc, tokens)

    def await_keyword_check(self, original, loc, tokens):
        """Checks for Python 3.5 await expression."""
        return self.check_py("35", "await expression", original, loc, tokens)

    def star_expr_check(self, original, loc, tokens):
        """Checks for Python 3.5 star unpacking."""
        return self.check_py("35", "star unpacking", original, loc, tokens)

    def f_string_check(self, original, loc, tokens):
        """Checks for Python 3.5 format strings."""
        return self.check_py("36", "format string", original, loc, tokens)

# end: CHECKING HANDLERS
#-----------------------------------------------------------------------------------------------------------------------
# ENDPOINTS:
#-----------------------------------------------------------------------------------------------------------------------

    def parse_single(self, inputstring):
        """Parses line code."""
        return self.parse(inputstring, self.single_parser, {}, {"header": "none", "initial": "none"})

    def parse_file(self, inputstring, addhash=True):
        """Parses file code."""
        if addhash:
            usehash = self.genhash(False, inputstring)
        else:
            usehash = None
        return self.parse(inputstring, self.file_parser, {"nl_at_eof_check": True}, {"header": "file", "usehash": usehash})

    def parse_exec(self, inputstring):
        """Parses exec code."""
        return self.parse(inputstring, self.file_parser, {}, {"header": "file", "initial": "none"})

    def parse_module(self, inputstring, addhash=True):
        """Parses module code."""
        if addhash:
            usehash = self.genhash(True, inputstring)
        else:
            usehash = None
        return self.parse(inputstring, self.file_parser, {"nl_at_eof_check": True}, {"header": "module", "usehash": usehash})

    def parse_block(self, inputstring):
        """Parses block code."""
        return self.parse(inputstring, self.file_parser, {}, {"header": "none", "initial": "none"})

    def parse_eval(self, inputstring):
        """Parses eval code."""
        return self.parse(inputstring, self.eval_parser, {"strip": True}, {"header": "none", "initial": "none"})

    def parse_debug(self, inputstring):
        """Parses debug code."""
        return self.parse(inputstring, self.file_parser, {"strip": True}, {"header": "none", "initial": "none"})

# end: ENDPOINTS
