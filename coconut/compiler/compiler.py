#!/usr/bin/env python

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

from coconut.root import *

import sys

from pyparsing import (
    ParseBaseException,
    col,
    line,
    lineno,
    nums,
    Keyword,
)

from coconut.constants import (
    specific_targets,
    targets,
    pseudo_targets,
    sys_target,
    default_encoding,
    hash_sep,
    openindent,
    closeindent,
    strwrapper,
    lnwrapper,
    unwrapper,
    downs,
    ups,
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
    const_vars,
    new_to_old_stdlib,
    minimum_recursion_limit,
    checksum,
)
from coconut.exceptions import (
    CoconutException,
    CoconutSyntaxError,
    CoconutParseError,
    CoconutStyleError,
    CoconutTargetError,
    CoconutWarning,
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
    target_info,
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
)
from coconut.compiler.header import (
    gethash,
    minify,
    getheader,
)

# end: IMPORTS
#-----------------------------------------------------------------------------------------------------------------------
# SETUP:
#-----------------------------------------------------------------------------------------------------------------------

if sys.getrecursionlimit() < minimum_recursion_limit:
    sys.setrecursionlimit(minimum_recursion_limit)

# end: SETUP
#-----------------------------------------------------------------------------------------------------------------------
# HANDLERS:
#-----------------------------------------------------------------------------------------------------------------------

def set_to_tuple(tokens):
    """Converts set literal tokens to tuples."""
    if len(tokens) != 1:
        raise CoconutException("invalid set maker tokens", tokens)
    elif "comp" in tokens.keys() or "list" in tokens.keys():
        return "(" + tokens[0] + ")"
    elif "test" in tokens.keys():
        return "(" + tokens[0] + ",)"
    else:
        raise CoconutException("invalid set maker item", tokens[0])

def gen_imports(path, impas):
    """Generates import statements."""
    out = []
    parts = path.split("./") # denotes from ... import ...
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
        ) & 0xffffffff) # necessary for cross-compatibility

    def reset(self):
        """Resets references."""
        self.indchar = None
        self.refs = []
        self.skips = set()
        self.docstring = ""
        self.ichain_count = 0
        self.stmt_lambdas = []
        self.bind()

    def bind(self):
        """Binds reference objects to the proper parse actions."""
        self.endline <<= attach(self.endline_ref, self.endline_handle, copy=True)
        self.moduledoc_item <<= trace(attach(self.moduledoc, self.set_docstring, copy=True), "moduledoc")
        self.name <<= trace(attach(self.name_ref, self.name_check, copy=True), "name")
        self.atom_item <<= trace(attach(self.atom_item_ref, self.item_handle, copy=True), "atom_item")
        self.simple_assign <<= trace(attach(self.simple_assign_ref, self.item_handle, copy=True), "simple_assign")
        self.set_literal <<= trace(attach(self.set_literal_ref, self.set_literal_handle, copy=True), "set_literal")
        self.set_letter_literal <<= trace(attach(self.set_letter_literal_ref, self.set_letter_literal_handle, copy=True), "set_letter_literal")
        self.classlist <<= trace(attach(self.classlist_ref, self.classlist_handle, copy=True), "classlist")
        self.import_stmt <<= trace(attach(self.import_stmt_ref, self.import_handle, copy=True), "import_stmt")
        self.complex_raise_stmt <<= trace(attach(self.complex_raise_stmt_ref, self.complex_raise_stmt_handle, copy=True), "complex_raise_stmt")
        self.augassign_stmt <<= trace(attach(self.augassign_stmt_ref, self.augassign_handle, copy=True), "augassign_stmt")
        self.dict_comp <<= trace(attach(self.dict_comp_ref, self.dict_comp_handle, copy=True), "dict_comp")
        self.destructuring_stmt <<= trace(attach(self.destructuring_stmt_ref, self.destructuring_stmt_handle, copy=True), "destructuring_stmt")
        self.name_match_funcdef <<= trace(attach(self.name_match_funcdef_ref, self.name_match_funcdef_handle, copy=True), "name_match_funcdef")
        self.op_match_funcdef <<= trace(attach(self.op_match_funcdef_ref, self.op_match_funcdef_handle, copy=True), "op_match_funcdef")
        self.yield_from <<= trace(attach(self.yield_from_ref, self.yield_from_handle, copy=True), "yield_from")
        self.exec_stmt <<= trace(attach(self.exec_stmt_ref, self.exec_stmt_handle, copy=True), "exec_stmt")
        self.stmt_lambdef <<= trace(attach(self.stmt_lambdef_ref, self.stmt_lambdef_handle, copy=True), "stmt_lambdef")
        self.decoratable_func_stmt <<= trace(attach(self.decoratable_func_stmt_ref, self.decoratable_func_stmt_handle, copy=True), "decoratable_func_stmt")
        self.u_string <<= attach(self.u_string_ref, self.u_string_check, copy=True)
        self.f_string <<= attach(self.f_string_ref, self.f_string_check, copy=True)
        self.typedef <<= attach(self.typedef_ref, self.typedef_check, copy=True)
        self.return_typedef <<= attach(self.return_typedef_ref, self.typedef_check, copy=True)
        self.matrix_at <<= attach(self.matrix_at_ref, self.matrix_at_check, copy=True)
        self.nonlocal_stmt <<= attach(self.nonlocal_stmt_ref, self.nonlocal_check, copy=True)
        self.star_assign_item <<= attach(self.star_assign_item_ref, self.star_assign_item_check, copy=True)
        self.classic_lambdef <<= attach(self.classic_lambdef_ref, self.lambdef_check, copy=True)
        self.async_funcdef <<= attach(self.async_funcdef_ref, self.async_stmt_check, copy=True)
        self.async_match_funcdef <<= attach(self.async_match_funcdef_ref, self.async_stmt_check, copy=True)
        self.async_stmt <<= attach(self.async_stmt_ref, self.async_stmt_check, copy=True)
        self.await_keyword <<= attach(self.await_keyword_ref, self.await_keyword_check, copy=True)
        self.star_expr <<= attach(self.star_expr_ref, self.star_expr_check, copy=True)
        self.dubstar_expr <<= attach(self.dubstar_expr_ref, self.star_expr_check, copy=True)

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
            return self.repl_proc(snip, careful=False, add_to_line=False)

    def make_err(self, errtype, message, original, location, ln=None, reformat=True, *args, **kwargs):
        """Generates an error of the specified type."""
        if ln is None:
            ln = self.adjust(lineno(location, original))
        errstr, index = line(location, original), col(location, original)-1
        if reformat:
            errstr, index = self.reformat(errstr, index)
        return errtype(message, errstr, index, ln, *args, **kwargs)

    def strict_err_or_warn(self, *args, **kwargs):
        """Raises an error if in strict mode, otherwise raises a warning."""
        if self.strict:
            raise self.make_err(CoconutStyleError, *args, **kwargs)
        else:
            logger.warn(self.make_err(CoconutWarning, *args, **kwargs))

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
            raise CoconutException("invalid reference", index)

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

    def apply_procs(self, procs, kwargs, inputstring):
        """Applies processors to inputstring."""
        for get_proc in procs:
            proc = get_proc(self)
            inputstring = proc(inputstring, **kwargs)
            logger.log_tag(proc.__name__, inputstring, multiline=True)
        return inputstring

    def pre(self, inputstring, **kwargs):
        """Performs pre-processing."""
        out = self.apply_procs(self.preprocs, kwargs, str(inputstring))
        logger.log_tag("skips", list(sorted(self.skips)))
        return out

    def post(self, tokens, **kwargs):
        """Performs post-processing."""
        if len(tokens) == 1:
            return self.apply_procs(self.postprocs, kwargs, tokens[0])
        else:
            raise CoconutException("multiple tokens leftover", tokens)

    def headers(self, which, usehash=None):
        """Gets a formatted header."""
        return self.polish(getheader(which, self.target, usehash))

    def target_info(self):
        """Returns information on the current target as a version tuple."""
        return target_info(self.target)

    def should_indent(self, code):
        """Determines whether the next line should be indented."""
        last = rem_comment(code.splitlines()[-1])
        return last.endswith(":") or last.endswith("\\") or paren_change(last) < 0

    def parse(self, inputstring, parser, preargs, postargs):
        """Uses the parser to parse the inputstring."""
        self.reset()
        try:
            out = self.post(parser.parseWithTabs().parseString(self.pre(inputstring, **preargs)), **postargs)
        except ParseBaseException as err:
            err_line, err_index = self.reformat(err.line, err.col-1)
            raise CoconutParseError(None, err_line, err_index, self.adjust(err.lineno))
        except RuntimeError as err:
            if logger.verbose:
                logger.print_exc()
            raise CoconutException(str(err)
                + " (try again with --recursion-limit greater than the current "
                + str(sys.getrecursionlimit()) + ")")
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
        found = None # store of characters that might be the start of a string
        hold = None
        # hold = [_comment]:
        _comment = 0 # the contents of the comment so far
        # hold = [_contents, _start, _stop]:
        _contents = 0 # the contents of the string so far
        _start = 1 # the string of characters that started the string
        _stop = 2 # store of characters that might be the end of the string
        x = 0
        skips = self.skips.copy()

        while x <= len(inputstring):
            if x == len(inputstring):
                c = "\n"
            else:
                c = inputstring[x]

            if hold is not None:
                if len(hold) == 1: # hold == [_comment]
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
                        hold[_contents] += hold[_stop]+c
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
                elif len(found) == 1: # found == "_"
                    if c == "\n":
                        raise self.make_err(CoconutSyntaxError, "linebreak in non-multiline string", inputstring, x, reformat=False)
                    else:
                        hold = [c, found, None] # [_contents, _start, _stop]
                        found = None
                elif len(found) == 2: # found == "__"
                    out.append(self.wrap_str("", found[0], False))
                    found = None
                    x -= 1
                elif len(found) == 3: # found == "___"
                    if c == "\n":
                        skips = addskip(skips, self.adjust(lineno(x, inputstring)))
                    hold = [c, found, None] # [_contents, _start, _stop]
                    found = None
                else:
                    raise self.make_err(CoconutSyntaxError, "invalid number of string starts", inputstring, x, reformat=False)
            elif c == "#":
                hold = [""] # [_comment]
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
        found = None # store of characters that might be the start of a passthrough
        hold = None # the contents of the passthrough so far
        count = None # current parenthetical level
        multiline = None
        skips = self.skips.copy()

        for x in range(0, len(inputstring)+1):
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
        for x in range(0, len(inputstring)):
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

        for ln in range(0, len(lines)):
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
                    raise self.make_err(CoconutStyleError, "found backslash continuation", last, len(last), self.adjust(ln-1))
                else:
                    skips = addskip(skips, self.adjust(ln))
                    new[-1] = last[:-1]+" "+line
            elif count < 0:
                skips = addskip(skips, self.adjust(ln))
                new[-1] = last+" "+line
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
                    line = closeindent*(len(levels[point:]) + 1) + line
                    levels = levels[:point]
                    current = levels.pop()
                elif current != check:
                    raise self.make_err(CoconutSyntaxError, "illegal dedent to unused indentation level", line, 0, self.adjust(ln))
                new.append(line)
            count += paren_change(line)

        self.skips = skips
        if new:
            last = rem_comment(new[-1])
            if last.endswith("\\"):
                raise self.make_err(CoconutSyntaxError, "illegal final backslash continuation", last, len(last), self.adjust(len(new)))
            if count != 0:
                raise self.make_err(CoconutSyntaxError, "unclosed parenthetical", new[-1], len(new[-1]), self.adjust(len(new)))
        new.append(closeindent*len(levels))
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

    def reind_proc(self, inputstring, **kwargs):
        """Adds back indentation."""
        out = []
        level = 0

        for line in inputstring.splitlines():
            line = line.strip()
            if "#" in line:
                line, comment = line.split("#", 1)
                line = line.rstrip()
                comment = "#" + comment
            else:
                comment = ""

            indent, line = split_leading_indent(line)
            level += ind_change(indent)

            if line and not line.startswith("#"):
                line = " "*(1 if self.minify else tabideal)*level + line

            line, indent = split_trailing_indent(line)
            level += ind_change(indent)

            out.append(line + comment)

        if level != 0:
            complain(CoconutException("non-zero final indentation level", level))
        return "\n".join(out)

    def endline_comment(self, ln):
        """Gets an end line comment."""
        if ln < 0 or (self.keep_lines and ln > len(self.original_lines)):
            raise CoconutException("out of bounds line number", ln)
        elif self.line_numbers and self.keep_lines:
            if self.minify:
                comment = str(ln) + " " + self.original_lines[ln-1]
            else:
                comment = " line " + str(ln) + ": " + self.original_lines[ln-1]
        elif self.keep_lines:
            if self.minify:
                comment = self.original_lines[ln-1]
            else:
                comment = " " + self.original_lines[ln-1]
        elif self.line_numbers:
            if self.minify:
                comment = str(ln)
            else:
                comment = " line " + str(ln)
        else:
            raise CoconutException("attempted to add line number comment without --line-numbers or --keep-lines")
        return self.wrap_comment(comment)

    def endline_repl(self, inputstring, add_to_line=True, careful=True, **kwargs):
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
                            raise CoconutException("invalid reference for a line number", ln)
                        line = line.rstrip()
                        fix = True
                    elif fix:
                        ln += 1
                        fix = False
                    if add_to_line and line and not line.lstrip().startswith("#"):
                        line += self.endline_comment(ln)
                except CoconutException as err:
                    if careful:
                        complain(err)
                    fix = False
                out.append(line)
            return "\n".join(out)
        else:
            return inputstring

    def passthrough_repl(self, inputstring, careful=True, **kwargs):
        """Adds back passthroughs."""
        out = []
        index = None
        for x in range(len(inputstring)+1):
            c = inputstring[x] if x != len(inputstring) else None
            try:
                if index is not None:
                    if c is not None and c in nums:
                        index += c
                    elif c == unwrapper and index:
                        ref = self.get_ref(index)
                        if not isinstance(ref, str):
                            raise CoconutException("invalid reference for a passthrough", ref)
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
            except CoconutException:
                if careful:
                    raise
                if index is not None:
                    out.append(index)
                    index = None
                out.append(c)
        return "".join(out)

    def str_repl(self, inputstring, careful=True, **kwargs):
        """Adds back strings."""
        out = []
        comment = None
        string = None

        for x in range(len(inputstring)+1):
            c = inputstring[x] if x != len(inputstring) else None
            try:

                if comment is not None:
                    if c is not None and c in nums:
                        comment += c
                    elif c == unwrapper and comment:
                        ref = self.get_ref(comment)
                        if not isinstance(ref, str):
                            raise CoconutException("invalid reference for a comment", ref)
                        if out and not out[-1].endswith("\n"):
                            out.append(" ")
                        out.append("#" + ref)
                        comment = None
                    else:
                        raise CoconutException("invalid comment marker in", line(x, inputstring))
                elif string is not None:
                    if c is not None and c in nums:
                        string += c
                    elif c == unwrapper and string:
                        ref = self.get_ref(string)
                        if not isinstance(ref, tuple):
                            raise CoconutException("invalid reference for a str", ref)
                        text, strchar, multiline = ref
                        if multiline:
                            out.append(strchar*3 + text + strchar*3)
                        else:
                            out.append(strchar + text + strchar)
                        string = None
                    else:
                        raise CoconutException("invalid string marker in", line(x, inputstring))
                elif c is not None:
                    if c == "#":
                        comment = ""
                    elif c == strwrapper:
                        string = ""
                    else:
                        out.append(c)

            except CoconutException:
                if careful:
                    raise
                if comment is not None:
                    out.append(comment)
                    comment = None
                if string is not None:
                    out.append(string)
                    string = None
                out.append(c)

        return "".join(out)

    def repl_proc(self, inputstring, **kwargs):
        """Processes using replprocs."""
        return self.apply_procs(self.replprocs, kwargs, inputstring)

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

    def set_docstring(self, original, location, tokens):
        """Sets the docstring."""
        if len(tokens) == 2:
            self.docstring = self.reformat(tokens[0]) + "\n\n"
            return tokens[1]
        else:
            raise CoconutException("invalid docstring tokens", tokens)

    def yield_from_handle(self, tokens):
        """Processes Python 3.3 yield from."""
        if len(tokens) != 1:
            raise CoconutException("invalid yield from tokens", tokens)
        elif self.target_info() < (3, 3):
            return (yield_from_var + " = " + tokens[0]
                + "\nfor " + yield_item_var + " in " + yield_from_var + ":\n"
                + openindent + "yield " + yield_item_var + "\n" + closeindent)
        else:
            return "yield from " + tokens[0]

    def endline_handle(self, original, location, tokens):
        """Inserts line number comments when in line_numbers mode."""
        if len(tokens) != 1:
            raise CoconutException("invalid endline tokens", tokens)
        out = tokens[0]
        if self.minify:
            out = out.splitlines(True)[0] # if there are multiple new lines, take only the first one
        if self.line_numbers or self.keep_lines:
            out = self.wrap_line_number(self.adjust(lineno(location, original))) + out
        return out

    def item_handle(self, original, location, tokens):
        """Processes items."""
        out = tokens.pop(0)
        for trailer in tokens:
            if isinstance(trailer, str):
                out += trailer
            elif len(trailer) == 1:
                if trailer[0] == "$[]":
                    out = "_coconut.functools.partial(_coconut_igetitem, "+out+")"
                elif trailer[0] == "$":
                    out = "_coconut.functools.partial(_coconut.functools.partial, "+out+")"
                elif trailer[0] == "[]":
                    out = "_coconut.functools.partial(_coconut.operator.getitem, "+out+")"
                elif trailer[0] == ".":
                    out = "_coconut.functools.partial(_coconut.getattr, "+out+")"
                elif trailer[0] == "$(":
                    raise self.make_err(CoconutSyntaxError, "a partial application argument is required", original, location)
                else:
                    raise CoconutException("invalid trailer symbol", trailer[0])
            elif len(trailer) == 2:
                if trailer[0] == "$(":
                    out = "_coconut.functools.partial("+out+", "+trailer[1]+")"
                elif trailer[0] == "$[":
                    out = "_coconut_igetitem("+out+", "+trailer[1]+")"
                else:
                    raise CoconutException("invalid special trailer", trailer[0])
            else:
                raise CoconutException("invalid trailer tokens", trailer)
        return out

    def augassign_handle(self, tokens):
        """Processes assignments."""
        if len(tokens) == 3:
            name, op, item = tokens
            out = ""
            if op == "|>=":
                out += name+" = ("+item+")("+name+")"
            elif op == "|*>=":
                out += name+" = ("+item+")(*"+name+")"
            elif op == "<|=":
                out += name+" = "+name+"(("+item+"))"
            elif op == "<*|=":
                out += name+" = "+name+"(*("+item+"))"
            elif op == "..=":
                out += name+" = (lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs)))("+name+", ("+item+"))"
            elif op == "::=":
                ichain_var = lazy_chain_var + "_" + str(self.ichain_count) # necessary to prevent a segfault caused by self-reference
                out += ichain_var + " = " + name + "\n"
                out += name + " = _coconut.itertools.chain.from_iterable(" + lazy_list_handle([ichain_var, "("+item+")"]) + ")"
                self.ichain_count += 1
            else:
                out += name+" "+op+" "+item
            return out
        else:
            raise CoconutException("invalid assignment tokens", tokens)

    def classlist_handle(self, original, location, tokens):
        """Processes class inheritance lists."""
        if len(tokens) == 0:
            if self.target.startswith("3"):
                return ""
            else:
                return "(_coconut.object)"
        elif len(tokens) == 1 and len(tokens[0]) == 1:
            if "tests" in tokens[0].keys():
                return "(" + tokens[0][0] + ")"
            elif "args" in tokens[0].keys():
                if self.target.startswith("3"):
                    return "(" + tokens[0][0] + ")"
                else:
                    raise self.make_err(CoconutTargetError, "found Python 3 keyword class definition", original, location, target="3")
            else:
                raise CoconutException("invalid inner classlist token", tokens[0])
        else:
            raise CoconutException("invalid classlist tokens", tokens)

    def import_handle(self, original, location, tokens):
        """Universalizes imports."""
        if len(tokens) == 1:
            imp_from, imports = None, tokens[0]
        elif len(tokens) == 2:
            imp_from, imports = tokens
            if imp_from == "__future__":
                self.strict_err_or_warn("unnecessary from __future__ import (Coconut does these automatically)", original, location)
                return ""
        else:
            raise CoconutException("invalid import tokens", tokens)
        importmap = [] # [((imp | old_imp, imp, version_check), impas), ...]
        for imps in imports:
            if len(imps) == 1:
                imp, impas = imps[0], imps[0]
            else:
                imp, impas = imps
            if imp_from is not None:
                imp = imp_from + "./" + imp # marker for from ... import ...
            old_imp = None
            path = imp.split(".")
            for i in reversed(range(1, len(path)+1)):
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
            elif not self.target or self.target_info() < version_check:
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
            raise CoconutException("invalid raise from tokens", tokens)
        elif self.target.startswith("3"):
            return "raise " + tokens[0] + " from " + tokens[1]
        else:
            return (raise_from_var + " = " + tokens[0] + "\n"
                + raise_from_var + ".__cause__ = " + tokens[1] + "\n"
                + "raise " + raise_from_var)

    def dict_comp_handle(self, original, location, tokens):
        """Processes Python 2.7 dictionary comprehension."""
        if len(tokens) != 3:
            raise CoconutException("invalid dictionary comprehension tokens", tokens)
        elif self.target.startswith("3"):
            key, val, comp = tokens
            return "{" + key + ": " + val + " " + comp + "}"
        else:
            key, val, comp = tokens
            return "dict(((" + key + "), (" + val + ")) " + comp + ")"

    def pattern_error(self, original, loc):
        """Constructs a pattern-matching error message."""
        base_line = clean(self.reformat(line(loc, original)))
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
            raise CoconutException("invalid destructuring assignment tokens", tokens)

    def name_match_funcdef_handle(self, original, loc, tokens):
        """Processes match defs."""
        if len(tokens) == 2:
            func, matches = tokens
            cond = None
        elif len(tokens) == 3:
            func, matches, cond = tokens
        else:
            raise CoconutException("invalid match function definition tokens", tokens)
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
            raise CoconutException("invalid infix match function definition tokens", tokens)
        return self.name_match_funcdef_handle(original, loc, name_tokens)

    def set_literal_handle(self, tokens):
        """Converts set literals to the right form for the target Python."""
        if len(tokens) != 1:
            raise CoconutException("invalid set literal tokens", tokens)
        elif len(tokens[0]) != 1:
            raise CoconutException("invalid set literal item", tokens[0])
        elif self.target_info() < (2, 7):
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
                raise CoconutException("invalid set type", set_type)
        elif len(tokens) == 2:
            set_type, set_items = tokens
            if len(set_items) != 1:
                raise CoconutException("invalid set literal item", tokens[0])
            elif set_type == "s":
                return self.set_literal_handle([set_items])
            elif set_type == "f":
                return "_coconut.frozenset(" + set_to_tuple(set_items) + ")"
            else:
                raise CoconutException("invalid set type", set_type)
        else:
            raise CoconutException("invalid set literal tokens", tokens)

    def exec_stmt_handle(self, tokens):
        """Handles Python-3-style exec statements."""
        if len(tokens) < 1 or len(tokens) > 3:
            raise CoconutException("invalid exec statement tokens", tokens)
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

    def stmt_lambdef_handle(self, tokens):
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
            raise CoconutException("invalid statement lambda tokens", tokens)
        name = self.stmt_lambda_name()
        self.stmt_lambdas.append(
            "def " + name + params + ":\n"
            + openindent + self.stmt_lambda_proc("\n".join(stmts)) + closeindent
        )
        return name

    def decoratable_func_stmt_handle(self, tokens):
        """Determines if tail call optimization can be done and if so does it."""
        if len(tokens) != 1:
            raise CoconutException("invalid function definition tokens", tokens)
        elif not tokens[0].startswith("def "):
            # either has decorators or is an async def, neither of which we can tco
            return tokens[0]
        else:
            lines = [] # transformed
            tco = False # whether tco was done
            level = 0 # indentation level
            in_func = None # if inside of a func, the indentation level outside that func

            for i, line in enumerate(tokens[0].splitlines(True)):
                body, indent = split_trailing_indent(line)
                level += ind_change(body)
                if in_func is not None:
                    if level <= in_func:
                        in_func = None
                if in_func is None:
                    if match_in(Keyword("yield"), body):
                        # we can't tco generators
                        return tokens[0]
                    elif i and match_in(Keyword("def"), body):
                        in_func = level
                    else:
                        base, comment = split_comment(body)
                        tco_base = transform(self.tco_return, base)
                        if tco_base is not None:
                            line = tco_base + comment + indent
                            tco = True
                lines.append(line)
                level += ind_change(indent)

            if tco:
                return "@_coconut_tco\n" + "".join(lines)
            else:
                return tokens[0]

# end: COMPILER HANDLERS
#-----------------------------------------------------------------------------------------------------------------------
# CHECKING HANDLERS:
#-----------------------------------------------------------------------------------------------------------------------

    def check_strict(self, name, original, location, tokens):
        """Checks that syntax meets --strict requirements."""
        if len(tokens) != 1:
            raise CoconutException("invalid "+name+" tokens", tokens)
        elif self.strict:
            raise self.make_err(CoconutStyleError, "found "+name, original, location)
        else:
            return tokens[0]

    def lambdef_check(self, original, location, tokens):
        """Checks for Python-style lambdas."""
        return self.check_strict("Python-style lambda", original, location, tokens)

    def u_string_check(self, original, location, tokens):
        """Checks for Python2-style unicode strings."""
        return self.check_strict("Python-2-style unicode string", original, location, tokens)

    def check_py(self, version, name, original, location, tokens):
        """Checks for Python-version-specific syntax."""
        if len(tokens) != 1:
            raise CoconutException("invalid "+name+" tokens", tokens)
        elif self.target_info() < target_info(version):
            raise self.make_err(CoconutTargetError, "found Python "+version+" " + name, original, location, target=version)
        else:
            return tokens[0]

    def name_check(self, original, location, tokens):
        """Checks for Python 3 exec function."""
        if len(tokens) != 1:
            raise CoconutException("invalid name tokens", tokens)
        elif tokens[0] == "exec":
            return self.check_py("3", "exec function", original, location, tokens)
        else:
            return tokens[0]

    def typedef_check(self, original, location, tokens):
        """Checks for Python 3 type defs."""
        return self.check_py("3", "type annotation", original, location, tokens)

    def nonlocal_check(self, original, location, tokens):
        """Checks for Python 3 nonlocal statement."""
        return self.check_py("3", "nonlocal statement", original, location, tokens)

    def star_assign_item_check(self, original, location, tokens):
        """Checks for Python 3 starred assignment."""
        return self.check_py("3", "starred assignment", original, location, tokens)

    def matrix_at_check(self, original, location, tokens):
        """Checks for Python 3.5 matrix multiplication."""
        return self.check_py("35", "matrix multiplication", original, location, tokens)

    def async_stmt_check(self, original, location, tokens):
        """Checks for Python 3.5 async statement."""
        return self.check_py("35", "async statement", original, location, tokens)

    def await_keyword_check(self, original, location, tokens):
        """Checks for Python 3.5 await expression."""
        return self.check_py("35", "await expression", original, location, tokens)

    def star_expr_check(self, original, location, tokens):
        """Checks for Python 3.5 star unpacking."""
        return self.check_py("35", "star unpacking", original, location, tokens)

    def f_string_check(self, original, location, tokens):
        """Checks for Python 3.5 format strings."""
        return self.check_py("36", "format string", original, location, tokens)

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
