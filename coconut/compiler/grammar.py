#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Defines the Coconut grammar.
"""

# Table of Contents:
#   - Imports
#   - Helpers
#   - Handlers
#   - Main Grammar
#   - Extra Grammar
#   - Tracing

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import re
from functools import reduce

from coconut._pyparsing import (
    CaselessLiteral,
    Forward,
    Group,
    Literal,
    OneOrMore,
    Optional,
    ParserElement,
    StringEnd,
    StringStart,
    Word,
    ZeroOrMore,
    hexnums,
    nums,
    originalTextFor,
    nestedExpr,
    FollowedBy,
)
from coconut.exceptions import (
    CoconutInternalException,
    CoconutDeferredSyntaxError,
)
from coconut.terminal import (
    trace,
    internal_assert,
)
from coconut.constants import (
    openindent,
    closeindent,
    strwrapper,
    unwrapper,
    keywords,
    const_vars,
    reserved_vars,
    none_coalesce_var,
    func_var,
)
from coconut.compiler.util import (
    CustomCombine as Combine,
    attach,
    fixto,
    addspace,
    condense,
    maybeparens,
    tokenlist,
    itemlist,
    longest,
    exprlist,
    join_args,
    disable_inside,
    disable_outside,
    final,
    split_trailing_indent,
    split_leading_indent,
    collapse_indents,
    keyword,
    match_in,
    disallow_keywords,
    regex_item,
    stores_loc_item,
)

# end: IMPORTS
# -----------------------------------------------------------------------------------------------------------------------
# HELPERS:
# -----------------------------------------------------------------------------------------------------------------------


def split_function_call(tokens, loc):
    """Split into positional arguments and keyword arguments."""
    pos_args = []
    star_args = []
    kwd_args = []
    dubstar_args = []
    for arg in tokens:
        argstr = "".join(arg)
        if len(arg) == 1:
            if star_args or kwd_args or dubstar_args:
                raise CoconutDeferredSyntaxError("positional arguments must come first", loc)
            pos_args.append(argstr)
        elif len(arg) == 2:
            if arg[0] == "*":
                if kwd_args or dubstar_args:
                    raise CoconutDeferredSyntaxError("star unpacking must come before keyword arguments", loc)
                star_args.append(argstr)
            elif arg[0] == "**":
                dubstar_args.append(argstr)
            else:
                kwd_args.append(argstr)
        else:
            raise CoconutInternalException("invalid function call argument", arg)
    return pos_args, star_args, kwd_args, dubstar_args


def attrgetter_atom_split(tokens):
    """Split attrgetter_atom_tokens into (attr_or_method_name, method_args_or_none_if_attr)."""
    if len(tokens) == 1:  # .attr
        return tokens[0], None
    elif len(tokens) >= 2 and tokens[1] == "(":  # .method(...
        if len(tokens) == 2:  # .method()
            return tokens[0], ""
        elif len(tokens) == 3:  # .method(args)
            return tokens[0], tokens[2]
        else:
            raise CoconutInternalException("invalid methodcaller literal tokens", tokens)
    else:
        raise CoconutInternalException("invalid attrgetter literal tokens", tokens)


def pipe_item_split(tokens, loc):
    """Process a pipe item, which could be a partial, an attribute access, a method call, or an expression.
    Return (type, split) where split is
        - (expr,) for expression,
        - (func, pos_args, kwd_args) for partial,
        - (name, args) for attr/method, and
        - (op, args) for itemgetter."""
    # list implies artificial tokens, which must be expr
    if isinstance(tokens, list) or "expr" in tokens:
        internal_assert(len(tokens) == 1, "invalid expr pipe item tokens", tokens)
        return "expr", (tokens[0],)
    elif "partial" in tokens:
        func, args = tokens
        pos_args, star_args, kwd_args, dubstar_args = split_function_call(args, loc)
        return "partial", (func, join_args(pos_args, star_args), join_args(kwd_args, dubstar_args))
    elif "attrgetter" in tokens:
        name, args = attrgetter_atom_split(tokens)
        return "attrgetter", (name, args)
    elif "itemgetter" in tokens:
        op, args = tokens
        return "itemgetter", (op, args)
    else:
        raise CoconutInternalException("invalid pipe item tokens", tokens)


def infix_error(tokens):
    """Raise inner infix error."""
    raise CoconutInternalException("invalid inner infix tokens", tokens)


def get_infix_items(tokens, callback=infix_error):
    """Perform infix token processing.

    Takes a callback that (takes infix tokens and returns a string) to handle inner infix calls.
    """
    internal_assert(len(tokens) >= 3, "invalid infix tokens", tokens)
    (arg1, func, arg2), tokens = tokens[:3], tokens[3:]
    args = list(arg1) + list(arg2)
    while tokens:
        args = [callback([args, func, []])]
        (func, newarg), tokens = tokens[:2], tokens[2:]
        args += list(newarg)
    return func, args


def pipe_info(op):
    """Returns (direction, stars, None-aware) where direction is 'forwards' or 'backwards'.
    Works with normal pipe operators and composition pipe operators."""
    none_aware = "?" in op
    stars = op.count("*")
    if not 0 <= stars <= 2:
        raise CoconutInternalException("invalid stars in pipe operator", op)
    if ">" in op:
        direction = "forwards"
    elif "<" in op:
        direction = "backwards"
    else:
        raise CoconutInternalException("invalid direction in pipe operator", op)
    return direction, stars, none_aware


# end: HELPERS
# -----------------------------------------------------------------------------------------------------------------------
# HANDLERS:
# -----------------------------------------------------------------------------------------------------------------------


def add_paren_handle(tokens):
    """Add parentheses."""
    internal_assert(len(tokens) == 1, "invalid tokens for parentheses adding", tokens)
    return "(" + tokens[0] + ")"


def function_call_handle(loc, tokens):
    """Enforce properly ordered function parameters."""
    return "(" + join_args(*split_function_call(tokens, loc)) + ")"


def item_handle(loc, tokens):
    """Process trailers."""
    out = tokens.pop(0)
    for i, trailer in enumerate(tokens):
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
            elif trailer[0] == "type:[]":
                out = "_coconut.typing.Sequence[" + out + "]"
            elif trailer[0] == "type:$[]":
                out = "_coconut.typing.Iterable[" + out + "]"
            elif trailer[0] == "type:?":
                out = "_coconut.typing.Optional[" + out + "]"
            elif trailer[0] == "?":
                # short-circuit the rest of the evaluation
                rest_of_trailers = tokens[i + 1:]
                if len(rest_of_trailers) == 0:
                    raise CoconutDeferredSyntaxError("None-coalescing ? must have something after it", loc)
                not_none_tokens = [none_coalesce_var]
                not_none_tokens.extend(rest_of_trailers)
                return "(lambda {x}: None if {x} is None else {rest})({inp})".format(
                    x=none_coalesce_var,
                    rest=item_handle(loc, not_none_tokens),
                    inp=out,
                )
            else:
                raise CoconutInternalException("invalid trailer symbol", trailer[0])
        elif len(trailer) == 2:
            if trailer[0] == "$[":
                out = "_coconut_igetitem(" + out + ", " + trailer[1] + ")"
            elif trailer[0] == "$(":
                args = trailer[1][1:-1]
                if not args:
                    raise CoconutDeferredSyntaxError("a partial application argument is required", loc)
                out = "_coconut.functools.partial(" + out + ", " + args + ")"
            elif trailer[0] == "$[":
                out = "_coconut_igetitem(" + out + ", " + trailer[1] + ")"
            elif trailer[0] == "$(?":
                pos_args, star_args, kwd_args, dubstar_args = split_function_call(trailer[1], loc)
                extra_args_str = join_args(star_args, kwd_args, dubstar_args)
                argdict_pairs = []
                has_question_mark = False
                for i, arg in enumerate(pos_args):
                    if arg == "?":
                        has_question_mark = True
                    else:
                        argdict_pairs.append(str(i) + ": " + arg)
                if not has_question_mark:
                    raise CoconutInternalException("no question mark in question mark partial", trailer[1])
                elif argdict_pairs or extra_args_str:
                    out = (
                        "_coconut_partial("
                        + out
                        + ", {" + ", ".join(argdict_pairs) + "}"
                        + ", " + str(len(pos_args))
                        + (", " if extra_args_str else "") + extra_args_str
                        + ")"
                    )
                else:
                    raise CoconutDeferredSyntaxError("a non-? partial application argument is required", loc)
            else:
                raise CoconutInternalException("invalid special trailer", trailer[0])
        else:
            raise CoconutInternalException("invalid trailer tokens", trailer)
    return out


item_handle.ignore_one_token = True


def pipe_handle(loc, tokens, **kwargs):
    """Process pipe calls."""
    internal_assert(set(kwargs) <= set(("top",)), "unknown pipe_handle keyword arguments", kwargs)
    top = kwargs.get("top", True)
    if len(tokens) == 1:
        item = tokens.pop()
        if not top:  # defer to other pipe_handle call
            return item

        # we've only been given one operand, so we can't do any optimization, so just produce the standard object
        name, split_item = pipe_item_split(item, loc)
        if name == "expr":
            internal_assert(len(split_item) == 1)
            return split_item[0]
        elif name == "partial":
            internal_assert(len(split_item) == 3)
            return "_coconut.functools.partial(" + join_args(split_item) + ")"
        elif name == "attrgetter":
            return attrgetter_atom_handle(loc, item)
        elif name == "itemgetter":
            return itemgetter_handle(item)
        else:
            raise CoconutInternalException("invalid split pipe item", split_item)

    else:
        item, op = tokens.pop(), tokens.pop()
        direction, stars, none_aware = pipe_info(op)
        star_str = "*" * stars

        if direction == "backwards":
            # for backwards pipes, we just reuse the machinery for forwards pipes
            inner_item = pipe_handle(loc, tokens, top=False)
            if isinstance(inner_item, str):
                inner_item = [inner_item]  # artificial pipe item
            return pipe_handle(loc, [item, "|" + ("?" if none_aware else "") + star_str + ">", inner_item])

        elif none_aware:
            # for none_aware forward pipes, we wrap the normal forward pipe in a lambda
            return "(lambda {x}: None if {x} is None else {pipe})({subexpr})".format(
                x=none_coalesce_var,
                pipe=pipe_handle(loc, [[none_coalesce_var], "|" + star_str + ">", item]),
                subexpr=pipe_handle(loc, tokens),
            )

        elif direction == "forwards":
            # if this is an implicit partial, we have something to apply it to, so optimize it
            name, split_item = pipe_item_split(item, loc)
            subexpr = pipe_handle(loc, tokens)

            if name == "expr":
                func, = split_item
                return "({f})({stars}{x})".format(f=func, stars=star_str, x=subexpr)
            elif name == "partial":
                func, partial_args, partial_kwargs = split_item
                return "({f})({args})".format(f=func, args=join_args((partial_args, star_str + subexpr, partial_kwargs)))
            elif name == "attrgetter":
                attr, method_args = split_item
                call = "(" + method_args + ")" if method_args is not None else ""
                if stars:
                    raise CoconutDeferredSyntaxError("cannot star pipe into attribute access or method call", loc)
                return "({x}).{attr}{call}".format(x=subexpr, attr=attr, call=call)
            elif name == "itemgetter":
                op, args = split_item
                if stars:
                    raise CoconutDeferredSyntaxError("cannot star pipe into item getting", loc)
                if op == "[":
                    fmtstr = "({x})[{args}]"
                elif op == "$[":
                    fmtstr = "_coconut_igetitem({x}, ({args}))"
                else:
                    raise CoconutInternalException("pipe into invalid implicit itemgetter operation", op)
                return fmtstr.format(x=subexpr, args=args)
            else:
                raise CoconutInternalException("invalid split pipe item", split_item)

        else:
            raise CoconutInternalException("invalid pipe operator direction", direction)


def comp_pipe_handle(loc, tokens):
    """Process pipe function composition."""
    internal_assert(len(tokens) >= 3 and len(tokens) % 2 == 1, "invalid composition pipe tokens", tokens)
    funcs = [tokens[0]]
    stars_per_func = []
    direction = None
    for i in range(1, len(tokens), 2):
        op, fn = tokens[i], tokens[i + 1]
        new_direction, stars, none_aware = pipe_info(op)
        if none_aware:
            raise CoconutInternalException("found unsupported None-aware composition pipe")
        if direction is None:
            direction = new_direction
        elif new_direction != direction:
            raise CoconutDeferredSyntaxError("cannot mix function composition pipe operators with different directions", loc)
        funcs.append(fn)
        stars_per_func.append(stars)
    if direction == "backwards":
        funcs.reverse()
        stars_per_func.reverse()
    func = funcs.pop(0)
    funcstars = zip(funcs, stars_per_func)
    return "_coconut_base_compose(" + func + ", " + ", ".join(
        "(%s, %s)" % (f, star) for f, star in funcstars
    ) + ")"


def none_coalesce_handle(tokens):
    """Process the None-coalescing operator."""
    if len(tokens) == 1:
        return tokens[0]
    elif tokens[0] == "None":
        return none_coalesce_handle(tokens[1:])
    elif match_in(Grammar.just_non_none_atom, tokens[0]):
        return tokens[0]
    elif tokens[0].isalnum():
        return "({b} if {a} is None else {a})".format(
            a=tokens[0],
            b=none_coalesce_handle(tokens[1:]),
        )
    else:
        return "(lambda {x}: {b} if {x} is None else {x})({a})".format(
            x=none_coalesce_var,
            a=tokens[0],
            b=none_coalesce_handle(tokens[1:]),
        )


none_coalesce_handle.ignore_one_token = True


def attrgetter_atom_handle(loc, tokens):
    """Process attrgetter literals."""
    name, args = attrgetter_atom_split(tokens)
    if args is None:
        return '_coconut.operator.attrgetter("' + name + '")'
    elif "." in name:
        raise CoconutDeferredSyntaxError("cannot have attribute access in implicit methodcaller partial", loc)
    elif args == "":
        return '_coconut.operator.methodcaller("' + tokens[0] + '")'
    else:
        return '_coconut.operator.methodcaller("' + tokens[0] + '", ' + tokens[2] + ")"


def lazy_list_handle(tokens):
    """Process lazy lists."""
    if len(tokens) == 0:
        return "_coconut_reiterable(())"
    else:
        return "_coconut_reiterable({func_var}() for {func_var} in ({lambdas}{tuple_comma}))".format(
            func_var=func_var,
            lambdas="lambda: " + ", lambda: ".join(tokens),
            tuple_comma="," if len(tokens) == 1 else "",
        )


def chain_handle(tokens):
    """Process chain calls."""
    if len(tokens) == 1:
        return tokens[0]
    else:
        return "_coconut.itertools.chain.from_iterable(" + lazy_list_handle(tokens) + ")"


chain_handle.ignore_one_token = True


def infix_handle(tokens):
    """Process infix calls."""
    func, args = get_infix_items(tokens, callback=infix_handle)
    return "(" + func + ")(" + ", ".join(args) + ")"


def op_funcdef_handle(tokens):
    """Process infix defs."""
    func, base_args = get_infix_items(tokens)
    args = []
    for arg in base_args[:-1]:
        rstrip_arg = arg.rstrip()
        if not rstrip_arg.endswith(unwrapper):
            if not rstrip_arg.endswith(","):
                arg += ", "
            elif arg.endswith(","):
                arg += " "
        args.append(arg)
    last_arg = base_args[-1]
    if last_arg.rstrip().endswith(","):
        last_arg = last_arg.rsplit(",")[0]
    args.append(last_arg)
    return func + "(" + "".join(args) + ")"


def lambdef_handle(tokens):
    """Process lambda calls."""
    if len(tokens) == 0:
        return "lambda:"
    elif len(tokens) == 1:
        return "lambda " + tokens[0] + ":"
    else:
        raise CoconutInternalException("invalid lambda tokens", tokens)


def typedef_callable_handle(tokens):
    """Process -> to Callable inside type annotations."""
    if len(tokens) == 1:
        return '_coconut.typing.Callable[..., ' + tokens[0] + ']'
    elif len(tokens) == 2:
        return '_coconut.typing.Callable[[' + tokens[0] + '], ' + tokens[1] + ']'
    else:
        raise CoconutInternalException("invalid Callable typedef tokens", tokens)


def make_suite_handle(tokens):
    """Make simple statements into suites."""
    internal_assert(len(tokens) == 1, "invalid simple suite tokens", tokens)
    return "\n" + openindent + tokens[0] + closeindent


def invalid_return_stmt_handle(_, loc, __):
    """Raise a syntax error if encountered a return statement where an implicit return is expected."""
    raise CoconutDeferredSyntaxError("Expected expression but got return statement", loc)


def implicit_return_handle(tokens):
    """Add an implicit return."""
    internal_assert(len(tokens) == 1, "invalid implicit return tokens", tokens)
    return "return " + tokens[0]


def math_funcdef_handle(tokens):
    """Process assignment function definition."""
    internal_assert(len(tokens) == 2, "invalid assignment function definition tokens", tokens)
    return tokens[0] + ("" if tokens[1].startswith("\n") else " ") + tokens[1]


def except_handle(tokens):
    """Process except statements."""
    if len(tokens) == 1:
        errs, asname = tokens[0], None
    elif len(tokens) == 2:
        errs, asname = tokens
    else:
        raise CoconutInternalException("invalid except tokens", tokens)
    out = "except "
    if "list" in tokens:
        out += "(" + errs + ")"
    else:
        out += errs
    if asname is not None:
        out += " as " + asname
    return out


def subscriptgroup_handle(tokens):
    """Process subscriptgroups."""
    internal_assert(0 < len(tokens) <= 3, "invalid slice args", tokens)
    args = []
    for arg in tokens:
        if not arg:
            arg = "None"
        args.append(arg)
    if len(args) == 1:
        return args[0]
    else:
        return "_coconut.slice(" + ", ".join(args) + ")"


def itemgetter_handle(tokens):
    """Process implicit itemgetter partials."""
    internal_assert(len(tokens) == 2, "invalid implicit itemgetter args", tokens)
    op, args = tokens
    if op == "[":
        return "_coconut.operator.itemgetter((" + args + "))"
    elif op == "$[":
        return "_coconut.functools.partial(_coconut_igetitem, index=(" + args + "))"
    else:
        raise CoconutInternalException("invalid implicit itemgetter type", op)


def class_suite_handle(tokens):
    """Process implicit pass in class suite."""
    internal_assert(len(tokens) == 1, "invalid implicit pass in class suite tokens", tokens)
    return ": pass" + tokens[0]


def simple_kwd_assign_handle(tokens):
    """Process inline nonlocal and global statements."""
    if len(tokens) == 1:
        return tokens[0]
    elif len(tokens) == 2:
        return tokens[0] + "\n" + tokens[0] + " = " + tokens[1]
    else:
        raise CoconutInternalException("invalid in-line nonlocal / global tokens", tokens)


simple_kwd_assign_handle.ignore_one_token = True


def compose_item_handle(tokens):
    """Process function composition."""
    if len(tokens) == 1:
        return tokens[0]
    internal_assert(len(tokens) >= 1, "invalid function composition tokens", tokens)
    return "_coconut_forward_compose(" + ", ".join(reversed(tokens)) + ")"


compose_item_handle.ignore_one_token = True


def impl_call_item_handle(tokens):
    """Process implicit function application."""
    internal_assert(len(tokens) > 1, "invalid implicit function application tokens", tokens)
    return tokens[0] + "(" + ", ".join(tokens[1:]) + ")"


def tco_return_handle(tokens):
    """Process tail-call-optimizable return statements."""
    internal_assert(len(tokens) >= 1, "invalid tail-call-optimizable return statement tokens", tokens)
    if len(tokens) == 1:
        return "return _coconut_tail_call(" + tokens[0] + ")"
    else:
        return "return _coconut_tail_call(" + tokens[0] + ", " + ", ".join(tokens[1:]) + ")"


def split_func_handle(tokens):
    """Process splitting a function into name, params, and args."""
    internal_assert(len(tokens) == 2, "invalid function definition splitting tokens", tokens)
    func_name, func_arg_tokens = tokens
    func_args = []
    func_params = []
    for arg in func_arg_tokens:
        if len(arg) > 1 and arg[0] in ("*", "**"):
            func_args.append(arg[1])
        elif arg[0] != "*":
            func_args.append(arg[0])
        func_params.append("".join(arg))
    return [
        func_name,
        ", ".join(func_args),
        "(" + ", ".join(func_params) + ")",
    ]


def join_match_funcdef(tokens):
    """Join the pieces of a pattern-matching function together."""
    if len(tokens) == 2:
        (func, insert_after_docstring), body = tokens
        docstring = None
    elif len(tokens) == 3:
        (func, insert_after_docstring), docstring, body = tokens
    else:
        raise CoconutInternalException("invalid docstring insertion tokens", tokens)
    # insert_after_docstring and body are their own self-contained suites, but we
    # expect them to both be one suite, so we have to join them together
    insert_after_docstring, dedent = split_trailing_indent(insert_after_docstring)
    indent, body = split_leading_indent(body)
    indentation = collapse_indents(dedent + indent)
    return (
        func
        + (docstring if docstring is not None else "")
        + insert_after_docstring
        + indentation
        + body
    )


def where_handle(tokens):
    """Process where statements."""
    internal_assert(len(tokens) == 2, "invalid where statement tokens", tokens)
    final_stmt, init_stmts = tokens
    return "".join(init_stmts) + final_stmt + "\n"


# end: HANDLERS
# -----------------------------------------------------------------------------------------------------------------------
# MAIN GRAMMAR:
# -----------------------------------------------------------------------------------------------------------------------


class Grammar(object):
    """Coconut grammar specification."""

    comma = Literal(",")
    dubstar = Literal("**")
    star = ~dubstar + Literal("*")
    at = Literal("@")
    arrow = Literal("->") | fixto(Literal("\u2192"), "->")
    unsafe_dubcolon = Literal("::")
    unsafe_colon = Literal(":")
    colon = ~unsafe_dubcolon + unsafe_colon
    colon_eq = Literal(":=")
    semicolon = Literal(";")
    eq = Literal("==")
    equals = ~eq + Literal("=")
    lbrack = Literal("[")
    rbrack = Literal("]")
    lbrace = Literal("{")
    rbrace = Literal("}")
    lbanana = Literal("(|") + ~Word(")>*?", exact=1)
    rbanana = Literal("|)")
    lparen = ~lbanana + Literal("(")
    rparen = Literal(")")
    unsafe_dot = Literal(".")
    dot = ~Literal("..") + unsafe_dot
    plus = Literal("+")
    minus = ~Literal("->") + Literal("-")
    dubslash = Literal("//")
    slash = ~dubslash + Literal("/")
    pipe = Literal("|>") | fixto(Literal("\u21a6"), "|>")
    star_pipe = Literal("|*>") | fixto(Literal("*\u21a6"), "|*>")
    dubstar_pipe = Literal("|**>") | fixto(Literal("**\u21a6"), "|**>")
    back_pipe = Literal("<|") | fixto(Literal("\u21a4"), "<|")
    back_star_pipe = Literal("<*|") | ~Literal("\u21a4**") + fixto(Literal("\u21a4*"), "<*|")
    back_dubstar_pipe = Literal("<**|") | fixto(Literal("\u21a4**"), "<**|")
    none_pipe = Literal("|?>") | fixto(Literal("?\u21a6"), "|?>")
    none_star_pipe = Literal("|?*>") | fixto(Literal("?*\u21a6"), "|?*>")
    none_dubstar_pipe = Literal("|?**>") | fixto(Literal("?**\u21a6"), "|?**>")
    dotdot = (
        ~Literal("...") + ~Literal("..>") + ~Literal("..*>") + Literal("..")
        | ~Literal("\u2218>") + ~Literal("\u2218*>") + fixto(Literal("\u2218"), "..")
    )
    comp_pipe = Literal("..>") | fixto(Literal("\u2218>"), "..>")
    comp_back_pipe = Literal("<..") | fixto(Literal("<\u2218"), "<..")
    comp_star_pipe = Literal("..*>") | fixto(Literal("\u2218*>"), "..*>")
    comp_back_star_pipe = Literal("<*..") | fixto(Literal("<*\u2218"), "<*..")
    comp_dubstar_pipe = Literal("..**>") | fixto(Literal("\u2218**>"), "..**>")
    comp_back_dubstar_pipe = Literal("<**..") | fixto(Literal("<**\u2218"), "<**..")
    amp = Literal("&") | fixto(Literal("\u2227") | Literal("\u2229"), "&")
    caret = Literal("^") | fixto(Literal("\u22bb") | Literal("\u2295"), "^")
    unsafe_bar = ~Literal("|>") + ~Literal("|*>") + Literal("|") | fixto(Literal("\u2228") | Literal("\u222a"), "|")
    bar = ~rbanana + unsafe_bar
    percent = Literal("%")
    dollar = Literal("$")
    lshift = Literal("<<") | fixto(Literal("\xab"), "<<")
    rshift = Literal(">>") | fixto(Literal("\xbb"), ">>")
    tilde = Literal("~") | fixto(~Literal("\xac=") + Literal("\xac"), "~")
    underscore = Literal("_")
    pound = Literal("#")
    unsafe_backtick = Literal("`")
    dubbackslash = Literal("\\\\")
    backslash = ~dubbackslash + Literal("\\")
    dubquestion = Literal("??")
    questionmark = ~dubquestion + Literal("?")

    ellipsis = Forward()
    ellipsis_ref = Literal("...") | Literal("\u2026")

    lt = ~Literal("<<") + ~Literal("<=") + ~Literal("<..") + Literal("<")
    gt = ~Literal(">>") + ~Literal(">=") + Literal(">")
    le = Literal("<=") | fixto(Literal("\u2264"), "<=")
    ge = Literal(">=") | fixto(Literal("\u2265"), ">=")
    ne = Literal("!=") | fixto(Literal("\xac=") | Literal("\u2260"), "!=")

    mul_star = star | fixto(Literal("\xd7"), "*")
    exp_dubstar = dubstar | fixto(Literal("\u2191"), "**")
    neg_minus = minus | fixto(Literal("\u207b"), "-")
    sub_minus = minus | fixto(Literal("\u2212"), "-")
    div_slash = slash | fixto(Literal("\xf7") + ~slash, "/")
    div_dubslash = dubslash | fixto(Combine(Literal("\xf7") + slash), "//")
    matrix_at_ref = at | fixto(Literal("\u22c5"), "@")
    matrix_at = Forward()

    test = Forward()
    test_no_chain, dubcolon = disable_inside(test, unsafe_dubcolon)
    test_no_infix, backtick = disable_inside(test, unsafe_backtick)

    name = Forward()
    base_name = (
        disallow_keywords(keywords + const_vars)
        + regex_item(r"(?![0-9])\w+\b")
    )
    for k in reserved_vars:
        base_name |= backslash.suppress() + keyword(k)
    dotted_base_name = condense(base_name + ZeroOrMore(dot + base_name))
    dotted_name = condense(name + ZeroOrMore(dot + name))
    must_be_dotted_name = condense(name + OneOrMore(dot + name))

    integer = Combine(Word(nums) + ZeroOrMore(underscore.suppress() + Word(nums)))
    binint = Combine(Word("01") + ZeroOrMore(underscore.suppress() + Word("01")))
    octint = Combine(Word("01234567") + ZeroOrMore(underscore.suppress() + Word("01234567")))
    hexint = Combine(Word(hexnums) + ZeroOrMore(underscore.suppress() + Word(hexnums)))

    imag_j = CaselessLiteral("j") | fixto(CaselessLiteral("i"), "j")
    basenum = Combine(
        integer + dot + Optional(integer)
        | Optional(integer) + dot + integer,
    ) | integer
    sci_e = Combine(CaselessLiteral("e") + Optional(plus | neg_minus))
    numitem = ~(Literal("0") + Word(nums + "_", exact=1)) + Combine(basenum + Optional(sci_e + integer))
    imag_num = Combine(numitem + imag_j)
    bin_num = Combine(CaselessLiteral("0b") + Optional(underscore.suppress()) + binint)
    oct_num = Combine(CaselessLiteral("0o") + Optional(underscore.suppress()) + octint)
    hex_num = Combine(CaselessLiteral("0x") + Optional(underscore.suppress()) + hexint)
    number = addspace(
        (
            bin_num
            | oct_num
            | hex_num
            | imag_num
            | numitem
        )
        + Optional(condense(dot + name)),
    )

    moduledoc_item = Forward()
    unwrap = Literal(unwrapper)
    comment = Forward()
    comment_ref = Combine(pound + integer + unwrap)
    string_item = Combine(Literal(strwrapper) + integer + unwrap)
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
    format_f = CaselessLiteral("f").suppress()
    f_string_ref = Combine((format_f + raw_r | raw_r + format_f) + string_item)
    string = trace(b_string | u_string | f_string)
    moduledoc = string + newline
    docstring = condense(moduledoc)

    augassign = (
        Combine(pipe + equals)
        | Combine(star_pipe + equals)
        | Combine(dubstar_pipe + equals)
        | Combine(back_pipe + equals)
        | Combine(back_star_pipe + equals)
        | Combine(back_dubstar_pipe + equals)
        | Combine(none_pipe + equals)
        | Combine(none_star_pipe + equals)
        | Combine(none_dubstar_pipe + equals)
        | Combine(comp_pipe + equals)
        | Combine(dotdot + equals)
        | Combine(comp_back_pipe + equals)
        | Combine(comp_star_pipe + equals)
        | Combine(comp_back_star_pipe + equals)
        | Combine(comp_dubstar_pipe + equals)
        | Combine(comp_back_dubstar_pipe + equals)
        | Combine(unsafe_dubcolon + equals)
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
        | Combine(dubquestion + equals)
    )

    comp_op = (
        le | ge | ne | lt | gt | eq
        | addspace(keyword("not") + keyword("in"))
        | keyword("in")
        | addspace(keyword("is") + keyword("not"))
        | keyword("is")
    )

    expr = Forward()
    star_expr = Forward()
    dubstar_expr = Forward()
    comp_for = Forward()
    test_no_cond = Forward()
    namedexpr_test = Forward()
    # for namedexpr locations only supported in Python 3.10
    new_namedexpr_test = Forward()

    testlist = trace(itemlist(test, comma, suppress_trailing=False))
    testlist_star_expr = trace(itemlist(test | star_expr, comma, suppress_trailing=False))
    testlist_star_namedexpr = trace(itemlist(namedexpr_test | star_expr, comma, suppress_trailing=False))
    testlist_has_comma = trace(addspace(OneOrMore(condense(test + comma)) + Optional(test)))
    new_namedexpr_testlist_has_comma = trace(addspace(OneOrMore(condense(new_namedexpr_test + comma)) + Optional(test)))

    yield_from = Forward()
    dict_comp = Forward()
    yield_classic = addspace(keyword("yield") + Optional(testlist))
    yield_from_ref = keyword("yield").suppress() + keyword("from").suppress() + test
    yield_expr = yield_from | yield_classic
    dict_comp_ref = lbrace.suppress() + (test + colon.suppress() + test | dubstar_expr) + comp_for + rbrace.suppress()
    dict_item = condense(
        lbrace
        + Optional(
            itemlist(
                addspace(condense(test + colon) + test) | dubstar_expr,
                comma,
            ),
        )
        + rbrace,
    )
    test_expr = yield_expr | testlist_star_expr

    op_item = (
        # must go dubstar then star then no star
        fixto(dubstar_pipe, "_coconut_dubstar_pipe")
        | fixto(back_dubstar_pipe, "_coconut_back_dubstar_pipe")
        | fixto(none_dubstar_pipe, "_coconut_none_dubstar_pipe")
        | fixto(star_pipe, "_coconut_star_pipe")
        | fixto(back_star_pipe, "_coconut_back_star_pipe")
        | fixto(none_star_pipe, "_coconut_none_star_pipe")
        | fixto(pipe, "_coconut_pipe")
        | fixto(back_pipe, "_coconut_back_pipe")
        | fixto(none_pipe, "_coconut_none_pipe")

        # must go dubstar then star then no star
        | fixto(comp_dubstar_pipe, "_coconut_forward_dubstar_compose")
        | fixto(comp_back_dubstar_pipe, "_coconut_back_dubstar_compose")
        | fixto(comp_star_pipe, "_coconut_forward_star_compose")
        | fixto(comp_back_star_pipe, "_coconut_back_star_compose")
        | fixto(comp_pipe, "_coconut_forward_compose")
        | fixto(dotdot | comp_back_pipe, "_coconut_back_compose")

        | fixto(keyword("assert"), "_coconut_assert")
        | fixto(keyword("and"), "_coconut_bool_and")
        | fixto(keyword("or"), "_coconut_bool_or")
        | fixto(dubquestion, "_coconut_none_coalesce")
        | fixto(minus, "_coconut_minus")
        | fixto(dot, "_coconut.getattr")
        | fixto(unsafe_dubcolon, "_coconut.itertools.chain")
        | fixto(dollar + lbrack + rbrack, "_coconut_igetitem")
        | fixto(dollar, "_coconut.functools.partial")
        | fixto(exp_dubstar, "_coconut.operator.pow")
        | fixto(mul_star, "_coconut.operator.mul")
        | fixto(div_dubslash, "_coconut.operator.floordiv")
        | fixto(div_slash, "_coconut.operator.truediv")
        | fixto(percent, "_coconut.operator.mod")
        | fixto(plus, "_coconut.operator.add")
        | fixto(amp, "_coconut.operator.and_")
        | fixto(caret, "_coconut.operator.xor")
        | fixto(unsafe_bar, "_coconut.operator.or_")
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
        | fixto(keyword("not"), "_coconut.operator.not_")
        | fixto(keyword("is"), "_coconut.operator.is_")
        | fixto(keyword("in"), "_coconut.operator.contains")
    )

    typedef = Forward()
    typedef_default = Forward()
    unsafe_typedef_default = Forward()
    typedef_test = Forward()

    # we include (var)arg_comma to ensure the pattern matches the whole arg
    arg_comma = comma | fixto(FollowedBy(rparen), "")
    vararg_comma = arg_comma | fixto(FollowedBy(colon), "")
    typedef_ref = name + colon.suppress() + typedef_test + arg_comma
    default = condense(equals + test)
    unsafe_typedef_default_ref = name + colon.suppress() + typedef_test + Optional(default)
    typedef_default_ref = unsafe_typedef_default_ref + arg_comma
    tfpdef = typedef | condense(name + arg_comma)
    tfpdef_default = typedef_default | condense(name + Optional(default) + arg_comma)

    star_sep_arg = Forward()
    star_sep_arg_ref = condense(star + arg_comma)
    star_sep_vararg = Forward()
    star_sep_vararg_ref = condense(star + vararg_comma)

    slash_sep_arg = Forward()
    slash_sep_arg_ref = condense(slash + arg_comma)
    slash_sep_vararg = Forward()
    slash_sep_vararg_ref = condense(slash + vararg_comma)

    just_star = star + rparen
    just_slash = slash + rparen
    just_op = just_star | just_slash

    match = Forward()
    args_list = trace(
        ~just_op
        + addspace(
            ZeroOrMore(
                condense(
                    # everything here must end with arg_comma
                    (star | dubstar) + tfpdef
                    | star_sep_arg
                    | slash_sep_arg
                    | tfpdef_default,
                ),
            ),
        ),
    )
    parameters = condense(lparen + args_list + rparen)
    var_args_list = trace(
        ~just_op
        + addspace(
            ZeroOrMore(
                condense(
                    # everything here must end with vararg_comma
                    (star | dubstar) + name + vararg_comma
                    | star_sep_vararg
                    | slash_sep_vararg
                    | name + Optional(default) + vararg_comma,
                ),
            ),
        ),
    )
    match_args_list = trace(
        Group(
            Optional(
                tokenlist(
                    Group(
                        (star | dubstar) + match
                        | star  # not star_sep because pattern-matching can handle star separators on any Python version
                        | slash  # not slash_sep as above
                        | match + Optional(equals.suppress() + test),
                    ),
                    comma,
                ),
            ),
        ),
    )

    call_item = (
        dubstar + test
        | star + test
        | name + default
        | namedexpr_test
    )
    function_call_tokens = lparen.suppress() + (
        # everything here must end with rparen
        rparen.suppress()
        | Group(op_item) + rparen.suppress()
        | Group(attach(addspace(test + comp_for), add_paren_handle)) + rparen.suppress()
        | tokenlist(Group(call_item), comma) + rparen.suppress()
    )
    function_call = attach(function_call_tokens, function_call_handle)
    questionmark_call_tokens = Group(
        tokenlist(
            Group(
                questionmark
                | call_item,
            ),
            comma,
        ),
    )
    methodcaller_args = (
        itemlist(condense(call_item), comma)
        | op_item
    )

    slicetest = Optional(test_no_chain)
    sliceop = condense(unsafe_colon + slicetest)
    subscript = condense(slicetest + sliceop + Optional(sliceop)) | test
    subscriptlist = itemlist(subscript, comma, suppress_trailing=False) | new_namedexpr_test

    slicetestgroup = Optional(test_no_chain, default="")
    sliceopgroup = unsafe_colon.suppress() + slicetestgroup
    subscriptgroup = attach(slicetestgroup + sliceopgroup + Optional(sliceopgroup) | test, subscriptgroup_handle)
    subscriptgrouplist = itemlist(subscriptgroup, comma)

    testlist_comp = addspace((namedexpr_test | star_expr) + comp_for) | testlist_star_namedexpr
    list_comp = condense(lbrack + Optional(testlist_comp) + rbrack)
    paren_atom = condense(lparen + Optional(yield_expr | testlist_comp) + rparen)
    op_atom = lparen.suppress() + op_item + rparen.suppress()
    keyword_atom = reduce(lambda acc, x: acc | keyword(x), const_vars)
    string_atom = addspace(OneOrMore(string))
    passthrough_atom = trace(addspace(OneOrMore(passthrough)))
    set_literal = Forward()
    set_letter_literal = Forward()
    set_s = fixto(CaselessLiteral("s"), "s")
    set_f = fixto(CaselessLiteral("f"), "f")
    set_letter = set_s | set_f
    setmaker = Group(addspace(new_namedexpr_test + comp_for)("comp") | new_namedexpr_testlist_has_comma("list") | new_namedexpr_test("test"))
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
        | ellipsis
        | list_comp
        | dict_comp
        | dict_item
        | set_literal
        | set_letter_literal
        | lazy_list,
    )
    func_atom = (
        name
        | op_atom
        | paren_atom
    )
    atom = (
        known_atom
        | passthrough_atom
        | func_atom
    )

    typedef_atom = Forward()
    typedef_atom_ref = (  # use special type signifier for item_handle
        Group(fixto(lbrack + rbrack, "type:[]"))
        | Group(fixto(dollar + lbrack + rbrack, "type:$[]"))
        | Group(fixto(questionmark + ~questionmark, "type:?"))
    )

    simple_trailer = (
        condense(lbrack + subscriptlist + rbrack)
        | condense(dot + name)
    )
    call_trailer = (
        function_call
        | Group(dollar + ~lparen + ~lbrack + ~questionmark)  # keep $ for item_handle
    )
    known_trailer = typedef_atom | (
        Group(condense(dollar + lbrack) + subscriptgroup + rbrack.suppress())  # $[
        | Group(condense(dollar + lbrack + rbrack))  # $[]
        | Group(condense(lbrack + rbrack))  # []
        | Group(dot + ~name + ~lbrack)  # .
        | Group(questionmark)  # ?
    ) + ~questionmark
    partial_trailer = (
        Group(fixto(dollar, "$(") + function_call)  # $(
        | Group(fixto(dollar + lparen, "$(?") + questionmark_call_tokens) + rparen.suppress()  # $(?
    ) + ~questionmark
    partial_trailer_tokens = Group(dollar.suppress() + function_call_tokens)

    no_call_trailer = simple_trailer | partial_trailer | known_trailer

    no_partial_complex_trailer = call_trailer | known_trailer
    no_partial_trailer = simple_trailer | no_partial_complex_trailer

    complex_trailer = partial_trailer | no_partial_complex_trailer
    trailer = simple_trailer | complex_trailer

    attrgetter_atom_tokens = dot.suppress() + dotted_name + Optional(
        lparen + Optional(methodcaller_args) + rparen.suppress(),
    )
    attrgetter_atom = attach(attrgetter_atom_tokens, attrgetter_atom_handle)
    itemgetter_atom_tokens = dot.suppress() + condense(Optional(dollar) + lbrack) + subscriptgrouplist + rbrack.suppress()
    itemgetter_atom = attach(itemgetter_atom_tokens, itemgetter_handle)
    implicit_partial_atom = attrgetter_atom | itemgetter_atom

    atom_item = (
        implicit_partial_atom
        | attach(atom + ZeroOrMore(trailer), item_handle)
    )
    partial_atom_tokens = attach(atom + ZeroOrMore(no_partial_trailer), item_handle) + partial_trailer_tokens

    simple_assign = attach(
        maybeparens(
            lparen,
            (name | passthrough_atom)
            + ZeroOrMore(ZeroOrMore(complex_trailer) + OneOrMore(simple_trailer)),
            rparen,
        ),
        item_handle,
    )
    simple_assignlist = maybeparens(lparen, itemlist(simple_assign, comma, suppress_trailing=False), rparen)

    assignlist = Forward()
    star_assign_item = Forward()
    base_assign_item = condense(simple_assign | lparen + assignlist + rparen | lbrack + assignlist + rbrack)
    star_assign_item_ref = condense(star + base_assign_item)
    assign_item = star_assign_item | base_assign_item
    assignlist <<= itemlist(assign_item, comma, suppress_trailing=False)

    augassign_stmt = Forward()
    typed_assign_stmt = Forward()
    augassign_stmt_ref = simple_assign + augassign + test_expr
    typed_assign_stmt_ref = simple_assign + colon.suppress() + typedef_test + Optional(equals.suppress() + test_expr)
    basic_stmt = trace(addspace(ZeroOrMore(assignlist + equals) + test_expr))

    compose_item = attach(atom_item + ZeroOrMore(dotdot.suppress() + atom_item), compose_item_handle)

    impl_call_arg = disallow_keywords(reserved_vars) + (
        keyword_atom
        | number
        | dotted_name
    )
    impl_call = attach(
        disallow_keywords(reserved_vars)
        + compose_item
        + OneOrMore(impl_call_arg),
        impl_call_item_handle,
    )
    impl_call_item = (
        compose_item + ~impl_call_arg
        | impl_call
    )

    await_item = Forward()
    await_item_ref = keyword("await").suppress() + impl_call_item
    power_item = await_item | impl_call_item

    factor = Forward()
    unary = plus | neg_minus | tilde
    power = trace(condense(power_item + Optional(exp_dubstar + factor)))
    factor <<= condense(ZeroOrMore(unary) + power)

    mulop = mul_star | div_dubslash | div_slash | percent | matrix_at
    addop = plus | sub_minus
    shift = lshift | rshift

    term = exprlist(factor, mulop)
    arith_expr = exprlist(term, addop)
    shift_expr = exprlist(arith_expr, shift)
    and_expr = exprlist(shift_expr, amp)
    xor_expr = exprlist(and_expr, caret)
    or_expr = exprlist(xor_expr, bar)

    chain_expr = attach(or_expr + ZeroOrMore(dubcolon.suppress() + or_expr), chain_handle)

    lambdef = Forward()

    infix_op = condense(backtick.suppress() + test_no_infix + backtick.suppress())

    infix_expr = Forward()
    infix_expr <<= (
        chain_expr + ~backtick
        | attach(
            Group(Optional(chain_expr))
            + OneOrMore(
                infix_op + Group(Optional(lambdef | chain_expr)),
            ),
            infix_handle,
        )
    )

    none_coalesce_expr = attach(infix_expr + ZeroOrMore(dubquestion.suppress() + infix_expr), none_coalesce_handle)

    comp_pipe_op = (
        comp_pipe
        | comp_star_pipe
        | comp_back_pipe
        | comp_back_star_pipe
        | comp_dubstar_pipe
        | comp_back_dubstar_pipe
    )
    comp_pipe_expr = (
        none_coalesce_expr + ~comp_pipe_op
        | attach(
            OneOrMore(none_coalesce_expr + comp_pipe_op) + (lambdef | none_coalesce_expr),
            comp_pipe_handle,
        )
    )

    pipe_op = (
        pipe
        | star_pipe
        | dubstar_pipe
        | back_pipe
        | back_star_pipe
        | back_dubstar_pipe
        | none_pipe
        | none_star_pipe
        | none_dubstar_pipe
    )
    pipe_item = (
        # we need the pipe_op since any of the atoms could otherwise be the start of an expression
        Group(attrgetter_atom_tokens("attrgetter")) + pipe_op
        | Group(itemgetter_atom_tokens("itemgetter")) + pipe_op
        | Group(partial_atom_tokens("partial")) + pipe_op
        | Group(comp_pipe_expr("expr")) + pipe_op
    )
    last_pipe_item = Group(
        lambdef("expr")
        | longest(
            # we need longest here because there's no following pipe_op we can use as above
            attrgetter_atom_tokens("attrgetter"),
            itemgetter_atom_tokens("itemgetter"),
            partial_atom_tokens("partial"),
            comp_pipe_expr("expr"),
        ),
    )
    pipe_expr = (
        comp_pipe_expr + ~pipe_op
        | attach(OneOrMore(pipe_item) + last_pipe_item, pipe_handle)
    )

    expr <<= pipe_expr

    star_expr_ref = condense(star + expr)
    dubstar_expr_ref = condense(dubstar + expr)

    comparison = exprlist(expr, comp_op)
    not_test = addspace(ZeroOrMore(keyword("not")) + comparison)
    and_test = exprlist(not_test, keyword("and"))
    test_item = trace(exprlist(and_test, keyword("or")))

    simple_stmt_item = Forward()
    unsafe_simple_stmt_item = Forward()
    simple_stmt = Forward()
    stmt = Forward()
    suite = Forward()
    nocolon_suite = Forward()
    base_suite = Forward()

    classic_lambdef = Forward()
    classic_lambdef_params = maybeparens(lparen, var_args_list, rparen)
    new_lambdef_params = lparen.suppress() + var_args_list + rparen.suppress() | name
    classic_lambdef_ref = addspace(keyword("lambda") + condense(classic_lambdef_params + colon))
    new_lambdef = attach(new_lambdef_params + arrow.suppress(), lambdef_handle)
    implicit_lambdef = fixto(arrow, "lambda _=None:")
    lambdef_base = classic_lambdef | new_lambdef | implicit_lambdef

    stmt_lambdef = Forward()
    match_guard = Optional(keyword("if").suppress() + namedexpr_test)
    closing_stmt = longest(testlist("tests"), unsafe_simple_stmt_item)
    stmt_lambdef_params = Optional(
        attach(name, add_paren_handle)
        | parameters
        | Group(lparen.suppress() + match_args_list + match_guard + rparen.suppress()),
        default="(_=None)",
    )
    stmt_lambdef_ref = (
        keyword("def").suppress() + stmt_lambdef_params + arrow.suppress()
        + (
            Group(OneOrMore(simple_stmt_item + semicolon.suppress())) + Optional(closing_stmt)
            | Group(ZeroOrMore(simple_stmt_item + semicolon.suppress())) + closing_stmt
        )
    )

    lambdef <<= addspace(lambdef_base + test) | stmt_lambdef
    lambdef_no_cond = trace(addspace(lambdef_base + test_no_cond))

    typedef_callable_params = (
        lparen.suppress() + Optional(testlist, default="") + rparen.suppress()
        | Optional(atom_item)
    )
    typedef_callable = attach(typedef_callable_params + arrow.suppress() + typedef_test, typedef_callable_handle)
    _typedef_test, typedef_callable, _typedef_atom = disable_outside(
        test,
        typedef_callable,
        typedef_atom_ref,
    )
    typedef_atom <<= _typedef_atom
    typedef_test <<= _typedef_test

    test <<= (
        typedef_callable
        | lambdef
        | addspace(test_item + Optional(keyword("if") + test_item + keyword("else") + test))
    )
    test_no_cond <<= lambdef_no_cond | test_item

    namedexpr = Forward()
    namedexpr_ref = addspace(name + colon_eq + test)
    namedexpr_test <<= (
        test + ~colon_eq
        | namedexpr
    )

    new_namedexpr = Forward()
    new_namedexpr_ref = namedexpr_ref
    new_namedexpr_test <<= (
        test + ~colon_eq
        | new_namedexpr
    )

    async_comp_for = Forward()
    classdef = Forward()
    classlist = Group(
        Optional(
            lparen.suppress() + rparen.suppress()
            | Group(
                condense(lparen + testlist + rparen)("tests")
                | function_call("args"),
            ),
        )
        + ~equals,  # don't match class destructuring assignment
    )
    class_suite = suite | attach(newline, class_suite_handle)
    classdef_ref = keyword("class").suppress() + name + classlist + class_suite
    comp_iter = Forward()
    base_comp_for = addspace(keyword("for") + assignlist + keyword("in") + test_item + Optional(comp_iter))
    async_comp_for_ref = addspace(keyword("async") + base_comp_for)
    comp_for <<= async_comp_for | base_comp_for
    comp_if = addspace(keyword("if") + test_no_cond + Optional(comp_iter))
    comp_iter <<= comp_for | comp_if

    complex_raise_stmt = Forward()
    pass_stmt = keyword("pass")
    break_stmt = keyword("break")
    continue_stmt = keyword("continue")
    return_stmt = addspace(keyword("return") - Optional(testlist))
    simple_raise_stmt = addspace(keyword("raise") + Optional(test))
    complex_raise_stmt_ref = keyword("raise").suppress() + test + keyword("from").suppress() - test
    raise_stmt = complex_raise_stmt | simple_raise_stmt
    flow_stmt = (
        break_stmt
        | continue_stmt
        | return_stmt
        | raise_stmt
        | yield_expr
    )

    dotted_as_name = Group(dotted_name - Optional(keyword("as").suppress() - name))
    import_as_name = Group(name - Optional(keyword("as").suppress() - name))
    import_names = Group(maybeparens(lparen, tokenlist(dotted_as_name, comma), rparen))
    from_import_names = Group(maybeparens(lparen, tokenlist(import_as_name, comma), rparen))
    basic_import = keyword("import").suppress() - (import_names | Group(star))
    from_import = (
        keyword("from").suppress()
        - condense(ZeroOrMore(unsafe_dot) + dotted_name | OneOrMore(unsafe_dot) | star)
        - keyword("import").suppress() - (from_import_names | Group(star))
    )
    import_stmt = Forward()
    import_stmt_ref = from_import | basic_import

    simple_kwd_assign = attach(
        maybeparens(lparen, itemlist(name, comma), rparen) + Optional(equals.suppress() - test_expr),
        simple_kwd_assign_handle,
    )
    kwd_augassign = Forward()
    kwd_augassign_ref = name + augassign - test_expr
    kwd_assign = (
        kwd_augassign
        | simple_kwd_assign
    )
    global_stmt = addspace(keyword("global") - kwd_assign)
    nonlocal_stmt = Forward()
    nonlocal_stmt_ref = addspace(keyword("nonlocal") - kwd_assign)

    del_stmt = addspace(keyword("del") - simple_assignlist)

    matchlist_tuple_items = (
        match + OneOrMore(comma.suppress() + match) + Optional(comma.suppress())
        | match + comma.suppress()
    )
    matchlist_tuple = Group(Optional(matchlist_tuple_items))
    matchlist_list = Group(Optional(tokenlist(match, comma)))
    matchlist_star = (
        Optional(Group(OneOrMore(match + comma.suppress())))
        + star.suppress() + name
        + Optional(Group(OneOrMore(comma.suppress() + match)))
        + Optional(comma.suppress())
    )
    matchlist_data_item = Group(Optional(star | name + equals) + match)
    matchlist_data = Group(Optional(tokenlist(matchlist_data_item, comma)))

    match_dotted_name_const = Forward()
    complex_number = condense(Optional(neg_minus) + number + (plus | sub_minus) + Optional(neg_minus) + imag_num)
    match_const = condense(
        equals.suppress() + atom_item
        | complex_number
        | Optional(neg_minus) + const_atom
        | match_dotted_name_const,
    )
    match_string = (
        (string + plus.suppress() + name + plus.suppress() + string)("mstring")
        | (string + plus.suppress() + name)("string")
        | (name + plus.suppress() + string)("rstring")
    )
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
        ((match_list | match_tuple | match_lazy) + unsafe_dubcolon.suppress() + name)
        | match_lazy
    )("iter")
    star_match = (
        lbrack.suppress() + matchlist_star + rbrack.suppress()
        | lparen.suppress() + matchlist_star + rparen.suppress()
    )("star")
    base_match = trace(
        Group(
            match_string
            | match_const("const")
            | (lbrace.suppress() + matchlist_dict + Optional(dubstar.suppress() + (name | condense(lbrace + rbrace))) + rbrace.suppress())("dict")
            | (Optional(set_s.suppress()) + lbrace.suppress() + matchlist_set + rbrace.suppress())("set")
            | iter_match
            | series_match
            | star_match
            | (lparen.suppress() + match + rparen.suppress())("paren")
            | (keyword("data").suppress() + name + lparen.suppress() + matchlist_data + rparen.suppress())("data")
            | (keyword("class").suppress() + name + lparen.suppress() + matchlist_data + rparen.suppress())("class")
            | (name + lparen.suppress() + matchlist_data + rparen.suppress())("data_or_class")
            | name("var"),
        ),
    )

    matchlist_trailer = base_match + OneOrMore(keyword("as") + name | keyword("is") + atom_item)
    as_match = Group(matchlist_trailer("trailer")) | base_match

    matchlist_and = as_match + OneOrMore(keyword("and").suppress() + as_match)
    and_match = Group(matchlist_and("and")) | as_match

    match_or_op = (keyword("or") | bar).suppress()
    matchlist_or = and_match + OneOrMore(match_or_op + and_match)
    or_match = Group(matchlist_or("or")) | and_match

    matchlist_walrus = name + colon_eq.suppress() + or_match
    walrus_match = Group(matchlist_walrus("walrus")) | or_match

    match <<= trace(walrus_match)

    many_match = (
        Group(matchlist_star("star"))
        | Group(matchlist_tuple_items("implicit_tuple"))
        | match
    )

    else_stmt = condense(keyword("else") - suite)
    full_suite = colon.suppress() + Group((newline.suppress() + indent.suppress() + OneOrMore(stmt) + dedent.suppress()) | simple_stmt)
    full_match = Forward()
    full_match_ref = (
        keyword("match").suppress()
        + many_match
        + addspace(Optional(keyword("not")) + keyword("in"))
        - testlist_star_namedexpr
        - match_guard
        - full_suite
    )
    match_stmt = trace(condense(full_match - Optional(else_stmt)))

    destructuring_stmt = Forward()
    base_destructuring_stmt = Optional(keyword("match").suppress()) + many_match + equals.suppress() + test_expr
    destructuring_stmt_ref, match_dotted_name_const_ref = disable_inside(base_destructuring_stmt, must_be_dotted_name)

    case_stmt = Forward()
    # syntaxes 1 and 2 here must be kept matching except for the keywords
    case_match_syntax_1 = trace(
        Group(
            keyword("match").suppress()
            + stores_loc_item
            + many_match
            + Optional(keyword("if").suppress() + namedexpr_test)
            + full_suite,
        ),
    )
    case_stmt_syntax_1 = (
        keyword("case") + testlist_star_namedexpr + colon.suppress() + newline.suppress()
        + indent.suppress() + Group(OneOrMore(case_match_syntax_1))
        + dedent.suppress() + Optional(keyword("else").suppress() + suite)
    )
    case_match_syntax_2 = trace(
        Group(
            keyword("case").suppress()
            + stores_loc_item
            + many_match
            + Optional(keyword("if").suppress() + namedexpr_test)
            + full_suite,
        ),
    )
    case_stmt_syntax_2 = (
        keyword("match") + testlist_star_namedexpr + colon.suppress() + newline.suppress()
        + indent.suppress() + Group(OneOrMore(case_match_syntax_2))
        + dedent.suppress() + Optional(keyword("else").suppress() - suite)
    )
    case_stmt_ref = case_stmt_syntax_1 | case_stmt_syntax_2

    exec_stmt = Forward()
    assert_stmt = addspace(keyword("assert") - testlist)
    if_stmt = condense(
        addspace(keyword("if") - condense(namedexpr_test - suite))
        - ZeroOrMore(addspace(keyword("elif") - condense(namedexpr_test - suite)))
        - Optional(else_stmt),
    )
    while_stmt = addspace(keyword("while") - condense(namedexpr_test - suite - Optional(else_stmt)))
    for_stmt = addspace(keyword("for") - assignlist - keyword("in") - condense(testlist - suite - Optional(else_stmt)))
    except_clause = attach(
        keyword("except").suppress() + (
            testlist_has_comma("list") | test("test")
        ) - Optional(keyword("as").suppress() - name),
        except_handle,
    )
    try_stmt = condense(
        keyword("try") - suite + (
            keyword("finally") - suite
            | (
                OneOrMore(except_clause - suite) - Optional(keyword("except") - suite)
                | keyword("except") - suite
            ) - Optional(else_stmt) - Optional(keyword("finally") - suite)
        ),
    )
    exec_stmt_ref = keyword("exec").suppress() + lparen.suppress() + test + Optional(
        comma.suppress() + test + Optional(
            comma.suppress() + test + Optional(
                comma.suppress(),
            ),
        ),
    ) + rparen.suppress()

    with_item = addspace(test - Optional(keyword("as") - name))
    with_item_list = Group(maybeparens(lparen, tokenlist(with_item, comma), rparen))
    with_stmt_ref = keyword("with").suppress() - with_item_list - suite
    with_stmt = Forward()

    return_typedef = Forward()
    name_funcdef = trace(condense(dotted_name + parameters))
    op_tfpdef = unsafe_typedef_default | condense(name + Optional(default))
    op_funcdef_arg = name | condense(lparen.suppress() + op_tfpdef + rparen.suppress())
    op_funcdef_name = unsafe_backtick.suppress() + dotted_name + unsafe_backtick.suppress()
    op_funcdef = trace(
        attach(
            Group(Optional(op_funcdef_arg))
            + op_funcdef_name
            + Group(Optional(op_funcdef_arg)),
            op_funcdef_handle,
        ),
    )
    return_typedef_ref = arrow.suppress() + typedef_test
    end_func_colon = return_typedef + colon.suppress() | colon
    base_funcdef = op_funcdef | name_funcdef
    funcdef = trace(addspace(keyword("def") + condense(base_funcdef + end_func_colon + nocolon_suite)))

    name_match_funcdef = Forward()
    op_match_funcdef = Forward()
    op_match_funcdef_arg = Group(
        Optional(
            lparen.suppress()
            + Group(match + Optional(equals.suppress() + test))
            + rparen.suppress(),
        ),
    )
    name_match_funcdef_ref = keyword("def").suppress() + dotted_name + lparen.suppress() + match_args_list + match_guard + rparen.suppress()
    op_match_funcdef_ref = keyword("def").suppress() + op_match_funcdef_arg + op_funcdef_name + op_match_funcdef_arg + match_guard
    base_match_funcdef = trace(op_match_funcdef | name_match_funcdef)
    def_match_funcdef = trace(
        attach(
            base_match_funcdef
            + colon.suppress()
            + (
                attach(simple_stmt, make_suite_handle)
                | newline.suppress() + indent.suppress()
                + Optional(docstring)
                + attach(condense(OneOrMore(stmt)), make_suite_handle)
                + dedent.suppress()
            ),
            join_match_funcdef,
        ),
    )
    match_def_modifiers = trace(
        Optional(
            # we don't suppress addpattern so its presence can be detected later
            keyword("match").suppress() + Optional(keyword("addpattern"))
            | keyword("addpattern") + Optional(keyword("match")).suppress(),
        ),
    )
    match_funcdef = addspace(match_def_modifiers + def_match_funcdef)

    where_stmt = attach(
        unsafe_simple_stmt_item
        + keyword("where").suppress()
        - full_suite,
        where_handle,
    )

    implicit_return = (
        attach(return_stmt, invalid_return_stmt_handle)
        | attach(testlist, implicit_return_handle)
    )
    implicit_return_where = attach(
        implicit_return
        + keyword("where").suppress()
        - full_suite,
        where_handle,
    )
    implicit_return_stmt = (
        condense(implicit_return + newline)
        | implicit_return_where
    )
    math_funcdef_body = condense(ZeroOrMore(~(implicit_return_stmt + dedent) + stmt) - implicit_return_stmt)
    math_funcdef_suite = (
        attach(implicit_return_stmt, make_suite_handle)
        | condense(newline - indent - math_funcdef_body - dedent)
    )
    end_func_equals = return_typedef + equals.suppress() | fixto(equals, ":")
    math_funcdef = trace(
        attach(
            condense(addspace(keyword("def") + base_funcdef) + end_func_equals) - math_funcdef_suite,
            math_funcdef_handle,
        ),
    )
    math_match_funcdef = trace(
        addspace(
            match_def_modifiers
            + attach(
                base_match_funcdef
                + equals.suppress()
                + (
                    attach(implicit_return_stmt, make_suite_handle)
                    | (
                        newline.suppress() - indent.suppress()
                        + Optional(docstring)
                        + attach(math_funcdef_body, make_suite_handle)
                        + dedent.suppress()
                    )
                ),
                join_match_funcdef,
            ),
        ),
    )

    async_stmt = Forward()
    async_stmt_ref = addspace(keyword("async") + (with_stmt | for_stmt))

    async_funcdef = keyword("async").suppress() + (funcdef | math_funcdef)
    async_match_funcdef = trace(
        addspace(
            (
                # we don't suppress addpattern so its presence can be detected later
                keyword("match").suppress() + keyword("addpattern") + keyword("async").suppress()
                | keyword("addpattern") + keyword("match").suppress() + keyword("async").suppress()
                | keyword("match").suppress() + keyword("async").suppress() + Optional(keyword("addpattern"))
                | keyword("addpattern") + keyword("async").suppress() + Optional(keyword("match")).suppress()
                | keyword("async").suppress() + match_def_modifiers
            ) + (def_match_funcdef | math_match_funcdef),
        ),
    )

    datadef = Forward()
    data_args = Group(
        Optional(
            lparen.suppress() + ZeroOrMore(
                Group(
                    # everything here must end with arg_comma
                    (name + arg_comma.suppress())("name")
                    | (name + equals.suppress() + test + arg_comma.suppress())("default")
                    | (star.suppress() + name + arg_comma.suppress())("star")
                    | (name + colon.suppress() + typedef_test + equals.suppress() + test + arg_comma.suppress())("type default")
                    | (name + colon.suppress() + typedef_test + arg_comma.suppress())("type"),
                ),
            ) + rparen.suppress(),
        ),
    ) + Optional(keyword("from").suppress() + testlist)
    data_suite = Group(
        colon.suppress() - (
            (newline.suppress() + indent.suppress() + Optional(docstring) + Group(OneOrMore(stmt)) + dedent.suppress())("complex")
            | (newline.suppress() + indent.suppress() + docstring + dedent.suppress() | docstring)("docstring")
            | simple_stmt("simple")
        ) | newline("empty"),
    )
    datadef_ref = keyword("data").suppress() + name + data_args + data_suite

    match_datadef = Forward()
    match_data_args = lparen.suppress() + Group(
        match_args_list + match_guard,
    ) + rparen.suppress() + Optional(keyword("from").suppress() + testlist)
    match_datadef_ref = Optional(keyword("match").suppress()) + keyword("data").suppress() + name + match_data_args + data_suite

    simple_decorator = condense(dotted_name + Optional(function_call))("simple")
    complex_decorator = namedexpr_test("complex")
    decorators_ref = OneOrMore(at.suppress() - Group(longest(simple_decorator, complex_decorator)) - newline.suppress())
    decorators = Forward()

    decoratable_normal_funcdef_stmt = Forward()
    normal_funcdef_stmt = (
        funcdef
        | math_funcdef
        | math_match_funcdef
        | match_funcdef
    )
    decoratable_normal_funcdef_stmt_ref = Optional(decorators) + normal_funcdef_stmt

    decoratable_async_funcdef_stmt = Forward()
    async_funcdef_stmt = async_funcdef | async_match_funcdef
    decoratable_async_funcdef_stmt_ref = Optional(decorators) + async_funcdef_stmt

    decoratable_func_stmt = decoratable_normal_funcdef_stmt | decoratable_async_funcdef_stmt

    class_stmt = classdef | datadef | match_datadef
    decoratable_class_stmt = trace(condense(Optional(decorators) + class_stmt))

    passthrough_stmt = condense(passthrough_block - (base_suite | newline))

    simple_compound_stmt = trace(
        if_stmt
        | try_stmt
        | match_stmt
        | passthrough_stmt,
    )
    compound_stmt = trace(
        decoratable_class_stmt
        | decoratable_func_stmt
        | for_stmt
        | while_stmt
        | with_stmt
        | async_stmt
        | simple_compound_stmt
        | where_stmt,
    )
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
        | exec_stmt,
    )
    special_stmt = (
        keyword_stmt
        | augassign_stmt
        | typed_assign_stmt
    )
    unsafe_simple_stmt_item <<= special_stmt | longest(basic_stmt, destructuring_stmt)
    end_simple_stmt_item = FollowedBy(semicolon | newline)
    simple_stmt_item <<= (
        special_stmt
        | basic_stmt + end_simple_stmt_item
        | destructuring_stmt + end_simple_stmt_item
    )
    simple_stmt <<= condense(
        simple_stmt_item
        + ZeroOrMore(fixto(semicolon, "\n") + simple_stmt_item)
        + (newline | endline_semicolon),
    )
    stmt <<= final(
        compound_stmt
        | simple_stmt
        # must come at end due to ambiguity with destructuring
        | case_stmt,
    )
    base_suite <<= condense(newline + indent - OneOrMore(stmt) - dedent)
    simple_suite = attach(stmt, make_suite_handle)
    nocolon_suite <<= base_suite | simple_suite
    suite <<= condense(colon + nocolon_suite)
    line = trace(newline | stmt)

    single_input = trace(condense(Optional(line) - ZeroOrMore(newline)))
    file_input = trace(condense(moduledoc_marker - ZeroOrMore(line)))
    eval_input = trace(condense(testlist - ZeroOrMore(newline)))

    single_parser = start_marker - single_input - end_marker
    file_parser = start_marker - file_input - end_marker
    eval_parser = start_marker - eval_input - end_marker

# end: MAIN GRAMMAR
# -----------------------------------------------------------------------------------------------------------------------
# EXTRA GRAMMAR:
# -----------------------------------------------------------------------------------------------------------------------

    just_non_none_atom = start_marker + ~keyword("None") + known_atom + end_marker

    parens = originalTextFor(nestedExpr("(", ")"))
    brackets = originalTextFor(nestedExpr("[", "]"))
    braces = originalTextFor(nestedExpr("{", "}"))
    any_char = regex_item(r".", re.DOTALL)

    original_function_call_tokens = lparen.suppress() + (
        rparen.suppress()
        # we need to add parens here, since f(x for x in y) is fine but tail_call(f, x for x in y) is not
        | attach(originalTextFor(test + comp_for), add_paren_handle) + rparen.suppress()
        | originalTextFor(tokenlist(call_item, comma)) + rparen.suppress()
    )

    def get_tre_return_grammar(self, func_name):
        return self.start_marker + (keyword("return") + keyword(func_name)).suppress() + self.original_function_call_tokens + self.end_marker

    tco_return = attach(
        start_marker + keyword("return").suppress() + condense(
            (base_name | parens | brackets | braces | string)
            + ZeroOrMore(dot + base_name | brackets | parens + ~end_marker),
        ) + original_function_call_tokens + end_marker,
        tco_return_handle,
        # this is the root in what it's used for, so might as well evaluate greedily
        greedy=True,
    )

    rest_of_arg = ZeroOrMore(parens | brackets | braces | ~comma + ~rparen + any_char)
    tfpdef_tokens = base_name - Optional(originalTextFor(colon - rest_of_arg))
    tfpdef_default_tokens = base_name - Optional(originalTextFor((equals | colon) - rest_of_arg))
    parameters_tokens = Group(
        Optional(
            tokenlist(
                Group(
                    dubstar - tfpdef_tokens
                    | star - Optional(tfpdef_tokens)
                    | slash
                    | tfpdef_default_tokens,
                ) + Optional(passthrough.suppress()),
                comma + Optional(passthrough),  # implicitly suppressed
            ),
        ),
    )

    split_func = attach(
        start_marker
        - keyword("def").suppress()
        - dotted_base_name
        - lparen.suppress() - parameters_tokens - rparen.suppress(),
        split_func_handle,
        # this is the root in what it's used for, so might as well evaluate greedily
        greedy=True,
    )

    stores_scope = (
        keyword("lambda")
        # match comprehensions but not for loops
        | ~indent + ~dedent + any_char + keyword("for") + base_name + keyword("in")
    )

    just_a_string = start_marker + string + end_marker

    end_of_line = end_marker | Literal("\n") | pound


# end: EXTRA GRAMMAR
# -----------------------------------------------------------------------------------------------------------------------
# TRACING:
# -----------------------------------------------------------------------------------------------------------------------


def set_grammar_names():
    """Set names of grammar elements to their variable names."""
    for varname, val in vars(Grammar).items():
        if isinstance(val, ParserElement):
            setattr(Grammar, varname, val.setName(varname))
            if isinstance(val, Forward):
                trace(val)


if DEVELOP:
    set_grammar_names()


# end: TRACING
