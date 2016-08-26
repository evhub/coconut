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
#   - Grammar
#   - Endpoints

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *

import sys

from pyparsing import (
    CaselessLiteral,
    Combine,
    Forward,
    Group,
    Keyword,
    Literal,
    OneOrMore,
    Optional,
    ParseBaseException,
    ParserElement,
    Regex,
    stringEnd,
    stringStart,
    Word,
    ZeroOrMore,
    col,
    line,
    lineno,
    hexnums,
    nums,
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
    reserved_prefix,
    decorator_var,
    match_to_var,
    match_check_var,
    match_iter_var,
    match_err_var,
    lazy_item_var,
    lazy_chain_var,
    import_as_var,
    yield_from_var,
    yield_item_var,
    raise_from_var,
    stmt_lambda_var,
    wildcard,
    keywords,
    const_vars,
    reserved_vars,
    new_to_old_stdlib,
    default_whitespace_chars,
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
from coconut.logging import logger, trace
from coconut.compiler.util import (
    target_info,
    addskip,
    count_end,
    change,
    attach,
    fixto,
    addspace,
    condense,
    parenwrap,
    tokenlist,
    itemlist,
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

ParserElement.enablePackrat()
ParserElement.setDefaultWhitespaceChars(default_whitespace_chars)

# end: SETUP
#-----------------------------------------------------------------------------------------------------------------------
# HANDLERS:
#-----------------------------------------------------------------------------------------------------------------------

def add_paren_handle(tokens):
    """Adds parentheses."""
    if len(tokens) == 1:
        return "(" + tokens[0] + ")"
    else:
        raise CoconutException("invalid tokens for parentheses adding", tokens)

def attr_handle(tokens):
    """Processes attrgetter literals."""
    if len(tokens) == 1:
        return '_coconut.operator.attrgetter("'+tokens[0]+'")'
    elif len(tokens) == 2:
        return '_coconut.operator.methodcaller("'+tokens[0]+'", '+tokens[1]+")"
    else:
        raise CoconutException("invalid attrgetter literal tokens", tokens)

def lazy_list_handle(tokens):
    """Processes lazy lists."""
    if len(tokens) == 0:
        return "_coconut.iter(())"
    else:
        return ("(" + lazy_item_var + "() for " + lazy_item_var + " in ("
            + "lambda: " + ", lambda: ".join(tokens) + ("," if len(tokens) == 1 else "") + "))")

def chain_handle(tokens):
    """Processes chain calls."""
    if len(tokens) == 1:
        return tokens[0]
    else:
        return "_coconut.itertools.chain.from_iterable(" + lazy_list_handle(tokens) + ")"

def infix_error(tokens):
    """Raises inner infix error."""
    raise CoconutException("invalid inner infix tokens", tokens)

def infix_handle(tokens):
    """Processes infix calls."""
    func, args = get_infix_items(tokens, infix_handle)
    return "(" + func + ")(" + ", ".join(args) + ")"

def get_infix_items(tokens, callback=infix_error):
    """Performs infix token processing."""
    if len(tokens) < 3:
        raise CoconutException("invalid infix tokens", tokens)
    else:
        items = []
        for item in tokens[0]:
            items.append(item)
        for item in tokens[2]:
            items.append(item)
        if len(tokens) > 3:
            items.append(callback([[]]+tokens[3:]))
        args = []
        for arg in items:
            if arg:
                args.append(arg)
        return tokens[1], args

def op_funcdef_handle(tokens):
    """Processes infix defs."""
    func, args = get_infix_items(tokens)
    return func + "(" + ", ".join(args) + ")"

def pipe_handle(tokens):
    """Processes pipe calls."""
    if len(tokens) == 1:
        return tokens[0]
    else:
        func = tokens.pop()
        op = tokens.pop()
        if op == "|>":
            return "(" + func + ")(" + pipe_handle(tokens) + ")"
        elif op == "|*>":
            return "(" + func + ")(*" + pipe_handle(tokens) + ")"
        elif op == "<|":
            return "(" + pipe_handle(tokens) + ")(" + func + ")"
        elif op == "<*|":
            return "(" + pipe_handle(tokens) + ")(*" + func + ")"
        else:
            raise CoconutException("invalid pipe operator", op)

def lambdef_handle(tokens):
    """Processes lambda calls."""
    if len(tokens) == 0:
        return "lambda:"
    elif len(tokens) == 1:
        return "lambda " + tokens[0] + ":"
    else:
        raise CoconutException("invalid lambda tokens", tokens)

def math_funcdef_suite_handle(original, location, tokens):
    """Processes shorthand function definiton suites."""
    if len(tokens) < 1:
        raise CoconutException("invalid shorthand function definition suite tokens", tokens)
    else:
        return "".join(tokens[:-1]) + "return " + tokens[-1]

def math_funcdef_handle(tokens):
    """Processes shorthand function definition."""
    if len(tokens) == 2:
        return tokens[0] + ("" if tokens[1].startswith("\n") else " ") + tokens[1]
    else:
        raise CoconutException("invalid shorthand function definition tokens")

def math_match_funcdef_handle(tokens):
    """Processes match shorthand function definitions."""
    if len(tokens) == 1:
        return tokens[0] + "\n" + closeindent
    else:
        raise CoconutException("invalid pattern-matching shorthand function definition tokens", tokens)

def def_match_funcdef_handle(tokens):
    """Processes full match function definition."""
    if len(tokens) == 2:
        return tokens[0] + "".join(tokens[1]) + closeindent
    else:
        raise CoconutException("invalid pattern-matching function definition tokens", tokens)

def data_handle(tokens):
    """Processes data blocks."""
    if len(tokens) == 2:
        name, stmts = tokens
        attrs = ""
    elif len(tokens) == 3:
        name, attrs, stmts = tokens
    else:
        raise CoconutException("invalid data tokens", tokens)
    out = "class " + name + '(_coconut.collections.namedtuple("' + name + '", "' + attrs + '")):\n' + openindent
    rest = None
    if "simple" in stmts.keys() and len(stmts) == 1:
        out += "__slots__ = ()\n"
        rest = stmts[0]
    elif "docstring" in stmts.keys() and len(stmts) == 1:
        out += stmts[0] + "__slots__ = ()\n"
    elif "complex" in stmts.keys() and len(stmts) == 1:
        out += "__slots__ = ()\n"
        rest = "".join(stmts[0])
    elif "complex" in stmts.keys() and len(stmts) == 2:
        out += stmts[0] + "__slots__ = ()\n"
        rest = "".join(stmts[1])
    elif "empty" in stmts.keys() and len(stmts) == 1:
        out += "__slots__ = ()" + stmts[0]
    else:
        raise CoconutException("invalid inner data tokens", stmts)
    if rest is not None and rest != "pass\n":
        out += rest
    out += closeindent
    return out

def decorator_handle(tokens):
    """Processes decorators."""
    defs = []
    decorates = []
    for x in range(0, len(tokens)):
        if "simple" in tokens[x].keys() and len(tokens[x]) == 1:
            decorates.append("@"+tokens[x][0])
        elif "test" in tokens[x].keys() and len(tokens[x]) == 1:
            varname = decorator_var + "_" + str(x)
            defs.append(varname+" = "+tokens[x][0])
            decorates.append("@"+varname)
        else:
            raise CoconutException("invalid decorator tokens", tokens[x])
    return "\n".join(defs + decorates) + "\n"

def else_handle(tokens):
    """Processes compound else statements."""
    if len(tokens) == 1:
        return "\n" + openindent + tokens[0] + closeindent
    else:
        raise CoconutException("invalid compound else statement tokens", tokens)

class Matcher(object):
    """Pattern-matching processor."""
    matchers = {
        "dict": lambda self: self.match_dict,
        "iter": lambda self: self.match_iterator,
        "series": lambda self: self.match_sequence,
        "rseries": lambda self: self.match_rsequence,
        "mseries": lambda self: self.match_msequence,
        "const": lambda self: self.match_const,
        "var": lambda self: self.match_var,
        "set": lambda self: self.match_set,
        "data": lambda self: self.match_data,
        "paren": lambda self: self.match_paren,
        "trailer": lambda self: self.match_trailer,
        "and": lambda self: self.match_and,
        "or": lambda self: self.match_or,
    }
    __slots__ = (
        "position",
        "iter_index",
        "checkdefs",
        "checks",
        "defs",
        "names",
        "others"
        )

    def __init__(self, checkdefs=None, names=None):
        """Creates the matcher."""
        self.position = 0
        self.iter_index = 0
        self.checkdefs = []
        if checkdefs is None:
            self.increment()
        else:
            for checks, defs in checkdefs:
                self.checkdefs.append([checks[:], defs[:]])
            self.checks = self.get_checks(-1)
            self.defs = self.get_defs(-1)
        if names is None:
            self.names = {}
        else:
            self.names = dict(names)
        self.others = []

    def duplicate(self):
        """Duplicates the matcher to others."""
        self.others.append(Matcher(self.checkdefs, self.names))
        self.others[-1].set_checks(0, ["not "+match_check_var] + self.others[-1].get_checks(0))
        return self.others[-1]

    def get_checks(self, position):
        """Gets the checks at the position."""
        return self.checkdefs[position][0]

    def set_checks(self, position, checks):
        """Sets the checks at the position."""
        self.checkdefs[position][0] = checks

    def set_defs(self, position, defs):
        """Sets the defs at the position."""
        self.checkdefs[position][1] = defs

    def get_defs(self, position):
        """Gets the defs at the position."""
        return self.checkdefs[position][1]

    def add_check(self, check_item):
        """Adds a check universally."""
        self.checks.append(check_item)
        for other in self.others:
            other.add_check(check_item)

    def add_def(self, def_item):
        """Adds a def universally."""
        self.defs.append(def_item)
        for other in self.others:
            other.add_def(def_item)

    def set_position(self, position):
        """Sets the if-statement position."""
        if position > 0:
            while position >= len(self.checkdefs):
                self.checkdefs.append([[], []])
            self.checks = self.checkdefs[position][0]
            self.defs = self.checkdefs[position][1]
            self.position = position
        else:
            raise CoconutException("invalid match index: "+str(position))

    def increment(self, forall=False):
        """Advances the if-statement position."""
        self.set_position(self.position+1)
        if forall:
            for other in self.others:
                other.increment(True)

    def decrement(self, forall=False):
        """Decrements the if-statement position."""
        self.set_position(self.position-1)
        if forall:
            for other in self.others:
                other.decrement(True)

    def add_guard(self, cond):
        """Adds cond as a guard."""
        self.increment(True)
        self.add_check(cond)

    def match_dict(self, original, item):
        """Matches a dictionary."""
        if len(original) == 1:
            match = original[0]
        else:
            raise CoconutException("invalid dict match tokens", original)
        self.checks.append("_coconut.isinstance("+item+", _coconut.abc.Mapping)")
        self.checks.append("_coconut.len("+item+") == "+str(len(match)))
        for x in range(0, len(match)):
            k,v = match[x]
            self.checks.append(k+" in "+item)
            self.match(v, item+"["+k+"]")

    def match_sequence(self, original, item, typecheck=True):
        """Matches a sequence."""
        tail = None
        if len(original) == 2:
            series_type, match = original
        else:
            series_type, match, tail = original
        if typecheck:
            self.checks.append("_coconut.isinstance("+item+", _coconut.abc.Sequence)")
        if tail is None:
            self.checks.append("_coconut.len("+item+") == "+str(len(match)))
        else:
            self.checks.append("_coconut.len("+item+") >= "+str(len(match)))
            if len(match):
                splice = "["+str(len(match))+":]"
            else:
                splice = ""
            if series_type == "(":
                self.defs.append(tail+" = _coconut.tuple("+item+splice+")")
            elif series_type == "[":
                self.defs.append(tail+" = _coconut.list("+item+splice+")")
            else:
                raise CoconutException("invalid series match type", series_type)
        for x in range(0, len(match)):
            self.match(match[x], item+"["+str(x)+"]")

    def match_iterator(self, original, item):
        """Matches an iterator."""
        tail = None
        if len(original) == 2:
            _, match = original
        else:
            _, match, tail = original
        self.checks.append("_coconut.isinstance("+item+", _coconut.abc.Iterable)")
        itervar = match_iter_var + "_" + str(self.iter_index)
        self.iter_index += 1
        if tail is None:
            self.defs.append(itervar+" = _coconut.tuple("+item+")")
        else:
            self.defs.append(tail+" = _coconut.iter("+item+")")
            self.defs.append(itervar+" = _coconut.tuple(_coconut_igetitem("+tail+", _coconut.slice(None, "+str(len(match))+")))")
        self.increment()
        self.checks.append("_coconut.len("+itervar+") == "+str(len(match)))
        for x in range(0, len(match)):
            self.match(match[x], itervar+"["+str(x)+"]")
        self.decrement()

    def match_rsequence(self, original, item):
        """Matches a reverse sequence."""
        front, series_type, match = original
        self.checks.append("_coconut.isinstance("+item+", _coconut.abc.Sequence)")
        self.checks.append("_coconut.len("+item+") >= "+str(len(match)))
        if len(match):
            splice = "[:"+str(-len(match))+"]"
        else:
            splice = ""
        if series_type == "(":
            self.defs.append(front+" = _coconut.tuple("+item+splice+")")
        elif series_type == "[":
            self.defs.append(front+" = _coconut.list("+item+splice+")")
        else:
            raise CoconutException("invalid series match type", series_type)
        for x in range(0, len(match)):
            self.match(match[x], item+"["+str(x-len(match))+"]")

    def match_msequence(self, original, item):
        """Matches a middle sequence."""
        series_type, head_match, middle, _, last_match = original
        self.checks.append("_coconut.isinstance("+item+", _coconut.abc.Sequence)")
        self.checks.append("_coconut.len("+item+") >= "+str(len(head_match) + len(last_match)))
        if len(head_match) and len(last_match):
            splice = "["+str(len(head_match))+":"+str(-len(last_match))+"]"
        elif len(head_match):
            splice = "["+str(len(head_match))+":]"
        elif len(last_match):
            splice = "[:"+str(-len(last_match))+"]"
        else:
            splice = ""
        if series_type == "(":
            self.defs.append(middle+" = _coconut.tuple("+item+splice+")")
        elif series_type == "[":
            self.defs.append(middle+" = _coconut.list("+item+splice+")")
        else:
            raise CoconutException("invalid series match type", series_type)
        for x in range(0, len(head_match)):
            self.match(head_match[x], item+"["+str(x)+"]")
        for x in range(0, len(last_match)):
            self.match(last_match[x], item+"["+str(x-len(last_match))+"]")

    def match_const(self, original, item):
        """Matches a constant."""
        (match,) = original
        if match in const_vars:
            self.checks.append(item+" is "+match)
        else:
            self.checks.append(item+" == "+match)

    def match_var(self, original, item):
        """Matches a variable."""
        (setvar,) = original
        if setvar != wildcard:
            if setvar in self.names:
                self.checks.append(self.names[setvar]+" == "+item)
            else:
                self.defs.append(setvar+" = "+item)
                self.names[setvar] = item

    def match_set(self, original, item):
        """Matches a set."""
        if len(original) == 1:
            match = original[0]
        else:
            raise CoconutException("invalid set match tokens", original)
        self.checks.append("_coconut.isinstance("+item+", _coconut.abc.Set)")
        self.checks.append("_coconut.len("+item+") == "+str(len(match)))
        for const in match:
            self.checks.append(const+" in "+item)

    def match_data(self, original, item):
        """Matches a data type."""
        data_type, match = original
        self.checks.append("_coconut.isinstance("+item+", "+data_type+")")
        self.checks.append("_coconut.len("+item+") == "+str(len(match)))
        for x in range(0, len(match)):
            self.match(match[x], item+"["+str(x)+"]")

    def match_paren(self, original, item):
        """Matches a paren."""
        (match,) = original
        self.match(match, item)

    def match_trailer(self, original, item):
        """Matches typedefs and as patterns."""
        if len(original) <= 1 or len(original) % 2 != 1:
            raise CoconutException("invalid trailer match tokens", original)
        else:
            match, trailers = original[0], original[1:]
            for i in range(0, len(trailers), 2):
                op, arg = trailers[i], trailers[i+1]
                if op == "is":
                    self.checks.append("_coconut.isinstance("+item+", "+arg+")")
                elif op == "as":
                    if arg in self.names:
                        self.checks.append(self.names[arg]+" == "+item)
                    elif arg != wildcard:
                        self.defs.append(arg+" = "+item)
                        self.names[arg] = item
                else:
                    raise CoconutException("invalid trailer match operation", op)
            self.match(match, item)

    def match_and(self, original, item):
        """Matches and."""
        for match in original:
            self.match(match, item)

    def match_or(self, original, item):
        """Matches or."""
        for x in range(1, len(original)):
            self.duplicate().match(original[x], item)
        self.match(original[0], item)

    def match(self, original, item):
        """Performs pattern-matching processing."""
        for flag, handler in self.matchers.items():
            if flag in original.keys():
                return handler(self)(original, item)
        raise CoconutException("invalid inner match tokens", original)

    def out(self):
        out = ""
        closes = 0
        for checks, defs in self.checkdefs:
            if checks:
                out += "if (" + (") and (").join(checks) + "):\n" + openindent
                closes += 1
            if defs:
                out += "\n".join(defs) + "\n"
        out += match_check_var + " = True\n"
        out += closeindent * closes
        for other in self.others:
            out += other.out()
        return out

def match_handle(o, l, tokens, top=True):
    """Processes match blocks."""
    if len(tokens) == 3:
        matches, item, stmts = tokens
        cond = None
    elif len(tokens) == 4:
        matches, item, cond, stmts = tokens
    else:
        raise CoconutException("invalid outer match tokens", tokens)
    matching = Matcher()
    matching.match(matches, match_to_var)
    if cond:
        matching.add_guard(cond)
    out = ""
    if top:
        out += match_check_var + " = False\n"
    out += match_to_var + " = " + item + "\n"
    out += matching.out()
    if stmts is not None:
        out += "if "+match_check_var+":" + "\n" + openindent + "".join(stmts) + closeindent
    return out

def case_to_match(tokens, item):
    """Converts case tokens to match tokens."""
    if len(tokens) == 2:
        matches, stmts = tokens
        return matches, item, stmts
    elif len(tokens) == 3:
        matches, cond, stmts = tokens
        return matches, item, cond, stmts
    else:
        raise CoconutException("invalid case match tokens", tokens)

def case_handle(o, l, tokens):
    """Processes case blocks."""
    if len(tokens) == 2:
        item, cases = tokens
        default = None
    elif len(tokens) == 3:
        item, cases, default = tokens
    else:
        raise CoconutException("invalid top-level case tokens", tokens)
    out = match_handle(o, l, case_to_match(cases[0], item))
    for case in cases[1:]:
        out += ("if not "+match_check_var+":\n" + openindent
            + match_handle(o, l, case_to_match(case, item), top=False) + closeindent)
    if default is not None:
        out += "if not "+match_check_var+default
    return out

def except_handle(tokens):
    """Processes except statements."""
    if len(tokens) == 1:
        errs, asname = tokens[0], None
    elif len(tokens) == 2:
        errs, asname = tokens
    else:
        raise CoconutException("invalid except tokens", tokens)
    out = "except "
    if "list" in tokens.keys():
        out += "(" + errs + ")"
    else:
        out += errs
    if asname is not None:
        out += " as " + asname
    return out

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

def subscriptgroup_handle(tokens):
    """Processes subscriptgroups."""
    if 0 < len(tokens) <= 3:
        args = []
        for x in range(0, len(tokens)):
            arg = tokens[x]
            if not arg:
                arg = "None"
            args.append(arg)
        if len(args) == 1:
            return args[0]
        else:
            return "_coconut.slice(" + ", ".join(args) + ")"
    else:
        raise CoconutException("invalid slice args", tokens)

def itemgetter_handle(tokens):
    """Processes implicit itemgetter partials."""
    if len(tokens) != 2:
        raise CoconutException("invalid implicit itemgetter args", tokens)
    else:
        op, args = tokens
        if op == "[":
            return "_coconut.operator.itemgetter(" + args + ")"
        elif op == "$[":
            return "_coconut.functools.partial(_coconut_igetitem, index=" + args + ")"
        else:
            raise CoconutException("invalid implicit itemgetter type", op)

def class_suite_handle(tokens):
    """Processes implicit pass in class suite."""
    if len(tokens) != 1:
        raise CoconutException("invalid implicit pass in class suite tokens", tokens)
    else:
        return ": pass" + tokens[0]

def namelist_handle(tokens):
    """Handles inline nonlocal and global statements."""
    if len(tokens) == 1:
        return tokens[0]
    elif len(tokens) == 2:
        return tokens[0] + "; " + tokens[0] + " = " + tokens[1]
    else:
        raise CoconutException("invalid in-line nonlocal / global tokens", tokens)

# end: HANDLERS
#-----------------------------------------------------------------------------------------------------------------------
# COMPILER:
#-----------------------------------------------------------------------------------------------------------------------

class Compiler(object):
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
        lambda self: self.autopep8_proc,
    ]
    replprocs = [
        lambda self: self.endline_repl,
        lambda self: self.passthrough_repl,
        lambda self: self.str_repl,
    ]

    def __init__(self, *args, **kwargs):
        """Creates a new compiler with the given parsing parameters."""
        self.setup(*args, **kwargs)

    def setup(self, target=None, strict=False, minify=False, line_numbers=False, keep_lines=False, autopep8=None):
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
        self.tablen = 1 if self.minify else tabideal
        if autopep8 is not None:
            autopep8 = tuple(autopep8)
        self.autopep8_args = autopep8

    def __reduce__(self):
        """Return pickling information."""
        return (Compiler, (self.target, self.strict, self.minify, self.line_numbers, self.keep_lines, self.autopep8_args))

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
        self.async_block <<= attach(self.async_block_ref, self.async_stmt_check, copy=True)
        self.await_keyword <<= attach(self.await_keyword_ref, self.await_keyword_check, copy=True)
        self.star_expr <<= attach(self.star_expr_ref, self.star_expr_check, copy=True)
        self.dubstar_expr <<= attach(self.dubstar_expr_ref, self.star_expr_check, copy=True)

    def genhash(self, package, code):
        """Generates a hash from code."""
        return hex(checksum(
                hash_sep.join(str(item) for item in (
                    VERSION_STR,
                    self.target,
                    self.minify,
                    self.line_numbers,
                    self.autopep8_args,
                    package,
                    code
                )).encode(default_encoding)
            ) & 0xffffffff) # necessary for cross-compatibility

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
        if index is None:
            return self.repl_proc(snip, careful=False, add_to_line=False)
        else:
            return (self.repl_proc(snip, careful=False, add_to_line=False),
                    len(self.repl_proc(snip[:index], careful=False, add_to_line=False)))

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
            logger.log_tag(proc.__name__, inputstring)
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
        last = code.splitlines()[-1].split("#", 1)[0].rstrip()
        return last.endswith(":") or change(last) < 0

    def parse(self, inputstring, parser, preargs, postargs):
        """Uses the parser to parse the inputstring."""
        self.reset()
        try:
            out = self.post(parser.parseWithTabs().parseString(self.pre(inputstring, **preargs)), **postargs)
        except ParseBaseException as err:
            err_line, err_index = self.reformat(err.line, err.col-1)
            raise CoconutParseError(None, err_line, err_index, self.adjust(err.lineno))
        except RuntimeError as err:
            if True or logger.verbose:
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
        if self.keep_lines:
            self.original_lines = inputstring.splitlines()
        if strip:
            inputstring = inputstring.strip()
        return "\n".join(inputstring.splitlines()) # str_proc will add a newline to the end

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
        for x in range(0, len(inputstring)):
            c = inputstring[x]
            if hold is not None:
                count += change(c)
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
        """Processes indentation and fixes line/file endings."""
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
                last = new[-1].split("#", 1)[0].rstrip()
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
            count += change(line)
        self.skips = skips
        if new:
            last = new[-1].split("#", 1)[0].rstrip()
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
                    indents = ""
                    while line.startswith(openindent) or line.startswith(closeindent):
                        indents += line[0]
                        line = line[1:]
                    out.append(indents + self.stmt_lambdas[i])
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
            while line.startswith(openindent) or line.startswith(closeindent):
                if line[0] == openindent:
                    level += 1
                elif line[0] == closeindent:
                    level -= 1
                line = line[1:].lstrip()
            if line and not line.startswith("#"):
                line = " "*self.tablen*level + line
            while line.endswith(openindent) or line.endswith(closeindent):
                if line[-1] == openindent:
                    level += 1
                elif line[-1] == closeindent:
                    level -= 1
                line = line[:-1].rstrip()
            out.append(line + comment)
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
                except CoconutException:
                    if careful:
                        raise
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

    def autopep8_proc(self, inputstring, use_autopep8=True, **kwargs):
        """Applies autopep8."""
        if use_autopep8 and self.autopep8_args is not None:
            import autopep8
            return autopep8.fix_code(inputstring, options=autopep8.parse_args(("autopep8",) + self.autopep8_args))
        else:
            return inputstring

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
                elif trailer[0] == "..":
                    out = "_coconut_compose("+out+", "+trailer[1]+")"
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
        out += self.pattern_error(original, loc)
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
# GRAMMAR:
#-----------------------------------------------------------------------------------------------------------------------

    comma = Literal(",")
    dubstar = Literal("**")
    star = ~dubstar+Literal("*")
    at = Literal("@")
    arrow = Literal("->") | fixto(Literal("\u2192"), "->")
    dubcolon = Literal("::")
    unsafe_colon = Literal(":")
    colon = ~dubcolon+unsafe_colon
    semicolon = Literal(";")
    eq = Literal("==")
    equals = ~eq+Literal("=")
    lbrack = Literal("[")
    rbrack = Literal("]")
    lbrace = Literal("{")
    rbrace = Literal("}")
    lbanana = ~Literal("(|)")+~Literal("(|>)")+~Literal("(|*>)")+Literal("(|")
    rbanana = Literal("|)")
    lparen = ~lbanana+Literal("(")
    rparen = ~rbanana+Literal(")")
    unsafe_dot = Literal(".")
    dot = ~Literal("..")+unsafe_dot
    plus = Literal("+")
    minus = ~Literal("->")+Literal("-")
    dubslash = Literal("//")
    slash = ~dubslash+Literal("/")
    pipeline = Literal("|>") | fixto(Literal("\u21a6"), "|>")
    starpipe = Literal("|*>") | fixto(Literal("*\u21a6"), "|*>")
    backpipe = Literal("<|") | fixto(Literal("\u21a4"), "<|")
    backstarpipe = Literal("<*|") | fixto(Literal("\u21a4*"), "<*|")
    amp = Literal("&") | fixto(Literal("\u2227") | Literal("\u2229"), "&")
    caret = Literal("^") | fixto(Literal("\u22bb") | Literal("\u2295"), "^")
    bar = ~Literal("|>")+~Literal("|*>")+Literal("|") | fixto(Literal("\u2228") | Literal("\u222a"), "|")
    percent = Literal("%")
    dotdot = ~Literal("...")+Literal("..") | fixto(Literal("\u2218"), "..")
    dollar = Literal("$")
    ellipses = fixto(Literal("...") | Literal("\u2026"), "...")
    lshift = Literal("<<") | fixto(Literal("\xab"), "<<")
    rshift = Literal(">>") | fixto(Literal("\xbb"), ">>")
    tilde = Literal("~") | fixto(~Literal("\xac=")+Literal("\xac"), "~")
    underscore = Literal("_")
    pound = Literal("#")
    backtick = Literal("`")
    dubbackslash = Literal("\\\\")
    backslash = ~dubbackslash+Literal("\\")

    lt = ~Literal("<<")+~Literal("<=")+Literal("<")
    gt = ~Literal(">>")+~Literal(">=")+Literal(">")
    le = Literal("<=") | fixto(Literal("\u2264"), "<=")
    ge = Literal(">=") | fixto(Literal("\u2265"), ">=")
    ne = Literal("!=") | fixto(Literal("\xac=") | Literal("\u2260"), "!=")

    mul_star = fixto(star | Literal("\u22c5"), "*")
    exp_dubstar = fixto(dubstar | Literal("\u2191"), "**")
    neg_minus = fixto(minus | Literal("\u207b"), "-")
    sub_minus = fixto(minus | Literal("\u2212"), "-")
    div_slash = fixto(slash | Literal("\xf7")+~slash, "/")
    div_dubslash = fixto(dubslash | Combine(Literal("\xf7")+slash), "//")
    matrix_at_ref = fixto(at | Literal("\xd7"), "@")
    matrix_at = Forward()

    name = Forward()
    name_ref = ~Literal(reserved_prefix) + Regex(r"\b(?![0-9])\w+\b")
    for k in keywords + const_vars:
        name_ref = ~Keyword(k) + name_ref
    for k in reserved_vars:
        name_ref |= backslash.suppress() + Keyword(k)
    dotted_name = condense(name + ZeroOrMore(dot + name))

    integer = Combine(Word(nums) + ZeroOrMore(underscore.suppress() + Word(nums)))
    binint = Combine(Word("01") + ZeroOrMore(underscore.suppress() + Word("01")))
    octint = Combine(Word("01234567") + ZeroOrMore(underscore.suppress() + Word("01234567")))
    hexint = Combine(Word(hexnums) + ZeroOrMore(underscore.suppress() + Word(hexnums)))

    basenum = Combine(integer + dot + Optional(integer) | Optional(integer) + dot + integer) | integer
    sci_e = Combine(CaselessLiteral("e") + Optional(plus | neg_minus))
    numitem = Combine(basenum + sci_e + integer) | basenum
    complex_i = CaselessLiteral("j") | fixto(CaselessLiteral("i"), "j")
    complex_num = Combine(numitem + complex_i)
    bin_num = Combine(CaselessLiteral("0b") + Optional(underscore.suppress()) + binint)
    oct_num = Combine(CaselessLiteral("0o") + Optional(underscore.suppress()) + octint)
    hex_num = Combine(CaselessLiteral("0x") + Optional(underscore.suppress()) + hexint)
    number = bin_num | oct_num | hex_num | complex_num | numitem

    moduledoc_item = Forward()
    unwrap = Literal(unwrapper)
    string_item = Combine(Literal(strwrapper) + integer + unwrap)
    comment = Combine(pound + integer + unwrap)
    passthrough = Combine(backslash + integer + unwrap)
    passthrough_block = Combine(fixto(dubbackslash, "\\", copy=True) + integer + unwrap)

    endline = Forward()
    endline_ref = condense(OneOrMore(Literal("\n")))
    lineitem = Combine(Optional(comment) + endline)
    newline = condense(OneOrMore(lineitem))
    start_marker = stringStart
    moduledoc_marker = condense(ZeroOrMore(lineitem) - Optional(moduledoc_item))
    end_marker = stringEnd
    indent = Literal(openindent)
    dedent = Literal(closeindent)

    u_string = Forward()
    f_string = Forward()
    bit_b = Optional(CaselessLiteral("b"))
    raw_r = Optional(CaselessLiteral("r"))
    b_string = Combine((bit_b + raw_r | raw_r + bit_b) + string_item)
    unicode_u = CaselessLiteral("u").suppress()
    u_string_ref = Combine((unicode_u + raw_r | raw_r + unicode_u) + string_item)
    format_f = CaselessLiteral("f")
    f_string_ref = Combine((format_f + raw_r | raw_r + format_f) + string_item)
    string = trace(b_string | u_string | f_string, "string")
    moduledoc = string + newline
    docstring = condense(moduledoc, copy=True)

    augassign = (
        Combine(pipeline + equals)
        | Combine(starpipe + equals)
        | Combine(backpipe + equals)
        | Combine(backstarpipe + equals)
        | Combine(dotdot + equals)
        | Combine(dubcolon + equals)
        | Combine(div_dubslash + equals)
        | Combine(div_slash + equals)
        | Combine(exp_dubstar + equals)
        | Combine(mul_star + equals)
        | Combine(plus + equals)
        | Combine(sub_minus + equals)
        | Combine(percent + equals)
        | Combine(amp + equals)
        | Combine(bar + equals)
        | Combine(caret + equals)
        | Combine(lshift + equals)
        | Combine(rshift + equals)
        | Combine(matrix_at + equals)
        )

    comp_op = (le | ge | ne | lt | gt | eq
               | addspace(Keyword("not") + Keyword("in"))
               | Keyword("in")
               | addspace(Keyword("is") + Keyword("not"))
               | Keyword("is")
               )

    test = Forward()
    expr = Forward()
    star_expr = Forward()
    dubstar_expr = Forward()
    comp_for = Forward()
    test_nochain = Forward()
    test_nocond = Forward()

    testlist = trace(itemlist(test, comma), "testlist")
    testlist_star_expr = trace(itemlist(test | star_expr, comma), "testlist_star_expr")
    multi_testlist = trace(addspace(OneOrMore(condense(test + comma)) + Optional(test)), "multi_testlist")

    yield_from = Forward()
    dict_comp = Forward()
    yield_classic = addspace(Keyword("yield") + testlist)
    yield_from_ref = Keyword("yield").suppress() + Keyword("from").suppress() + test
    yield_expr = yield_from | yield_classic
    dict_comp_ref = lbrace.suppress() + (test + colon.suppress() + test | dubstar_expr) + comp_for + rbrace.suppress()
    dict_item = condense(lbrace + Optional(itemlist(addspace(condense(test + colon) + test) | dubstar_expr, comma)) + rbrace)
    test_expr = yield_expr | testlist_star_expr

    op_item = (
        fixto(pipeline, "_coconut_pipe", copy=True)
        | fixto(starpipe, "_coconut_starpipe", copy=True)
        | fixto(backpipe, "_coconut_backpipe", copy=True)
        | fixto(backstarpipe, "_coconut_backstarpipe", copy=True)
        | fixto(dotdot, "_coconut_compose", copy=True)
        | fixto(Keyword("and"), "_coconut_bool_and", copy=True)
        | fixto(Keyword("or"), "_coconut_bool_or", copy=True)
        | fixto(minus, "_coconut_minus", copy=True)
        | fixto(dot, "_coconut.getattr", copy=True)
        | fixto(dubcolon, "_coconut.itertools.chain", copy=True)
        | fixto(dollar, "_coconut.functools.partial", copy=True)
        | fixto(exp_dubstar, "_coconut.operator.pow", copy=True)
        | fixto(mul_star, "_coconut.operator.mul", copy=True)
        | fixto(div_dubslash, "_coconut.operator.floordiv", copy=True)
        | fixto(div_slash, "_coconut.operator.truediv", copy=True)
        | fixto(percent, "_coconut.operator.mod", copy=True)
        | fixto(plus, "_coconut.operator.add", copy=True)
        | fixto(amp, "_coconut.operator.and_", copy=True)
        | fixto(caret, "_coconut.operator.xor", copy=True)
        | fixto(bar, "_coconut.operator.or_", copy=True)
        | fixto(lshift, "_coconut.operator.lshift", copy=True)
        | fixto(rshift, "_coconut.operator.rshift", copy=True)
        | fixto(lt, "_coconut.operator.lt", copy=True)
        | fixto(gt, "_coconut.operator.gt", copy=True)
        | fixto(eq, "_coconut.operator.eq", copy=True)
        | fixto(le, "_coconut.operator.le", copy=True)
        | fixto(ge, "_coconut.operator.ge", copy=True)
        | fixto(ne, "_coconut.operator.ne", copy=True)
        | fixto(tilde, "_coconut.operator.inv", copy=True)
        | fixto(matrix_at, "_coconut.operator.matmul", copy=True)
        | fixto(Keyword("not"), "_coconut.operator.not_")
        | fixto(Keyword("is"), "_coconut.operator.is_")
        | fixto(Keyword("in"), "_coconut.operator.contains")
    )

    typedef = Forward()
    typedef_ref = addspace(condense(name + colon) + test)
    tfpdef = typedef | name
    default = condense(equals + test)

    argslist = trace(Optional(itemlist(condense(
        dubstar + tfpdef
        | star + Optional(tfpdef)
        | tfpdef + Optional(default)
        ), comma)), "argslist")
    varargslist = trace(Optional(itemlist(condense(
        dubstar + name
        | star + Optional(name)
        | name + Optional(default)
        ), comma)), "varargslist")
    parameters = condense(lparen + argslist + rparen)

    callargslist = Optional(trace(
        attach(addspace(test + comp_for), add_paren_handle)
        | itemlist(condense(dubstar + test | star + test | name + default | test), comma)
        | op_item
        , "callargslist"))
    methodcaller_args = (
        itemlist(condense(name + default | test), comma)
        | op_item
        )

    slicetest = Optional(test_nochain)
    sliceop = condense(unsafe_colon + slicetest)
    subscript = condense(slicetest + sliceop + Optional(sliceop)) | test
    subscriptlist = itemlist(subscript, comma)

    slicetestgroup = Optional(test_nochain, default="")
    sliceopgroup = unsafe_colon.suppress() + slicetestgroup
    subscriptgroup = attach(slicetestgroup + sliceopgroup + Optional(sliceopgroup) | test, subscriptgroup_handle)

    testlist_comp = addspace((test | star_expr) + comp_for) | testlist_star_expr
    list_comp = condense(lbrack + Optional(testlist_comp) + rbrack)
    composable_atom = trace(
        name
        | condense(lparen + Optional(yield_expr | testlist_comp) + rparen)
        | lparen.suppress() + op_item + rparen.suppress()
        , "composable_atom")
    keyword_atom = Keyword(const_vars[0])
    for x in range(1, len(const_vars)):
        keyword_atom |= Keyword(const_vars[x])
    string_atom = addspace(OneOrMore(string))
    passthrough_atom = trace(addspace(OneOrMore(passthrough)), "passthrough_atom")
    attr_atom = attach(dot.suppress() + name + Optional(lparen.suppress() + methodcaller_args + rparen.suppress()), attr_handle)
    itemgetter_atom = attach(dot.suppress() + condense(Optional(dollar) + lbrack) + subscriptgroup + rbrack.suppress(), itemgetter_handle)
    set_literal = Forward()
    set_letter_literal = Forward()
    set_s = fixto(CaselessLiteral("s"), "s")
    set_f = fixto(CaselessLiteral("f"), "f")
    set_letter = set_s | set_f
    setmaker = Group(addspace(test + comp_for)("comp") | multi_testlist("list") | test("test"))
    set_literal_ref = lbrace.suppress() + setmaker + rbrace.suppress()
    set_letter_literal_ref = set_letter + lbrace.suppress() + Optional(setmaker) + rbrace.suppress()
    lazy_items = Optional(test + ZeroOrMore(comma.suppress() + test) + Optional(comma.suppress()))
    lazy_list = attach(lbanana.suppress() + lazy_items + rbanana.suppress(), lazy_list_handle)
    const_atom = (
        keyword_atom
        | number
        | string_atom
        )
    known_atom = trace(
        const_atom
        | ellipses
        | attr_atom
        | itemgetter_atom
        | list_comp
        | dict_comp
        | dict_item
        | set_literal
        | set_letter_literal
        | lazy_list
        , "known_atom")
    atom = (
        known_atom
        | passthrough_atom
        | composable_atom
        )

    simple_trailer = (
        condense(lbrack + subscriptlist + rbrack)
        | condense(dot + name)
        )
    complex_trailer = (
        condense(lparen + callargslist + rparen)
        | Group(condense(dollar + lparen) + callargslist + rparen.suppress())
        | Group(dotdot + composable_atom)
        | Group(condense(dollar + lbrack) + subscriptgroup + rbrack.suppress())
        | Group(condense(dollar + lbrack + rbrack))
        | Group(dollar)
        | Group(condense(lbrack + rbrack))
        | Group(~(dot + (name | lbrack)) + dot)
        )
    trailer = simple_trailer | complex_trailer

    atom_item = Forward()
    atom_item_ref = atom + ZeroOrMore(trailer)
    simple_assign = Forward()
    simple_assign_ref = (name | passthrough_atom) + ZeroOrMore(ZeroOrMore(complex_trailer) + OneOrMore(simple_trailer))

    assignlist = Forward()
    star_assign_item = Forward()
    simple_assignlist = parenwrap(lparen, itemlist(simple_assign, comma), rparen)
    base_assign_item = condense(simple_assign | lparen + assignlist + rparen | lbrack + assignlist + rbrack)
    star_assign_item_ref = condense(star + base_assign_item)
    assign_item = star_assign_item | base_assign_item
    assignlist <<= itemlist(assign_item, comma)

    factor = Forward()
    await_keyword = Forward()
    await_keyword_ref = Keyword("await")
    power = trace(condense(addspace(Optional(await_keyword) + atom_item) + Optional(exp_dubstar + factor)), "power")
    unary = plus | neg_minus | tilde

    factor <<= trace(condense(ZeroOrMore(unary) + power), "factor")

    mulop = mul_star | div_dubslash | div_slash | percent | matrix_at
    term = addspace(factor + ZeroOrMore(mulop + factor))
    arith = plus | sub_minus
    arith_expr = addspace(term + ZeroOrMore(arith + term))

    shift = lshift | rshift
    shift_expr = addspace(arith_expr + ZeroOrMore(shift + arith_expr))
    and_expr = addspace(shift_expr + ZeroOrMore(amp + shift_expr))
    xor_expr = addspace(and_expr + ZeroOrMore(caret + and_expr))
    or_expr = addspace(xor_expr + ZeroOrMore(bar + xor_expr))

    chain_expr = attach(or_expr + ZeroOrMore(dubcolon.suppress() + or_expr), chain_handle)

    infix_expr = Forward()
    infix_op = condense(backtick.suppress() + chain_expr + backtick.suppress())
    infix_item = attach(Group(Optional(chain_expr)) + infix_op + Group(Optional(infix_expr)), infix_handle)
    infix_expr <<= infix_item | chain_expr
    nochain_infix_expr = Forward()
    nochain_infix_item = attach(Group(Optional(or_expr)) + infix_op + Group(Optional(nochain_infix_expr)), infix_handle)
    nochain_infix_expr <<= nochain_infix_item | or_expr

    pipe_op = pipeline | starpipe | backpipe | backstarpipe
    pipe_expr = attach(infix_expr + ZeroOrMore(pipe_op + infix_expr), pipe_handle)
    nochain_pipe_expr = attach(nochain_infix_expr + ZeroOrMore(pipe_op + nochain_infix_expr), pipe_handle)

    expr <<= trace(pipe_expr, "expr")
    star_expr_ref = condense(star + expr)
    dubstar_expr_ref = condense(dubstar + expr)
    comparison = addspace(expr + ZeroOrMore(comp_op + expr))
    not_test = addspace(ZeroOrMore(Keyword("not")) + comparison)
    and_test = addspace(not_test + ZeroOrMore(Keyword("and") + not_test))
    or_test = addspace(and_test + ZeroOrMore(Keyword("or") + and_test))
    test_item = trace(or_test, "test_item")
    nochain_expr = trace(nochain_pipe_expr, "nochain_expr")
    nochain_comparison = addspace(nochain_expr + ZeroOrMore(comp_op + nochain_expr))
    nochain_not_test = addspace(ZeroOrMore(Keyword("not")) + nochain_comparison)
    nochain_and_test = addspace(nochain_not_test + ZeroOrMore(Keyword("and") + nochain_not_test))
    nochain_or_test = addspace(nochain_and_test + ZeroOrMore(Keyword("or") + nochain_and_test))
    nochain_test_item = trace(nochain_or_test, "nochain_test_item")

    small_stmt = Forward()
    simple_stmt = Forward()
    simple_compound_stmt = Forward()
    stmt = Forward()
    suite = Forward()
    base_suite = Forward()
    classlist = Forward()

    classic_lambdef = Forward()
    classic_lambdef_params = parenwrap(lparen, varargslist, rparen)
    new_lambdef_params = lparen.suppress() + varargslist + rparen.suppress()
    classic_lambdef_ref = addspace(Keyword("lambda") + condense(classic_lambdef_params + colon))
    new_lambdef = attach(new_lambdef_params + arrow.suppress(), lambdef_handle)
    implicit_lambdef = fixto(arrow, "lambda _=None:", copy=True)
    lambdef_base = classic_lambdef | new_lambdef | implicit_lambdef

    stmt_lambdef = Forward()
    closing_stmt = testlist("tests") ^ small_stmt
    stmt_lambdef_ref = (
        Keyword("def").suppress() + Optional(parameters, default="(_=None)") + arrow.suppress()
        + (
            Group(OneOrMore(small_stmt + semicolon.suppress())) + Optional(closing_stmt)
            | Group(ZeroOrMore(small_stmt + semicolon.suppress())) + closing_stmt
            )
        )

    lambdef = trace(addspace(lambdef_base + test) | stmt_lambdef, "lambdef")
    lambdef_nocond = trace(addspace(lambdef_base + test_nocond), "lambdef_nocond")
    lambdef_nochain = trace(addspace(lambdef_base + test_nochain), "lambdef_nochain")

    test <<= trace(lambdef | addspace(test_item + Optional(Keyword("if") + test_item + Keyword("else") + test)), "test")
    test_nocond <<= trace(lambdef_nocond | test_item, "test_nocond")
    test_nochain <<= trace(lambdef_nochain
        | addspace(nochain_test_item + Optional(Keyword("if") + nochain_test_item + Keyword("else") + test_nochain)), "test_nochain")

    classlist_ref = Optional(
        lparen.suppress() + rparen.suppress()
        | Group(
            lparen.suppress() + testlist("tests") + rparen.suppress()
            | lparen.suppress() + callargslist("args") + rparen.suppress()
            )
        )
    class_suite = suite | attach(newline, class_suite_handle, copy=True)
    classdef = condense(addspace(Keyword("class") - name) + classlist + class_suite)
    comp_iter = Forward()
    comp_for <<= trace(addspace(Keyword("for") + assignlist + Keyword("in") + test_item + Optional(comp_iter)), "comp_for")
    comp_if = addspace(Keyword("if") + test_nocond + Optional(comp_iter))
    comp_iter <<= comp_for | comp_if

    complex_raise_stmt = Forward()
    pass_stmt = Keyword("pass")
    break_stmt = Keyword("break")
    continue_stmt = Keyword("continue")
    return_stmt = addspace(Keyword("return") - Optional(testlist))
    simple_raise_stmt = addspace(Keyword("raise") + Optional(test))
    complex_raise_stmt_ref = Keyword("raise").suppress() + test + Keyword("from").suppress() - test
    raise_stmt = complex_raise_stmt | simple_raise_stmt
    flow_stmt = break_stmt | continue_stmt | return_stmt | raise_stmt | yield_expr

    dotted_as_name = Group(dotted_name - Optional(Keyword("as").suppress() - name))
    import_as_name = Group(name - Optional(Keyword("as").suppress() - name))
    import_names = Group(parenwrap(lparen, tokenlist(dotted_as_name, comma), rparen, tokens=True))
    import_from_names = Group(parenwrap(lparen, tokenlist(import_as_name, comma), rparen, tokens=True))
    import_name = Keyword("import").suppress() - import_names
    import_from = (Keyword("from").suppress()
        - condense(ZeroOrMore(unsafe_dot) + dotted_name | OneOrMore(unsafe_dot))
        - Keyword("import").suppress() - (Group(star) | import_from_names))
    import_stmt = Forward()
    import_stmt_ref = import_from | import_name

    nonlocal_stmt = Forward()
    namelist = attach(
        parenwrap(lparen, itemlist(name, comma), rparen)
        - Optional(equals.suppress() - test_expr)
        , namelist_handle)
    global_stmt = addspace(Keyword("global") - namelist)
    nonlocal_stmt_ref = addspace(Keyword("nonlocal") - namelist)
    del_stmt = addspace(Keyword("del") - simple_assignlist)
    with_item = addspace(test - Optional(Keyword("as") - name))
    with_item_list = parenwrap(lparen, condense(itemlist(with_item, comma)), rparen)

    match = Forward()
    matchlist_list = Group(Optional(tokenlist(match, comma)))
    matchlist_tuple = Group(Optional(match + OneOrMore(comma.suppress() + match) + Optional(comma.suppress())
                                     | match + comma.suppress()))
    match_const = const_atom | condense(equals.suppress() + atom_item)
    matchlist_set = Group(Optional(tokenlist(match_const, comma)))
    match_pair = Group(match_const + colon.suppress() + match)
    matchlist_dict = Group(Optional(tokenlist(match_pair, comma)))
    match_list = lbrack + matchlist_list + rbrack.suppress()
    match_tuple = lparen + matchlist_tuple + rparen.suppress()
    match_lazy = lbanana + matchlist_list + rbanana.suppress()
    base_match = Group(
        match_const("const")
        | (lparen.suppress() + match + rparen.suppress())("paren")
        | (lbrace.suppress() + matchlist_dict + rbrace.suppress())("dict")
        | (Optional(set_s.suppress()) + lbrace.suppress() + matchlist_set + rbrace.suppress())("set")
        | ((match_list | match_tuple | match_lazy) + dubcolon.suppress() + name)("iter")
        | match_lazy("iter")
        | (match_list + plus.suppress() + name + plus.suppress() + match_list)("mseries")
        | (match_tuple + plus.suppress() + name + plus.suppress() + match_tuple)("mseries")
        | ((match_list | match_tuple) + Optional(plus.suppress() + name))("series")
        | (name + plus.suppress() + (match_list | match_tuple))("rseries")
        | (name + lparen.suppress() + matchlist_list + rparen.suppress())("data")
        | name("var")
        )
    matchlist_trailer = base_match + OneOrMore(Keyword("as") + name | Keyword("is") + atom_item)
    as_match = Group(matchlist_trailer("trailer")) | base_match
    matchlist_and = as_match + OneOrMore(Keyword("and").suppress() + as_match)
    and_match = Group(matchlist_and("and")) | as_match
    matchlist_or = and_match + OneOrMore(Keyword("or").suppress() + and_match)
    or_match = Group(matchlist_or("or")) | and_match
    match <<= trace(or_match, "match")

    else_suite = condense(colon + trace(attach(simple_compound_stmt, else_handle, copy=True), "else_suite")) | suite
    else_stmt = condense(Keyword("else") - else_suite)

    match_guard = Optional(Keyword("if").suppress() + test)
    full_suite = colon.suppress() + Group((newline.suppress() + indent.suppress() + OneOrMore(stmt) + dedent.suppress()) | simple_stmt)
    full_match = trace(attach(
        Keyword("match").suppress() + match + Keyword("in").suppress() - test - match_guard - full_suite
        , match_handle), "full_match")
    match_stmt = condense(full_match - Optional(else_stmt))

    destructuring_stmt = Forward()
    destructuring_stmt_ref = match + equals.suppress() - test_expr - newline.suppress()
    match_assign_stmt = Keyword("match").suppress() + destructuring_stmt

    case_match = trace(Group(
        Keyword("match").suppress() - match - Optional(Keyword("if").suppress() - test) - full_suite
        ), "case_match")
    case_stmt = attach(
        Keyword("case").suppress() + test - colon.suppress() - newline.suppress()
        - indent.suppress() - Group(OneOrMore(case_match))
        - dedent.suppress() - Optional(Keyword("else").suppress() - else_suite)
        , case_handle)

    exec_stmt = Forward()
    assert_stmt = addspace(Keyword("assert") - testlist)
    if_stmt = condense(addspace(Keyword("if") - condense(test - suite))
                       - ZeroOrMore(addspace(Keyword("elif") - condense(test - suite)))
                       - Optional(else_stmt)
                       )
    while_stmt = addspace(Keyword("while") - condense(test - suite - Optional(else_stmt)))
    for_stmt = addspace(Keyword("for") - assignlist - Keyword("in") - condense(testlist - suite - Optional(else_stmt)))
    except_clause = attach(Keyword("except").suppress() + (
            multi_testlist("list") | test("test")
        ) - Optional(Keyword("as").suppress() - name), except_handle)
    try_stmt = condense(Keyword("try") - suite + (
        Keyword("finally") - suite
        | (
            OneOrMore(except_clause - suite) - Optional(Keyword("except") - suite)
            | Keyword("except") - suite
          ) - Optional(else_stmt) - Optional(Keyword("finally") - suite)
        ))
    with_stmt = addspace(Keyword("with") - with_item_list - suite)
    exec_stmt_ref = Keyword("exec").suppress() + lparen.suppress() + test + Optional(
        comma.suppress() + test + Optional(
            comma.suppress() + test + Optional(
                comma.suppress()
                )
            )
        ) + rparen.suppress()

    return_typedef = Forward()
    async_funcdef = Forward()
    async_block = Forward()
    name_funcdef = condense(name + parameters)
    op_funcdef_arg = name | condense(lparen.suppress() + tfpdef + Optional(default) + rparen.suppress())
    op_funcdef_name = backtick.suppress() + name + backtick.suppress()
    op_funcdef = attach(Group(Optional(op_funcdef_arg)) + op_funcdef_name + Group(Optional(op_funcdef_arg)), op_funcdef_handle)
    return_typedef_ref = addspace(arrow + test)
    base_funcdef = trace(addspace((op_funcdef | name_funcdef) + Optional(return_typedef)), "base_funcdef")
    funcdef = trace(addspace(Keyword("def") + condense(base_funcdef + suite)), "funcdef")

    name_match_funcdef = Forward()
    op_match_funcdef = Forward()
    async_match_funcdef = Forward()
    name_match_funcdef_ref = name + lparen.suppress() + matchlist_list + match_guard + rparen.suppress()
    op_match_funcdef_arg = lparen.suppress() + match + rparen.suppress()
    op_match_funcdef_ref = Group(Optional(op_match_funcdef_arg)) + op_funcdef_name + Group(Optional(op_match_funcdef_arg)) + match_guard
    base_match_funcdef = trace(Keyword("def").suppress() + (op_match_funcdef | name_match_funcdef), "base_match_funcdef")
    def_match_funcdef = trace(attach(base_match_funcdef + full_suite, def_match_funcdef_handle), "def_match_funcdef")
    match_funcdef = Optional(Keyword("match").suppress()) + def_match_funcdef

    testlist_stmt = condense(testlist + newline)
    math_funcdef_suite = attach(
        testlist_stmt
        | condense(newline - indent) - ZeroOrMore(~(testlist_stmt + dedent) + stmt) - condense(testlist_stmt - dedent)
        , math_funcdef_suite_handle)
    math_funcdef = trace(attach(
        condense(addspace(Keyword("def") + base_funcdef) + fixto(equals, ":", copy=True)) - math_funcdef_suite
        , math_funcdef_handle), "math_funcdef")
    math_match_funcdef = trace(attach(
        Optional(Keyword("match").suppress()) + condense(base_match_funcdef + equals.suppress() - math_funcdef_suite)
        , math_match_funcdef_handle), "math_match_funcdef")

    async_funcdef_ref = addspace(Keyword("async") + (funcdef | math_funcdef))
    async_block_ref = addspace(Keyword("async") + (with_stmt | for_stmt))
    async_match_funcdef_ref = addspace(
        (
            Optional(Keyword("match")).suppress() + Keyword("async")
            | Keyword("async") + Optional(Keyword("match")).suppress()
            )
        + (def_match_funcdef | math_match_funcdef)
        )
    async_stmt = async_block | async_funcdef | async_match_funcdef_ref

    data_args = Optional(lparen.suppress() + Optional(itemlist(~underscore + name, comma)) + rparen.suppress())
    data_suite = Group(colon.suppress() - (
        (newline.suppress() + indent.suppress() + Optional(docstring) + Group(OneOrMore(stmt)) + dedent.suppress())("complex")
        | (newline.suppress() + indent.suppress() + docstring + dedent.suppress() | docstring)("docstring")
        | simple_stmt("simple")
        ) | newline("empty"))
    datadef = condense(attach(Keyword("data").suppress() + name - data_args - data_suite, data_handle))

    simple_decorator = condense(dotted_name + Optional(lparen + callargslist + rparen))("simple")
    complex_decorator = test("test")
    decorators = attach(OneOrMore(at.suppress() - Group(simple_decorator ^ complex_decorator) - newline.suppress()), decorator_handle)
    decoratable_stmt = trace(
        classdef
        | datadef
        | funcdef
        | async_funcdef
        | async_match_funcdef
        | math_funcdef
        | math_match_funcdef
        | match_funcdef
        , "decoratable_stmt")
    decorated = condense(decorators - decoratable_stmt)

    passthrough_stmt = condense(passthrough_block - (base_suite | newline))

    simple_compound_stmt <<= trace(
        if_stmt
        | try_stmt
        | case_stmt
        | match_stmt
        | passthrough_stmt
        , "simple_compound_stmt")
    compound_stmt = trace(
        decoratable_stmt
        | with_stmt
        | while_stmt
        | for_stmt
        | async_stmt
        | simple_compound_stmt
        | decorated
        | match_assign_stmt
        , "compound_stmt")
    keyword_stmt = trace(
        del_stmt
        | pass_stmt
        | flow_stmt
        | import_stmt
        | global_stmt
        | nonlocal_stmt
        | assert_stmt
        | exec_stmt
        , "keyword_stmt")
    augassign_stmt = Forward()
    augassign_stmt_ref = simple_assign + augassign + test_expr
    expr_stmt = trace(addspace(
        augassign_stmt
        | ZeroOrMore(assignlist + equals) + test_expr
        ), "expr_stmt")

    small_stmt <<= trace(keyword_stmt | expr_stmt, "small_stmt")
    simple_stmt <<= trace(condense(itemlist(small_stmt, semicolon) + newline), "simple_stmt")
    stmt <<= compound_stmt | simple_stmt | destructuring_stmt
    base_suite <<= condense(newline + indent - OneOrMore(stmt) - dedent)
    suite <<= trace(condense(colon + base_suite) | addspace(colon + simple_stmt), "suite")
    line = trace(newline | stmt, "line")

    single_input = trace(condense(Optional(line) - ZeroOrMore(newline)), "single_input")
    file_input = trace(condense(moduledoc_marker - ZeroOrMore(line)), "file_input")
    eval_input = trace(condense(testlist - ZeroOrMore(newline)), "eval_input")

    single_parser = condense(start_marker - single_input - end_marker)
    file_parser = condense(start_marker - file_input - end_marker)
    eval_parser = condense(start_marker - eval_input - end_marker)

# end: GRAMMAR
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
