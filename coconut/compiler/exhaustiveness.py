#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Authors: Claude
License: Apache 2.0
Description: Type-checker-only exhaustiveness checks for pattern-matching.

Coconut can't know the types of the things being matched, but type checkers can, so for
each match, we generate (behind "if TYPE_CHECKING:", so it never runs) a decision tree of
isinstance and literal checks over the subject and its fields that mirrors the cases. Every
path that ends in "pass" is definitely handled by some case, and at every point where
something might be left over, we pass the unhandled remainder to a checking function that
type checkers will reject if anything is in fact left over.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

from coconut.constants import (
    openindent,
    closeindent,
    strwrapper,
    self_match_types,
)

# -----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
# -----------------------------------------------------------------------------------------------------------------------

# the largest number of branches we'll generate for a single exhaustiveness check
max_exhaustiveness_branches = 128

# full mode: anything left over is an error (for --pure and assert_never)
total_check_func = "_coconut.match_must_be_total"

# case data mode: only case data variants left over are an error
case_data_check_func = "_coconut.match_must_handle_case_data"
case_data_leftover_func = "_coconut.case_data_leftover"

# never returns when given something with nothing left in it, telling type checkers that can't
#  otherwise tell (e.g. Pyright) that the code after it is unreachable
unhandled_func = "_coconut.match_unhandled"

# -----------------------------------------------------------------------------------------------------------------------
# COVERAGE:
# -----------------------------------------------------------------------------------------------------------------------


class Unanalyzable(Exception):
    """Raised when a pattern can't be expressed to a type checker."""


ANY = ("any",)


def is_any(cov):
    """Whether the given coverage matches everything."""
    return cov == ANY


def class_coverage(cls_name, pos_covs=(), kwd_covs=()):
    """Coverage of instances of cls_name whose positional fields match pos_covs and named fields match kwd_covs."""
    return ("class", cls_name, tuple(pos_covs), tuple(sorted(kwd_covs)))


def split_class_args(matches):
    """Split data/class pattern arguments into (positional patterns, {name: pattern}), raising Unanalyzable for anything else."""
    pos_matches = []
    name_matches = {}
    for match_arg in matches:
        if len(match_arg) == 1:
            match, = match_arg
            if name_matches:
                raise Unanalyzable()
            pos_matches.append(match)
        elif len(match_arg) == 2 and match_arg[0] in ("*", "**"):
            # starred arguments only count if they match anything
            _, match = match_arg
            if not is_any(pattern_coverage(match, ())):
                raise Unanalyzable()
        elif len(match_arg) == 3 and match_arg[1] == "=":
            name_grp, _, match = match_arg
            if len(name_grp) != 1:
                raise Unanalyzable()
            name, = name_grp
            name_matches[name] = match
        else:
            raise Unanalyzable()
    return pos_matches, name_matches


def pattern_coverage(tokens, data_type_names):
    """Get the coverage of the given pattern tokens: what values the pattern definitely matches."""
    if "var" in tokens:
        return ANY
    if "paren" in tokens:
        match, = tokens
        return pattern_coverage(match, data_type_names)
    if "as" in tokens:
        return pattern_coverage(tokens[0], data_type_names)
    if "and" in tokens:
        covs = [pattern_coverage(match, data_type_names) for match in tokens]
        non_any = [cov for cov in covs if not is_any(cov)]
        if len(non_any) > 1:
            raise Unanalyzable()
        return non_any[0] if non_any else ANY
    if "or" in tokens:
        covs = []
        for match in tokens:
            cov = pattern_coverage(match, data_type_names)
            if is_any(cov):
                return ANY
            covs.extend(cov[1] if cov[0] == "or" else [cov])
        return ("or", tuple(covs))
    if "is" in tokens:
        atom, = tokens
        if atom not in ("None", "True", "False"):
            raise Unanalyzable()
        return ("literal", " is ", atom)
    if "const" in tokens:
        const, = tokens
        # (strings have already been replaced by markers at this point)
        if const.startswith(strwrapper) or const.lstrip("-").replace(".", "", 1).isdigit():
            return ("literal", " == ", const)
        if "." in const and all(part.replace("_", "a").isalnum() and not part[:1].isdigit() for part in const.split(".")):
            # dotted names (e.g. enum members) are compared by identity, which type checkers narrow on
            return ("literal", " is ", const)
        raise Unanalyzable()
    if "isinstance_is" in tokens:
        match, isinstance_checks = tokens[0], tokens[1:]
        if len(isinstance_checks) != 1 or not is_any(pattern_coverage(match, data_type_names)):
            raise Unanalyzable()
        return class_coverage(isinstance_checks[0])
    if "data" in tokens or "class" in tokens or "data_or_class" in tokens:
        cls_name, matches = tokens
        pos_matches, name_matches = split_class_args(matches)
        pos_covs = [pattern_coverage(match, data_type_names) for match in pos_matches]
        kwd_covs = [(name, pattern_coverage(match, data_type_names)) for name, match in name_matches.items()]
        if any(not is_any(cov) for cov in pos_covs):
            # positional fields are only accessible (by index) for data types we know about
            if "class" in tokens or cls_name in self_match_types or cls_name not in data_type_names:
                raise Unanalyzable()
        return class_coverage(
            cls_name,
            [] if all(is_any(cov) for cov in pos_covs) else pos_covs,
            [(name, cov) for name, cov in kwd_covs if not is_any(cov)],
        )
    # sequence, mapping, string, view, search, etc. patterns can't be expressed to type checkers
    raise Unanalyzable()


# -----------------------------------------------------------------------------------------------------------------------
# DECISION TREES:
# -----------------------------------------------------------------------------------------------------------------------


def constructor_key(cov):
    """The constructor that the given (non-ANY, non-or) coverage tests for."""
    if cov[0] == "class":
        return ("class", cov[1])
    if cov[0] == "literal":
        return ("literal", cov[1], cov[2])
    raise Unanalyzable()


def expand_ors(rows, col):
    """Split rows with or-patterns in the given column into one row per alternative."""
    out = []
    for row in rows:
        if row[col][0] == "or":
            for alt in row[col][1]:
                out.append(row[:col] + (alt,) + row[col + 1:])
        else:
            out.append(row)
    return out


class TreeBuilder(object):
    """Builds the decision tree for an exhaustiveness check."""

    def __init__(self, check_func, data_type_names, get_temp_var, ln_marker=""):
        self.check_func = check_func
        self.data_type_names = data_type_names
        self.get_temp_var = get_temp_var
        self.ln_marker = ln_marker
        self.num_branches = 0

    def line(self, code):
        """A single line of code."""
        return code + self.ln_marker + "\n"

    def block(self, header, body):
        """An indented block of code."""
        self.num_branches += 1
        if self.num_branches > max_exhaustiveness_branches:
            raise Unanalyzable()
        return self.line(header) + openindent + body + closeindent

    def check(self, expr):
        """Check that nothing is left over in expr."""
        if self.check_func == case_data_check_func:
            return self.line(self.check_func + "(" + case_data_leftover_func + "(" + expr + "))")
        return self.line(self.check_func + "(" + expr + ")")

    def build(self, exprs, rows):
        """Build the decision tree for the given subject expressions and rows of coverages."""
        if not rows:
            return self.check(exprs[0])
        if all(is_any(cov) for cov in rows[0]):
            return self.line("pass")

        # split on the first column that the first row cares about
        col = next(i for i, cov in enumerate(rows[0]) if not is_any(cov))
        rows = expand_ors(rows, col)
        expr = exprs[col]

        # the constructors used in that column, in order
        keys = []
        key_covs = {}
        for row in rows:
            if not is_any(row[col]):
                key = constructor_key(row[col])
                if key not in key_covs:
                    keys.append(key)
                    key_covs[key] = []
                key_covs[key].append(row[col])

        # classes we don't know to be disjoint from others (e.g. base classes) are only safe when nothing needs splitting
        needs_splitting = any(cov[0] == "class" and (cov[2] or cov[3]) for covs in key_covs.values() for cov in covs)
        if needs_splitting:
            for key in keys:
                if key[0] == "class" and key[1] not in self.data_type_names and key[1] not in self_match_types:
                    raise Unanalyzable()

        out = []
        for i, key in enumerate(keys):
            if key[0] == "class":
                cls_name = key[1]
                cond = "_coconut.isinstance(" + expr + ", " + cls_name + ")"
                # the fields that rows for this class look at
                num_pos = max(len(cov[2]) for cov in key_covs[key])
                kwd_names = sorted(set(name for cov in key_covs[key] for name, _ in cov[3]))
                field_accesses = [expr + "[" + str(j) + "]" for j in range(num_pos)] + [expr + "." + name for name in kwd_names]
                # give each field a name, since not all type checkers can narrow e.g. x[0] directly
                field_exprs = [self.get_temp_var("exhaustiveness_field") for _ in field_accesses]
                field_defs = "".join(self.line(field_expr + " = " + access) for field_expr, access in zip(field_exprs, field_accesses))
                new_rows = []
                for row in rows:
                    cov = row[col]
                    if is_any(cov):
                        field_covs = (ANY,) * len(field_exprs)
                    elif constructor_key(cov) == key:
                        pos_covs = cov[2] + (ANY,) * (num_pos - len(cov[2]))
                        kwd_cov_dict = dict(cov[3])
                        field_covs = pos_covs + tuple(kwd_cov_dict.get(name, ANY) for name in kwd_names)
                    else:
                        continue
                    new_rows.append(row[:col] + field_covs + row[col + 1:])
                new_exprs = exprs[:col] + tuple(field_exprs) + exprs[col + 1:]
            else:
                _, op, value = key
                cond = expr + op + value
                new_rows = [row[:col] + row[col + 1:] for row in rows if is_any(row[col]) or constructor_key(row[col]) == key]
                new_exprs = exprs[:col] + exprs[col + 1:]
                field_defs = ""
            if not new_exprs:
                body = self.line("pass")
            elif new_rows and all(is_any(cov) for cov in new_rows[0]):
                # (no need to name the fields if nothing is going to check them)
                body = self.build(new_exprs, new_rows)
            else:
                body = field_defs + self.build(new_exprs, new_rows)
            out.append(self.block(("if " if i == 0 else "elif ") + cond + ":", body))

        # everything else in this column
        default_rows = [row[:col] + row[col + 1:] for row in rows if is_any(row[col])]
        default_exprs = exprs[:col] + exprs[col + 1:]
        if default_rows:
            if default_exprs:
                # if nothing can get here, then the other columns don't need checking here
                default_body = self.line(unhandled_func + "(" + expr + ")") + self.build(default_exprs, default_rows)
            else:
                default_body = self.line("pass")
        else:
            default_body = self.check(expr)
        out.append(self.block("else:", default_body) if keys else default_body)
        return "".join(out)


def exhaustiveness_tree(subject_exprs, case_patterns, total, data_type_names, get_temp_var, ln_marker=""):
    """Get the decision tree code checking that the given cases handle everything they should.

    case_patterns is a list of lists of pattern tokens (one per subject expression), or None for
    a case that handles nothing (e.g. one with a guard). If total, anything left over is an error;
    otherwise, only case data variants left over are an error. Returns None if no check is needed
    (the cases are trivially exhaustive) or the check can't be done."""
    try:
        rows = []
        for patterns in case_patterns:
            if patterns is None:
                continue
            rows.append(tuple(pattern_coverage(pattern, data_type_names) for pattern in patterns))
        # trivially exhaustive matches don't need checking
        if any(all(is_any(cov) for cov in row) for row in rows):
            return None
        builder = TreeBuilder(total_check_func if total else case_data_check_func, data_type_names, get_temp_var, ln_marker)
        return builder.build(tuple(subject_exprs), rows)
    except Unanalyzable:
        return None


def exhaustiveness_check(subject_exprs, case_patterns, total, data_type_names, get_temp_var, ln_marker=""):
    """Same as exhaustiveness_tree, but wrapped in "if TYPE_CHECKING:" so that it never runs."""
    tree = exhaustiveness_tree(subject_exprs, case_patterns, total, data_type_names, get_temp_var, ln_marker)
    if tree is None:
        return None
    return "if TYPE_CHECKING:" + ln_marker + "\n" + openindent + tree + closeindent
