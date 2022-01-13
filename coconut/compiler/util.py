#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Utilities for use in the compiler.
"""

# Table of Contents:
#   - Imports
#   - Computation Graph
#   - Targets
#   - Parse Elements
#   - Utilities

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import sys
import re
import ast
import inspect
import __future__
from functools import partial, reduce
from contextlib import contextmanager
from pprint import pformat

from coconut._pyparsing import (
    USE_COMPUTATION_GRAPH,
    replaceWith,
    ZeroOrMore,
    OneOrMore,
    Optional,
    SkipTo,
    CharsNotIn,
    ParseElementEnhance,
    ParseException,
    ParseBaseException,
    ParseResults,
    Combine,
    Regex,
    Empty,
    Literal,
    Group,
    ParserElement,
    _trim_arity,
    _ParseResultsWithOffset,
)

from coconut import embed
from coconut.util import (
    override,
    get_name,
    get_target_info,
)
from coconut.terminal import (
    logger,
    complain,
    internal_assert,
    trace,
)
from coconut.constants import (
    CPYTHON,
    opens,
    closes,
    openindent,
    closeindent,
    default_whitespace_chars,
    supported_py2_vers,
    supported_py3_vers,
    tabideal,
    embed_on_internal_exc,
    specific_targets,
    pseudo_targets,
    reserved_vars,
    use_packrat_parser,
    packrat_cache_size,
    temp_grammar_item_ref_count,
    indchars,
)
from coconut.exceptions import (
    CoconutException,
    CoconutInternalException,
    CoconutDeferredSyntaxError,
)

# -----------------------------------------------------------------------------------------------------------------------
# COMPUTATION GRAPH:
# -----------------------------------------------------------------------------------------------------------------------

indexable_evaluated_tokens_types = (ParseResults, list, tuple)


def evaluate_tokens(tokens, **kwargs):
    """Evaluate the given tokens in the computation graph."""
    # can't have this be a normal kwarg to make evaluate_tokens a valid parse action
    evaluated_toklists = kwargs.pop("evaluated_toklists", ())
    internal_assert(not kwargs, "invalid keyword arguments to evaluate_tokens", kwargs)

    if isinstance(tokens, ParseResults):

        # evaluate the list portion of the ParseResults
        old_toklist, name, asList, modal = tokens.__getnewargs__()
        new_toklist = None
        for eval_old_toklist, eval_new_toklist in evaluated_toklists:
            if old_toklist == eval_old_toklist:
                new_toklist = eval_new_toklist
                break
        if new_toklist is None:
            new_toklist = [evaluate_tokens(toks, evaluated_toklists=evaluated_toklists) for toks in old_toklist]
            # overwrite evaluated toklists rather than appending, since this
            #  should be all the information we need for evaluating the dictionary
            evaluated_toklists = ((old_toklist, new_toklist),)
        new_tokens = ParseResults(new_toklist, name, asList, modal)
        new_tokens._ParseResults__accumNames.update(tokens._ParseResults__accumNames)

        # evaluate the dictionary portion of the ParseResults
        new_tokdict = {}
        for name, occurrences in tokens._ParseResults__tokdict.items():
            new_occurrences = []
            for value, position in occurrences:
                new_value = evaluate_tokens(value, evaluated_toklists=evaluated_toklists)
                new_occurrences.append(_ParseResultsWithOffset(new_value, position))
            new_tokdict[name] = new_occurrences
        new_tokens._ParseResults__tokdict.update(new_tokdict)

        return new_tokens

    else:

        if evaluated_toklists:
            for eval_old_toklist, eval_new_toklist in evaluated_toklists:
                indices = multi_index_lookup(eval_old_toklist, tokens, indexable_types=indexable_evaluated_tokens_types)
                if indices is not None:
                    new_tokens = eval_new_toklist
                    for ind in indices:
                        new_tokens = new_tokens[ind]
                    return new_tokens
            complain(
                lambda: CoconutInternalException(
                    "inefficient reevaluation of tokens: {tokens} not in:\n{toklists}".format(
                        tokens=tokens,
                        toklists=pformat([eval_old_toklist for eval_old_toklist, eval_new_toklist in evaluated_toklists]),
                    ),
                ),
            )

        if isinstance(tokens, str):
            return tokens

        elif isinstance(tokens, ComputationNode):
            return tokens.evaluate()

        elif isinstance(tokens, list):
            return [evaluate_tokens(inner_toks, evaluated_toklists=evaluated_toklists) for inner_toks in tokens]

        elif isinstance(tokens, tuple):
            return tuple(evaluate_tokens(inner_toks, evaluated_toklists=evaluated_toklists) for inner_toks in tokens)

        else:
            raise CoconutInternalException("invalid computation graph tokens", tokens)


class ComputationNode(object):
    """A single node in the computation graph."""
    __slots__ = ("action", "original", "loc", "tokens") + (("been_called",) if DEVELOP else ())

    def __new__(cls, action, original, loc, tokens, ignore_no_tokens=False, ignore_one_token=False, greedy=False, trim_arity=True):
        """Create a ComputionNode to return from a parse action.

        If ignore_no_tokens, then don't call the action if there are no tokens.
        If ignore_one_token, then don't call the action if there is only one token.
        If greedy, then never defer the action until later."""
        if ignore_no_tokens and len(tokens) == 0:
            return []
        elif ignore_one_token and len(tokens) == 1:
            return tokens[0]  # could be a ComputationNode, so we can't have an __init__
        else:
            self = super(ComputationNode, cls).__new__(cls)
            if trim_arity:
                self.action = _trim_arity(action)
            else:
                self.action = action
            self.original = original
            self.loc = loc
            self.tokens = tokens
            if DEVELOP:
                self.been_called = False
            if greedy:
                return self.evaluate()
            else:
                return self

    @property
    def name(self):
        """Get the name of the action."""
        name = getattr(self.action, "__name__", None)
        # repr(action) not defined for all actions, so must only be evaluated if getattr fails
        return name if name is not None else repr(self.action)

    def evaluate(self):
        """Get the result of evaluating the computation graph at this node."""
        if DEVELOP:
            internal_assert(not self.been_called, "inefficient reevaluation of action " + self.name + " with tokens", self.tokens)
            self.been_called = True
        evaluated_toks = evaluate_tokens(self.tokens)
        if logger.tracing:  # avoid the overhead of the call if not tracing
            logger.log_trace(self.name, self.original, self.loc, evaluated_toks, self.tokens)
        try:
            return self.action(
                self.original,
                self.loc,
                evaluated_toks,
            )
        except CoconutException:
            raise
        except (Exception, AssertionError):
            logger.print_exc()
            error = CoconutInternalException("error computing action " + self.name + " of evaluated tokens", evaluated_toks)
            if embed_on_internal_exc:
                logger.warn_err(error)
                embed(depth=2)
            else:
                raise error

    def __repr__(self):
        """Get a representation of the entire computation graph below this node."""
        if not logger.tracing:
            logger.warn_err(CoconutInternalException("ComputationNode.__repr__ called when not tracing"))
        inner_repr = "\n".join("\t" + line for line in repr(self.tokens).splitlines())
        return self.name + "(\n" + inner_repr + "\n)"


class CombineNode(Combine):
    """Modified Combine to work with the computation graph."""
    __slots__ = ()

    def _combine(self, original, loc, tokens):
        """Implement the parse action for Combine."""
        combined_tokens = super(CombineNode, self).postParse(original, loc, tokens)
        if DEVELOP:  # avoid the overhead of the call if not develop
            internal_assert(len(combined_tokens) == 1, "Combine produced multiple tokens", combined_tokens)
        return combined_tokens[0]

    @override
    def postParse(self, original, loc, tokens):
        """Create a ComputationNode for Combine."""
        return ComputationNode(self._combine, original, loc, tokens, ignore_no_tokens=True, ignore_one_token=True, trim_arity=False)


if USE_COMPUTATION_GRAPH:
    combine = CombineNode
else:
    combine = Combine


def add_action(item, action, make_copy=None):
    """Add a parse action to the given item."""
    if make_copy is None:
        item_ref_count = sys.getrefcount(item) if CPYTHON else float("inf")
        internal_assert(item_ref_count >= temp_grammar_item_ref_count, "add_action got item with too low ref count", (item, type(item), item_ref_count))
        make_copy = item_ref_count > temp_grammar_item_ref_count
    if make_copy:
        item = item.copy()
    return item.addParseAction(action)


def attach(item, action, ignore_no_tokens=None, ignore_one_token=None, ignore_tokens=None, trim_arity=None, **kwargs):
    """Set the parse action for the given item to create a node in the computation graph."""
    if ignore_tokens is None:
        ignore_tokens = getattr(action, "ignore_tokens", False)
    # if ignore_tokens, then we can just pass in the computation graph and have it be ignored
    if not ignore_tokens and USE_COMPUTATION_GRAPH:
        # use the action's annotations to generate the defaults
        if ignore_no_tokens is None:
            ignore_no_tokens = getattr(action, "ignore_no_tokens", False)
        if ignore_one_token is None:
            ignore_one_token = getattr(action, "ignore_one_token", False)
        if trim_arity is None:
            trim_arity = getattr(action, "trim_arity", None)
            if trim_arity is None:
                trim_arity = should_trim_arity(action)
        # only include keyword arguments in the partial that are not the same as the default
        if ignore_no_tokens:
            kwargs["ignore_no_tokens"] = ignore_no_tokens
        if ignore_one_token:
            kwargs["ignore_one_token"] = ignore_one_token
        if not trim_arity:
            kwargs["trim_arity"] = trim_arity
        action = partial(ComputationNode, action, **kwargs)
    return add_action(item, action)


def trace_attach(*args, **kwargs):
    """trace_attach = trace .. attach"""
    return trace(attach(*args, **kwargs))


def final_evaluate_tokens(tokens):
    """Same as evaluate_tokens but should only be used once a parse is assured."""
    if use_packrat_parser:
        # clear cache without resetting stats
        ParserElement.packrat_cache.clear()
    if USE_COMPUTATION_GRAPH:
        return evaluate_tokens(tokens)
    else:
        return tokens


def final(item):
    """Collapse the computation graph upon parsing the given item."""
    # evaluate_tokens expects a computation graph, so we just call add_action directly
    return add_action(item, final_evaluate_tokens)


def unpack(tokens):
    """Evaluate and unpack the given computation graph."""
    logger.log_tag("unpack", tokens)
    if USE_COMPUTATION_GRAPH:
        tokens = evaluate_tokens(tokens)
    if isinstance(tokens, ParseResults) and len(tokens) == 1:
        tokens = tokens[0]
    return tokens


@contextmanager
def parsing_context(inner_parse):
    """Context to manage the packrat cache across parse calls."""
    if inner_parse and use_packrat_parser:
        # store old packrat cache
        old_cache = ParserElement.packrat_cache
        old_cache_stats = ParserElement.packrat_cache_stats[:]

        # give inner parser a new packrat cache
        ParserElement._packratEnabled = False
        ParserElement.enablePackrat(packrat_cache_size)
    try:
        yield
    finally:
        if inner_parse and use_packrat_parser:
            ParserElement.packrat_cache = old_cache
            ParserElement.packrat_cache_stats[0] += old_cache_stats[0]
            ParserElement.packrat_cache_stats[1] += old_cache_stats[1]


def parse(grammar, text, inner=False):
    """Parse text using grammar."""
    with parsing_context(inner):
        return unpack(grammar.parseWithTabs().parseString(text))


def try_parse(grammar, text, inner=False):
    """Attempt to parse text using grammar else None."""
    with parsing_context(inner):
        try:
            return parse(grammar, text)
        except ParseBaseException:
            return None


def all_matches(grammar, text, inner=False):
    """Find all matches for grammar in text."""
    with parsing_context(inner):
        for tokens, start, stop in grammar.parseWithTabs().scanString(text):
            yield unpack(tokens), start, stop


def parse_where(grammar, text, inner=False):
    """Determine where the first parse is."""
    with parsing_context(inner):
        for tokens, start, stop in grammar.parseWithTabs().scanString(text):
            return start, stop
    return None, None


def match_in(grammar, text, inner=False):
    """Determine if there is a match for grammar in text."""
    start, stop = parse_where(grammar, text, inner)
    internal_assert((start is None) == (stop is None), "invalid parse_where results", (start, stop))
    return start is not None


def transform(grammar, text, inner=False):
    """Transform text by replacing matches to grammar."""
    with parsing_context(inner):
        result = add_action(grammar, unpack).parseWithTabs().transformString(text)
        if result == text:
            result = None
        return result


# -----------------------------------------------------------------------------------------------------------------------
# TARGETS:
# -----------------------------------------------------------------------------------------------------------------------


raw_sys_target = str(sys.version_info[0]) + str(sys.version_info[1])
if raw_sys_target in pseudo_targets:
    sys_target = pseudo_targets[raw_sys_target]
elif raw_sys_target in specific_targets:
    sys_target = raw_sys_target
elif sys.version_info > supported_py3_vers[-1]:
    sys_target = "".join(str(i) for i in supported_py3_vers[-1])
elif sys.version_info < supported_py2_vers[0]:
    sys_target = "".join(str(i) for i in supported_py2_vers[0])
elif sys.version_info < (3,):
    sys_target = "".join(str(i) for i in supported_py2_vers[-1])
else:
    sys_target = "".join(str(i) for i in supported_py3_vers[0])


def get_vers_for_target(target):
    """Gets a list of the versions supported by the given target."""
    target_info = get_target_info(target)
    if not target_info:
        return supported_py2_vers + supported_py3_vers
    elif len(target_info) == 1:
        if target_info == (2,):
            return supported_py2_vers
        elif target_info == (3,):
            return supported_py3_vers
        else:
            raise CoconutInternalException("invalid target info", target_info)
    elif target_info[0] == 2:
        return tuple(ver for ver in supported_py2_vers if ver >= target_info)
    elif target_info[0] == 3:
        return tuple(ver for ver in supported_py3_vers if ver >= target_info)
    else:
        raise CoconutInternalException("invalid target info", target_info)


def get_target_info_smart(target, mode="lowest"):
    """Converts target into a length 2 Python version tuple.

    Modes:
    - "lowest" (default): Gets the lowest version supported by the target.
    - "highest": Gets the highest version supported by the target.
    - "nearest": Gets the supported version that is nearest to the current one.
    - "mypy": Gets the version to use for --mypy."""
    supported_vers = get_vers_for_target(target)
    if mode == "lowest":
        return supported_vers[0]
    elif mode == "highest":
        return supported_vers[-1]
    elif mode == "nearest":
        sys_ver = sys.version_info[:2]
        if sys_ver in supported_vers:
            return sys_ver
        elif sys_ver > supported_vers[-1]:
            return supported_vers[-1]
        elif sys_ver < supported_vers[0]:
            return supported_vers[0]
        else:
            raise CoconutInternalException("invalid sys version", sys_ver)
    elif mode == "mypy":
        if any(v[0] == 2 for v in supported_vers):
            return supported_py2_vers[-1]
        else:
            return supported_vers[-1]
    else:
        raise CoconutInternalException("unknown get_target_info_smart mode", mode)


# -----------------------------------------------------------------------------------------------------------------------
# PARSE ELEMENTS:
# -----------------------------------------------------------------------------------------------------------------------

class Wrap(ParseElementEnhance):
    """PyParsing token that wraps the given item in the given context manager."""
    __slots__ = ("errmsg", "wrapper")

    def __init__(self, item, wrapper):
        super(Wrap, self).__init__(item)
        self.errmsg = item.errmsg + " (Wrapped)"
        self.wrapper = wrapper
        self.setName(get_name(item))

    @property
    def _wrapper_name(self):
        """Wrapper display name."""
        return self.name + " wrapper"

    @override
    def parseImpl(self, instring, loc, *args, **kwargs):
        """Wrapper around ParseElementEnhance.parseImpl."""
        if logger.tracing:  # avoid the overhead of the call if not tracing
            logger.log_trace(self._wrapper_name, instring, loc)
        with logger.indent_tracing():
            with self.wrapper(self, instring, loc):
                evaluated_toks = super(Wrap, self).parseImpl(instring, loc, *args, **kwargs)
        if logger.tracing:  # avoid the overhead of the call if not tracing
            logger.log_trace(self._wrapper_name, instring, loc, evaluated_toks)
        return evaluated_toks


def disable_inside(item, *elems, **kwargs):
    """Prevent elems from matching inside of item.

    Returns (item with elem disabled, *new versions of elems).
    """
    _invert = kwargs.pop("_invert", False)
    internal_assert(not kwargs, "excess keyword arguments passed to disable_inside")

    level = [0]  # number of wrapped items deep we are; in a list to allow modification

    @contextmanager
    def manage_item(self, instring, loc):
        level[0] += 1
        try:
            yield
        finally:
            level[0] -= 1

    yield Wrap(item, manage_item)

    @contextmanager
    def manage_elem(self, instring, loc):
        if level[0] == 0 if not _invert else level[0] > 0:
            yield
        else:
            raise ParseException(instring, loc, self.errmsg, self)

    for elem in elems:
        yield Wrap(elem, manage_elem)


def disable_outside(item, *elems):
    """Prevent elems from matching outside of item.

    Returns (item with elem enabled, *new versions of elems).
    """
    for wrapped in disable_inside(item, *elems, **{"_invert": True}):
        yield wrapped


def labeled_group(item, label):
    """A labeled pyparsing Group."""
    return Group(item(label))


def invalid_syntax(item, msg, **kwargs):
    """Mark a grammar item as an invalid item that raises a syntax err with msg."""
    if isinstance(item, str):
        item = Literal(item)
    elif isinstance(item, tuple):
        item = reduce(lambda a, b: a | b, map(Literal, item))

    def invalid_syntax_handle(loc, tokens):
        raise CoconutDeferredSyntaxError(msg, loc)
    return attach(item, invalid_syntax_handle, ignore_tokens=True, **kwargs)


def skip_to_in_line(item):
    """Skip parsing to the next match of item in the current line."""
    return SkipTo(item, failOn=Literal("\n"))


skip_whitespace = SkipTo(CharsNotIn(default_whitespace_chars)).suppress()


def longest(*args):
    """Match the longest of the given grammar elements."""
    internal_assert(len(args) >= 2, "longest expects at least two args")
    matcher = args[0] + skip_whitespace
    for elem in args[1:]:
        matcher ^= elem + skip_whitespace
    return matcher


def compile_regex(regex, options=None):
    """Compiles the given regex to support unicode."""
    if options is None:
        options = re.U
    else:
        options |= re.U
    return re.compile(regex, options)


def regex_item(regex, options=None):
    """pyparsing.Regex except it always uses unicode."""
    if options is None:
        options = re.U
    else:
        options |= re.U
    return Regex(regex, options)


any_char = regex_item(r".", re.DOTALL)


def fixto(item, output):
    """Force an item to result in a specific output."""
    return attach(item, replaceWith(output), ignore_tokens=True)


def addspace(item):
    """Condense and adds space to the tokenized output."""
    return attach(item, " ".join, ignore_no_tokens=True, ignore_one_token=True)


def condense(item):
    """Condense the tokenized output."""
    return attach(item, "".join, ignore_no_tokens=True, ignore_one_token=True)


def maybeparens(lparen, item, rparen, prefer_parens=False):
    """Wrap an item in optional parentheses, only applying them if necessary."""
    if prefer_parens:
        return lparen.suppress() + item + rparen.suppress() | item
    else:
        return item | lparen.suppress() + item + rparen.suppress()


def tokenlist(item, sep, suppress=True, allow_trailing=True, at_least_two=False):
    """Create a list of tokens matching the item."""
    if suppress:
        sep = sep.suppress()
    out = item + (OneOrMore if at_least_two else ZeroOrMore)(sep + item)
    if allow_trailing:
        out += Optional(sep)
    return out


def interleaved_tokenlist(required_item, other_item, sep, allow_trailing=False, at_least_two=False):
    """Create a grammar to match interleaved required_items and other_items,
    where required_item must show up at least once."""
    sep = sep.suppress()
    if at_least_two:
        out = (
            # required sep other (sep other)*
            Group(required_item)
            + Group(OneOrMore(sep + other_item))
            # other (sep other)* sep required (sep required)*
            | Group(other_item + ZeroOrMore(sep + other_item))
            + Group(OneOrMore(sep + required_item))
            # required sep required (sep required)*
            | Group(required_item + OneOrMore(sep + required_item))
        )
    else:
        out = (
            Optional(Group(OneOrMore(other_item + sep)))
            + Group(required_item + ZeroOrMore(sep + required_item))
            + Optional(Group(OneOrMore(sep + other_item)))
        )
    out += ZeroOrMore(
        Group(OneOrMore(sep + required_item))
        | Group(OneOrMore(sep + other_item)),
    )
    if allow_trailing:
        out += Optional(sep)
    return out


def add_list_spacing(tokens):
    """Parse action to add spacing after seps but not elsewhere."""
    out = []
    for i, tok in enumerate(tokens):
        out.append(tok)
        if i % 2 == 1 and i < len(tokens) - 1:
            out.append(" ")
    return "".join(out)


add_list_spacing.ignore_zero_tokens = True
add_list_spacing.ignore_one_token = True


def itemlist(item, sep, suppress_trailing=True):
    """Create a list of items separated by seps with comma-like spacing added.
    A trailing sep is allowed."""
    return attach(
        item
        + ZeroOrMore(sep + item)
        + Optional(sep.suppress() if suppress_trailing else sep),
        add_list_spacing,
    )


def exprlist(expr, op):
    """Create a list of exprs separated by ops with plus-like spacing added.
    No trailing op is allowed."""
    return addspace(expr + ZeroOrMore(op + expr))


def stores_loc_action(loc, tokens):
    """Action that just parses to loc."""
    internal_assert(len(tokens) == 0, "invalid store loc tokens", tokens)
    return str(loc)


stores_loc_action.ignore_tokens = True


stores_loc_item = attach(Empty(), stores_loc_action)


def disallow_keywords(kwds, with_suffix=None):
    """Prevent the given kwds from matching."""
    item = ~(
        keyword(kwds[0], explicit_prefix=False)
        if with_suffix is None else
        keyword(kwds[0], explicit_prefix=False) + with_suffix
    )
    for k in kwds[1:]:
        item += ~(
            keyword(k, explicit_prefix=False)
            if with_suffix is None else
            keyword(k, explicit_prefix=False) + with_suffix
        )
    return item


def any_keyword_in(kwds):
    """Match any of the given keywords."""
    return regex_item(r"|".join(k + r"\b" for k in kwds))


def keyword(name, explicit_prefix=None):
    """Construct a grammar which matches name as a Python keyword."""
    if explicit_prefix is not False:
        internal_assert(
            (name in reserved_vars) is (explicit_prefix is not None),
            "invalid keyword call for", name,
            extra="pass explicit_prefix to keyword for all reserved_vars and only reserved_vars",
        )

    base_kwd = regex_item(name + r"\b")
    if explicit_prefix in (None, False):
        return base_kwd
    else:
        return Optional(explicit_prefix.suppress()) + base_kwd


# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------

def multi_index_lookup(iterable, item, indexable_types, default=None):
    """Nested lookup of item in iterable."""
    for i, inner_iterable in enumerate(iterable):
        if inner_iterable == item:
            return (i,)
        if isinstance(inner_iterable, indexable_types):
            inner_indices = multi_index_lookup(inner_iterable, item, indexable_types)
            if inner_indices is not None:
                return (i,) + inner_indices
    return default


def append_it(iterator, last_val):
    """Iterate through iterator then yield last_val."""
    for x in iterator:
        yield x
    yield last_val


def join_args(*arglists):
    """Join split argument tokens."""
    return ", ".join(arg for args in arglists for arg in args if arg)


def paren_join(items, sep):
    """Join items by sep with parens around individual items but not the whole."""
    return items[0] if len(items) == 1 else "(" + (") " + sep + " (").join(items) + ")"


def addskip(skips, skip):
    """Add a line skip to the skips."""
    if skip < 1:
        complain(CoconutInternalException("invalid skip of line " + str(skip)))
    else:
        skips.append(skip)
    return skips


def count_end(teststr, testchar):
    """Count instances of testchar at end of teststr."""
    count = 0
    x = len(teststr) - 1
    while x >= 0 and teststr[x] == testchar:
        count += 1
        x -= 1
    return count


def paren_change(inputstring, opens=opens, closes=closes):
    """Determine the parenthetical change of level (num closes - num opens)."""
    count = 0
    for c in inputstring:
        if c in opens:  # open parens/brackets/braces
            count -= 1
        elif c in closes:  # close parens/brackets/braces
            count += 1
    return count


def ind_change(inputstring):
    """Determine the change in indentation level (num opens - num closes)."""
    return inputstring.count(openindent) - inputstring.count(closeindent)


def tuple_str_of(items, add_quotes=False, add_parens=True):
    """Make a tuple repr of the given items."""
    item_tuple = tuple(items)
    if add_quotes:
        # calling repr on each item ensures we strip unwanted u prefixes on Python 2
        out = ", ".join(repr(x) for x in item_tuple)
    else:
        out = ", ".join(item_tuple)
    out += ("," if len(item_tuple) == 1 else "")
    if add_parens:
        out = "(" + out + ")"
    return out


def rem_comment(line):
    """Remove a comment from a line."""
    return line.split("#", 1)[0].rstrip()


def should_indent(code):
    """Determines whether the next line should be indented."""
    last_line = rem_comment(code.splitlines()[-1])
    return last_line.endswith((":", "=", "\\")) or paren_change(last_line) < 0


def split_comment(line):
    """Split line into base and comment."""
    base = rem_comment(line)
    return base, line[len(base):]


def split_leading_comment(inputstring):
    """Split into leading comment and rest."""
    if inputstring.startswith("#"):
        comment, rest = inputstring.split("\n", 1)
        return comment + "\n", rest
    else:
        return "", inputstring


def split_leading_indent(line, max_indents=None):
    """Split line into leading indent and main."""
    indent = ""
    while (
        (max_indents is None or max_indents > 0)
        and line.startswith(indchars)
    ) or line.lstrip() != line:
        if max_indents is not None and line.startswith(indchars):
            max_indents -= 1
        indent += line[0]
        line = line[1:]
    return indent, line


def split_trailing_indent(line, max_indents=None):
    """Split line into leading indent and main."""
    indent = ""
    while (
        (max_indents is None or max_indents > 0)
        and line.endswith(indchars)
    ) or line.rstrip() != line:
        if max_indents is not None and line.endswith(indchars):
            max_indents -= 1
        indent = line[-1] + indent
        line = line[:-1]
    return line, indent


def split_leading_trailing_indent(line, max_indents=None):
    """Split leading and trailing indent."""
    leading_indent, line = split_leading_indent(line, max_indents)
    line, trailing_indent = split_trailing_indent(line, max_indents)
    return leading_indent, line, trailing_indent


def collapse_indents(indentation):
    """Removes all openindent-closeindent pairs."""
    change_in_level = ind_change(indentation)
    if change_in_level == 0:
        indents = ""
    elif change_in_level < 0:
        indents = closeindent * (-change_in_level)
    else:
        indents = openindent * change_in_level
    return indentation.replace(openindent, "").replace(closeindent, "") + indents


def final_indentation_level(code):
    """Determine the final indentation level of the given code."""
    level = 0
    for line in code.splitlines():
        leading_indent, _, trailing_indent = split_leading_trailing_indent(line)
        level += ind_change(leading_indent) + ind_change(trailing_indent)
    return level


def interleaved_join(first_list, second_list):
    """Interleaves two lists of strings and joins the result.

    Example: interleaved_join(['1', '3'], ['2']) == '123'
    The first list must be 1 longer than the second list.
    """
    internal_assert(len(first_list) == len(second_list) + 1, "invalid list lengths to interleaved_join", (first_list, second_list))
    interleaved = []
    for first_second in zip(first_list, second_list):
        interleaved.extend(first_second)
    interleaved.append(first_list[-1])
    return "".join(interleaved)


def handle_indentation(inputstr, add_newline=False):
    """Replace tabideal indentation with openindent and closeindent.
    Ignores whitespace-only lines."""
    out_lines = []
    prev_ind = None
    for line in inputstr.splitlines():
        line = line.rstrip()
        if line:
            new_ind_str, _ = split_leading_indent(line)
            internal_assert(new_ind_str.strip(" ") == "", "invalid indentation characters for handle_indentation", new_ind_str)
            internal_assert(len(new_ind_str) % tabideal == 0, "invalid indentation level for handle_indentation", len(new_ind_str))
            new_ind = len(new_ind_str) // tabideal
            if prev_ind is None:  # first line
                indent = ""
            elif new_ind > prev_ind:  # indent
                indent = openindent * (new_ind - prev_ind)
            elif new_ind < prev_ind:  # dedent
                indent = closeindent * (prev_ind - new_ind)
            else:
                indent = ""
            out_lines.append(indent + line)
            prev_ind = new_ind
    if add_newline:
        out_lines.append("")
    if prev_ind > 0:
        out_lines[-1] += closeindent * prev_ind
    out = "\n".join(out_lines)
    internal_assert(lambda: out.count(openindent) == out.count(closeindent), "failed to properly handle indentation in", out)
    return out


def get_func_closure(func):
    """Get variables in func's closure."""
    if PY2:
        varnames = func.func_code.co_freevars
        cells = func.func_closure
    else:
        varnames = func.__code__.co_freevars
        cells = func.__closure__
    return {v: c.cell_contents for v, c in zip(varnames, cells)}


def get_highest_parse_loc():
    """Get the highest observed parse location."""
    try:
        # extract the actual cache object (pyparsing does not make this easy)
        packrat_cache = ParserElement.packrat_cache
        if isinstance(packrat_cache, dict):  # if enablePackrat is never called
            cache = packrat_cache
        elif hasattr(packrat_cache, "cache"):  # cPyparsing adds this
            cache = packrat_cache.cache
        else:  # on pyparsing we have to do this
            cache = get_func_closure(packrat_cache.get.__func__)["cache"]

        # find the highest observed parse location
        highest_loc = 0
        for item in cache:
            loc = item[2]
            if loc > highest_loc:
                highest_loc = loc
        return highest_loc

    # everything here is sketchy, so errors should only be complained
    except Exception as err:
        complain(err)
        return 0


def literal_eval(py_code):
    """Version of ast.literal_eval that attempts to be version-independent."""
    try:
        compiled = compile(
            py_code,
            "<string>",
            "eval",
            (
                ast.PyCF_ONLY_AST
                | __future__.unicode_literals.compiler_flag
                | __future__.division.compiler_flag
            ),
        )
        return ast.literal_eval(compiled)
    except BaseException:
        raise CoconutInternalException("failed to literal eval", py_code)


def should_trim_arity(func):
    """Determine if we need to call _trim_arity on func."""
    try:
        func_args = inspect.getargspec(func)[0]
    except TypeError:
        return True
    if func_args[:3] == ["original", "loc", "tokens"]:
        return False
    if func_args[:4] == ["self", "original", "loc", "tokens"]:
        return False
    return True
