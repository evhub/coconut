#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Defines the Coconut grammar.
"""

# Table of Contents:
#   - Imports
#   - Setup
#   - Handlers
#   - Main Grammar
#   - Extra Grammar

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import re
from contextlib import contextmanager

from pyparsing import (
    CaselessLiteral,
    Combine,
    Forward,
    Group,
    Keyword,
    Literal,
    OneOrMore,
    Optional,
    ParserElement,
    Regex,
    StringEnd,
    StringStart,
    Word,
    ZeroOrMore,
    hexnums,
    nums,
    originalTextFor,
    nestedExpr,
    SkipTo,
    FollowedBy,
)

from coconut.exceptions import CoconutInternalException
from coconut.logging import trace
from coconut.constants import (
    openindent,
    closeindent,
    strwrapper,
    unwrapper,
    keywords,
    const_vars,
    reserved_vars,
    default_whitespace_chars,
    decorator_var,
    match_to_var,
    match_check_var,
    match_iter_var,
    lazy_item_var,
    wildcard,
)
from coconut.compiler.util import (
    attach,
    fixto,
    addspace,
    condense,
    parenwrap,
    tokenlist,
    itemlist,
    longest,
)

# end: IMPORTS
#-----------------------------------------------------------------------------------------------------------------------
# SETUP:
#-----------------------------------------------------------------------------------------------------------------------

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
        raise CoconutInternalException("invalid tokens for parentheses adding", tokens)


def attr_handle(tokens):
    """Processes attrgetter literals."""
    if len(tokens) == 1:
        return '_coconut.operator.attrgetter("' + tokens[0] + '")'
    elif len(tokens) == 2 and tokens[1] == "(":
        return '_coconut.operator.methodcaller("' + tokens[0] + '")'
    elif len(tokens) == 3 and tokens[1] == "(":
        return '_coconut.operator.methodcaller("' + tokens[0] + '", ' + tokens[2] + ")"
    else:
        raise CoconutInternalException("invalid attrgetter literal tokens", tokens)


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
    raise CoconutInternalException("invalid inner infix tokens", tokens)


def infix_handle(tokens):
    """Processes infix calls."""
    func, args = get_infix_items(tokens, infix_handle)
    return "(" + func + ")(" + ", ".join(args) + ")"


def get_infix_items(tokens, callback=infix_error):
    """Performs infix token processing."""
    if len(tokens) < 3:
        raise CoconutInternalException("invalid infix tokens", tokens)
    else:
        items = []
        for item in tokens[0]:
            items.append(item)
        for item in tokens[2]:
            items.append(item)
        if len(tokens) > 3:
            items.append(callback([[]] + tokens[3:]))
        args = []
        for arg in items:
            if arg:
                args.append(arg)
        return tokens[1], args


def op_funcdef_handle(tokens):
    """Processes infix defs."""
    func, base_args = get_infix_items(tokens)
    args = []
    for arg in base_args:
        rstrip_arg = arg.rstrip()
        # if arg has a typedef, it will already have a comma, so don't add one
        if not (rstrip_arg.endswith(",") or rstrip_arg.endswith(unwrapper)):
            arg += ", "
        args.append(arg)
    return func + "(" + "".join(args) + ")"


def lambdef_handle(tokens):
    """Processes lambda calls."""
    if len(tokens) == 0:
        return "lambda:"
    elif len(tokens) == 1:
        return "lambda " + tokens[0] + ":"
    else:
        raise CoconutInternalException("invalid lambda tokens", tokens)


def math_funcdef_suite_handle(original, location, tokens):
    """Processes assignment function definiton suites."""
    if len(tokens) < 1:
        raise CoconutInternalException("invalid assignment function definition suite tokens", tokens)
    else:
        return "\n" + openindent + "".join(tokens[:-1]) + "return " + tokens[-1] + closeindent


def math_funcdef_handle(tokens):
    """Processes assignment function definition."""
    if len(tokens) == 2:
        return tokens[0] + ("" if tokens[1].startswith("\n") else " ") + tokens[1]
    else:
        raise CoconutInternalException("invalid assignment function definition tokens")


def data_handle(tokens):
    """Processes data blocks."""
    if len(tokens) == 2:
        name, stmts = tokens
        attrs = ""
    elif len(tokens) == 3:
        name, attrs, stmts = tokens
    else:
        raise CoconutInternalException("invalid data tokens", tokens)
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
        raise CoconutInternalException("invalid inner data tokens", stmts)
    if rest is not None and rest != "pass\n":
        out += rest
    out += closeindent
    return out


def decorator_handle(tokens):
    """Processes decorators."""
    defs = []
    decorates = []
    for x in range(len(tokens)):
        if "simple" in tokens[x].keys() and len(tokens[x]) == 1:
            decorates.append("@" + tokens[x][0])
        elif "test" in tokens[x].keys() and len(tokens[x]) == 1:
            varname = decorator_var + "_" + str(x)
            defs.append(varname + " = " + tokens[x][0])
            decorates.append("@" + varname)
        else:
            raise CoconutInternalException("invalid decorator tokens", tokens[x])
    return "\n".join(defs + decorates) + "\n"


def else_handle(tokens):
    """Processes compound else statements."""
    if len(tokens) == 1:
        return "\n" + openindent + tokens[0] + closeindent
    else:
        raise CoconutInternalException("invalid compound else statement tokens", tokens)


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
        "star": lambda self: self.match_star,
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
        self.others[-1].set_checks(0, ["not " + match_check_var] + self.others[-1].get_checks(0))
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
            raise CoconutInternalException("invalid match index", position)

    @contextmanager
    def incremented(self, forall=False):
        """Increment then decrement."""
        self.increment(forall)
        yield
        self.decrement(forall)

    def increment(self, forall=False):
        """Advances the if-statement position."""
        self.set_position(self.position + 1)
        if forall:
            for other in self.others:
                other.increment(True)

    def decrement(self, forall=False):
        """Decrements the if-statement position."""
        self.set_position(self.position - 1)
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
            raise CoconutInternalException("invalid dict match tokens", original)
        self.checks.append("_coconut.isinstance(" + item + ", _coconut.abc.Mapping)")
        self.checks.append("_coconut.len(" + item + ") == " + str(len(match)))
        for x in range(len(match)):
            k, v = match[x]
            self.checks.append(k + " in " + item)
            self.match(v, item + "[" + k + "]")

    def match_sequence(self, original, item, typecheck=True):
        """Matches a sequence."""
        tail = None
        if len(original) == 2:
            series_type, match = original
        else:
            series_type, match, tail = original
        if typecheck:
            self.checks.append("_coconut.isinstance(" + item + ", _coconut.abc.Sequence)")
        if tail is None:
            self.checks.append("_coconut.len(" + item + ") == " + str(len(match)))
        else:
            self.checks.append("_coconut.len(" + item + ") >= " + str(len(match)))
            if len(match):
                splice = "[" + str(len(match)) + ":]"
            else:
                splice = ""
            if series_type == "(":
                self.defs.append(tail + " = _coconut.tuple(" + item + splice + ")")
            elif series_type == "[":
                self.defs.append(tail + " = _coconut.list(" + item + splice + ")")
            else:
                raise CoconutInternalException("invalid series match type", series_type)
        for x in range(len(match)):
            self.match(match[x], item + "[" + str(x) + "]")

    def get_iter_var(self):
        """Gets the next match_iter_var."""
        itervar = match_iter_var + "_" + str(self.iter_index)
        self.iter_index += 1
        return itervar

    def match_iterator(self, original, item):
        """Matches an iterator."""
        tail = None
        if len(original) == 2:
            _, match = original
        else:
            _, match, tail = original
        self.checks.append("_coconut.isinstance(" + item + ", _coconut.abc.Iterable)")
        itervar = self.get_iter_var()
        if tail is None:
            self.defs.append(itervar + " = _coconut.tuple(" + item + ")")
        else:
            self.defs.append(tail + " = _coconut.iter(" + item + ")")
            self.defs.append(itervar + " = _coconut.tuple(_coconut_igetitem(" + tail + ", _coconut.slice(None, " + str(len(match)) + ")))")
        with self.incremented():
            self.checks.append("_coconut.len(" + itervar + ") == " + str(len(match)))
            for x in range(len(match)):
                self.match(match[x], itervar + "[" + str(x) + "]")

    def match_star(self, original, item):
        """Matches starred assignment."""
        head_match, last_match = None, None
        if len(original) == 1:
            middle = original[0]
        elif len(original) == 2:
            if isinstance(original[0], str):
                middle, last_match = original
            else:
                head_match, middle = original
        else:
            head_match, middle, last_match = original
        self.checks.append("_coconut.isinstance(" + item + ", _coconut.abc.Iterable)")
        if head_match is None and last_match is None:
            self.defs.append(middle + " = _coconut.list(" + item + ")")
        else:
            itervar = self.get_iter_var()
            self.defs.append(itervar + " = _coconut.list(" + item + ")")
            with self.incremented():
                req_length = (len(head_match) if head_match is not None else 0) + (len(last_match) if last_match is not None else 0)
                self.checks.append("_coconut.len(" + itervar + ") >= " + str(req_length))
                head_splice = str(len(head_match)) if head_match is not None else ""
                last_splice = "-" + str(len(last_match)) if last_match is not None else ""
                self.defs.append(middle + " = " + itervar + "[" + head_splice + ":" + last_splice + "]")
                if head_match is not None:
                    for x in range(len(head_match)):
                        self.match(head_match[x], itervar + "[" + str(x) + "]")
                if last_match is not None:
                    for x in range(1, len(last_match) + 1):
                        self.match(last_match[-x], itervar + "[-" + str(x) + "]")

    def match_rsequence(self, original, item):
        """Matches a reverse sequence."""
        front, series_type, match = original
        self.checks.append("_coconut.isinstance(" + item + ", _coconut.abc.Sequence)")
        self.checks.append("_coconut.len(" + item + ") >= " + str(len(match)))
        if len(match):
            splice = "[:" + str(-len(match)) + "]"
        else:
            splice = ""
        if series_type == "(":
            self.defs.append(front + " = _coconut.tuple(" + item + splice + ")")
        elif series_type == "[":
            self.defs.append(front + " = _coconut.list(" + item + splice + ")")
        else:
            raise CoconutInternalException("invalid series match type", series_type)
        for x in range(len(match)):
            self.match(match[x], item + "[" + str(x - len(match)) + "]")

    def match_msequence(self, original, item):
        """Matches a middle sequence."""
        series_type, head_match, middle, _, last_match = original
        self.checks.append("_coconut.isinstance(" + item + ", _coconut.abc.Sequence)")
        self.checks.append("_coconut.len(" + item + ") >= " + str(len(head_match) + len(last_match)))
        if len(head_match) and len(last_match):
            splice = "[" + str(len(head_match)) + ":" + str(-len(last_match)) + "]"
        elif len(head_match):
            splice = "[" + str(len(head_match)) + ":]"
        elif len(last_match):
            splice = "[:" + str(-len(last_match)) + "]"
        else:
            splice = ""
        if series_type == "(":
            self.defs.append(middle + " = _coconut.tuple(" + item + splice + ")")
        elif series_type == "[":
            self.defs.append(middle + " = _coconut.list(" + item + splice + ")")
        else:
            raise CoconutInternalException("invalid series match type", series_type)
        for x in range(len(head_match)):
            self.match(head_match[x], item + "[" + str(x) + "]")
        for x in range(len(last_match)):
            self.match(last_match[x], item + "[" + str(x - len(last_match)) + "]")

    def match_const(self, original, item):
        """Matches a constant."""
        (match,) = original
        if match in const_vars:
            self.checks.append(item + " is " + match)
        else:
            self.checks.append(item + " == " + match)

    def match_var(self, original, item):
        """Matches a variable."""
        (setvar,) = original
        if setvar != wildcard:
            if setvar in self.names:
                self.checks.append(self.names[setvar] + " == " + item)
            else:
                self.defs.append(setvar + " = " + item)
                self.names[setvar] = item

    def match_set(self, original, item):
        """Matches a set."""
        if len(original) == 1:
            match = original[0]
        else:
            raise CoconutInternalException("invalid set match tokens", original)
        self.checks.append("_coconut.isinstance(" + item + ", _coconut.abc.Set)")
        self.checks.append("_coconut.len(" + item + ") == " + str(len(match)))
        for const in match:
            self.checks.append(const + " in " + item)

    def match_data(self, original, item):
        """Matches a data type."""
        data_type, match = original
        self.checks.append("_coconut.isinstance(" + item + ", " + data_type + ")")
        self.checks.append("_coconut.len(" + item + ") == " + str(len(match)))
        for x in range(len(match)):
            self.match(match[x], item + "[" + str(x) + "]")

    def match_paren(self, original, item):
        """Matches a paren."""
        (match,) = original
        self.match(match, item)

    def match_trailer(self, original, item):
        """Matches typedefs and as patterns."""
        if len(original) <= 1 or len(original) % 2 != 1:
            raise CoconutInternalException("invalid trailer match tokens", original)
        else:
            match, trailers = original[0], original[1:]
            for i in range(0, len(trailers), 2):
                op, arg = trailers[i], trailers[i + 1]
                if op == "is":
                    self.checks.append("_coconut.isinstance(" + item + ", " + arg + ")")
                elif op == "as":
                    if arg in self.names:
                        self.checks.append(self.names[arg] + " == " + item)
                    elif arg != wildcard:
                        self.defs.append(arg + " = " + item)
                        self.names[arg] = item
                else:
                    raise CoconutInternalException("invalid trailer match operation", op)
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
        for flag, get_handler in self.matchers.items():
            if flag in original.keys():
                return get_handler(self)(original, item)
        raise CoconutInternalException("invalid inner match tokens", original)

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
        raise CoconutInternalException("invalid outer match tokens", tokens)
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
        out += "if " + match_check_var + ":" + "\n" + openindent + "".join(stmts) + closeindent
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
        raise CoconutInternalException("invalid case match tokens", tokens)


def case_handle(o, l, tokens):
    """Processes case blocks."""
    if len(tokens) == 2:
        item, cases = tokens
        default = None
    elif len(tokens) == 3:
        item, cases, default = tokens
    else:
        raise CoconutInternalException("invalid top-level case tokens", tokens)
    out = match_handle(o, l, case_to_match(cases[0], item))
    for case in cases[1:]:
        out += ("if not " + match_check_var + ":\n" + openindent
                + match_handle(o, l, case_to_match(case, item), top=False) + closeindent)
    if default is not None:
        out += "if not " + match_check_var + default
    return out


def except_handle(tokens):
    """Processes except statements."""
    if len(tokens) == 1:
        errs, asname = tokens[0], None
    elif len(tokens) == 2:
        errs, asname = tokens
    else:
        raise CoconutInternalException("invalid except tokens", tokens)
    out = "except "
    if "list" in tokens.keys():
        out += "(" + errs + ")"
    else:
        out += errs
    if asname is not None:
        out += " as " + asname
    return out


def subscriptgroup_handle(tokens):
    """Processes subscriptgroups."""
    if 0 < len(tokens) <= 3:
        args = []
        for x in range(len(tokens)):
            arg = tokens[x]
            if not arg:
                arg = "None"
            args.append(arg)
        if len(args) == 1:
            return args[0]
        else:
            return "_coconut.slice(" + ", ".join(args) + ")"
    else:
        raise CoconutInternalException("invalid slice args", tokens)


def itemgetter_handle(tokens):
    """Processes implicit itemgetter partials."""
    if len(tokens) != 2:
        raise CoconutInternalException("invalid implicit itemgetter args", tokens)
    else:
        op, args = tokens
        if op == "[":
            return "_coconut.operator.itemgetter(" + args + ")"
        elif op == "$[":
            return "_coconut.functools.partial(_coconut_igetitem, index=" + args + ")"
        else:
            raise CoconutInternalException("invalid implicit itemgetter type", op)


def class_suite_handle(tokens):
    """Processes implicit pass in class suite."""
    if len(tokens) != 1:
        raise CoconutInternalException("invalid implicit pass in class suite tokens", tokens)
    else:
        return ": pass" + tokens[0]


def namelist_handle(tokens):
    """Handles inline nonlocal and global statements."""
    if len(tokens) == 1:
        return tokens[0]
    elif len(tokens) == 2:
        return tokens[0] + "\n" + tokens[0] + " = " + tokens[1]
    else:
        raise CoconutInternalException("invalid in-line nonlocal / global tokens", tokens)


def compose_item_handle(tokens):
    """Handles function composition."""
    if len(tokens) < 1:
        raise CoconutInternalException("invalid function composition tokens", tokens)
    elif len(tokens) == 1:
        return tokens[0]
    else:
        return "_coconut_compose(" + ", ".join(tokens) + ")"


def make_suite_handle(tokens):
    """Makes simple statements into suites.
    Necessary because multiline lambdas count on every statement having its own line to work."""
    if len(tokens) != 1:
        raise CoconutInternalException("invalid simple suite tokens", tokens)
    else:
        return "\n" + openindent + tokens[0] + closeindent


def tco_return_handle(tokens):
    """Handles tail-call-optimizable return statements."""
    if len(tokens) != 2:
        raise CoconutInternalException("invalid tail-call-optimizable return statement tokens", tokens)
    elif tokens[1].startswith("()"):
        return "raise _coconut_tail_call(" + tokens[0] + ")" + tokens[1][2:]  # tokens[1] contains \n
    else:
        return "raise _coconut_tail_call(" + tokens[0] + ", " + tokens[1][1:]  # tokens[1] contains )\n


def split_func_name_args_params_handle(tokens):
    """Handles splitting a function into name, params, and args."""
    if len(tokens) != 2:
        raise CoconutInternalException("invalid function definition splitting tokens", tokens)
    else:
        func_name = tokens[0]
        func_args = []
        func_params = []
        for arg in tokens[1]:
            if len(arg) > 1 and arg[0] in ("*", "**"):
                func_args.append(arg[1])
            elif arg[0] != "*":
                func_args.append(arg[0])
            func_params.append("".join(arg))
        return [
            func_name,
            ", ".join(func_args),
            "(" + ", ".join(func_params) + ")"
        ]

# end: HANDLERS
#-----------------------------------------------------------------------------------------------------------------------
# MAIN GRAMMAR:
#-----------------------------------------------------------------------------------------------------------------------


class Grammar(object):
    """Contains Coconut grammar definitions."""

    comma = Literal(",")
    dubstar = Literal("**")
    star = ~dubstar + Literal("*")
    at = Literal("@")
    arrow = Literal("->") | fixto(Literal("\u2192"), "->")
    dubcolon = Literal("::")
    unsafe_colon = Literal(":")
    colon = ~dubcolon + unsafe_colon
    semicolon = Literal(";")
    eq = Literal("==")
    equals = ~eq + Literal("=")
    lbrack = Literal("[")
    rbrack = Literal("]")
    lbrace = Literal("{")
    rbrace = Literal("}")
    lbanana = ~Literal("(|)") + ~Literal("(|>)") + ~Literal("(|*>)") + Literal("(|")
    rbanana = Literal("|)")
    lparen = ~lbanana + Literal("(")
    rparen = ~rbanana + Literal(")")
    unsafe_dot = Literal(".")
    dot = ~Literal("..") + unsafe_dot
    plus = Literal("+")
    minus = ~Literal("->") + Literal("-")
    dubslash = Literal("//")
    slash = ~dubslash + Literal("/")
    pipeline = Literal("|>") | fixto(Literal("\u21a6"), "|>")
    starpipe = Literal("|*>") | fixto(Literal("*\u21a6"), "|*>")
    backpipe = Literal("<|") | fixto(Literal("\u21a4"), "<|")
    backstarpipe = Literal("<*|") | fixto(Literal("\u21a4*"), "<*|")
    amp = Literal("&") | fixto(Literal("\u2227") | Literal("\u2229"), "&")
    caret = Literal("^") | fixto(Literal("\u22bb") | Literal("\u2295"), "^")
    bar = ~Literal("|>") + ~Literal("|*>") + Literal("|") | fixto(Literal("\u2228") | Literal("\u222a"), "|")
    percent = Literal("%")
    dotdot = ~Literal("...") + Literal("..") | fixto(Literal("\u2218"), "..")
    dollar = Literal("$")
    ellipses = fixto(Literal("...") | Literal("\u2026"), "...")
    lshift = Literal("<<") | fixto(Literal("\xab"), "<<")
    rshift = Literal(">>") | fixto(Literal("\xbb"), ">>")
    tilde = Literal("~") | fixto(~Literal("\xac=") + Literal("\xac"), "~")
    underscore = Literal("_")
    pound = Literal("#")
    backtick = Literal("`")
    dubbackslash = Literal("\\\\")
    backslash = ~dubbackslash + Literal("\\")

    lt = ~Literal("<<") + ~Literal("<=") + Literal("<")
    gt = ~Literal(">>") + ~Literal(">=") + Literal(">")
    le = Literal("<=") | fixto(Literal("\u2264"), "<=")
    ge = Literal(">=") | fixto(Literal("\u2265"), ">=")
    ne = Literal("!=") | fixto(Literal("\xac=") | Literal("\u2260"), "!=")

    mul_star = fixto(star | Literal("\u22c5"), "*")
    exp_dubstar = fixto(dubstar | Literal("\u2191"), "**")
    neg_minus = fixto(minus | Literal("\u207b"), "-")
    sub_minus = fixto(minus | Literal("\u2212"), "-")
    div_slash = fixto(slash | Literal("\xf7") + ~slash, "/")
    div_dubslash = fixto(dubslash | Combine(Literal("\xf7") + slash), "//")
    matrix_at_ref = fixto(at | Literal("\xd7"), "@")
    matrix_at = Forward()

    name = Forward()
    base_name = Regex(r"\b(?![0-9])\w+\b", re.U)
    for k in keywords + const_vars:
        base_name = ~Keyword(k) + base_name
    for k in reserved_vars:
        base_name |= backslash.suppress() + Keyword(k)
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
    passthrough_block = Combine(fixto(dubbackslash, "\\") + integer + unwrap)

    endline = Forward()
    endline_ref = condense(OneOrMore(Literal("\n")))
    lineitem = Combine(Optional(comment) + endline)
    newline = condense(OneOrMore(lineitem))
    start_marker = StringStart()
    moduledoc_marker = condense(ZeroOrMore(lineitem) - Optional(moduledoc_item))
    end_marker = StringEnd()
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
    docstring = condense(moduledoc)

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
    no_chain_expr = Forward()
    star_expr = Forward()
    dubstar_expr = Forward()
    comp_for = Forward()
    test_no_chain = Forward()
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
        fixto(pipeline, "_coconut_pipe")
        | fixto(starpipe, "_coconut_starpipe")
        | fixto(backpipe, "_coconut_backpipe")
        | fixto(backstarpipe, "_coconut_backstarpipe")
        | fixto(dotdot, "_coconut_compose")
        | fixto(Keyword("and"), "_coconut_bool_and")
        | fixto(Keyword("or"), "_coconut_bool_or")
        | fixto(minus, "_coconut_minus")
        | fixto(dot, "_coconut.getattr")
        | fixto(dubcolon, "_coconut.itertools.chain")
        | fixto(dollar, "_coconut.functools.partial")
        | fixto(exp_dubstar, "_coconut.operator.pow")
        | fixto(mul_star, "_coconut.operator.mul")
        | fixto(div_dubslash, "_coconut.operator.floordiv")
        | fixto(div_slash, "_coconut.operator.truediv")
        | fixto(percent, "_coconut.operator.mod")
        | fixto(plus, "_coconut.operator.add")
        | fixto(amp, "_coconut.operator.and_")
        | fixto(caret, "_coconut.operator.xor")
        | fixto(bar, "_coconut.operator.or_")
        | fixto(lshift, "_coconut.operator.lshift")
        | fixto(rshift, "_coconut.operator.rshift")
        | fixto(lt, "_coconut.operator.lt")
        | fixto(gt, "_coconut.operator.gt")
        | fixto(eq, "_coconut.operator.eq")
        | fixto(le, "_coconut.operator.le")
        | fixto(ge, "_coconut.operator.ge")
        | fixto(ne, "_coconut.operator.ne")
        | fixto(tilde, "_coconut.operator.inv")
        | fixto(matrix_at, "_coconut.operator.matmul")
        | fixto(Keyword("not"), "_coconut.operator.not_")
        | fixto(Keyword("is"), "_coconut.operator.is_")
        | fixto(Keyword("in"), "_coconut.operator.contains")
    )

    typedef = Forward()
    typedef_default = Forward()
    default = condense(equals + test)
    typedef_ref = name + colon.suppress() + test
    typedef_default_ref = typedef_ref + Optional(default)
    arg_comma = comma | FollowedBy(rparen)
    tfpdef = typedef + arg_comma.suppress() | condense(name + arg_comma)
    tfpdef_default = typedef_default + arg_comma.suppress() | condense(name + Optional(default) + arg_comma)

    argslist = trace(addspace(ZeroOrMore(condense(
        dubstar + tfpdef
        | star + (tfpdef | arg_comma)
        | tfpdef_default
    ))), "argslist")
    varargslist = trace(Optional(itemlist(condense(
        dubstar + name
        | star + Optional(name)
        | name + Optional(default)
    ), comma)), "varargslist")
    parameters = condense(lparen + argslist + rparen)

    function_call = Forward()
    function_call_tokens = lparen.suppress() + Optional(
        Group(attach(addspace(test + comp_for), add_paren_handle))
        | tokenlist(Group(dubstar + test | star + test | name + default | test), comma)
        | Group(op_item)
    ) + rparen.suppress()
    methodcaller_args = (
        itemlist(condense(name + default | test), comma)
        | op_item
    )

    slicetest = Optional(test_no_chain)
    sliceop = condense(unsafe_colon + slicetest)
    subscript = condense(slicetest + sliceop + Optional(sliceop)) | test
    subscriptlist = itemlist(subscript, comma)

    slicetestgroup = Optional(test_no_chain, default="")
    sliceopgroup = unsafe_colon.suppress() + slicetestgroup
    subscriptgroup = attach(slicetestgroup + sliceopgroup + Optional(sliceopgroup) | test, subscriptgroup_handle)

    testlist_comp = addspace((test | star_expr) + comp_for) | testlist_star_expr
    list_comp = condense(lbrack + Optional(testlist_comp) + rbrack)
    func_atom = (
        name
        | condense(lparen + Optional(yield_expr | testlist_comp) + rparen)
        | lparen.suppress() + op_item + rparen.suppress()
    )
    keyword_atom = Keyword(const_vars[0])
    for x in range(1, len(const_vars)):
        keyword_atom |= Keyword(const_vars[x])
    string_atom = addspace(OneOrMore(string))
    passthrough_atom = trace(addspace(OneOrMore(passthrough)), "passthrough_atom")
    attr_atom = attach(
        dot.suppress() + name
        + Optional(
            lparen + Optional(methodcaller_args) + rparen.suppress()
        ), attr_handle)
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
        | lazy_list, "known_atom")
    atom = (
        known_atom
        | passthrough_atom
        | func_atom
    )

    simple_trailer = (
        condense(lbrack + subscriptlist + rbrack)
        | condense(dot + name)
    )
    partial_trailer = Group(fixto(dollar, "$(") + function_call)
    partial_trailer_tokens = Group(dollar.suppress() + function_call_tokens)
    complex_trailer_no_partial = (
        condense(function_call)
        | Group(condense(dollar + lbrack) + subscriptgroup + rbrack.suppress())
        | Group(condense(dollar + lbrack + rbrack))
        | Group(dollar + ~lparen + ~lbrack)
        | Group(condense(lbrack + rbrack))
        | Group(dot + ~name + ~lbrack)
    )
    complex_trailer = partial_trailer | complex_trailer_no_partial
    trailer = simple_trailer | complex_trailer

    atom_item = Forward()
    atom_item_ref = atom + ZeroOrMore(trailer)
    no_partial_atom_item = Forward()
    no_partial_atom_item_ref = atom + ZeroOrMore(complex_trailer_no_partial)
    simple_assign = Forward()
    simple_assign_ref = (name | passthrough_atom) + ZeroOrMore(ZeroOrMore(complex_trailer) + OneOrMore(simple_trailer))
    simple_assignlist = parenwrap(lparen, itemlist(simple_assign, comma), rparen)

    assignlist = Forward()
    star_assign_item = Forward()
    base_assign_item = condense(simple_assign | lparen + assignlist + rparen | lbrack + assignlist + rbrack)
    star_assign_item_ref = condense(star + base_assign_item)
    assign_item = star_assign_item | base_assign_item
    assignlist <<= trace(itemlist(assign_item, comma), "assignlist")

    augassign_stmt = Forward()
    augassign_stmt_ref = simple_assign + augassign + test_expr
    assign_stmt = trace(addspace(ZeroOrMore(assignlist + equals) + test_expr), "assign_stmt")

    compose_item = attach(atom_item + ZeroOrMore(dotdot.suppress() + atom_item), compose_item_handle)

    factor = Forward()
    await_keyword = Forward()
    await_keyword_ref = Keyword("await")
    power = trace(condense(addspace(Optional(await_keyword) + compose_item) + Optional(exp_dubstar + factor)), "power")
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
    no_chain_infix_expr = Forward()
    no_chain_infix_item = attach(Group(Optional(or_expr)) + infix_op + Group(Optional(no_chain_infix_expr)), infix_handle)
    no_chain_infix_expr <<= no_chain_infix_item | or_expr

    pipe_op = pipeline | starpipe | backpipe | backstarpipe
    pipe_expr = Forward()
    pipe_item = Group(no_partial_atom_item + partial_trailer_tokens) + pipe_op | Group(infix_expr) + pipe_op
    last_pipe_item = Group(longest(no_partial_atom_item + partial_trailer_tokens, infix_expr))
    pipe_expr_ref = OneOrMore(pipe_item) + last_pipe_item
    expr <<= infix_expr + ~pipe_op | pipe_expr
    no_chain_pipe_expr = Forward()
    no_chain_pipe_item = Group(no_partial_atom_item + partial_trailer_tokens) + pipe_op | Group(no_chain_infix_expr) + pipe_op
    no_chain_last_pipe_item = Group(longest(no_partial_atom_item + partial_trailer_tokens, no_chain_infix_expr))
    no_chain_pipe_expr_ref = OneOrMore(no_chain_pipe_item) + no_chain_last_pipe_item
    no_chain_expr <<= no_chain_infix_expr + ~pipe_op | no_chain_pipe_expr

    star_expr_ref = condense(star + expr)
    dubstar_expr_ref = condense(dubstar + expr)
    comparison = addspace(expr + ZeroOrMore(comp_op + expr))
    not_test = addspace(ZeroOrMore(Keyword("not")) + comparison)
    and_test = addspace(not_test + ZeroOrMore(Keyword("and") + not_test))
    or_test = addspace(and_test + ZeroOrMore(Keyword("or") + and_test))
    test_item = trace(or_test, "test_item")
    no_chain_comparison = addspace(no_chain_expr + ZeroOrMore(comp_op + no_chain_expr))
    no_chain_not_test = addspace(ZeroOrMore(Keyword("not")) + no_chain_comparison)
    no_chain_and_test = addspace(no_chain_not_test + ZeroOrMore(Keyword("and") + no_chain_not_test))
    no_chain_or_test = addspace(no_chain_and_test + ZeroOrMore(Keyword("or") + no_chain_and_test))
    no_chain_test_item = trace(no_chain_or_test, "no_chain_test_item")

    small_stmt = Forward()
    simple_stmt = Forward()
    simple_compound_stmt = Forward()
    stmt = Forward()
    suite = Forward()
    nocolon_suite = Forward()
    base_suite = Forward()
    classlist = Forward()

    classic_lambdef = Forward()
    classic_lambdef_params = parenwrap(lparen, varargslist, rparen)
    new_lambdef_params = lparen.suppress() + varargslist + rparen.suppress() | name
    classic_lambdef_ref = addspace(Keyword("lambda") + condense(classic_lambdef_params + colon))
    new_lambdef = attach(new_lambdef_params + arrow.suppress(), lambdef_handle)
    implicit_lambdef = fixto(arrow, "lambda _=None:")
    lambdef_base = classic_lambdef | new_lambdef | implicit_lambdef

    match = Forward()
    matchlist_list = Forward()
    match_guard = Optional(Keyword("if").suppress() + test)

    stmt_lambdef = Forward()
    closing_stmt = longest(testlist("tests"), small_stmt)
    stmt_lambdef_params = Optional(
        attach(name, add_paren_handle)
        | parameters
        | Group(lparen.suppress() + matchlist_list + match_guard + rparen.suppress()),
        default="(_=None)")
    stmt_lambdef_ref = (
        Keyword("def").suppress() + stmt_lambdef_params + arrow.suppress()
        + (
            Group(OneOrMore(small_stmt + semicolon.suppress())) + Optional(closing_stmt)
            | Group(ZeroOrMore(small_stmt + semicolon.suppress())) + closing_stmt
        )
    )

    lambdef = trace(addspace(lambdef_base + test) | stmt_lambdef, "lambdef")
    lambdef_nocond = trace(addspace(lambdef_base + test_nocond), "lambdef_nocond")
    lambdef_no_chain = trace(addspace(lambdef_base + test_no_chain), "lambdef_no_chain")

    test <<= trace(lambdef | addspace(test_item + Optional(Keyword("if") + test_item + Keyword("else") + test)), "test")
    test_nocond <<= trace(lambdef_nocond | test_item, "test_nocond")
    test_no_chain <<= trace(
        lambdef_no_chain
        | addspace(
            no_chain_test_item + Optional(Keyword("if") + no_chain_test_item + Keyword("else") + test_no_chain)
        ), "test_no_chain")

    classlist_ref = Optional(
        lparen.suppress() + rparen.suppress()
        | Group(
            condense(lparen + testlist + rparen)("tests")
            | function_call("args")
        )
    )
    class_suite = suite | attach(newline, class_suite_handle)
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
        - Optional(equals.suppress() - test_expr), namelist_handle)
    global_stmt = addspace(Keyword("global") - namelist)
    nonlocal_stmt_ref = addspace(Keyword("nonlocal") - namelist)
    del_stmt = addspace(Keyword("del") - simple_assignlist)
    with_item = addspace(test - Optional(Keyword("as") - name))
    with_item_list = parenwrap(lparen, condense(itemlist(with_item, comma)), rparen)

    matchlist_list <<= Group(Optional(tokenlist(match, comma)))
    matchlist_tuple = Group(Optional(
        match + OneOrMore(comma.suppress() + match) + Optional(comma.suppress())
        | match + comma.suppress())
    )
    matchlist_star = (
        Optional(Group(OneOrMore(match + comma.suppress())))
        + star.suppress() + name
        + Optional(Group(OneOrMore(comma.suppress() + match)))
        + Optional(comma.suppress())
    )

    match_const = const_atom | condense(equals.suppress() + atom_item)
    matchlist_set = Group(Optional(tokenlist(match_const, comma)))
    match_pair = Group(match_const + colon.suppress() + match)
    matchlist_dict = Group(Optional(tokenlist(match_pair, comma)))
    match_list = lbrack + matchlist_list + rbrack.suppress()
    match_tuple = lparen + matchlist_tuple + rparen.suppress()
    match_lazy = lbanana + matchlist_list + rbanana.suppress()
    series_match = (
        (match_list + plus.suppress() + name + plus.suppress() + match_list)("mseries")
        | (match_tuple + plus.suppress() + name + plus.suppress() + match_tuple)("mseries")
        | ((match_list | match_tuple) + Optional(plus.suppress() + name))("series")
        | (name + plus.suppress() + (match_list | match_tuple))("rseries")
    )
    iter_match = (
        ((match_list | match_tuple | match_lazy) + dubcolon.suppress() + name)
        | match_lazy
    )("iter")
    star_match = (
        lbrack.suppress() + matchlist_star + rbrack.suppress()
        | lparen.suppress() + matchlist_star + rparen.suppress()
    )("star")
    base_match = trace(Group(
        match_const("const")
        | (lparen.suppress() + match + rparen.suppress())("paren")
        | (lbrace.suppress() + matchlist_dict + rbrace.suppress())("dict")
        | (Optional(set_s.suppress()) + lbrace.suppress() + matchlist_set + rbrace.suppress())("set")
        | iter_match
        | series_match
        | star_match
        | (name + lparen.suppress() + matchlist_list + rparen.suppress())("data")
        | name("var")
    ), "base_match")
    matchlist_trailer = base_match + OneOrMore(Keyword("as") + name | Keyword("is") + atom_item)
    as_match = Group(matchlist_trailer("trailer")) | base_match
    matchlist_and = as_match + OneOrMore(Keyword("and").suppress() + as_match)
    and_match = Group(matchlist_and("and")) | as_match
    matchlist_or = and_match + OneOrMore(Keyword("or").suppress() + and_match)
    or_match = Group(matchlist_or("or")) | and_match
    match <<= trace(or_match, "match")

    else_suite = condense(colon + trace(attach(simple_compound_stmt, else_handle), "else_suite")) | suite
    else_stmt = condense(Keyword("else") - else_suite)

    full_suite = colon.suppress() + Group((newline.suppress() + indent.suppress() + OneOrMore(stmt) + dedent.suppress()) | simple_stmt)
    full_match = trace(attach(
        Keyword("match").suppress() + match + Keyword("in").suppress() - test - match_guard - full_suite, match_handle), "full_match")
    match_stmt = condense(full_match - Optional(else_stmt))

    destructuring_stmt = Forward()
    destructuring_stmt_ref = Optional(Keyword("match").suppress()) + match + equals.suppress() + test_expr

    case_match = trace(Group(
        Keyword("match").suppress() - match - Optional(Keyword("if").suppress() - test) - full_suite
    ), "case_match")
    case_stmt = attach(
        Keyword("case").suppress() + test - colon.suppress() - newline.suppress()
        - indent.suppress() - Group(OneOrMore(case_match))
        - dedent.suppress() - Optional(Keyword("else").suppress() - else_suite), case_handle)

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
    async_stmt = Forward()
    name_funcdef = trace(condense(name + parameters), "name_funcdef")
    op_tfpdef = typedef_default | condense(name + Optional(default))
    op_funcdef_arg = name | condense(lparen.suppress() + op_tfpdef + rparen.suppress())
    op_funcdef_name = backtick.suppress() + name + backtick.suppress()
    op_funcdef = trace(attach(
        Group(Optional(op_funcdef_arg))
        + op_funcdef_name
        + Group(Optional(op_funcdef_arg)),
        op_funcdef_handle), "op_funcdef")
    return_typedef_ref = addspace(arrow + test)
    end_func_colon = return_typedef + colon.suppress() | colon
    base_funcdef = op_funcdef | name_funcdef
    funcdef = trace(addspace(Keyword("def") + condense(base_funcdef + end_func_colon + nocolon_suite)), "funcdef")

    name_match_funcdef = Forward()
    op_match_funcdef = Forward()
    async_match_funcdef = Forward()
    name_match_funcdef_ref = name + lparen.suppress() + matchlist_list + match_guard + rparen.suppress()
    op_match_funcdef_arg = lparen.suppress() + match + rparen.suppress()
    op_match_funcdef_ref = Group(Optional(op_match_funcdef_arg)) + op_funcdef_name + Group(Optional(op_match_funcdef_arg)) + match_guard
    base_match_funcdef = trace(Keyword("def").suppress() + (op_match_funcdef | name_match_funcdef), "base_match_funcdef")
    def_match_funcdef = trace(condense(base_match_funcdef + colon.suppress() + nocolon_suite), "def_match_funcdef")
    match_funcdef = Optional(Keyword("match").suppress()) + def_match_funcdef

    testlist_stmt = condense(testlist + newline)
    math_funcdef_suite = attach(
        testlist_stmt
        | (newline - indent).suppress() - ZeroOrMore(~(testlist_stmt + dedent) + stmt) - testlist_stmt - dedent.suppress(),
        math_funcdef_suite_handle)
    end_func_equals = return_typedef + equals.suppress() | fixto(equals, ":")
    math_funcdef = trace(attach(
        condense(addspace(Keyword("def") + base_funcdef) + end_func_equals) - math_funcdef_suite, math_funcdef_handle), "math_funcdef")
    math_match_funcdef = trace(
        Optional(Keyword("match").suppress()) + condense(base_match_funcdef + equals.suppress() - math_funcdef_suite), "math_match_funcdef")

    async_funcdef_ref = addspace(Keyword("async") + (funcdef | math_funcdef))
    async_stmt_ref = addspace(Keyword("async") + (with_stmt | for_stmt))
    async_match_funcdef_ref = addspace(
        (
            Optional(Keyword("match")).suppress() + Keyword("async")
            | Keyword("async") + Optional(Keyword("match")).suppress()
        )
        + (def_match_funcdef | math_match_funcdef)
    )

    data_args = Optional(lparen.suppress() + Optional(itemlist(~underscore + name, comma)) + rparen.suppress())
    data_suite = Group(colon.suppress() - (
        (newline.suppress() + indent.suppress() + Optional(docstring) + Group(OneOrMore(stmt)) + dedent.suppress())("complex")
        | (newline.suppress() + indent.suppress() + docstring + dedent.suppress() | docstring)("docstring")
        | simple_stmt("simple")
    ) | newline("empty"))
    datadef = condense(attach(Keyword("data").suppress() + name - data_args - data_suite, data_handle))

    simple_decorator = condense(dotted_name + Optional(function_call))("simple")
    complex_decorator = test("test")
    decorators = attach(OneOrMore(at.suppress() - Group(longest(simple_decorator, complex_decorator)) - newline.suppress()), decorator_handle)

    decoratable_normal_funcdef_stmt = Forward()
    normal_funcdef_stmt = (
        funcdef
        | math_funcdef
        | math_match_funcdef
        | match_funcdef
    )
    decoratable_normal_funcdef_stmt_ref = Optional(decorators) + normal_funcdef_stmt

    async_funcdef_stmt = async_funcdef | async_match_funcdef
    decoratable_async_funcdef_stmt = trace(condense(Optional(decorators) + async_funcdef_stmt), "decoratable_async_func_stmt")

    decoratable_func_stmt = decoratable_normal_funcdef_stmt | decoratable_async_funcdef_stmt

    class_stmt = classdef | datadef
    decoratable_class_stmt = trace(condense(Optional(decorators) + class_stmt), "decoratable_class_stmt")

    passthrough_stmt = condense(passthrough_block - (base_suite | newline))

    simple_compound_stmt <<= trace(
        if_stmt
        | try_stmt
        | case_stmt
        | match_stmt
        | passthrough_stmt, "simple_compound_stmt")
    compound_stmt = trace(
        decoratable_class_stmt
        | decoratable_func_stmt
        | with_stmt
        | while_stmt
        | for_stmt
        | async_stmt
        | simple_compound_stmt, "compound_stmt")
    endline_semicolon = Forward()
    endline_semicolon_ref = semicolon.suppress() + newline
    keyword_stmt = trace(
        del_stmt
        | pass_stmt
        | flow_stmt
        | import_stmt
        | global_stmt
        | nonlocal_stmt
        | assert_stmt
        | exec_stmt, "keyword_stmt")
    small_stmt <<= trace(
        keyword_stmt
        | augassign_stmt
        | longest(assign_stmt, destructuring_stmt), "small_stmt")
    simple_stmt <<= trace(condense(
        small_stmt
        + ZeroOrMore(fixto(semicolon, "\n") + small_stmt)
        + (newline | endline_semicolon)
    ), "simple_stmt")
    stmt <<= trace(compound_stmt | simple_stmt, "stmt")
    base_suite <<= condense(newline + indent - OneOrMore(stmt) - dedent)
    nocolon_suite <<= trace(base_suite | attach(simple_stmt, make_suite_handle), "nocolon_suite")
    suite <<= condense(colon + nocolon_suite)
    line = trace(newline | stmt, "line")

    single_input = trace(condense(Optional(line) - ZeroOrMore(newline)), "single_input")
    file_input = trace(condense(moduledoc_marker - ZeroOrMore(line)), "file_input")
    eval_input = trace(condense(testlist - ZeroOrMore(newline)), "eval_input")

    single_parser = condense(start_marker - single_input - end_marker)
    file_parser = condense(start_marker - file_input - end_marker)
    eval_parser = condense(start_marker - eval_input - end_marker)

# end: MAIN GRAMMAR
#-----------------------------------------------------------------------------------------------------------------------
# EXTRA GRAMMAR:
#-----------------------------------------------------------------------------------------------------------------------

    parens = originalTextFor(nestedExpr("(", ")"))
    brackets = originalTextFor(nestedExpr("[", "]"))
    braces = originalTextFor(nestedExpr("{", "}"))

    tco_return = attach(
        Keyword("return").suppress() + condense(
            (base_name | parens | brackets | braces | string)
            + ZeroOrMore(dot + base_name | brackets)
        ) + parens + end_marker, tco_return_handle)

    rest_of_arg = SkipTo(comma | rparen)
    tfpdef_tokens = base_name + Optional(originalTextFor(colon + rest_of_arg))
    tfpdef_default_tokens = base_name + Optional(originalTextFor((equals | colon) + rest_of_arg))
    parameters_tokens = Group(Optional(tokenlist(Group(
        dubstar + tfpdef_tokens
        | star + Optional(tfpdef_tokens)
        | tfpdef_default_tokens
    ), comma + Optional(passthrough))))

    split_func_name_args_params = attach(
        (start_marker + Keyword("def")).suppress() + base_name + lparen.suppress()
        + parameters_tokens + rparen.suppress(), split_func_name_args_params_handle)

# end: EXTRA GRAMMAR
