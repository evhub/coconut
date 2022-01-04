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

from collections import defaultdict

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
    quotedString,
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
    keyword_vars,
    const_vars,
    reserved_vars,
    none_coalesce_var,
    func_var,
    untcoable_funcs,
)
from coconut.compiler.util import (
    combine,
    attach,
    fixto,
    addspace,
    condense,
    maybeparens,
    tokenlist,
    interleaved_tokenlist,
    itemlist,
    longest,
    exprlist,
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
    invalid_syntax,
    skip_to_in_line,
    handle_indentation,
    labeled_group,
    any_keyword_in,
    any_char,
    tuple_str_of,
)

# end: IMPORTS
# -----------------------------------------------------------------------------------------------------------------------
# HELPERS:
# -----------------------------------------------------------------------------------------------------------------------


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


def add_parens_handle(tokens):
    """Add parentheses."""
    item, = tokens
    return "(" + item + ")"


def add_bracks_handle(tokens):
    """Add brackets."""
    item, = tokens
    return "[" + item + "]"


def strip_parens_handle(tokens):
    """Strip parentheses."""
    item, = tokens
    internal_assert(item.startswith("(") and item.endswith(")"), "invalid strip_parens tokens", tokens)
    return item[1:-1]


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


def none_coalesce_handle(loc, tokens):
    """Process the None-coalescing operator."""
    if len(tokens) == 1:
        return tokens[0]
    elif tokens[0] == "None":
        return none_coalesce_handle(loc, tokens[1:])
    elif match_in(Grammar.just_non_none_atom, tokens[0]):
        return tokens[0]
    elif tokens[0].isalnum():
        return "({b} if {a} is None else {a})".format(
            a=tokens[0],
            b=none_coalesce_handle(loc, tokens[1:]),
        )
    else:
        else_expr = none_coalesce_handle(loc, tokens[1:])
        # := changes meaning inside lambdas, so we must disallow it when wrapping
        #  user expressions in lambdas (and naive string analysis is safe here)
        if ":=" in else_expr:
            raise CoconutDeferredSyntaxError("illegal assignment expression with None-coalescing operator", loc)
        return "(lambda {x}: {b} if {x} is None else {x})({a})".format(
            x=none_coalesce_var,
            a=tokens[0],
            b=else_expr,
        )


none_coalesce_handle.ignore_one_token = True


def attrgetter_atom_handle(loc, tokens):
    """Process attrgetter literals."""
    name, args = attrgetter_atom_split(tokens)
    if args is None:
        return '_coconut.operator.attrgetter("' + name + '")'
    elif "." in name:
        attr, method = name.rsplit(".", 1)
        return '_coconut_forward_compose(_coconut.operator.attrgetter("{attr}"), {methodcaller})'.format(
            attr=attr,
            methodcaller=attrgetter_atom_handle(loc, [method, "(", args]),
        )
    elif args == "":
        return '_coconut.operator.methodcaller("' + name + '")'
    else:
        return '_coconut.operator.methodcaller("' + name + '", ' + args + ")"


def lazy_list_handle(loc, tokens):
    """Process lazy lists."""
    if len(tokens) == 0:
        return "_coconut_reiterable(())"
    else:
        lambda_exprs = "lambda: " + ", lambda: ".join(tokens)
        # := changes meaning inside lambdas, so we must disallow it when wrapping
        #  user expressions in lambdas (and naive string analysis is safe here)
        if ":=" in lambda_exprs:
            raise CoconutDeferredSyntaxError("illegal assignment expression in lazy list or chain expression", loc)
        return "_coconut_reiterable({func_var}() for {func_var} in ({lambdas}{tuple_comma}))".format(
            func_var=func_var,
            lambdas=lambda_exprs,
            tuple_comma="," if len(tokens) == 1 else "",
        )


def chain_handle(loc, tokens):
    """Process chain calls."""
    if len(tokens) == 1:
        return tokens[0]
    else:
        return "_coconut.itertools.chain.from_iterable(" + lazy_list_handle(loc, tokens) + ")"


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
    if len(tokens) == 2:
        except_kwd, errs = tokens
        asname = None
    elif len(tokens) == 3:
        except_kwd, errs, asname = tokens
    else:
        raise CoconutInternalException("invalid except tokens", tokens)

    out = except_kwd + " "
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
    if len(tokens) == 2:
        op, args = tokens
        if op == "[":
            return "_coconut.operator.itemgetter((" + args + "))"
        elif op == "$[":
            return "_coconut.functools.partial(_coconut_iter_getitem, index=(" + args + "))"
        else:
            raise CoconutInternalException("invalid implicit itemgetter type", op)
    elif len(tokens) > 2:
        internal_assert(len(tokens) % 2 == 0, "invalid itemgetter composition tokens", tokens)
        itemgetters = []
        for i in range(0, len(tokens), 2):
            itemgetters.append(itemgetter_handle(tokens[i:i + 2]))
        return "_coconut_forward_compose(" + ", ".join(itemgetters) + ")"
    else:
        raise CoconutInternalException("invalid implicit itemgetter tokens", tokens)


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


def join_match_funcdef(tokens):
    """Join the pieces of a pattern-matching function together."""
    if len(tokens) == 3:
        (before_colon, after_docstring), colon, body = tokens
        docstring = None
    elif len(tokens) == 4:
        (before_colon, after_docstring), colon, docstring, body = tokens
    else:
        raise CoconutInternalException("invalid match def joining tokens", tokens)
    # after_docstring and body are their own self-contained suites, but we
    # expect them to both be one suite, so we have to join them together
    after_docstring, dedent = split_trailing_indent(after_docstring)
    indent, body = split_leading_indent(body)
    indentation = collapse_indents(dedent + indent)
    return (
        before_colon
        + colon + "\n"
        + (openindent + docstring + closeindent if docstring is not None else "")
        + after_docstring
        + indentation
        + body
    )


def where_handle(tokens):
    """Process where statements."""
    final_stmt, init_stmts = tokens
    return "".join(init_stmts) + final_stmt + "\n"


def kwd_err_msg_handle(tokens):
    """Handle keyword parse error messages."""
    internal_assert(len(tokens) == 1, "invalid keyword err msg tokens", tokens)
    return 'invalid use of the keyword "' + tokens[0] + '"'


def alt_ternary_handle(tokens):
    """Handle if ... then ... else ternary operator."""
    cond, if_true, if_false = tokens
    return "{if_true} if {cond} else {if_false}".format(cond=cond, if_true=if_true, if_false=if_false)


def yield_funcdef_handle(tokens):
    """Handle yield def explicit generators."""
    internal_assert(len(tokens) == 1, "invalid yield def tokens", tokens)
    return tokens[0] + openindent + handle_indentation(
        """
if False:
    yield
        """,
        add_newline=True,
    ) + closeindent


def partial_op_item_handle(tokens):
    """Handle operator function implicit partials."""
    tok_grp, = tokens
    if "left partial" in tok_grp:
        arg, op = tok_grp
        return "_coconut.functools.partial(" + op + ", " + arg + ")"
    elif "right partial" in tok_grp:
        op, arg = tok_grp
        return "_coconut_partial(" + op + ", {1: " + arg + "}, 2)"
    else:
        raise CoconutInternalException("invalid operator function implicit partial token group", tok_grp)


def array_literal_handle(loc, tokens):
    """Handle multidimensional array literals."""
    internal_assert(len(tokens) >= 1, "invalid array literal tokens", tokens)

    # find highest-level array literal seperators
    sep_indices_by_level = defaultdict(list)
    for i, tok in enumerate(tokens):
        if tok.lstrip(";") == "":
            sep_indices_by_level[len(tok)].append(i)

    internal_assert(sep_indices_by_level, "no array literal separators in", tokens)

    # split by highest-level seperators
    sep_level = max(sep_indices_by_level)
    pieces = []
    prev_ind = 0
    for sep_ind in sep_indices_by_level[sep_level]:
        pieces.append(tokens[prev_ind:sep_ind])
        prev_ind = sep_ind + 1
    pieces.append(tokens[prev_ind:])

    # get subarrays to stack
    array_elems = []
    for p in pieces:
        if p:
            if len(p) > 1:
                internal_assert(sep_level > 1, "failed to handle array literal tokens", tokens)
                subarr_item = array_literal_handle(loc, p)
            elif p[0].lstrip(";") == "":
                raise CoconutDeferredSyntaxError("naked multidimensional array separators are not allowed", loc)
            else:
                subarr_item = p[0]
            array_elems.append(subarr_item)

    if not array_elems:
        raise CoconutDeferredSyntaxError("multidimensional array literal cannot be only separators", loc)

    # build multidimensional array
    return "_coconut_multi_dim_arr(" + tuple_str_of(array_elems) + ", " + str(sep_level) + ")"

# end: HANDLERS
# -----------------------------------------------------------------------------------------------------------------------
# MAIN GRAMMAR:
# -----------------------------------------------------------------------------------------------------------------------


class Grammar(object):
    """Coconut grammar specification."""
    timing_info = None

    comma = Literal(",")
    dubstar = Literal("**")
    star = ~dubstar + Literal("*")
    at = Literal("@")
    arrow = Literal("->") | fixto(Literal("\u2192"), "->")
    colon_eq = Literal(":=")
    unsafe_dubcolon = Literal("::")
    unsafe_colon = Literal(":")
    colon = ~unsafe_dubcolon + ~colon_eq + unsafe_colon
    semicolon = Literal(";") | invalid_syntax("\u037e", "invalid Greek question mark instead of semicolon", greedy=True)
    multisemicolon = combine(OneOrMore(semicolon))
    eq = Literal("==")
    equals = ~eq + Literal("=")
    lbrack = Literal("[")
    rbrack = Literal("]")
    lbrace = Literal("{")
    rbrace = Literal("}")
    lbanana = ~Literal("(|)") + ~Literal("(|>") + ~Literal("(|*") + ~Literal("(|?") + Literal("(|")
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
        ~Literal("...") + ~Literal("..>") + ~Literal("..*") + Literal("..")
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
    unsafe_bar = ~Literal("|>") + ~Literal("|*") + Literal("|") | fixto(Literal("\u2228") | Literal("\u222a"), "|")
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
    bang = ~Literal("!=") + Literal("!")

    except_star_kwd = combine(keyword("except") + star)
    except_kwd = ~except_star_kwd + keyword("except")
    lambda_kwd = keyword("lambda") | fixto(keyword("\u03bb", explicit_prefix=colon), "lambda")
    async_kwd = keyword("async", explicit_prefix=colon)
    await_kwd = keyword("await", explicit_prefix=colon)
    data_kwd = keyword("data", explicit_prefix=colon)
    match_kwd = keyword("match", explicit_prefix=colon)
    case_kwd = keyword("case", explicit_prefix=colon)
    cases_kwd = keyword("cases", explicit_prefix=colon)
    where_kwd = keyword("where", explicit_prefix=colon)
    addpattern_kwd = keyword("addpattern", explicit_prefix=colon)
    then_kwd = keyword("then", explicit_prefix=colon)

    ellipsis = Forward()
    ellipsis_ref = Literal("...") | Literal("\u2026")

    lt = ~Literal("<<") + ~Literal("<=") + ~Literal("<|") + ~Literal("<..") + ~Literal("<*") + Literal("<")
    gt = ~Literal(">>") + ~Literal(">=") + Literal(">")
    le = Literal("<=") | fixto(Literal("\u2264"), "<=")
    ge = Literal(">=") | fixto(Literal("\u2265"), ">=")
    ne = Literal("!=") | fixto(Literal("\xac=") | Literal("\u2260"), "!=")

    mul_star = star | fixto(Literal("\xd7"), "*")
    exp_dubstar = dubstar | fixto(Literal("\u2191"), "**")
    neg_minus = (
        minus
        | fixto(Literal("\u207b"), "-")
    )
    sub_minus = (
        minus
        | invalid_syntax("\u207b", "U+207b is only for negation, not subtraction")
    )
    div_slash = slash | fixto(Literal("\xf7") + ~slash, "/")
    div_dubslash = dubslash | fixto(combine(Literal("\xf7") + slash), "//")
    matrix_at_ref = at | fixto(Literal("\u22c5"), "@")
    matrix_at = Forward()

    test = Forward()
    test_no_chain, dubcolon = disable_inside(test, unsafe_dubcolon)
    test_no_infix, backtick = disable_inside(test, unsafe_backtick)

    base_name_regex = r""
    for no_kwd in keyword_vars + const_vars:
        base_name_regex += r"(?!" + no_kwd + r"\b)"
    # we disallow '"{ after to not match the "b" in b"" or the "s" in s{}
    base_name_regex += r"(?![0-9])\w+\b(?![{" + strwrapper + r"])"
    base_name = (
        regex_item(base_name_regex)
        | backslash.suppress() + any_keyword_in(reserved_vars)
    )

    name = Forward()
    dotted_name = condense(name + ZeroOrMore(dot + name))
    must_be_dotted_name = condense(name + OneOrMore(dot + name))

    integer = combine(Word(nums) + ZeroOrMore(underscore.suppress() + Word(nums)))
    binint = combine(Word("01") + ZeroOrMore(underscore.suppress() + Word("01")))
    octint = combine(Word("01234567") + ZeroOrMore(underscore.suppress() + Word("01234567")))
    hexint = combine(Word(hexnums) + ZeroOrMore(underscore.suppress() + Word(hexnums)))

    imag_j = CaselessLiteral("j") | fixto(CaselessLiteral("i"), "j")
    basenum = combine(
        integer + dot + Optional(integer)
        | Optional(integer) + dot + integer,
    ) | integer
    sci_e = combine(CaselessLiteral("e") + Optional(plus | neg_minus))
    numitem = ~(Literal("0") + Word(nums + "_", exact=1)) + combine(basenum + Optional(sci_e + integer))
    imag_num = combine(numitem + imag_j)
    bin_num = combine(CaselessLiteral("0b") + Optional(underscore.suppress()) + binint)
    oct_num = combine(CaselessLiteral("0o") + Optional(underscore.suppress()) + octint)
    hex_num = combine(CaselessLiteral("0x") + Optional(underscore.suppress()) + hexint)
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
    comment_ref = combine(pound + integer + unwrap)
    string_item = (
        combine(Literal(strwrapper) + integer + unwrap)
        | invalid_syntax(("\u201c", "\u201d", "\u2018", "\u2019"), "invalid unicode quotation mark; strings must use \" or '", greedy=True)
    )

    xonsh_command = Forward()
    passthrough_item = combine(backslash + integer + unwrap) | xonsh_command
    passthrough_block = combine(fixto(dubbackslash, "\\") + integer + unwrap)

    endline = Forward()
    endline_ref = condense(OneOrMore(Literal("\n")))
    lineitem = ZeroOrMore(comment) + endline
    newline = condense(OneOrMore(lineitem))
    end_simple_stmt_item = FollowedBy(semicolon | newline)

    start_marker = StringStart()
    moduledoc_marker = condense(ZeroOrMore(lineitem) - Optional(moduledoc_item))
    end_marker = StringEnd()
    indent = Literal(openindent)
    dedent = Literal(closeindent)

    u_string = Forward()
    f_string = Forward()

    bit_b = CaselessLiteral("b")
    raw_r = CaselessLiteral("r")
    unicode_u = CaselessLiteral("u").suppress()
    format_f = CaselessLiteral("f").suppress()

    string = combine(Optional(raw_r) + string_item)
    # Python 2 only supports br"..." not rb"..."
    b_string = combine((bit_b + Optional(raw_r) | fixto(raw_r + bit_b, "br")) + string_item)
    u_string_ref = combine((unicode_u + Optional(raw_r) | raw_r + unicode_u) + string_item)
    f_string_ref = combine((format_f + Optional(raw_r) | raw_r + format_f) + string_item)
    nonbf_string = string | u_string
    nonb_string = nonbf_string | f_string
    any_string = nonb_string | b_string
    moduledoc = any_string + newline
    docstring = condense(moduledoc)

    pipe_augassign = (
        combine(pipe + equals)
        | combine(star_pipe + equals)
        | combine(dubstar_pipe + equals)
        | combine(back_pipe + equals)
        | combine(back_star_pipe + equals)
        | combine(back_dubstar_pipe + equals)
        | combine(none_pipe + equals)
        | combine(none_star_pipe + equals)
        | combine(none_dubstar_pipe + equals)
    )
    augassign = (
        pipe_augassign
        | combine(comp_pipe + equals)
        | combine(dotdot + equals)
        | combine(comp_back_pipe + equals)
        | combine(comp_star_pipe + equals)
        | combine(comp_back_star_pipe + equals)
        | combine(comp_dubstar_pipe + equals)
        | combine(comp_back_dubstar_pipe + equals)
        | combine(unsafe_dubcolon + equals)
        | combine(div_dubslash + equals)
        | combine(div_slash + equals)
        | combine(exp_dubstar + equals)
        | combine(mul_star + equals)
        | combine(plus + equals)
        | combine(sub_minus + equals)
        | combine(percent + equals)
        | combine(amp + equals)
        | combine(bar + equals)
        | combine(caret + equals)
        | combine(lshift + equals)
        | combine(rshift + equals)
        | combine(matrix_at + equals)
        | combine(dubquestion + equals)
    )

    comp_op = (
        le | ge | ne | lt | gt | eq
        | addspace(keyword("not") + keyword("in"))
        | keyword("in")
        | addspace(keyword("is") + keyword("not"))
        | keyword("is")
    )

    atom_item = Forward()
    expr = Forward()
    star_expr = Forward()
    dubstar_expr = Forward()
    comp_for = Forward()
    test_no_cond = Forward()
    namedexpr_test = Forward()
    # for namedexpr locations only supported in Python 3.10
    new_namedexpr_test = Forward()

    negable_atom_item = condense(Optional(neg_minus) + atom_item)

    testlist = trace(itemlist(test, comma, suppress_trailing=False))
    testlist_has_comma = trace(addspace(OneOrMore(condense(test + comma)) + Optional(test)))
    new_namedexpr_testlist_has_comma = trace(addspace(OneOrMore(condense(new_namedexpr_test + comma)) + Optional(test)))

    testlist_star_expr = Forward()
    testlist_star_expr_ref = tokenlist(Group(test) | star_expr, comma, suppress=False)
    testlist_star_namedexpr = Forward()
    testlist_star_namedexpr_tokens = tokenlist(Group(namedexpr_test) | star_expr, comma, suppress=False)

    yield_from = Forward()
    dict_comp = Forward()
    dict_literal = Forward()
    yield_classic = addspace(keyword("yield") + Optional(testlist))
    yield_from_ref = keyword("yield").suppress() + keyword("from").suppress() + test
    yield_expr = yield_from | yield_classic
    dict_comp_ref = lbrace.suppress() + (
        test + colon.suppress() + test + comp_for
        | invalid_syntax(dubstar_expr + comp_for, "dict unpacking cannot be used in dict comprehension")
    ) + rbrace.suppress()
    dict_literal_ref = (
        lbrace.suppress()
        + Optional(
            tokenlist(
                Group(addspace(condense(test + colon) + test)) | dubstar_expr,
                comma,
            ),
        )
        + rbrace.suppress()
    )
    test_expr = yield_expr | testlist_star_expr

    base_op_item = (
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

        # neg_minus must come after minus
        | fixto(minus, "_coconut_minus")
        | fixto(neg_minus, "_coconut.operator.neg")

        | fixto(keyword("assert"), "_coconut_assert")
        | fixto(keyword("and"), "_coconut_bool_and")
        | fixto(keyword("or"), "_coconut_bool_or")
        | fixto(comma, "_coconut_comma_op")
        | fixto(dubquestion, "_coconut_none_coalesce")
        | fixto(dot, "_coconut.getattr")
        | fixto(unsafe_dubcolon, "_coconut.itertools.chain")
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
    partial_op_item = attach(
        labeled_group(dot.suppress() + base_op_item + test, "right partial")
        | labeled_group(test + base_op_item + dot.suppress(), "left partial"),
        partial_op_item_handle,
    )
    op_item = trace(partial_op_item | base_op_item)

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
        | tokenlist(Group(call_item), comma) + rparen.suppress()
        | Group(attach(addspace(test + comp_for), add_parens_handle)) + rparen.suppress()
        | Group(op_item) + rparen.suppress()
    )
    function_call = Forward()
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

    anon_namedtuple = Forward()
    anon_namedtuple_ref = tokenlist(
        Group(
            name
            + Optional(colon.suppress() + typedef_test)
            + equals.suppress() + test,
        ),
        comma,
    )

    comprehension_expr = (
        addspace(namedexpr_test + comp_for)
        | invalid_syntax(star_expr + comp_for, "iterable unpacking cannot be used in comprehension")
    )
    paren_atom = condense(
        lparen + (
            # everything here must end with rparen
            yield_expr + rparen
            | comprehension_expr + rparen
            | testlist_star_namedexpr + rparen
            | op_item + rparen
            | anon_namedtuple + rparen
            | rparen
        ),
    )

    list_expr = Forward()
    list_expr_ref = testlist_star_namedexpr_tokens
    array_literal = attach(
        lbrack.suppress() + OneOrMore(
            multisemicolon
            | attach(comprehension_expr, add_bracks_handle)
            | namedexpr_test + ~comma
            | list_expr,
        ) + rbrack.suppress(),
        array_literal_handle,
    )
    list_item = (
        condense(lbrack + Optional(comprehension_expr) + rbrack)
        | lbrack.suppress() + list_expr + rbrack.suppress()
        | array_literal
    )

    string_atom = Forward()
    string_atom_ref = OneOrMore(nonb_string) | OneOrMore(b_string)
    fixed_len_string_atom = OneOrMore(nonbf_string) | OneOrMore(b_string)

    keyword_atom = any_keyword_in(const_vars)
    passthrough_atom = trace(addspace(OneOrMore(passthrough_item)))

    set_literal = Forward()
    set_letter_literal = Forward()
    set_s = fixto(CaselessLiteral("s"), "s")
    set_f = fixto(CaselessLiteral("f"), "f")
    set_letter = set_s | set_f
    setmaker = Group(
        addspace(new_namedexpr_test + comp_for)("comp")
        | new_namedexpr_testlist_has_comma("list")
        | new_namedexpr_test("test"),
    )
    set_literal_ref = lbrace.suppress() + setmaker + rbrace.suppress()
    set_letter_literal_ref = combine(set_letter + lbrace.suppress()) + Optional(setmaker) + rbrace.suppress()

    lazy_items = Optional(tokenlist(test, comma))
    lazy_list = attach(lbanana.suppress() + lazy_items + rbanana.suppress(), lazy_list_handle)

    known_atom = trace(
        keyword_atom
        | string_atom
        | number
        | list_item
        | dict_comp
        | dict_literal
        | set_literal
        | set_letter_literal
        | lazy_list
        | ellipsis,
    )
    atom = (
        # known_atom must come before name to properly parse string prefixes
        known_atom
        | name
        | paren_atom
        | passthrough_atom
    )

    typedef_atom = Forward()
    typedef_or_expr = Forward()

    simple_trailer = (
        condense(dot + name)
        | condense(lbrack + subscriptlist + rbrack)
    )
    call_trailer = (
        function_call
        | invalid_syntax(dollar + questionmark, "'?' must come before '$' in None-coalescing partial application")
        | Group(dollar + ~lparen + ~lbrack)  # keep $ for item_handle
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

    complex_trailer = no_partial_complex_trailer | partial_trailer
    trailer = simple_trailer | complex_trailer

    attrgetter_atom_tokens = dot.suppress() + dotted_name + Optional(
        lparen + Optional(methodcaller_args) + rparen.suppress(),
    )
    attrgetter_atom = attach(attrgetter_atom_tokens, attrgetter_atom_handle)
    itemgetter_atom_tokens = dot.suppress() + OneOrMore(condense(Optional(dollar) + lbrack) + subscriptgrouplist + rbrack.suppress())
    itemgetter_atom = attach(itemgetter_atom_tokens, itemgetter_handle)
    implicit_partial_atom = (
        attrgetter_atom
        | itemgetter_atom
        | fixto(dot + lbrack + rbrack, "_coconut.operator.getitem")
        | fixto(dot + dollar + lbrack + rbrack, "_coconut_iter_getitem")
    )

    trailer_atom = Forward()
    trailer_atom_ref = atom + ZeroOrMore(trailer)
    atom_item <<= (
        trailer_atom
        | implicit_partial_atom
    )

    no_partial_trailer_atom = Forward()
    no_partial_trailer_atom_ref = atom + ZeroOrMore(no_partial_trailer)
    partial_atom_tokens = no_partial_trailer_atom + partial_trailer_tokens

    simple_assign = Forward()
    simple_assign_ref = maybeparens(
        lparen,
        (name | passthrough_atom)
        + ZeroOrMore(ZeroOrMore(complex_trailer) + OneOrMore(simple_trailer)),
        rparen,
    )
    simple_assignlist = maybeparens(lparen, itemlist(simple_assign, comma, suppress_trailing=False), rparen)

    assignlist = Forward()
    star_assign_item = Forward()
    base_assign_item = condense(
        simple_assign
        | lparen + assignlist + rparen
        | lbrack + assignlist + rbrack,
    )
    star_assign_item_ref = condense(star + base_assign_item)
    assign_item = star_assign_item | base_assign_item
    assignlist <<= itemlist(assign_item, comma, suppress_trailing=False)

    typed_assign_stmt = Forward()
    typed_assign_stmt_ref = simple_assign + colon.suppress() + typedef_test + Optional(equals.suppress() + test_expr)
    basic_stmt = trace(addspace(ZeroOrMore(assignlist + equals) + test_expr))

    impl_call_arg = disallow_keywords(reserved_vars) + (
        keyword_atom
        | number
        | dotted_name
    )
    impl_call = attach(
        disallow_keywords(reserved_vars)
        + atom_item
        + OneOrMore(impl_call_arg),
        impl_call_item_handle,
    )
    impl_call_item = (
        atom_item + ~impl_call_arg
        | impl_call
    )

    await_expr = Forward()
    await_expr_ref = await_kwd.suppress() + impl_call_item
    await_item = await_expr | impl_call_item

    compose_item = attach(tokenlist(await_item, dotdot, allow_trailing=False), compose_item_handle)

    factor = Forward()
    unary = plus | neg_minus | tilde
    power = trace(condense(compose_item + Optional(exp_dubstar + factor)))
    factor <<= condense(ZeroOrMore(unary) + power)

    mulop = mul_star | div_slash | div_dubslash | percent | matrix_at
    addop = plus | sub_minus
    shift = lshift | rshift

    # we condense all of these down, since Python handles the precedence, not Coconut
    # term = exprlist(factor, mulop)
    # arith_expr = exprlist(term, addop)
    # shift_expr = exprlist(arith_expr, shift)
    # and_expr = exprlist(shift_expr, amp)
    # xor_expr = exprlist(and_expr, caret)
    xor_expr = exprlist(
        factor,
        mulop
        | addop
        | shift
        | amp
        | caret,
    )

    or_expr = typedef_or_expr | exprlist(xor_expr, bar)

    chain_expr = attach(tokenlist(or_expr, dubcolon, allow_trailing=False), chain_handle)

    lambdef = Forward()

    infix_op = condense(backtick.suppress() + test_no_infix + backtick.suppress())

    infix_expr = Forward()
    infix_item = attach(
        Group(Optional(chain_expr))
        + OneOrMore(
            infix_op + Group(Optional(lambdef | chain_expr)),
        ),
        infix_handle,
    )
    infix_expr <<= (
        chain_expr + ~backtick
        | infix_item
    )

    none_coalesce_expr = attach(tokenlist(infix_expr, dubquestion, allow_trailing=False), none_coalesce_handle)

    comp_pipe_op = (
        comp_pipe
        | comp_star_pipe
        | comp_back_pipe
        | comp_back_star_pipe
        | comp_dubstar_pipe
        | comp_back_dubstar_pipe
    )
    comp_pipe_item = attach(
        OneOrMore(none_coalesce_expr + comp_pipe_op) + (lambdef | none_coalesce_expr),
        comp_pipe_handle,
    )
    comp_pipe_expr = (
        comp_pipe_item
        | none_coalesce_expr
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
        labeled_group(attrgetter_atom_tokens, "attrgetter") + pipe_op
        | labeled_group(itemgetter_atom_tokens, "itemgetter") + pipe_op
        | labeled_group(partial_atom_tokens, "partial") + pipe_op
        | labeled_group(comp_pipe_expr, "expr") + pipe_op
    )
    pipe_augassign_item = trace(
        # should match pipe_item but with pipe_op -> end_simple_stmt_item and no expr
        labeled_group(attrgetter_atom_tokens, "attrgetter") + end_simple_stmt_item
        | labeled_group(itemgetter_atom_tokens, "itemgetter") + end_simple_stmt_item
        | labeled_group(partial_atom_tokens, "partial") + end_simple_stmt_item,
    )
    last_pipe_item = Group(
        lambdef("expr")
        # we need longest here because there's no following pipe_op we can use as above
        | longest(
            attrgetter_atom_tokens("attrgetter"),
            itemgetter_atom_tokens("itemgetter"),
            partial_atom_tokens("partial"),
            comp_pipe_expr("expr"),
        ),
    )
    normal_pipe_expr = Forward()
    normal_pipe_expr_tokens = OneOrMore(pipe_item) + last_pipe_item

    pipe_expr = (
        comp_pipe_expr + ~pipe_op
        | normal_pipe_expr
    )

    expr <<= pipe_expr

    star_expr <<= Group(star + expr)
    dubstar_expr <<= Group(dubstar + expr)

    comparison = exprlist(expr, comp_op)
    not_test = addspace(ZeroOrMore(keyword("not")) + comparison)
    # we condense "and" and "or" into one, since Python handles the precedence, not Coconut
    # and_test = exprlist(not_test, keyword("and"))
    # test_item = trace(exprlist(and_test, keyword("or")))
    test_item = trace(exprlist(not_test, keyword("and") | keyword("or")))

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
    classic_lambdef_ref = addspace(lambda_kwd + condense(classic_lambdef_params + colon))
    new_lambdef = attach(new_lambdef_params + arrow.suppress(), lambdef_handle)
    implicit_lambdef = fixto(arrow, "lambda _=None:")
    lambdef_base = classic_lambdef | new_lambdef | implicit_lambdef

    stmt_lambdef = Forward()
    match_guard = Optional(keyword("if").suppress() + namedexpr_test)
    closing_stmt = longest(testlist("tests"), unsafe_simple_stmt_item)
    stmt_lambdef_match_params = Group(lparen.suppress() + match_args_list + match_guard + rparen.suppress())
    stmt_lambdef_params = Optional(
        attach(name, add_parens_handle)
        | parameters
        | stmt_lambdef_match_params,
        default="(_=None)",
    )
    stmt_lambdef_body = (
        Group(OneOrMore(simple_stmt_item + semicolon.suppress())) + Optional(closing_stmt)
        | Group(ZeroOrMore(simple_stmt_item + semicolon.suppress())) + closing_stmt
    )
    general_stmt_lambdef = (
        keyword("def").suppress()
        + stmt_lambdef_params
        + arrow.suppress()
        + stmt_lambdef_body
    )
    match_stmt_lambdef = (
        match_kwd.suppress()
        + keyword("def").suppress()
        + stmt_lambdef_match_params
        + arrow.suppress()
        + stmt_lambdef_body
    )
    stmt_lambdef_ref = general_stmt_lambdef | match_stmt_lambdef

    lambdef <<= addspace(lambdef_base + test) | stmt_lambdef
    lambdef_no_cond = trace(addspace(lambdef_base + test_no_cond))

    typedef_callable_params = (
        lparen.suppress() + Optional(testlist, default="") + rparen.suppress()
        | Optional(negable_atom_item)
    )
    unsafe_typedef_callable = attach(typedef_callable_params + arrow.suppress() + typedef_test, typedef_callable_handle)
    unsafe_typedef_atom = (  # use special type signifier for item_handle
        Group(fixto(lbrack + rbrack, "type:[]"))
        | Group(fixto(dollar + lbrack + rbrack, "type:$[]"))
        | Group(fixto(questionmark + ~questionmark, "type:?"))
    )
    unsafe_typedef_or_expr = Forward()
    unsafe_typedef_or_expr_ref = tokenlist(xor_expr, bar, allow_trailing=False, at_least_two=True)

    _typedef_test, typedef_callable, _typedef_atom, _typedef_or_expr = disable_outside(
        test,
        unsafe_typedef_callable,
        unsafe_typedef_atom,
        unsafe_typedef_or_expr,
    )
    typedef_test <<= _typedef_test
    typedef_atom <<= _typedef_atom
    typedef_or_expr <<= _typedef_or_expr

    alt_ternary_expr = attach(keyword("if").suppress() + test_item + then_kwd.suppress() + test_item + keyword("else").suppress() + test, alt_ternary_handle)
    test <<= (
        typedef_callable
        | lambdef
        | alt_ternary_expr
        | addspace(test_item + Optional(keyword("if") + test_item + keyword("else") + test))  # must come last since it includes plain test_item
    )
    test_no_cond <<= lambdef_no_cond | test_item

    namedexpr = Forward()
    namedexpr_ref = addspace(
        name + colon_eq + (
            test + ~colon_eq
            | attach(namedexpr, add_parens_handle)
        ),
    )
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
        Optional(function_call_tokens)
        + ~equals,  # don't match class destructuring assignment
    )
    class_suite = suite | attach(newline, class_suite_handle)
    classdef_ref = keyword("class").suppress() + name + classlist + class_suite
    comp_iter = Forward()
    comp_it_item = (
        invalid_syntax(maybeparens(lparen, namedexpr, rparen), "PEP 572 disallows assignment expressions in comprehension iterable expressions")
        | test_item
    )
    base_comp_for = addspace(keyword("for") + assignlist + keyword("in") + comp_it_item + Optional(comp_iter))
    async_comp_for_ref = addspace(async_kwd + base_comp_for)
    comp_for <<= async_comp_for | base_comp_for
    comp_if = addspace(keyword("if") + test_no_cond + Optional(comp_iter))
    comp_iter <<= comp_for | comp_if

    return_testlist = Forward()
    return_testlist_ref = testlist_star_expr
    return_stmt = addspace(keyword("return") - Optional(return_testlist))

    complex_raise_stmt = Forward()
    pass_stmt = keyword("pass")
    break_stmt = keyword("break")
    continue_stmt = keyword("continue")
    simple_raise_stmt = addspace(keyword("raise") + Optional(test))
    complex_raise_stmt_ref = keyword("raise").suppress() + test + keyword("from").suppress() - test
    raise_stmt = complex_raise_stmt | simple_raise_stmt
    flow_stmt = (
        return_stmt
        | raise_stmt
        | break_stmt
        | yield_expr
        | continue_stmt
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

    augassign_stmt = Forward()
    augassign_rhs = (
        labeled_group(pipe_augassign + pipe_augassign_item, "pipe")
        | labeled_group(augassign + test_expr, "simple")
    )
    augassign_stmt_ref = simple_assign + augassign_rhs

    simple_kwd_assign = attach(
        maybeparens(lparen, itemlist(name, comma), rparen) + Optional(equals.suppress() - test_expr),
        simple_kwd_assign_handle,
    )
    kwd_augassign = Forward()
    kwd_augassign_ref = name + augassign_rhs
    kwd_assign = (
        kwd_augassign
        | simple_kwd_assign
    )
    global_stmt = addspace(keyword("global") - kwd_assign)
    nonlocal_stmt = Forward()
    nonlocal_stmt_ref = addspace(keyword("nonlocal") - kwd_assign)

    del_stmt = addspace(keyword("del") - simple_assignlist)

    matchlist_data_item = Group(Optional(star | name + equals) + match)
    matchlist_data = Group(Optional(tokenlist(matchlist_data_item, comma)))

    match_check_equals = Forward()
    match_check_equals_ref = equals

    match_dotted_name_const = Forward()
    complex_number = condense(Optional(neg_minus) + number + (plus | sub_minus) + Optional(neg_minus) + imag_num)
    match_const = condense(
        (eq | match_check_equals).suppress() + negable_atom_item
        | string_atom
        | complex_number
        | Optional(neg_minus) + number
        | match_dotted_name_const,
    )

    matchlist_set = Group(Optional(tokenlist(match_const, comma)))
    match_pair = Group(match_const + colon.suppress() + match)
    matchlist_dict = Group(Optional(tokenlist(match_pair, comma)))

    matchlist_tuple_items = (
        match + OneOrMore(comma.suppress() + match) + Optional(comma.suppress())
        | match + comma.suppress()
    )
    matchlist_tuple = Group(Optional(matchlist_tuple_items))
    matchlist_list = Group(Optional(tokenlist(match, comma)))
    match_list = Group(lbrack + matchlist_list + rbrack.suppress())
    match_tuple = Group(lparen + matchlist_tuple + rparen.suppress())
    match_lazy = Group(lbanana + matchlist_list + rbanana.suppress())

    interior_name_match = labeled_group(name, "var")
    match_string = interleaved_tokenlist(
        fixed_len_string_atom("string"),
        interior_name_match("capture"),
        plus,
        at_least_two=True,
    )("string")
    sequence_match = interleaved_tokenlist(
        (match_list | match_tuple)("literal"),
        interior_name_match("capture"),
        plus,
    )("sequence")
    iter_match = interleaved_tokenlist(
        (match_list | match_tuple | match_lazy)("literal"),
        interior_name_match("capture"),
        unsafe_dubcolon,
        at_least_two=True,
    )("iter")
    matchlist_star = interleaved_tokenlist(
        star.suppress() + match("capture"),
        match("elem"),
        comma,
        allow_trailing=True,
    )
    star_match = (
        lbrack.suppress() + matchlist_star + rbrack.suppress()
        | lparen.suppress() + matchlist_star + rparen.suppress()
    )("star")

    base_match = trace(
        Group(
            (negable_atom_item + arrow.suppress() + match)("view")
            | match_string
            | match_const("const")
            | (keyword_atom | keyword("is").suppress() + negable_atom_item)("is")
            | (lbrace.suppress() + matchlist_dict + Optional(dubstar.suppress() + (name | condense(lbrace + rbrace))) + rbrace.suppress())("dict")
            | (Optional(set_s.suppress()) + lbrace.suppress() + matchlist_set + rbrace.suppress())("set")
            | iter_match
            | match_lazy("lazy")
            | sequence_match
            | star_match
            | (lparen.suppress() + match + rparen.suppress())("paren")
            | (data_kwd.suppress() + name + lparen.suppress() + matchlist_data + rparen.suppress())("data")
            | (keyword("class").suppress() + name + lparen.suppress() + matchlist_data + rparen.suppress())("class")
            | (name + lparen.suppress() + matchlist_data + rparen.suppress())("data_or_class")
            | Optional(keyword("as").suppress()) + name("var"),
        ),
    )

    matchlist_isinstance = base_match + OneOrMore(keyword("is").suppress() + negable_atom_item)
    isinstance_match = labeled_group(matchlist_isinstance, "isinstance_is") | base_match

    matchlist_bar_or = isinstance_match + OneOrMore(bar.suppress() + isinstance_match)
    bar_or_match = labeled_group(matchlist_bar_or, "or") | isinstance_match

    matchlist_infix = bar_or_match + OneOrMore(infix_op + negable_atom_item)
    infix_match = labeled_group(matchlist_infix, "infix") | bar_or_match

    matchlist_as = infix_match + OneOrMore(keyword("as").suppress() + name)
    as_match = labeled_group(matchlist_as, "as") | infix_match

    matchlist_and = as_match + OneOrMore(keyword("and").suppress() + as_match)
    and_match = labeled_group(matchlist_and, "and") | as_match

    matchlist_kwd_or = and_match + OneOrMore(keyword("or").suppress() + and_match)
    kwd_or_match = labeled_group(matchlist_kwd_or, "or") | and_match

    match <<= trace(kwd_or_match)

    many_match = (
        labeled_group(matchlist_star, "star")
        | labeled_group(matchlist_tuple_items, "implicit_tuple")
        | match
    )

    else_stmt = condense(keyword("else") - suite)
    full_suite = colon.suppress() - Group((newline.suppress() - indent.suppress() - OneOrMore(stmt) - dedent.suppress()) | simple_stmt)
    full_match = Forward()
    full_match_ref = (
        match_kwd.suppress()
        + many_match
        + addspace(Optional(keyword("not")) + keyword("in"))
        - testlist_star_namedexpr
        - match_guard
        - full_suite
    )
    match_stmt = trace(condense(full_match - Optional(else_stmt)))

    destructuring_stmt = Forward()
    base_destructuring_stmt = Optional(match_kwd.suppress()) + many_match + equals.suppress() + test_expr
    destructuring_stmt_ref, match_dotted_name_const_ref = disable_inside(base_destructuring_stmt, must_be_dotted_name)

    cases_stmt = Forward()
    # both syntaxes here must be kept matching except for the keywords
    cases_kwd = cases_kwd | case_kwd
    case_match_co_syntax = trace(
        Group(
            (match_kwd | case_kwd).suppress()
            + stores_loc_item
            + many_match
            + Optional(keyword("if").suppress() + namedexpr_test)
            - full_suite,
        ),
    )
    cases_stmt_co_syntax = (
        cases_kwd + testlist_star_namedexpr + colon.suppress() + newline.suppress()
        + indent.suppress() + Group(OneOrMore(case_match_co_syntax))
        + dedent.suppress() + Optional(keyword("else").suppress() + suite)
    )
    case_match_py_syntax = trace(
        Group(
            case_kwd.suppress()
            + stores_loc_item
            + many_match
            + Optional(keyword("if").suppress() + namedexpr_test)
            - full_suite,
        ),
    )
    cases_stmt_py_syntax = (
        match_kwd + testlist_star_namedexpr + colon.suppress() + newline.suppress()
        + indent.suppress() + Group(OneOrMore(case_match_py_syntax))
        + dedent.suppress() + Optional(keyword("else").suppress() - suite)
    )
    cases_stmt_ref = cases_stmt_co_syntax | cases_stmt_py_syntax

    assert_stmt = addspace(keyword("assert") - testlist)
    if_stmt = condense(
        addspace(keyword("if") + condense(namedexpr_test + suite))
        - ZeroOrMore(addspace(keyword("elif") - condense(namedexpr_test - suite)))
        - Optional(else_stmt),
    )
    while_stmt = addspace(keyword("while") - condense(namedexpr_test - suite - Optional(else_stmt)))

    for_stmt = addspace(keyword("for") + assignlist + keyword("in") - condense(testlist - suite - Optional(else_stmt)))

    base_match_for_stmt = Forward()
    base_match_for_stmt_ref = keyword("for").suppress() + many_match + keyword("in").suppress() - testlist - colon.suppress() - condense(nocolon_suite - Optional(else_stmt))
    match_for_stmt = Optional(match_kwd.suppress()) + base_match_for_stmt

    except_item = (
        testlist_has_comma("list")
        | test("test")
    ) - Optional(
        keyword("as").suppress() - name,
    )
    except_clause = attach(except_kwd + except_item, except_handle)
    except_star_clause = Forward()
    except_star_clause_ref = attach(except_star_kwd + except_item, except_handle)
    try_stmt = condense(
        keyword("try") - suite + (
            keyword("finally") - suite
            | (
                OneOrMore(except_clause - suite) - Optional(except_kwd - suite)
                | except_kwd - suite
                | OneOrMore(except_star_clause - suite)
            ) - Optional(else_stmt) - Optional(keyword("finally") - suite)
        ),
    )

    with_item = addspace(test + Optional(keyword("as") + base_assign_item))
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
            + end_func_colon
            - (
                attach(simple_stmt, make_suite_handle)
                | (
                    newline.suppress()
                    - indent.suppress()
                    - Optional(docstring)
                    - attach(condense(OneOrMore(stmt)), make_suite_handle)
                    - dedent.suppress()
                )
            ),
            join_match_funcdef,
        ),
    )
    match_def_modifiers = trace(
        Optional(
            # we don't suppress addpattern so its presence can be detected later
            match_kwd.suppress() + Optional(addpattern_kwd)
            | addpattern_kwd + Optional(match_kwd.suppress()),
        ),
    )
    match_funcdef = addspace(match_def_modifiers + def_match_funcdef)

    where_stmt = attach(
        unsafe_simple_stmt_item
        + where_kwd.suppress()
        - full_suite,
        where_handle,
    )

    implicit_return = (
        invalid_syntax(return_stmt, "expected expression but got return statement")
        | attach(return_testlist, implicit_return_handle)
    )
    implicit_return_where = attach(
        implicit_return
        + where_kwd.suppress()
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
                + end_func_equals
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
    async_stmt_ref = addspace(
        async_kwd + (with_stmt | for_stmt | match_for_stmt)  # handles async [match] for
        | match_kwd.suppress() + async_kwd + base_match_for_stmt,  # handles match async for
    )

    async_funcdef = async_kwd.suppress() + (funcdef | math_funcdef)
    async_match_funcdef = trace(
        addspace(
            (
                # we don't suppress addpattern so its presence can be detected later
                match_kwd.suppress() + addpattern_kwd + async_kwd.suppress()
                | addpattern_kwd + match_kwd.suppress() + async_kwd.suppress()
                | match_kwd.suppress() + async_kwd.suppress() + Optional(addpattern_kwd)
                | addpattern_kwd + async_kwd.suppress() + Optional(match_kwd.suppress())
                | async_kwd.suppress() + match_def_modifiers
            ) + (def_match_funcdef | math_match_funcdef),
        ),
    )

    yield_normal_funcdef = keyword("yield").suppress() + funcdef
    yield_match_funcdef = trace(
        addspace(
            (
                # must match async_match_funcdef above with async_kwd -> keyword("yield")
                match_kwd.suppress() + addpattern_kwd + keyword("yield").suppress()
                | addpattern_kwd + match_kwd.suppress() + keyword("yield").suppress()
                | match_kwd.suppress() + keyword("yield").suppress() + Optional(addpattern_kwd)
                | addpattern_kwd + keyword("yield").suppress() + Optional(match_kwd.suppress())
                | keyword("yield").suppress() + match_def_modifiers
            ) + def_match_funcdef,
        ),
    )
    yield_funcdef = attach(yield_normal_funcdef | yield_match_funcdef, yield_funcdef_handle)

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
            (newline.suppress() + indent.suppress() + Optional(docstring) + Group(OneOrMore(stmt)) - dedent.suppress())("complex")
            | (newline.suppress() + indent.suppress() + docstring - dedent.suppress() | docstring)("docstring")
            | simple_stmt("simple")
        ) | newline("empty"),
    )
    datadef_ref = data_kwd.suppress() + name + data_args + data_suite

    match_datadef = Forward()
    match_data_args = lparen.suppress() + Group(
        match_args_list + match_guard,
    ) + rparen.suppress() + Optional(keyword("from").suppress() + testlist)
    match_datadef_ref = Optional(match_kwd.suppress()) + data_kwd.suppress() + name + match_data_args + data_suite

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
        | yield_funcdef
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
        | match_for_stmt
        | simple_compound_stmt
        | where_stmt,
    )
    endline_semicolon = Forward()
    endline_semicolon_ref = semicolon.suppress() + newline
    keyword_stmt = trace(
        flow_stmt
        | import_stmt
        | assert_stmt
        | pass_stmt
        | del_stmt
        | global_stmt
        | nonlocal_stmt,
    )
    special_stmt = (
        keyword_stmt
        | augassign_stmt
        | typed_assign_stmt
    )
    unsafe_simple_stmt_item <<= special_stmt | longest(basic_stmt, destructuring_stmt)
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
    anything_stmt = Forward()
    stmt <<= final(
        compound_stmt
        | simple_stmt
        # must be after destructuring due to ambiguity
        | cases_stmt
        # at the very end as a fallback case for the anything parser
        | anything_stmt,
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
    some_eval_parser = start_marker + eval_input

    parens = originalTextFor(nestedExpr("(", ")", ignoreExpr=None))
    brackets = originalTextFor(nestedExpr("[", "]", ignoreExpr=None))
    braces = originalTextFor(nestedExpr("{", "}", ignoreExpr=None))

    unsafe_anything_stmt = originalTextFor(regex_item("[^\n]+\n+"))
    unsafe_xonsh_command = originalTextFor(
        (Optional(at) + dollar | bang)
        + (parens | brackets | braces | name),
    )
    xonsh_parser, _anything_stmt, _xonsh_command = disable_outside(
        file_parser,
        unsafe_anything_stmt,
        unsafe_xonsh_command,
    )
    anything_stmt <<= _anything_stmt
    xonsh_command <<= _xonsh_command

# end: MAIN GRAMMAR
# -----------------------------------------------------------------------------------------------------------------------
# EXTRA GRAMMAR:
# -----------------------------------------------------------------------------------------------------------------------

    just_non_none_atom = start_marker + ~keyword("None") + known_atom + end_marker

    original_function_call_tokens = (
        lparen.suppress() + rparen.suppress()
        # we need to keep the parens here, since f(x for x in y) is fine but tail_call(f, x for x in y) is not
        | condense(lparen + originalTextFor(test + comp_for) + rparen)
        | attach(parens, strip_parens_handle)
    )

    def get_tre_return_grammar(self, func_name):
        """The TRE return grammar is parameterized by the name of the function being optimized."""
        return (
            self.start_marker
            + keyword("return").suppress()
            + maybeparens(
                self.lparen,
                keyword(func_name, explicit_prefix=False).suppress()
                + self.original_function_call_tokens,
                self.rparen,
            ) + self.end_marker
        )

    tco_return = attach(
        start_marker
        + keyword("return").suppress()
        + maybeparens(
            lparen,
            disallow_keywords(untcoable_funcs, with_suffix=lparen)
            + condense(
                (base_name | parens | brackets | braces | string_atom)
                + ZeroOrMore(
                    dot + base_name
                    | brackets
                    # don't match the last set of parentheses
                    | parens + ~end_marker + ~rparen,
                ),
            )
            + original_function_call_tokens,
            rparen,
        ) + end_marker,
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
                ) + Optional(passthrough_item.suppress()),
                comma + Optional(passthrough_item),  # implicitly suppressed
            ),
        ),
    )

    dotted_base_name = condense(base_name + ZeroOrMore(dot + base_name))
    split_func = (
        start_marker
        - keyword("def").suppress()
        - dotted_base_name
        - lparen.suppress() - parameters_tokens - rparen.suppress()
    )

    stores_scope = (
        lambda_kwd
        # match comprehensions but not for loops
        | ~indent + ~dedent + any_char + keyword("for") + base_name + keyword("in")
    )

    just_a_string = start_marker + string_atom + end_marker

    end_of_line = end_marker | Literal("\n") | pound

    unsafe_equals = Literal("=")

    kwd_err_msg = attach(any_keyword_in(keyword_vars), kwd_err_msg_handle)
    parse_err_msg = (
        start_marker + (
            fixto(end_of_line, "misplaced newline (maybe missing ':')")
            | fixto(Optional(keyword("if") + skip_to_in_line(unsafe_equals)) + equals, "misplaced assignment (maybe should be '==')")
            | kwd_err_msg
        )
        | fixto(
            questionmark
            + ~dollar
            + ~lparen
            + ~lbrack
            + ~dot,
            "misplaced '?' (naked '?' is only supported inside partial application arguments)",
        )
    )

    end_f_str_expr = start_marker + (bang | colon | rbrace)

    string_start = start_marker + quotedString

# end: EXTRA GRAMMAR
# -----------------------------------------------------------------------------------------------------------------------
# TRACING:
# -----------------------------------------------------------------------------------------------------------------------


def set_grammar_names():
    """Set names of grammar elements to their variable names."""
    for varname, val in vars(Grammar).items():
        if isinstance(val, ParserElement):
            val.setName(varname)
            if isinstance(val, Forward):
                trace(val)


# end: TRACING
