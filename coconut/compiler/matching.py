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

from coconut._pyparsing import ParseResults
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
    wildcard,
    openindent,
    closeindent,
    function_match_error_var,
    match_set_name_var,
    is_data_var,
    data_defaults_var,
    default_matcher_style,
    self_match_types,
    match_first_arg_var,
    match_to_args_var,
    match_to_kwargs_var,
)
from coconut.compiler.util import (
    paren_join,
    handle_indentation,
    add_int_and_strs,
    ordered,
    tuple_str_of,
)

# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


def get_match_names(match):
    """Gets keyword names for the given match."""
    internal_assert(not isinstance(match, str), "invalid match in get_match_names", match)
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
        (paren_match,) = match
        names += get_match_names(paren_match)
    elif "and" in match:
        for and_match in match:
            names += get_match_names(and_match)
    elif "infix" in match:
        infix_match = match[0]
        names += get_match_names(infix_match)
    elif "isinstance_is" in match:
        isinstance_is_match = match[0]
        names += get_match_names(isinstance_is_match)
    elif "class" in match or "data_or_class" in match:
        cls_name, class_matches = match
        if cls_name in self_match_types and len(class_matches) == 1 and len(class_matches[0]) == 1:
            names += get_match_names(class_matches[0][0])
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
        "name_list",
        "child_groups",
        "guards",
        "parent_names",
    )
    matchers = {
        "dict": lambda self: self.match_dict,
        "sequence": lambda self: self.match_sequence,
        "implicit_tuple": lambda self: self.match_implicit_tuple,
        "lazy": lambda self: self.match_lazy,
        "iter": lambda self: self.match_iter,
        "string_sequence": lambda self: self.match_string_sequence,
        "star": lambda self: self.match_star,
        "const": lambda self: self.match_const,
        "is": lambda self: self.match_is,
        "in": lambda self: self.match_in,
        "var": lambda self: self.match_var,
        "set": lambda self: self.match_set,
        "data": lambda self: self.match_data,
        "class": lambda self: self.match_class,
        "data_or_class": lambda self: self.match_data_or_class,
        "paren": lambda self: self.match_paren,
        "as": lambda self: self.match_as,
        "and": lambda self: self.match_and,
        "or": lambda self: self.match_or,
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

    def __init__(self, comp, original, loc, check_var, style=default_matcher_style, name_list=None, parent_names={}):
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
        self.parent_names = parent_names
        self.names = OrderedDict()  # ensures deterministic ordering of name setting code
        self.guards = []
        self.child_groups = []
        self.increment()

    def make_child(self):
        """Get an unregistered child matcher object."""
        return Matcher(self.comp, self.original, self.loc, self.check_var, self.style, self.name_list, self.names)

    def branches(self, num_branches):
        """Create num_branches child matchers, one of which must match for the parent match to succeed."""
        child_group = []
        for _ in range(num_branches):
            new_matcher = self.make_child()
            child_group.append(new_matcher)

        self.child_groups.append(child_group)
        return child_group

    def parameterized_branch(self, parameterization):
        """Create a pseudo-child-group parameterized by `for <parameterization>:`."""
        parameterized_child = self.make_child()
        self.child_groups.append((parameterization, parameterized_child))
        return parameterized_child

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

    def rule_conflict_warn(self, message, if_coconut=None, if_python=None, extra=None, only_strict=False):
        """Warns on conflicting style rules if callback was given."""
        if (
            self.style.endswith("warn") and (not only_strict or self.comp.strict)
            or self.style.endswith("strict") and self.comp.strict
        ):
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

    @contextmanager
    def down_to(self, pos):
        """Increment down to pos."""
        orig_pos = self.position
        self.set_position(max(orig_pos, pos))
        try:
            yield
        finally:
            self.set_position(orig_pos)

    @contextmanager
    def down_to_end(self):
        """Increment down until a new set of checkdefs is reached."""
        orig_pos = self.position
        self.set_position(len(self.checkdefs))
        try:
            yield
        finally:
            self.set_position(orig_pos)

    def get_temp_var(self):
        """Gets the next match_temp var."""
        return self.comp.get_temp_var("match_temp")

    def get_set_name_var(self, name):
        """Gets the var for checking whether a name should be set."""
        return match_set_name_var + "_" + name

    def register_name(self, name):
        """Register a new name at the current position."""
        internal_assert(lambda: name not in self.parent_names and name not in self.names, "attempt to register duplicate name", name)
        self.names[name] = self.position
        if self.name_list is not None and name not in self.name_list:
            self.name_list.append(name)

    def match_var(self, tokens, item, bind_wildcard=False):
        """Matches a variable."""
        varname, = tokens
        if varname == wildcard and not bind_wildcard:
            return
        set_name_var = self.get_set_name_var(varname)
        if varname in self.parent_names:
            # no need to increment if it's from the parent
            self.add_check(set_name_var + " == " + item)
        elif varname in self.names:
            var_pos = self.names[varname]
            with self.down_to(var_pos):
                self.add_check(set_name_var + " == " + item)
        else:
            self.add_def(set_name_var + " = " + item)
            with self.down_a_level():
                self.register_name(varname)

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

    def match_function(
        self,
        first_arg=match_first_arg_var,
        args=match_to_args_var,
        kwargs=match_to_kwargs_var,
        pos_only_match_args=(),
        match_args=(),
        star_arg=None,
        kwd_only_match_args=(),
        dubstar_arg=None,
    ):
        """Matches a pattern-matching function."""
        # before everything, pop the FunctionMatchError from context
        self.add_def(function_match_error_var + " = _coconut_get_function_match_error()")
        # and fix args to include first_arg, which we have to do to make super work
        self.add_def(
            handle_indentation(
                """
if {first_arg} is not _coconut_sentinel:
    {args} = ({first_arg},) + {args}
            """,
            ).format(
                first_arg=first_arg,
                args=args,
            ),
        )

        with self.down_a_level():

            self.match_in_args_kwargs(pos_only_match_args, match_args, args, kwargs, allow_star_args=star_arg is not None)

            if star_arg is not None:
                self.match(star_arg, args + "[" + str(len(match_args)) + ":]")

            self.match_in_kwargs(kwd_only_match_args, kwargs)

            # go down to end to ensure that all popping from kwargs has been done
            with self.down_to_end():
                if dubstar_arg is None:
                    self.add_check("not " + kwargs)
                else:
                    self.match(dubstar_arg, kwargs)

    def match_in_args_kwargs(self, pos_only_match_args, match_args, args, kwargs, allow_star_args=False):
        """Matches against args or kwargs."""
        req_len = 0
        arg_checks = {}
        # go down a level to ensure we're after the length-checking we do later on
        with self.down_a_level():
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
                        self.match(match, args + "[" + str(i) + "]")
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
                        with self.down_a_level():
                            self.match(match, tempvar)
                else:
                    if not names:
                        tempvar = self.get_temp_var()
                        self.add_def(tempvar + " = " + args + "[" + str(i) + "] if _coconut.len(" + args + ") > " + str(i) + " else " + default)
                        with self.down_a_level():
                            self.match(match, tempvar)
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
                        with self.down_a_level():
                            self.match(match, tempvar)

        # length checking
        max_len = None if allow_star_args else len(pos_only_match_args) + len(match_args)
        self.check_len_in(req_len, max_len, args)
        for i, (lt_check, ge_check) in ordered(arg_checks.items()):
            if i < req_len:
                if lt_check is not None:
                    self.add_check(lt_check)
            else:
                if ge_check is not None:
                    self.add_check(ge_check)

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
        if len(tokens) == 1:
            matches, rest = tokens[0], None
        else:
            matches, rest = tokens

        self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Mapping)")

        if rest is None:
            self.rule_conflict_warn(
                "found pattern with new behavior in Coconut v2; dict patterns now allow the dictionary being matched against to contain extra keys",
                extra="use explicit '{..., **_}' or '{..., **{}}' syntax to resolve",
                only_strict=True,
            )
            strict_len = not self.using_python_rules
        elif rest == "{}":
            strict_len = True
            rest = None
        else:
            strict_len = False

        if strict_len:
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
            rest_item = (
                "_coconut.dict((k, v) for k, v in "
                + item + ".items() if k not in _coconut.set(("
                + ", ".join(match_keys) + ("," if len(match_keys) == 1 else "")
                + ")))"
            )
            with self.down_a_level():
                self.match_var([rest], rest_item)

    def proc_sequence_match(self, tokens, iter_match=False):
        """Processes sequence match tokens."""
        seq_groups = []
        seq_type = None
        for group in tokens:
            if "capture" in group:
                group_type = "capture"
                if len(group) > 1:
                    raise CoconutDeferredSyntaxError("sequence/iterable patterns cannot contain multiple consecutive arbitrary-length captures", self.loc)
                group_contents = group[0]
            elif "literal" in group:
                group_type = "elem_matches"
                group_contents = []
                for seq_literal in group:
                    got_seq_type, matches = seq_literal
                    if not iter_match:
                        if seq_type is None:
                            seq_type = got_seq_type
                        elif got_seq_type != seq_type:
                            raise CoconutDeferredSyntaxError("list literals and tuple literals cannot be mixed in sequence patterns", self.loc)
                    group_contents.extend(matches)
            elif "elem" in group:
                group_type = "elem_matches"
                group_contents = group
            elif "string" in group:
                group_type = "string"
                for str_literal in group:
                    if str_literal.startswith("b"):
                        got_seq_type = 'b"'
                    else:
                        got_seq_type = '"'
                    if seq_type is None:
                        seq_type = got_seq_type
                    elif got_seq_type != seq_type:
                        raise CoconutDeferredSyntaxError("string literals and byte literals cannot be mixed in string patterns", self.loc)
                if len(group) == 1:
                    str_item = group[0]
                else:
                    str_item = self.comp.eval_now(" ".join(group))
                group_contents = (str_item, len(self.comp.literal_eval(str_item)))
            elif "f_string" in group:
                group_type = "f_string"
                # f strings are always unicode
                if seq_type is None:
                    seq_type = '"'
                elif seq_type != '"':
                    raise CoconutDeferredSyntaxError("string literals and byte literals cannot be mixed in string patterns", self.loc)
                internal_assert(len(group) == 1, "invalid f string sequence match group", group)
                str_item = group[0]
                group_contents = (str_item, "_coconut.len(" + str_item + ")")
            else:
                raise CoconutInternalException("invalid sequence match group", group)
            seq_groups.append((group_type, group_contents))
        return seq_type, seq_groups

    def handle_sequence(self, seq_type, seq_groups, item, iter_match=False):
        """Handle a processed sequence match."""
        # length check
        if not iter_match:
            min_len_int = 0
            min_len_strs = []
            bounded = True
            for gtype, gcontents in seq_groups:
                if gtype == "capture":
                    bounded = False
                elif gtype == "elem_matches":
                    min_len_int += len(gcontents)
                elif gtype == "string":
                    str_item, str_len = gcontents
                    min_len_int += str_len
                elif gtype == "f_string":
                    str_item, str_len = gcontents
                    min_len_strs.append(str_len)
                else:
                    raise CoconutInternalException("invalid sequence match group type", gtype)
            min_len = add_int_and_strs(min_len_int, min_len_strs)
            max_len = min_len if bounded else None
            self.check_len_in(min_len, max_len, item)

        # match head
        start_ind_int = 0
        start_ind_strs = []
        iterable_var = None
        if seq_groups[0][0] == "elem_matches":
            _, matches = seq_groups.pop(0)
            if not iter_match:
                self.match_all_in(matches, item)
            elif matches:
                iterable_var = self.get_temp_var()
                self.add_def(iterable_var + " = _coconut.iter(" + item + ")")
                head_var = self.get_temp_var()
                self.add_def(head_var + " = _coconut.tuple(_coconut_iter_getitem(" + iterable_var + ", _coconut.slice(None, " + str(len(matches)) + ")))")
                with self.down_a_level():
                    self.add_check("_coconut.len(" + head_var + ") == " + str(len(matches)))
                    self.match_all_in(matches, head_var)
            start_ind_int += len(matches)
        elif seq_groups[0][0] == "string":
            internal_assert(not iter_match, "cannot be both string and iter match")
            _, (str_item, str_len) = seq_groups.pop(0)
            if str_len > 0:
                self.add_check(item + ".startswith(" + str_item + ")")
            start_ind_int += str_len
        elif seq_groups[0][0] == "f_string":
            internal_assert(not iter_match, "cannot be both f string and iter match")
            _, (str_item, str_len) = seq_groups.pop(0)
            self.add_check(item + ".startswith(" + str_item + ")")
            start_ind_strs.append(str_len)
        if not seq_groups:
            return
        start_ind = add_int_and_strs(start_ind_int, start_ind_strs)

        # match tail
        last_ind_int = -1
        last_ind_strs = []
        if seq_groups[-1][0] == "elem_matches":
            internal_assert(not iter_match, "iter_match=True should not be passed for tail patterns")
            _, matches = seq_groups.pop()
            for i, match in enumerate(matches):
                self.match(match, item + "[-" + str(len(matches) - i) + "]")
            last_ind_int -= len(matches)
        elif seq_groups[-1][0] == "string":
            internal_assert(not iter_match, "cannot be both string and iter match")
            _, (str_item, str_len) = seq_groups.pop()
            if str_len > 0:
                self.add_check(item + ".endswith(" + str_item + ")")
            last_ind_int -= str_len
        elif seq_groups[-1][0] == "f_string":
            internal_assert(not iter_match, "cannot be both f string and iter match")
            _, (str_item, str_len) = seq_groups.pop()
            self.add_check(item + ".endswith(" + str_item + ")")
            last_ind_strs.append("-" + str_len)
        if not seq_groups:
            return
        last_ind = add_int_and_strs(last_ind_int, last_ind_strs)

        # we need to go down a level to ensure we're below 'match head' above
        with self.down_a_level():

            # extract middle
            cache_mid_item = False
            if iterable_var is None:

                # make middle by indexing into item
                start_ind_str = "" if start_ind == 0 else str(start_ind)
                last_ind_str = "" if last_ind == -1 else str(last_ind + 1) if isinstance(last_ind, int) else last_ind + " + 1"
                if start_ind_str or last_ind_str:
                    mid_item = item + "[" + start_ind_str + ":" + last_ind_str + "]"
                    cache_mid_item = True
                else:
                    mid_item = item

                # convert middle to proper sequence type if necessary
                if seq_type == "[":
                    mid_item = "_coconut.list(" + mid_item + ")"
                    cache_mid_item = True
                elif seq_type == "(":
                    mid_item = "_coconut.tuple(" + mid_item + ")"
                    cache_mid_item = True
                elif seq_type in (None, '"', 'b"', "(|"):
                    # if we know mid_item is already the desired type, no conversion is needed
                    pass
                elif seq_type is False:
                    raise CoconutInternalException("attempted to convert with to_sequence when seq_type was marked as False", mid_item)
                else:
                    raise CoconutInternalException("invalid sequence match type", seq_type)

            else:
                mid_item = iterable_var

            # cache middle
            if cache_mid_item:
                cached_mid_item = self.get_temp_var()
                self.add_def(cached_mid_item + " = " + mid_item)
                mid_item = cached_mid_item

            # we need to go down a level to ensure we're below 'cache middle' above
            with self.down_a_level():

                # handle single-capture middle
                if len(seq_groups) == 1:
                    gtype, match = seq_groups[0]
                    internal_assert(gtype == "capture", "invalid sequence match middle group", seq_groups)
                    self.match(match, mid_item)
                    return
                internal_assert(len(seq_groups) >= 3, "invalid sequence match middle groups", seq_groups)

                # handle linear search patterns
                if len(seq_groups) == 3:
                    (front_gtype, front_match), mid_group, (back_gtype, back_match) = seq_groups
                    internal_assert(front_gtype == "capture" == back_gtype, "invalid sequence match middle groups", seq_groups)
                    mid_gtype, mid_contents = mid_group

                    if iter_match:
                        internal_assert(mid_gtype == "elem_matches", "invalid iterable search match middle group", mid_group)
                        mid_len = len(mid_contents)
                        if mid_len == 0:
                            raise CoconutDeferredSyntaxError("found empty iterable search pattern", self.loc)

                        # ensure we have an iterable var to work with
                        if iterable_var is None:
                            iterable_var = self.get_temp_var()
                            self.add_def(iterable_var + " = _coconut.iter(" + mid_item + ")")

                        # create a cache variable to store elements so far
                        iter_cache_var = self.get_temp_var()
                        self.add_def(iter_cache_var + " = []")

                        # construct a parameterized child to perform the search
                        iter_item_var = self.get_temp_var()
                        parameterized_child = self.parameterized_branch(
                            "for {iter_item_var} in {iterable_var}".format(
                                iter_item_var=iter_item_var,
                                iterable_var=iterable_var,
                            ),
                        )
                        parameterized_child.add_def(iter_cache_var + ".append(" + iter_item_var + ")")
                        with parameterized_child.down_a_level():
                            parameterized_child.add_check("_coconut.len(" + iter_cache_var + ") >= " + str(mid_len))

                            # get the items to search against
                            front_item = "{iter_cache_var}[:-{mid_len}]".format(iter_cache_var=iter_cache_var, mid_len=mid_len)
                            searching_through = "{iter_cache_var}[-{mid_len}:]".format(iter_cache_var=iter_cache_var, mid_len=mid_len)
                            back_item = iterable_var

                            # perform the matches in the child
                            search_item = parameterized_child.get_temp_var()
                            parameterized_child.add_def(search_item + " = " + searching_through)
                            with parameterized_child.down_a_level():
                                parameterized_child.handle_sequence(seq_type, [mid_group], search_item)
                                # no need to make temp_vars here since these are guaranteed to be var matches
                                parameterized_child.match(front_match, front_item)
                                parameterized_child.match(back_match, back_item)

                    elif mid_gtype == "elem_matches":
                        mid_len = len(mid_contents)

                        # construct a parameterized child to perform the search
                        seq_ind_var = self.get_temp_var()
                        parameterized_child = self.parameterized_branch(
                            "for {seq_ind_var} in _coconut.range(_coconut.len({mid_item}))".format(
                                seq_ind_var=seq_ind_var,
                                mid_item=mid_item,
                            ),
                        )

                        # get the items to search against
                        front_item = "{mid_item}[:{seq_ind_var}]".format(
                            mid_item=mid_item,
                            seq_ind_var=seq_ind_var,
                        )
                        searching_through = "{mid_item}[{seq_ind_var}:{seq_ind_var} + {mid_len}]".format(
                            mid_item=mid_item,
                            seq_ind_var=seq_ind_var,
                            mid_len=mid_len,
                        )
                        back_item = "{mid_item}[{seq_ind_var} + {mid_len}:]".format(
                            mid_item=mid_item,
                            seq_ind_var=seq_ind_var,
                            mid_len=mid_len,
                        )

                        # perform the matches in the child
                        search_item = parameterized_child.get_temp_var()
                        parameterized_child.add_def(search_item + " = " + searching_through)
                        with parameterized_child.down_a_level():
                            parameterized_child.handle_sequence(seq_type, [mid_group], search_item)
                            # these are almost always var matches, so we don't bother to make new temp vars here
                            parameterized_child.match(front_match, front_item)
                            parameterized_child.match(back_match, back_item)

                    elif mid_gtype in ("string", "f_string"):
                        str_item, str_len = mid_contents
                        found_loc = self.get_temp_var()
                        self.add_def(found_loc + " = " + mid_item + ".find(" + str_item + ")")
                        with self.down_a_level():
                            self.add_check(found_loc + " != -1")
                            # no need to make temp_vars here since these are guaranteed to be var matches
                            self.match(front_match, "{mid_item}[:{found_loc}]".format(mid_item=mid_item, found_loc=found_loc))
                            self.match(back_match, "{mid_item}[{found_loc} + {str_len}:]".format(mid_item=mid_item, found_loc=found_loc, str_len=str_len))

                    else:
                        raise CoconutInternalException("invalid linear search group type", mid_gtype)
                    return

                # raise on unsupported quadratic matches
                raise CoconutDeferredSyntaxError("nonlinear sequence search patterns are not supported", self.loc)

    def match_sequence(self, tokens, item):
        """Matches an arbitrary sequence pattern."""
        internal_assert(len(tokens) >= 1, "invalid sequence match tokens", tokens)

        # abc check
        self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Sequence)")

        # extract groups
        seq_type, seq_groups = self.proc_sequence_match(tokens)

        # match sequence
        self.handle_sequence(seq_type, seq_groups, item)

    def match_lazy(self, tokens, item):
        """Matches lazy lists."""
        (seq_type, matches), = tokens
        internal_assert(seq_type == "(|", "invalid lazy list match tokens", tokens)

        # abc check
        self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Iterable)")

        # match sequence
        temp_item_var = self.get_temp_var()
        self.add_def(temp_item_var + " = _coconut.tuple(" + item + ")")
        with self.down_a_level():
            self.handle_sequence(False, [["elem_matches", matches]], temp_item_var)

    def match_implicit_tuple(self, tokens, item):
        """Matches an implicit tuple."""
        internal_assert(len(tokens) >= 1, "invalid implicit tuple tokens", tokens)

        # abc check
        self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Iterable)")

        # match sequence
        temp_item_var = self.get_temp_var()
        self.add_def(temp_item_var + " = _coconut.tuple(" + item + ")")
        with self.down_a_level():
            self.handle_sequence(False, [["elem_matches", tokens]], temp_item_var)

    def match_star(self, tokens, item):
        """Matches starred assignment."""
        internal_assert(len(tokens) >= 1, "invalid star match tokens", tokens)

        # abc check
        self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Iterable)")

        # extract groups
        _, seq_groups = self.proc_sequence_match(tokens)

        # match sequence
        temp_item_var = self.get_temp_var()
        self.add_def(temp_item_var + " = _coconut.list(" + item + ")")
        with self.down_a_level():
            self.handle_sequence(None, seq_groups, temp_item_var)

    def match_string_sequence(self, tokens, item):
        """Match string sequence patterns."""
        seq_type, seq_groups = self.proc_sequence_match(tokens)

        # type check
        if seq_type == '"':
            self.add_check("_coconut.isinstance(" + item + ", _coconut.str)")
        elif seq_type == 'b"':
            self.add_check("_coconut.isinstance(" + item + ", _coconut.bytes)")
        else:
            raise CoconutInternalException("invalid string match type", seq_type)

        # match sequence
        self.handle_sequence(seq_type, seq_groups, item)

    def match_iter(self, tokens, item):
        """Matches a chain."""
        internal_assert(len(tokens) >= 1, "invalid iterable match tokens", tokens)

        # abc check
        self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Iterable)")

        # match iterable
        _, seq_groups = self.proc_sequence_match(tokens, iter_match=True)
        if seq_groups[-1][0] == "elem_matches":  # tail pattern
            temp_item_var = self.get_temp_var()
            self.add_def(temp_item_var + " = _coconut.tuple(" + item + ")")
            with self.down_a_level():
                self.handle_sequence(None, seq_groups, temp_item_var)
        else:
            self.handle_sequence(None, seq_groups, item, iter_match=True)

    def match_const(self, tokens, item):
        """Matches an equality check."""
        match, = tokens
        self.add_check(item + " == " + match)

    def match_is(self, tokens, item):
        """Matches an identity check."""
        match, = tokens
        self.add_check(item + " is " + match)

    def match_in(self, tokens, item):
        """Matches a containment check."""
        match, = tokens
        self.add_check(item + " in " + match)

    def match_set(self, tokens, item):
        """Matches a set."""
        if len(tokens) == 2:
            letter_toks, match = tokens
            star = None
        else:
            letter_toks, match, star = tokens

        if letter_toks:
            letter, = letter_toks
        else:
            letter = "s"

        # process *() or *_
        if star is None:
            self.rule_conflict_warn(
                "found pattern with new behavior in Coconut v3; set patterns now allow the set being matched against to contain extra items",
                extra="use explicit '{..., *_}' or '{..., *()}' syntax to resolve",
            )
            strict_len = not self.using_python_rules
        elif star == wildcard:
            strict_len = False
        else:
            internal_assert(star == "()", "invalid set match tokens", tokens)
            strict_len = True

        # handle set letter
        if letter == "s":
            self.add_check("_coconut.isinstance(" + item + ", _coconut.abc.Set)")
        elif letter == "f":
            self.add_check("_coconut.isinstance(" + item + ", _coconut.frozenset)")
        elif letter == "m":
            self.add_check("_coconut.isinstance(" + item + ", _coconut.collections.Counter)")
        else:
            raise CoconutInternalException("invalid set match letter", letter)

        # match set contents
        if letter == "m":
            self.add_check("_coconut_multiset(" + tuple_str_of(match) + ") " + ("== " if strict_len else "<= ") + item)
        else:
            if strict_len:
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
            # positional arg
            if len(match_arg) == 1:
                match, = match_arg
                if star_match is not None:
                    raise CoconutDeferredSyntaxError("positional arg after starred arg in data/class match", self.loc)
                if name_matches:
                    raise CoconutDeferredSyntaxError("positional arg after keyword arg in data/class match", self.loc)
                pos_matches.append(match)
            # starred arg
            elif len(match_arg) == 2:
                internal_assert(match_arg[0] == "*", "invalid starred data/class match arg tokens", match_arg)
                _, match = match_arg
                if star_match is not None:
                    raise CoconutDeferredSyntaxError("duplicate starred arg in data/class match", self.loc)
                if name_matches:
                    raise CoconutDeferredSyntaxError("both starred arg and keyword arg in data/class match", self.loc)
                star_match = match
            # keyword arg
            else:
                if len(match_arg) == 3:
                    internal_assert(match_arg[1] == "=", "invalid keyword data/class match arg tokens", match_arg)
                    name, _, match = match_arg
                    strict = False
                elif len(match_arg) == 4:
                    internal_assert(match_arg[0] == "." and match_arg[2] == "=", "invalid strict keyword data/class match arg tokens", match_arg)
                    _, name, _, match = match_arg
                    strict = True
                else:
                    raise CoconutInternalException("invalid data/class match arg", match_arg)
                if star_match is not None:
                    raise CoconutDeferredSyntaxError("both keyword arg and starred arg in data/class match", self.loc)
                if name in name_matches:
                    raise CoconutDeferredSyntaxError("duplicate keyword arg {name!r} in data/class match".format(name=name), self.loc)
                name_matches[name] = (match, strict)

        return cls_name, pos_matches, name_matches, star_match

    def match_class_attr(self, match, attr, item):
        """Match an attribute for a class match where attr is an expression that evaluates to the attribute name."""
        attr_var = self.get_temp_var()
        self.add_def(attr_var + " = _coconut.getattr(" + item + ", " + attr + ", _coconut_sentinel)")
        with self.down_a_level():
            self.add_check(attr_var + " is not _coconut_sentinel")
            self.match(match, attr_var)

    def match_class_names(self, name_matches, item):
        """Matches keyword class patterns."""
        for name, (match, strict) in name_matches.items():
            if strict:
                self.match(match, item + "." + name)
            else:
                self.match_class_attr(match, ascii(name), item)

    def match_class(self, tokens, item):
        """Matches a class PEP-622-style."""
        cls_name, pos_matches, name_matches, star_match = self.split_data_or_class_match(tokens)

        self.add_check("_coconut.isinstance(" + item + ", " + cls_name + ")")

        self_match_matcher, other_cls_matcher = self.branches(2)

        # handle instances of _coconut_self_match_types
        self_match_matcher.add_check("_coconut.type(" + item + ") in _coconut_self_match_types")
        if pos_matches:
            if len(pos_matches) > 1:
                self_match_matcher.add_def(
                    handle_indentation(
                        """
raise _coconut.TypeError("too many positional args in class match (pattern requires {num_pos_matches}; '{cls_name}' only supports 1)")
                    """,
                    ).format(
                        num_pos_matches=len(pos_matches),
                        cls_name=cls_name,
                    ),
                )
            else:
                self_match_matcher.match(pos_matches[0], item)

        # handle all other classes
        other_cls_matcher.add_check("not _coconut.type(" + item + ") in _coconut_self_match_types")
        match_args_var = other_cls_matcher.get_temp_var()
        other_cls_matcher.add_def(
            handle_indentation("""
{match_args_var} = _coconut.getattr({cls_name}, '__match_args__', ()) {type_any} {type_ignore}
if not _coconut.isinstance({match_args_var}, _coconut.tuple):
    raise _coconut.TypeError("{cls_name}.__match_args__ must be a tuple")
if _coconut.len({match_args_var}) < {num_pos_matches}:
    raise _coconut.TypeError("too many positional args in class match (pattern requires {num_pos_matches}; '{cls_name}' only supports %s)" % (_coconut.len({match_args_var}),))
        """).format(
                cls_name=cls_name,
                match_args_var=match_args_var,
                num_pos_matches=len(pos_matches),
                type_any=self.comp.wrap_comment(" type: _coconut.typing.Any"),
                type_ignore=self.comp.type_ignore_comment(),
            ),
        )
        with other_cls_matcher.down_a_level():
            for i, match in enumerate(pos_matches):
                other_cls_matcher.match_class_attr(match, match_args_var + "[" + str(i) + "]", item)

        # handle starred arg
        if star_match is not None:
            star_match_var = self.get_temp_var()
            self.add_def(
                handle_indentation(
                    """
{match_args_var} = _coconut.getattr({cls_name}, '__match_args__', ())
{star_match_var} = _coconut.tuple(_coconut.getattr({item}, {match_args_var}[i]) for i in _coconut.range({num_pos_matches}, _coconut.len({match_args_var})))
                """,
                ).format(
                    match_args_var=self.get_temp_var(),
                    cls_name=cls_name,
                    star_match_var=star_match_var,
                    item=item,
                    num_pos_matches=len(pos_matches),
                ),
            )
            with self.down_a_level():
                self.match(star_match, star_match_var)

        # handle keyword args
        self.match_class_names(name_matches, item)

    def match_data(self, tokens, item):
        """Matches a data type."""
        cls_name, pos_matches, name_matches, star_match = self.split_data_or_class_match(tokens)

        self.add_check("_coconut.isinstance(" + item + ", " + cls_name + ")")

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

        # handle keyword args
        self.match_class_names(name_matches, item)

        # handle data types with defaults for some arguments
        if star_match is None:
            # use a def so we can type ignore it
            temp_var = self.get_temp_var()
            self.add_def(
                (
                    '{temp_var} ='
                    ' _coconut.len({item}) <= _coconut.max({min_len}, _coconut.len({item}.__match_args__))'
                    ' and _coconut.all('
                    'i in _coconut.getattr({item}, "{data_defaults_var}", {{}})'
                    ' and {item}[i] == _coconut.getattr({item}, "{data_defaults_var}", {{}})[i]'
                    ' for i in _coconut.range({min_len}, _coconut.len({item}.__match_args__))'
                    + (' if {item}.__match_args__[i] not in {name_matches}' if name_matches else '')
                    + ') if _coconut.hasattr({item}, "__match_args__")'
                    ' else _coconut.len({item}) == {min_len}'
                    ' {type_ignore}'
                ).format(
                    item=item,
                    temp_var=temp_var,
                    data_defaults_var=data_defaults_var,
                    min_len=len(pos_matches),
                    name_matches=tuple_str_of(name_matches, add_quotes=True),
                    type_ignore=self.comp.type_ignore_comment(),
                ),
            )
            with self.down_a_level():
                self.add_check(temp_var)

    def match_data_or_class(self, tokens, item):
        """Matches an ambiguous data or class match."""
        cls_name, matches = tokens

        is_data_result_var = self.get_temp_var()
        self.add_def(
            handle_indentation(
                """
{is_data_result_var} = _coconut.getattr({cls_name}, "{is_data_var}", False) or _coconut.isinstance({cls_name}, _coconut.tuple) and _coconut.all(_coconut.getattr(_coconut_x, "{is_data_var}", False) for _coconut_x in {cls_name}) {type_ignore}
            """,
            ).format(
                is_data_result_var=is_data_result_var,
                is_data_var=is_data_var,
                cls_name=cls_name,
                type_ignore=self.comp.type_ignore_comment(),
            ),
        )

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
        match, as_names = tokens[0], tokens[1:]
        for varname in as_names:
            self.match_var([varname], item, bind_wildcard=True)
        self.match(match, item)

    def match_isinstance_is(self, tokens, item):
        """Matches old-style isinstance checks."""
        match, isinstance_checks = tokens[0], tokens[1:]

        if "var" in match:
            varname, = match
        else:
            varname = "..."
        isinstance_checks_str = varname + " is " + " is ".join(isinstance_checks)
        cls_syntax = " and ".join(instcheck + "(" + varname + ")" for instcheck in isinstance_checks)
        explicit_syntax = " and ".join(varname + " `isinstance` " + instcheck for instcheck in isinstance_checks)
        self.comp.strict_err_or_warn(
            "found deprecated isinstance-checking " + repr(isinstance_checks_str) + " pattern;"
            " rewrite to use class patterns (try " + repr(cls_syntax) + ") or explicit isinstance-checking (" + repr(explicit_syntax) + " should always work)",
            self.original,
            self.loc,
        )

        for instcheck in isinstance_checks:
            self.add_check("_coconut.isinstance(" + item + ", " + instcheck + ")")
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
        match, infix_toks = tokens[0], tokens[1:]

        for toks in infix_toks:
            if len(toks) == 1:
                op, arg = toks[0], None
            else:
                op, arg = toks

            infix_check = "(" + op + ")(" + item
            if arg is not None:
                infix_check += ", " + arg
            infix_check += ")"
            self.add_check(infix_check)

        self.match(match, item)

    def make_match(self, flag, tokens):
        """Create an artificial match object."""
        return ParseResults(tokens, flag)

    def match(self, tokens, item):
        """Performs pattern-matching processing."""
        internal_assert(not isinstance(tokens, str), "invalid match tokens", tokens)
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
            internal_assert(children, "got child group with no children", self.child_groups)

            # handle parameterized child groups
            if isinstance(children[0], str):
                parameterization, child = children
                out.append(
                    handle_indentation(
                        """
if {check_var}:
    {check_var} = False
    {parameterization}:
        {child_checks}
        if {check_var}:
            break
                        """,
                        add_newline=True,
                    ).format(
                        check_var=self.check_var,
                        parameterization=parameterization,
                        child_checks=child.out().rstrip(),
                    ),
                )

            # handle normal child groups
            else:
                children_checks = "".join(
                    handle_indentation(
                        """
if not {check_var}:
    {child_out}
                        """,
                        add_newline=True,
                    ).format(
                        check_var=self.check_var,
                        child_out=child.out(),
                    ) for child in children
                )
                out.append(
                    handle_indentation(
                        """
if {check_var}:
    {check_var} = False
    {children_checks}
                        """,
                        add_newline=True,
                    ).format(
                        check_var=self.check_var,
                        children_checks=children_checks,
                    ),
                )

        # commit variable definitions
        name_set_code = []
        for name in self.names:
            name_set_code.append(
                handle_indentation(
                    """
if {set_name_var} is not _coconut_sentinel:
    {name} = {set_name_var}
                    """,
                    add_newline=True,
                ).format(
                    set_name_var=self.get_set_name_var(name),
                    name=name,
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
