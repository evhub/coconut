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
from collections import OrderedDict

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
    match_set_name_var,
    is_data_var,
    default_matcher_style,
)
from coconut.compiler.util import (
    paren_join,
    handle_indentation,
)

# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


def get_match_names(match):
    """Gets keyword names for the given match."""
    names = []
    # these constructs directly contain top-level variable names
    if "var" in match:
        (setvar,) = match
        if setvar != wildcard:
            names.append(setvar)
    elif "as" in match:
        as_match, as_names = match[0], match[1:]
        names.extend(as_names)
        names += get_match_names(as_match)
    # these constructs continue matching on the entire original item,
    #  meaning they can also contain top-level variable names
    elif "paren" in match:
        (match,) = match
        names += get_match_names(match)
    elif "and" in match:
        for and_match in match:
            names += get_match_names(and_match)
    elif "infix" in match:
        infix_match = match[0]
        names += get_match_names(infix_match)
    elif "isinstance_is" in match:
        isinstance_is_match = match[0]
        names += get_match_names(isinstance_is_match)
    return names


# -----------------------------------------------------------------------------------------------------------------------
# MATCHER:
# -----------------------------------------------------------------------------------------------------------------------


class Matcher(object):
    """Pattern-matching processor."""
    __slots__ = (
        "comp",
        "original",
        "loc",
        "check_var",
        "style",
        "position",
        "checkdefs",
        "names",
        "var_index_obj",
        "name_list",
        "child_groups",
        "guards",
        "parent_names",
    )
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
        "as": lambda self: self.match_as,
        "and": lambda self: self.match_and,
        "or": lambda self: self.match_or,
        "star": lambda self: self.match_star,
        "implicit_tuple": lambda self: self.match_implicit_tuple,
        "view": lambda self: self.match_view,
        "infix": lambda self: self.match_infix,
        "isinstance_is": lambda self: self.match_isinstance_is,
    }
    valid_styles = (
        "coconut",
        "python",
        "coconut warn",
        "python warn",
        "coconut warn on strict",
        "python warn on strict",
    )

    def __init__(self, comp, original, loc, check_var, style=default_matcher_style, name_list=None, checkdefs=None, parent_names={}, var_index_obj=None):
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
        self.parent_names = parent_names
        self.names = OrderedDict()  # ensures deterministic ordering of name setting code
        self.var_index_obj = [0] if var_index_obj is None else var_index_obj
        self.guards = []
        self.child_groups = []

    def branches(self, num_branches):
        """Create num_branches child matchers, one of which must match for the parent match to succeed."""
        child_group = []
        for _ in range(num_branches):
            new_matcher = Matcher(self.comp, self.original, self.loc, self.check_var, self.style, self.name_list, self.checkdefs, self.names, self.var_index_obj)
            new_matcher.insert_check(0, "not " + self.check_var)
            child_group.append(new_matcher)

        self.child_groups.append(child_group)
        return child_group

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

    def add_def(self, def_item):
        """Adds a def universally."""
        self.defs.append(def_item)

    def insert_check(self, index, check_item):
        """Inserts a check universally."""
        self.checks.insert(index, check_item)

    def insert_def(self, index, def_item):
        """Inserts a def universally."""
        self.defs.insert(index, def_item)

    @property
    def using_python_rules(self):
        """Whether the current style uses PEP 622 rules."""
        return self.style.startswith("python")

    def rule_conflict_warn(self, message, if_coconut=None, if_python=None, extra=None):
        """Warns on conflicting style rules if callback was given."""
        if self.style.endswith("warn") or self.style.endswith("strict") and self.comp.strict:
            full_msg = message
            if if_python or if_coconut:
                full_msg += " (" + (if_python if self.using_python_rules else if_coconut) + ")"
            if extra:
                full_msg += " (" + extra + ")"
            if self.style.endswith("strict"):
                full_msg += " (remove --strict to dismiss)"
            logger.warn_err(self.comp.make_err(CoconutSyntaxWarning, full_msg, self.original, self.loc))

    def add_guard(self, cond):
        """Adds cond as a guard."""
        self.guards.append(cond)

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

    def get_temp_var(self):
        """Gets the next match_temp_var."""
        tempvar = match_temp_var + "_" + str(self.var_index_obj[0])
        self.var_index_obj[0] += 1
        return tempvar

    def get_set_name_var(self, name):
        """Gets the var for checking whether a name should be set."""
        return match_set_name_var + "_" + name

    def register_name(self, name, value):
        """Register a new name and return its name set var."""
        self.names[name] = value
        if self.name_list is not None and name not in self.name_list:
            self.name_list.append(name)
        return self.get_set_name_var(name)

    def match_var(self, tokens, item, bind_wildcard=False):
        """Matches a variable."""
        varname, = tokens
        if varname == wildcard and not bind_wildcard:
            return
        if varname in self.parent_names:
            self.add_check(self.parent_names[varname] + " == " + item)
        elif varname in self.names:
            self.add_check(self.names[varname] + " == " + item)
        else:
            set_name_var = self.register_name(varname, item)
            self.add_def(set_name_var + " = " + item)

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

    def match_function(self, args, kwargs, pos_only_match_args=(), match_args=(), star_arg=None, kwd_only_match_args=(), dubstar_arg=None):
        """Matches a pattern-matching function."""
        # before everything, pop the FunctionMatchError from context
        self.add_def(function_match_error_var + " = _coconut_get_function_match_error()")
        with self.down_a_level():

            self.match_in_args_kwargs(pos_only_match_args, match_args, args, kwargs, allow_star_args=star_arg is not None)

            if star_arg is not None:
                self.match(star_arg, args + "[" + str(len(match_args)) + ":]")

            self.match_in_kwargs(kwd_only_match_args, kwargs)

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
            if not names:
                raise CoconutDeferredSyntaxError("keyword-only pattern-matching function arguments must be named", self.loc)
            tempvar = self.get_temp_var()
            self.add_def(
                tempvar + " = "
                + "".join(
                    kwargs + '.pop("' + name + '") if "' + name + '" in ' + kwargs + " else "
                    for name in names
                )
                + (default if default is not None else "_coconut_sentinel"),
            )
            with self.down_a_level():
                if default is None:
                    self.add_check(tempvar + " is not _coconut_sentinel")
                self.match(match, tempvar)

    def match_dict(self, tokens, item):
        """Matches a dictionary."""
        internal_assert(1 <= len(tokens) <= 2, "invalid dict match tokens", tokens)
        if len(tokens) == 1:
            matches, rest = tokens[0], None
        else:
            matches, rest = tokens

        self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Mapping)")

        if rest is None:
            self.rule_conflict_warn(
                "ambiguous pattern; could be old-style len-checking dict match or new-style len-ignoring dict match",
                extra="use explicit '{..., **_}' or '{..., **{}}' syntax to resolve",
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
        if self.using_python_rules or series_type == "[":
            self.add_def(name + " = _coconut.list(" + item + ")")
        elif series_type == "(":
            self.add_def(name + " = _coconut.tuple(" + item + ")")
        else:
            raise CoconutInternalException("invalid series match type", series_type)

    def match_implicit_tuple(self, tokens, item):
        """Matches an implicit tuple."""
        return self.match_sequence(["(", tokens], item)

    def match_sequence(self, tokens, item):
        """Matches a sequence."""
        internal_assert(2 <= len(tokens) <= 3, "invalid sequence match tokens", tokens)
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
        internal_assert(2 <= len(tokens) <= 3, "invalid iterator match tokens", tokens)
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
            self.add_def(itervar + " = _coconut.tuple(_coconut_iter_getitem(" + tail + ", _coconut.slice(None, " + str(len(matches)) + ")))")
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
        internal_assert(1 <= len(tokens) <= 3, "invalid star match tokens", tokens)
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
        return self.match_mstring((prefix, name, None), item)

    def match_rstring(self, tokens, item):
        """Match suffix string."""
        name, suffix = tokens
        return self.match_mstring((None, name, suffix), item)

    def match_mstring(self, tokens, item):
        """Match prefix and suffix string."""
        prefix, name, suffix = tokens
        if prefix is None:
            use_bytes = suffix.startswith("b")
        elif suffix is None:
            use_bytes = prefix.startswith("b")
        elif prefix.startswith("b") and suffix.startswith("b"):
            use_bytes = True
        elif prefix.startswith("b") or suffix.startswith("b"):
            raise CoconutDeferredSyntaxError("string literals and byte literals cannot be added in patterns", self.loc)
        else:
            use_bytes = False
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
                + ("" if prefix is None else self.comp.eval_now("len(" + prefix + ")")) + ":"
                + ("" if suffix is None else self.comp.eval_now("-len(" + suffix + ")")) + "]",
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

    def match_class_attr(self, match, name, item):
        """Match an attribute for a class match."""
        attr_var = self.get_temp_var()
        self.add_def(attr_var + " = _coconut.getattr(" + item + ", '" + name + "', _coconut_sentinel)")
        with self.down_a_level():
            self.add_check(attr_var + " is not _coconut_sentinel")
            self.match(match, attr_var)

    def match_class(self, tokens, item):
        """Matches a class PEP-622-style."""
        cls_name, pos_matches, name_matches, star_match = self.split_data_or_class_match(tokens)

        self.add_check("_coconut.isinstance(" + item + ", " + cls_name + ")")

        self_match_matcher, other_cls_matcher = self.branches(2)

        # handle instances of _coconut_self_match_types
        self_match_matcher.add_check("_coconut.isinstance(" + item + ", _coconut_self_match_types)")
        if pos_matches:
            if len(pos_matches) > 1:
                self_match_matcher.add_def('raise _coconut.TypeError("too many positional args in class match (got ' + str(len(pos_matches)) + '; type supports 1)")')
            else:
                self_match_matcher.match(pos_matches[0], item)

        # handle all other classes
        other_cls_matcher.add_check("not _coconut.isinstance(" + item + ", _coconut_self_match_types)")
        match_args_var = other_cls_matcher.get_temp_var()
        other_cls_matcher.add_def(match_args_var + " = _coconut.getattr(" + item + ", '__match_args__', ())")
        with other_cls_matcher.down_a_level():
            for i, match in enumerate(pos_matches):
                other_cls_matcher.match_class_attr(match, match_args_var + "[" + str(i) + "]", item)

        # handle starred arg
        if star_match is not None:
            temp_var = self.get_temp_var()
            self.add_def(
                "{temp_var} = _coconut.tuple(_coconut.getattr({item}, _coconut.getattr({item}, '__match_args__', ())[i]) for i in _coconut.range({min_ind}, _coconut.len({item}.__match_args__)))".format(
                    temp_var=temp_var,
                    item=item,
                    min_ind=len(pos_matches),
                ),
            )
            with self.down_a_level():
                self.match(star_match, temp_var)

        # handle keyword args
        for name, match in name_matches.items():
            self.match_class_attr(match, name, item)

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
        # avoid checking >= 0
        elif len(pos_matches):
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
        is_data_result_var = self.get_temp_var()
        self.add_def(is_data_result_var + " = _coconut.getattr(" + item + ", '" + is_data_var + "', False)")

        if_data, if_class = self.branches(2)

        if_data.add_check(is_data_result_var)
        if_data.match_data(tokens, item)

        if_class.add_check("not " + is_data_result_var)
        if_class.match_class(tokens, item)

    def match_paren(self, tokens, item):
        """Matches a paren."""
        match, = tokens
        return self.match(match, item)

    def match_as(self, tokens, item):
        """Matches as patterns."""
        internal_assert(len(tokens) > 1, "invalid as match tokens", tokens)
        match, as_names = tokens[0], tokens[1:]
        for varname in as_names:
            self.match_var([varname], item, bind_wildcard=True)
        self.match(match, item)

    def match_isinstance_is(self, tokens, item):
        """Matches old-style isinstance checks."""
        internal_assert(len(tokens) > 1, "invalid isinstance is match tokens", tokens)
        match, isinstance_checks = tokens[0], tokens[1:]

        if "var" in match:
            varname, = match
            if len(isinstance_checks) == 1:
                alt_syntax = isinstance_checks[0] + "() as " + varname
            else:
                alt_syntax = "(" + " and ".join(s + "()" for s in isinstance_checks) + ") as " + varname
        else:
            varname = "..."
            alt_syntax = "... `isinstance` " + " `isinstance` ".join(isinstance_checks)
        isinstance_checks_str = varname + " is " + " is ".join(isinstance_checks)
        self.comp.strict_err_or_warn(
            "found deprecated isinstance-checking " + repr(isinstance_checks_str) + " pattern; use " + repr(alt_syntax) + " instead",
            self.original,
            self.loc,
        )

        for is_item in isinstance_checks:
            self.add_check("_coconut.isinstance(" + item + ", " + is_item + ")")
        self.match(match, item)

    def match_and(self, tokens, item):
        """Matches and."""
        for match in tokens:
            self.match(match, item)

    def match_or(self, tokens, item):
        """Matches or."""
        new_matchers = self.branches(len(tokens))
        for m, tok in zip(new_matchers, tokens):
            m.match(tok, item)

    def match_view(self, tokens, item):
        """Matches view patterns"""
        view_func, view_pattern = tokens

        func_result_var = self.get_temp_var()
        self.add_def(
            handle_indentation(
                """
try:
    {func_result_var} = ({view_func})({item})
except _coconut.Exception as _coconut_view_func_exc:
    if _coconut.getattr(_coconut_view_func_exc.__class__, "__name__", None) == "MatchError":
        {func_result_var} = _coconut_sentinel
    else:
        raise
            """,
            ).format(
                func_result_var=func_result_var,
                view_func=view_func,
                item=item,
            ),
        )

        with self.down_a_level():
            self.add_check(func_result_var + " is not _coconut_sentinel")
            self.match(view_pattern, func_result_var)

    def match_infix(self, tokens, item):
        """Matches infix patterns."""
        internal_assert(len(tokens) > 1 and len(tokens) % 2 == 1, "invalid infix match tokens", tokens)
        match = tokens[0]
        for i in range(1, len(tokens), 2):
            op, arg = tokens[i], tokens[i + 1]
            self.add_check("(" + op + ")(" + item + ", " + arg + ")")
        self.match(match, item)

    def match(self, tokens, item):
        """Performs pattern-matching processing."""
        for flag, get_handler in self.matchers.items():
            if flag in tokens:
                return get_handler(self)(tokens, item)
        raise CoconutInternalException("invalid pattern-matching tokens", tokens)

    def out(self):
        """Return pattern-matching code assuming check_var starts False."""
        out = []

        # set match_set_name_vars to sentinels
        for name in self.names:
            out.append(self.get_set_name_var(name) + " = _coconut_sentinel\n")

        # match checkdefs setting check_var
        closes = 0
        for checks, defs in self.checkdefs:
            if checks:
                out.append("if " + paren_join(checks, "and") + ":\n" + openindent)
                closes += 1
            if defs:
                out.append("\n".join(defs) + "\n")
        out.append(self.check_var + " = True\n" + closeindent * closes)

        # handle children
        for children in self.child_groups:
            out.append(
                handle_indentation(
                    """
if {check_var}:
    {check_var} = False
    {children}
                """,
                    add_newline=True,
                ).format(
                    check_var=self.check_var,
                    children="".join(child.out() for child in children),
                ),
            )

        # commit variable definitions
        name_set_code = []
        for name, val in self.names.items():
            name_set_code.append(
                handle_indentation(
                    """
if {set_name_var} is not _coconut_sentinel:
    {name} = {val}
                """,
                    add_newline=True,
                ).format(
                    set_name_var=self.get_set_name_var(name),
                    name=name,
                    val=val,
                ),
            )
        if name_set_code:
            out.append(
                handle_indentation(
                    """
if {check_var}:
    {name_set_code}
                """,
                ).format(
                    check_var=self.check_var,
                    name_set_code="".join(name_set_code),
                ),
            )

        # handle guards
        if self.guards:
            out.append(
                handle_indentation(
                    """
if {check_var} and not ({guards}):
    {check_var} = False
                """,
                    add_newline=True,
                ).format(
                    check_var=self.check_var,
                    guards=paren_join(self.guards, "and"),
                ),
            )

        return "".join(out)

    def build(self, stmts=None, set_check_var=True, invert=False):
        """Construct code for performing the match then executing stmts."""
        out = []
        if set_check_var:
            out.append(self.check_var + " = False\n")
        out.append(self.out())
        if stmts is not None:
            out.append("if " + ("not " if invert else "") + self.check_var + ":" + "\n" + openindent + "".join(stmts) + closeindent)
        return "".join(out)
