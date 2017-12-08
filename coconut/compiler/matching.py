#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Handles Coconut pattern-matching.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

from contextlib import contextmanager

from coconut.exceptions import (
    CoconutInternalException,
    CoconutDeferredSyntaxError,
    internal_assert,
)
from coconut.constants import (
    match_temp_var,
    wildcard,
    openindent,
    closeindent,
    match_check_var,
    const_vars,
    sentinel_var,
)
from coconut.compiler.util import paren_join

#-----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------


def get_match_names(match):
    """Gets keyword names for the given match."""
    names = []
    if "paren" in match:
        (match,) = match
        names += get_match_names(match)
    elif "var" in match:
        (setvar,) = match
        if setvar != wildcard:
            names.append(setvar)
    elif "trailer" in match:
        match, trailers = match[0], match[1:]
        for i in range(0, len(trailers), 2):
            op, arg = trailers[i], trailers[i + 1]
            if op == "as":
                names.append(arg)
        names += get_match_names(match)
    return names


#-----------------------------------------------------------------------------------------------------------------------
# MATCHER:
#-----------------------------------------------------------------------------------------------------------------------


class Matcher(object):
    """Pattern-matching processor."""
    matchers = {
        "dict": lambda self: self.match_dict,
        "iter": lambda self: self.match_iterator,
        "series": lambda self: self.match_sequence,
        "rseries": lambda self: self.match_rsequence,
        "mseries": lambda self: self.match_msequence,
        "string": lambda self: self.match_string,
        "rstring": lambda self: self.match_rstring,
        "mstring": lambda self: self.match_mstring,
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
        "loc",
        "position",
        "checkdefs",
        "names",
        "var_index",
        "others",
        "guards",
        "use_sentinel",
    )

    def __init__(self, loc, checkdefs=None, names=None, var_index=0):
        """Creates the matcher."""
        self.loc = loc
        self.position = 0
        self.checkdefs = []
        if checkdefs is None:
            self.increment()
        else:
            for checks, defs in checkdefs:
                self.checkdefs.append((checks[:], defs[:]))
            self.set_position(-1)
        self.names = names if names is not None else {}
        self.var_index = var_index
        self.others = []
        self.guards = []
        self.use_sentinel = False

    def duplicate(self):
        """Duplicates the matcher to others."""
        other = Matcher(self.loc, self.checkdefs, self.names, self.var_index)
        other.insert_check(0, "not " + match_check_var)
        self.others.append(other)
        return other

    def add_guard(self, cond):
        """Adds cond as a guard."""
        self.guards.append(cond)

    def get_checks(self, position=None):
        """Gets the checks at the position."""
        if position is None:
            position = self.position
        return self.checkdefs[position][0]

    def set_checks(self, checks, position=None):
        """Sets the checks at the position."""
        if position is None:
            position = self.position
        self.checkdefs[position][0] = checks

    checks = property(get_checks, set_checks)

    def get_defs(self, position=None):
        """Gets the defs at the position."""
        if position is None:
            position = self.position
        return self.checkdefs[position][1]

    def set_defs(self, defs, position=None):
        """Sets the defs at the position."""
        if position is None:
            position = self.position
        self.checkdefs[position][1] = defs

    defs = property(get_defs, set_defs)

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

    def insert_check(self, index, check_item):
        """Inserts a check universally."""
        self.checks.insert(index, check_item)
        for other in self.others:
            other.insert_check(index, check_item)

    def insert_def(self, index, def_item):
        """Inserts a def universally."""
        self.defs.insert(index, def_item)
        for other in self.others:
            other.insert_def(index, def_item)

    def set_position(self, position):
        """Sets the if-statement position."""
        if position < 0:
            position += len(self.checkdefs)
        while position >= len(self.checkdefs):
            self.checkdefs.append(([], []))
        self.position = position

    def increment(self, by=1):
        """Advances the if-statement position."""
        self.set_position(self.position + by)

    def decrement(self, by=1):
        """Decrements the if-statement position."""
        self.set_position(self.position - by)

    @contextmanager
    def down_a_level(self, by=1):
        """Increment then decrement."""
        self.increment(by)
        try:
            yield
        finally:
            self.decrement(by)

    @contextmanager
    def only_self(self):
        """Only match in self not others."""
        others, self.others = self.others, []
        try:
            yield
        finally:
            self.others = others + self.others

    def get_temp_var(self):
        """Gets the next match_temp_var."""
        tempvar = match_temp_var + "_" + str(self.var_index)
        self.var_index += 1
        return tempvar

    def match_all_in(self, matches, item):
        """Matches all matches to elements of item."""
        for i, match in enumerate(matches):
            self.match(match, item + "[" + str(i) + "]")

    def check_len_in(self, min_len, max_len, item):
        """Checks that the length of item is in range(min_len, max_len+1)."""
        if max_len is None:
            if min_len:
                self.add_check("_coconut.len(" + item + ") >= " + str(min_len))
        elif min_len == max_len:
            self.add_check("_coconut.len(" + item + ") == " + str(min_len))
        elif not min_len:
            self.add_check("_coconut.len(" + item + ") <= " + str(max_len))
        else:
            self.add_check(str(min_len) + " <= _coconut.len(" + item + ") <= " + str(max_len))

    def match_function(self, args, kwargs, match_args=(), star_arg=None, kwd_args=(), dubstar_arg=None):
        """Matches a pattern-matching function."""
        self.match_in_args_kwargs(match_args, args, kwargs, allow_star_args=star_arg is not None)
        if star_arg is not None:
            self.match(star_arg, args + "[" + str(len(match_args)) + ":]")
        self.match_in_kwargs(kwd_args, kwargs)
        with self.down_a_level():
            if dubstar_arg is None:
                self.add_check("not " + kwargs)
            else:
                self.match(dubstar_arg, kwargs)

    def match_in_args_kwargs(self, match_args, args, kwargs, allow_star_args=False):
        """Matches against args or kwargs."""
        req_len = 0
        arg_checks = {}
        to_match = []  # [(move_down, match, against)]
        for i, arg in enumerate(match_args):
            if isinstance(arg, tuple):
                (match, default) = arg
            else:
                match, default = arg, None
            names = get_match_names(match)
            if default is None:
                if not names:
                    req_len = i + 1
                    to_match.append((False, match, args + "[" + str(i) + "]"))
                else:
                    arg_checks[i] = (
                        # if i < req_len
                        " and ".join('"' + name + '" not in ' + kwargs for name in names),
                        # if i >= req_len
                        "_coconut.sum((_coconut.len(" + args + ") > " + str(i) + ", "
                        + ", ".join('"' + name + '" in ' + kwargs for name in names)
                        + ")) == 1",
                    )
                    tempvar = self.get_temp_var()
                    self.add_def(
                        tempvar + " = "
                        + args + "[" + str(i) + "] if _coconut.len(" + args + ") > " + str(i) + " else "
                        + "".join(kwargs + '.pop("' + name + '") if "' + name + '" in ' + kwargs + " else "
                                  for name in names[:-1])
                        + kwargs + '.pop("' + names[-1] + '")',
                    )
                    to_match.append((True, match, tempvar))
            else:
                if not names:
                    tempvar = self.get_temp_var()
                    self.add_def(tempvar + " = " + args + "[" + str(i) + "] if _coconut.len(" + args + ") > " + str(i) + " else " + default)
                    to_match.append((True, match, tempvar))
                else:
                    arg_checks[i] = (
                        # if i < req_len
                        None,
                        # if i >= req_len
                        "_coconut.sum((_coconut.len(" + args + ") > " + str(i) + ", "
                        + ", ".join('"' + name + '" in ' + kwargs for name in names)
                        + ")) <= 1",
                    )
                    tempvar = self.get_temp_var()
                    self.add_def(
                        tempvar + " = "
                        + args + "[" + str(i) + "] if _coconut.len(" + args + ") > " + str(i) + " else "
                        + "".join(
                            kwargs + '.pop("' + name + '") if "' + name + '" in ' + kwargs + " else "
                            for name in names
                        )
                        + default,
                    )
                    to_match.append((True, match, tempvar))

        max_len = None if allow_star_args else len(match_args)
        self.check_len_in(req_len, max_len, args)
        for i in sorted(arg_checks):
            lt_check, ge_check = arg_checks[i]
            if i < req_len:
                if lt_check is not None:
                    self.add_check(lt_check)
            else:
                if ge_check is not None:
                    self.add_check(ge_check)

        for move_down, match, against in to_match:
            if move_down:
                with self.down_a_level():
                    self.match(match, against)
            else:
                self.match(match, against)

    def match_in_kwargs(self, match_args, kwargs):
        """Matches against kwargs."""
        for match, default in match_args:
            names = get_match_names(match)
            if names:
                tempvar = self.get_temp_var()
                self.add_def(
                    tempvar + " = "
                    + "".join(
                        kwargs + '.pop("' + name + '") if "' + name + '" in ' + kwargs + " else "
                        for name in names
                    )
                    + default,
                )
                with self.down_a_level():
                    self.match(match, tempvar)
            else:
                raise CoconutDeferredSyntaxError("keyword-only pattern-matching function arguments must have names", self.loc)

    def match_dict(self, tokens, item):
        """Matches a dictionary."""
        if len(tokens) == 1:
            matches, rest = tokens[0], None
        else:
            matches, rest = tokens
        self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Mapping)")
        if rest is None:
            self.add_check("_coconut.len(" + item + ") == " + str(len(matches)))

        if matches:
            self.use_sentinel = True
        for k, v in matches:
            key_var = self.get_temp_var()
            self.add_def(key_var + " = " + item + ".get(" + k + ", " + sentinel_var + ")")
            with self.down_a_level():
                self.add_check(key_var + " is not " + sentinel_var)
                self.match(v, key_var)
        if rest is not None and rest != wildcard:
            match_keys = [k for k, v in matches]
            with self.down_a_level():
                self.add_def(
                    rest + " = dict((k, v) for k, v in "
                    + item + ".items() if k not in set(("
                    + ", ".join(match_keys) + ("," if len(match_keys) == 1 else "")
                    + ")))",
                )

    def assign_to_series(self, name, series_type, item):
        """Assign name to item converted to the given series_type."""
        if series_type == "(":
            self.add_def(name + " = _coconut.tuple(" + item + ")")
        elif series_type == "[":
            self.add_def(name + " = _coconut.list(" + item + ")")
        else:
            raise CoconutInternalException("invalid series match type", series_type)

    def match_sequence(self, tokens, item):
        """Matches a sequence."""
        tail = None
        if len(tokens) == 2:
            series_type, matches = tokens
        else:
            series_type, matches, tail = tokens
        self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Sequence)")
        if tail is None:
            self.add_check("_coconut.len(" + item + ") == " + str(len(matches)))
        else:
            self.add_check("_coconut.len(" + item + ") >= " + str(len(matches)))
            if tail != wildcard:
                if len(matches) > 0:
                    splice = "[" + str(len(matches)) + ":]"
                else:
                    splice = ""
                self.assign_to_series(tail, series_type, item + splice)
        self.match_all_in(matches, item)

    def match_iterator(self, tokens, item):
        """Matches a lazy list or a chain."""
        tail = None
        if len(tokens) == 2:
            _, matches = tokens
        else:
            _, matches, tail = tokens
        self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Iterable)")
        if tail is None:
            itervar = self.get_temp_var()
            self.add_def(itervar + " = _coconut.tuple(" + item + ")")
        elif matches:
            itervar = self.get_temp_var()
            if tail == wildcard:
                tail = item
            else:
                self.add_def(tail + " = _coconut.iter(" + item + ")")
            self.add_def(itervar + " = _coconut.tuple(_coconut_igetitem(" + tail + ", _coconut.slice(None, " + str(len(matches)) + ")))")
        else:
            itervar = None
            if tail != wildcard:
                self.add_def(tail + " = " + item)
        if itervar is not None:
            with self.down_a_level():
                self.add_check("_coconut.len(" + itervar + ") == " + str(len(matches)))
                self.match_all_in(matches, itervar)

    def match_star(self, tokens, item):
        """Matches starred assignment."""
        head_matches, last_matches = None, None
        if len(tokens) == 1:
            middle = tokens[0]
        elif len(tokens) == 2:
            if isinstance(tokens[0], str):
                middle, last_matches = tokens
            else:
                head_matches, middle = tokens
        else:
            head_matches, middle, last_matches = tokens
        self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Iterable)")
        if head_matches is None and last_matches is None:
            if middle != wildcard:
                self.add_def(middle + " = _coconut.list(" + item + ")")
        else:
            itervar = self.get_temp_var()
            self.add_def(itervar + " = _coconut.list(" + item + ")")
            with self.down_a_level():
                req_length = (len(head_matches) if head_matches is not None else 0) + (len(last_matches) if last_matches is not None else 0)
                self.add_check("_coconut.len(" + itervar + ") >= " + str(req_length))
                if middle != wildcard:
                    head_splice = str(len(head_matches)) if head_matches is not None else ""
                    last_splice = "-" + str(len(last_matches)) if last_matches is not None else ""
                    self.add_def(middle + " = " + itervar + "[" + head_splice + ":" + last_splice + "]")
                if head_matches is not None:
                    self.match_all_in(head_matches, itervar)
                if last_matches is not None:
                    for x in range(1, len(last_matches) + 1):
                        self.match(last_matches[-x], itervar + "[-" + str(x) + "]")

    def match_rsequence(self, tokens, item):
        """Matches a reverse sequence."""
        front, series_type, matches = tokens
        self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Sequence)")
        self.add_check("_coconut.len(" + item + ") >= " + str(len(matches)))
        if front != wildcard:
            if len(matches):
                splice = "[:" + str(-len(matches)) + "]"
            else:
                splice = ""
            self.assign_to_series(front, series_type, item + splice)
        for i, match in enumerate(matches):
            self.match(match, item + "[" + str(i - len(matches)) + "]")

    def match_msequence(self, tokens, item):
        """Matches a middle sequence."""
        series_type, head_matches, middle, _, last_matches = tokens
        self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Sequence)")
        self.add_check("_coconut.len(" + item + ") >= " + str(len(head_matches) + len(last_matches)))
        if middle != wildcard:
            if len(head_matches) and len(last_matches):
                splice = "[" + str(len(head_matches)) + ":" + str(-len(last_matches)) + "]"
            elif len(head_matches):
                splice = "[" + str(len(head_matches)) + ":]"
            elif len(last_matches):
                splice = "[:" + str(-len(last_matches)) + "]"
            else:
                splice = ""
            self.assign_to_series(middle, series_type, item + splice)
        self.match_all_in(head_matches, item)
        for i, match in enumerate(last_matches):
            self.match(match, item + "[" + str(i - len(last_matches)) + "]")

    def match_string(self, tokens, item):
        """Match prefix string."""
        prefix, name = tokens
        return self.match_mstring((prefix, name, None), item, use_bytes=prefix.startswith("b"))

    def match_rstring(self, tokens, item):
        """Match suffix string."""
        name, suffix = tokens
        return self.match_mstring((None, name, suffix), item, use_bytes=suffix.startswith("b"))

    def match_mstring(self, tokens, item, use_bytes=None):
        """Match prefix and suffix string."""
        prefix, name, suffix = tokens
        if use_bytes is None:
            if prefix.startswith("b") or suffix.startswith("b"):
                if prefix.startswith("b") and suffix.startswith("b"):
                    use_bytes = True
                else:
                    raise CoconutDeferredSyntaxError("string literals and byte literals cannot be added in patterns", self.loc)
        if use_bytes:
            self.add_check("_coconut.isinstance(" + item + ", _coconut.bytes)")
        else:
            self.add_check("_coconut.isinstance(" + item + ", _coconut.str)")
        if prefix is not None:
            self.add_check(item + ".startswith(" + prefix + ")")
        if suffix is not None:
            self.add_check(item + ".endswith(" + suffix + ")")
        if name != wildcard:
            self.add_def(
                name + " = " + item + "[" +
                ("" if prefix is None else "_coconut.len(" + prefix + ")") + ":"
                + ("" if suffix is None else "-_coconut.len(" + suffix + ")") + "]",
            )

    def match_const(self, tokens, item):
        """Matches a constant."""
        match, = tokens
        if match in const_vars:
            self.add_check(item + " is " + match)
        else:
            self.add_check(item + " == " + match)

    def match_var(self, tokens, item):
        """Matches a variable."""
        setvar, = tokens
        if setvar != wildcard:
            if setvar in self.names:
                self.add_check(self.names[setvar] + " == " + item)
            else:
                self.add_def(setvar + " = " + item)
                self.names[setvar] = item

    def match_set(self, tokens, item):
        """Matches a set."""
        match, = tokens
        self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Set)")
        self.add_check("_coconut.len(" + item + ") == " + str(len(match)))
        for const in match:
            self.add_check(const + " in " + item)

    def match_data(self, tokens, item):
        """Matches a data type."""
        if len(tokens) == 2:
            data_type, matches = tokens
            star_match = None
        elif len(tokens) == 3:
            data_type, matches, star_match = tokens
        else:
            raise CoconutInternalException("invalid data match tokens", tokens)
        self.add_check("_coconut.isinstance(" + item + ", " + data_type + ")")
        if star_match is None:
            self.add_check("_coconut.len(" + item + ") == " + str(len(matches)))
        elif len(matches):
            self.add_check("_coconut.len(" + item + ") >= " + str(len(matches)))
        self.match_all_in(matches, item)
        if star_match is not None:
            self.match(star_match, item + "[" + str(len(matches)) + ":]")

    def match_paren(self, tokens, item):
        """Matches a paren."""
        match, = tokens
        return self.match(match, item)

    def match_trailer(self, tokens, item):
        """Matches typedefs and as patterns."""
        internal_assert(len(tokens) > 1 and len(tokens) % 2 == 1, "invalid trailer match tokens", tokens)
        match, trailers = tokens[0], tokens[1:]
        for i in range(0, len(trailers), 2):
            op, arg = trailers[i], trailers[i + 1]
            if op == "is":
                self.add_check("_coconut.isinstance(" + item + ", " + arg + ")")
            elif op == "as":
                if arg in self.names:
                    self.add_check(self.names[arg] + " == " + item)
                elif arg != wildcard:
                    self.add_def(arg + " = " + item)
                    self.names[arg] = item
            else:
                raise CoconutInternalException("invalid trailer match operation", op)
        self.match(match, item)

    def match_and(self, tokens, item):
        """Matches and."""
        for match in tokens:
            self.match(match, item)

    def match_or(self, tokens, item):
        """Matches or."""
        for x in range(1, len(tokens)):
            self.duplicate().match(tokens[x], item)
        with self.only_self():
            self.match(tokens[0], item)

    def match(self, tokens, item):
        """Performs pattern-matching processing."""
        for flag, get_handler in self.matchers.items():
            if flag in tokens:
                return get_handler(self)(tokens, item)
        raise CoconutInternalException("invalid pattern-matching tokens", tokens)

    def out(self):
        out = ""
        if self.use_sentinel:
            out += sentinel_var + " = _coconut.object()\n"
        closes = 0
        for checks, defs in self.checkdefs:
            if checks:
                out += "if " + paren_join(checks, "and") + ":\n" + openindent
                closes += 1
            if defs:
                out += "\n".join(defs) + "\n"
        return out + (
            match_check_var + " = True\n"
            + closeindent * closes
            + "".join(other.out() for other in self.others)
            + (
                "if " + match_check_var + " and not ("
                + paren_join(self.guards, "and")
                + "):\n" + openindent
                + match_check_var + " = False\n" + closeindent
                if self.guards else ""
            )
        )
