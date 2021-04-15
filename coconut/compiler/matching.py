#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Handles Coconut pattern-matching.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

from contextlib import contextmanager

from coconut.terminal import (
    internal_assert,
    logger,
)
from coconut.exceptions import (
    CoconutInternalException,
    CoconutDeferredSyntaxError,
    CoconutSyntaxWarning,
)
from coconut.constants import (
    match_temp_var,
    wildcard,
    openindent,
    closeindent,
    const_vars,
    function_match_error_var,
)
from coconut.compiler.util import paren_join

# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


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
    elif "walrus" in match:
        name, match = match
        names.append(name)
        names += get_match_names(match)
    return names


# -----------------------------------------------------------------------------------------------------------------------
# MATCHER:
# -----------------------------------------------------------------------------------------------------------------------


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
        "class": lambda self: self.match_class,
        "data_or_class": lambda self: self.match_data_or_class,
        "paren": lambda self: self.match_paren,
        "trailer": lambda self: self.match_trailer,
        "walrus": lambda self: self.match_walrus,
        "and": lambda self: self.match_and,
        "or": lambda self: self.match_or,
        "star": lambda self: self.match_star,
        "implicit_tuple": lambda self: self.match_implicit_tuple,
    }
    __slots__ = (
        "comp",
        "original",
        "loc",
        "check_var",
        "style",
        "position",
        "checkdefs",
        "names",
        "var_index",
        "name_list",
        "others",
        "guards",
    )
    valid_styles = (
        "coconut",
        "python",
        "coconut warn",
        "python warn",
        "coconut strict",
        "python strict",
    )

    def __init__(self, comp, original, loc, check_var, style="coconut", name_list=None, checkdefs=None, names=None, var_index=0):
        """Creates the matcher."""
        self.comp = comp
        self.original = original
        self.loc = loc
        self.check_var = check_var
        internal_assert(style in self.valid_styles, "invalid Matcher style", style)
        self.style = style
        self.name_list = name_list
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

    def duplicate(self, separate_names=True):
        """Duplicates the matcher to others."""
        new_names = self.names
        if separate_names:
            new_names = new_names.copy()
        other = Matcher(self.comp, self.original, self.loc, self.check_var, self.style, self.name_list, self.checkdefs, new_names, self.var_index)
        other.insert_check(0, "not " + self.check_var)
        self.others.append(other)
        return other

    @property
    def using_python_rules(self):
        """Whether the current style uses PEP 622 rules."""
        return self.style.startswith("python")

    def rule_conflict_warn(self, message, if_coconut=None, if_python=None, extra=None):
        """Warns on conflicting style rules if callback was given."""
        if self.style.endswith("warn") or self.style.endswith("strict"):
            full_msg = message
            if if_python or if_coconut:
                full_msg += " (" + (if_python if self.using_python_rules else if_coconut) + ")"
            if extra:
                full_msg += " (" + extra + ")"
            if self.style.endswith("strict"):
                full_msg += " (disable --strict to dismiss)"
            logger.warn_err(self.comp.make_err(CoconutSyntaxWarning, full_msg, self.original, self.loc))

    def register_name(self, name, value):
        """Register a new name."""
        self.names[name] = value
        if self.name_list is not None and name not in self.name_list:
            self.name_list.append(name)

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
        new_pos = self.position + by
        internal_assert(new_pos > 0, "invalid increment/decrement call to set pos to", new_pos)
        self.set_position(new_pos)

    def decrement(self, by=1):
        """Decrements the if-statement position."""
        self.increment(-by)

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

    def match_function(self, args, kwargs, pos_only_match_args=(), match_args=(), star_arg=None, kwd_match_args=(), dubstar_arg=None):
        """Matches a pattern-matching function."""
        # before everything, pop the FunctionMatchError from context
        self.add_def(function_match_error_var + " = _coconut_get_function_match_error()")
        with self.down_a_level():

            self.match_in_args_kwargs(pos_only_match_args, match_args, args, kwargs, allow_star_args=star_arg is not None)

            if star_arg is not None:
                self.match(star_arg, args + "[" + str(len(match_args)) + ":]")

            self.match_in_kwargs(kwd_match_args, kwargs)

            with self.down_a_level():
                if dubstar_arg is None:
                    self.add_check("not " + kwargs)
                else:
                    self.match(dubstar_arg, kwargs)

    def match_in_args_kwargs(self, pos_only_match_args, match_args, args, kwargs, allow_star_args=False):
        """Matches against args or kwargs."""
        req_len = 0
        arg_checks = {}
        to_match = []  # [(move_down, match, against)]
        for i, arg in enumerate(pos_only_match_args + match_args):
            if isinstance(arg, tuple):
                (match, default) = arg
            else:
                match, default = arg, None
            if i < len(pos_only_match_args):  # faster if arg in pos_only_match_args
                names = None
            else:
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
                        + "".join(
                            kwargs + '.pop("' + name + '") if "' + name + '" in ' + kwargs + " else "
                            for name in names[:-1]
                        )
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

        max_len = None if allow_star_args else len(pos_only_match_args) + len(match_args)
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
            self.rule_conflict_warn(
                "ambiguous pattern; could be Coconut-style len-checking dict match or Python-style len-ignoring dict match",
                'resolving to Coconut-style len-checking dict match by default',
                'resolving to Python-style len-ignoring dict match due to Python-style "match: case" block',
                "use explicit '{..., **_}' or '{..., **{}}' syntax to dismiss",
            )
            check_len = not self.using_python_rules
        elif rest == "{}":
            check_len = True
            rest = None
        else:
            check_len = False

        if check_len:
            self.add_check("_coconut.len(" + item + ") == " + str(len(matches)))

        seen_keys = set()
        for k, v in matches:
            if k in seen_keys:
                raise CoconutDeferredSyntaxError("duplicate key {k!r} in dictionary pattern".format(k=k), self.loc)
            seen_keys.add(k)
            key_var = self.get_temp_var()
            self.add_def(key_var + " = " + item + ".get(" + k + ", _coconut_sentinel)")
            with self.down_a_level():
                self.add_check(key_var + " is not _coconut_sentinel")
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

    def match_implicit_tuple(self, tokens, item):
        """Matches an implicit tuple."""
        return self.match_sequence(["(", tokens], item)

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
                name + " = " + item + "["
                + ("" if prefix is None else "_coconut.len(" + prefix + ")") + ":"
                + ("" if suffix is None else "-_coconut.len(" + suffix + ")") + "]",
            )

    def match_const(self, tokens, item):
        """Matches a constant."""
        match, = tokens
        if match in const_vars:
            self.add_check(item + " is " + match)
        else:
            self.add_check(item + " == " + match)

    def match_set(self, tokens, item):
        """Matches a set."""
        match, = tokens
        self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Set)")
        self.add_check("_coconut.len(" + item + ") == " + str(len(match)))
        for const in match:
            self.add_check(const + " in " + item)

    def split_data_or_class_match(self, tokens):
        """Split data/class match tokens into cls_name, pos_matches, name_matches, star_match."""
        internal_assert(len(tokens) == 2, "invalid data/class match tokens", tokens)
        cls_name, matches = tokens

        pos_matches = []
        name_matches = {}
        star_match = None
        for match_arg in matches:
            if len(match_arg) == 1:
                match, = match_arg
                if star_match is not None:
                    raise CoconutDeferredSyntaxError("positional arg after starred arg in data/class match", self.loc)
                if name_matches:
                    raise CoconutDeferredSyntaxError("positional arg after named arg in data/class match", self.loc)
                pos_matches.append(match)
            elif len(match_arg) == 2:
                internal_assert(match_arg[0] == "*", "invalid starred data/class match arg tokens", match_arg)
                _, match = match_arg
                if star_match is not None:
                    raise CoconutDeferredSyntaxError("duplicate starred arg in data/class match", self.loc)
                if name_matches:
                    raise CoconutDeferredSyntaxError("both starred arg and named arg in data/class match", self.loc)
                star_match = match
            elif len(match_arg) == 3:
                internal_assert(match_arg[1] == "=", "invalid named data/class match arg tokens", match_arg)
                name, _, match = match_arg
                if star_match is not None:
                    raise CoconutDeferredSyntaxError("both named arg and starred arg in data/class match", self.loc)
                if name in name_matches:
                    raise CoconutDeferredSyntaxError("duplicate named arg {name!r} in data/class match".format(name=name), self.loc)
                name_matches[name] = match
            else:
                raise CoconutInternalException("invalid data/class match arg", match_arg)

        return cls_name, pos_matches, name_matches, star_match

    def match_class(self, tokens, item):
        """Matches a class PEP-622-style."""
        cls_name, pos_matches, name_matches, star_match = self.split_data_or_class_match(tokens)

        self.add_check("_coconut.isinstance(" + item + ", " + cls_name + ")")

        for i, match in enumerate(pos_matches):
            self.match(match, "_coconut.getattr(" + item + ", " + item + ".__match_args__[" + str(i) + "])")

        if star_match is not None:
            temp_var = self.get_temp_var()
            self.add_def(
                "{temp_var} = _coconut.tuple(_coconut.getattr({item}, {item}.__match_args__[i]) for i in _coconut.range({min_ind}, _coconut.len({item}.__match_args__)))".format(
                    temp_var=temp_var,
                    item=item,
                    min_ind=len(pos_matches),
                ),
            )
            with self.down_a_level():
                self.match(star_match, temp_var)

        for name, match in name_matches.items():
            self.match(match, item + "." + name)

    def match_data(self, tokens, item):
        """Matches a data type."""
        cls_name, pos_matches, name_matches, star_match = self.split_data_or_class_match(tokens)

        self.add_check("_coconut.isinstance(" + item + ", " + cls_name + ")")

        if star_match is None:
            self.add_check(
                '_coconut.len({item}) == {total_len}'.format(
                    item=item,
                    total_len=len(pos_matches) + len(name_matches),
                ),
            )
        else:
            # avoid checking >= 0
            if len(pos_matches):
                self.add_check(
                    "_coconut.len({item}) >= {min_len}".format(
                        item=item,
                        min_len=len(pos_matches),
                    ),
                )

        self.match_all_in(pos_matches, item)

        if star_match is not None:
            self.match(star_match, item + "[" + str(len(pos_matches)) + ":]")

        for name, match in name_matches.items():
            self.match(match, item + "." + name)

    def match_data_or_class(self, tokens, item):
        """Matches an ambiguous data or class match."""
        self.rule_conflict_warn(
            "ambiguous pattern; could be class match or data match",
            'resolving to Coconut data match by default',
            'resolving to Python-style class match due to Python-style "match: case" block',
            "use explicit 'data data_name(args)' or 'class cls_name(args)' syntax to dismiss",
        )
        if self.using_python_rules:
            return self.match_class(tokens, item)
        else:
            return self.match_data(tokens, item)

    def match_paren(self, tokens, item):
        """Matches a paren."""
        match, = tokens
        return self.match(match, item)

    def match_var(self, tokens, item, bind_wildcard=False):
        """Matches a variable."""
        setvar, = tokens
        if setvar == wildcard and not bind_wildcard:
            return
        if setvar in self.names:
            self.add_check(self.names[setvar] + " == " + item)
        else:
            self.add_def(setvar + " = " + item)
            self.register_name(setvar, item)

    def match_trailer(self, tokens, item):
        """Matches typedefs and as patterns."""
        internal_assert(len(tokens) > 1 and len(tokens) % 2 == 1, "invalid trailer match tokens", tokens)
        match, trailers = tokens[0], tokens[1:]
        for i in range(0, len(trailers), 2):
            op, arg = trailers[i], trailers[i + 1]
            if op == "is":
                self.add_check("_coconut.isinstance(" + item + ", " + arg + ")")
            elif op == "as":
                self.match_var([arg], item, bind_wildcard=True)
            else:
                raise CoconutInternalException("invalid trailer match operation", op)
        self.match(match, item)

    def match_walrus(self, tokens, item):
        """Matches :=."""
        internal_assert(len(tokens) == 2, "invalid walrus match tokens", tokens)
        name, match = tokens
        self.match_var([name], item, bind_wildcard=True)
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
        """Return pattern-matching code."""
        out = ""
        closes = 0
        for checks, defs in self.checkdefs:
            if checks:
                out += "if " + paren_join(checks, "and") + ":\n" + openindent
                closes += 1
            if defs:
                out += "\n".join(defs) + "\n"
        return out + (
            self.check_var + " = True\n"
            + closeindent * closes
            + "".join(other.out() for other in self.others)
            + (
                "if " + self.check_var + " and not ("
                + paren_join(self.guards, "and")
                + "):\n" + openindent
                + self.check_var + " = False\n" + closeindent
                if self.guards else ""
            )
        )

    def build(self, stmts=None, set_check_var=True, invert=False):
        """Construct code for performing the match then executing stmts."""
        out = ""
        if set_check_var:
            out += self.check_var + " = False\n"
        out += self.out()
        if stmts is not None:
            out += "if " + ("not " if invert else "") + self.check_var + ":" + "\n" + openindent + "".join(stmts) + closeindent
        return out
