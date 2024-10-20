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
#   - Parsing Introspection
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
import itertools
import weakref
import datetime as dt
from functools import partial, reduce
from collections import defaultdict
from contextlib import contextmanager
from pprint import pformat, pprint
from weakref import ref as wkref

from coconut._pyparsing import (
    CPYPARSING,
    MODERN_PYPARSING,
    USE_COMPUTATION_GRAPH,
    SUPPORTS_INCREMENTAL,
    SUPPORTS_ADAPTIVE,
    SUPPORTS_PACKRAT_CONTEXT,
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
    CaselessLiteral,
    Group,
    ParserElement,
    MatchFirst,
    And,
    StringStart,
    _trim_arity,
    _ParseResultsWithOffset,
    line as _line,
    all_parse_elements,
)

from coconut.integrations import embed
from coconut.util import (
    pickle,
    override,
    get_name,
    get_target_info,
    memoize,
    get_clock_time,
    literal_lines,
    const,
    pickleable_obj,
)
from coconut.terminal import (
    logger,
    complain,
    internal_assert,
    trace,
)
from coconut.constants import (
    CPYTHON,
    open_chars,
    close_chars,
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
    packrat_cache_size,
    temp_grammar_item_ref_count,
    indchars,
    comment_chars,
    non_syntactic_newline,
    allow_explicit_keyword_vars,
    reserved_prefix,
    incremental_mode_cache_size,
    default_incremental_cache_size,
    repeatedly_clear_incremental_cache,
    py_vers_with_eols,
    unwrapper,
    incremental_cache_limit,
    incremental_mode_cache_successes,
    use_adaptive_any_of,
    use_fast_pyparsing_reprs,
    require_cache_clear_frac,
    reverse_any_of,
    all_keywords,
    always_keep_parse_name_prefix,
    keep_if_unchanged_parse_name_prefix,
    incremental_use_hybrid,
    test_computation_graph_pickling,
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


def evaluate_all_tokens(all_tokens, expand_inner=True, **kwargs):
    """Recursively evaluate all the tokens in all_tokens."""
    all_evaluated_toks = []
    for toks in all_tokens:
        evaluated_toks = evaluate_tokens(toks, **kwargs)
        # if we're a final parse, ExceptionNodes will just be raised, but otherwise, if we see any, we need to
        #  short-circuit the computation and return them, since they imply this parse contains invalid syntax
        if isinstance(evaluated_toks, ExceptionNode):
            return None, evaluated_toks
        elif expand_inner and isinstance(evaluated_toks, MergeNode):
            all_evaluated_toks = ParseResults(all_evaluated_toks)
            all_evaluated_toks += evaluated_toks  # use += to avoid an unnecessary copy
        else:
            all_evaluated_toks.append(evaluated_toks)
    return all_evaluated_toks, None


def make_modified_tokens(old_tokens, new_toklist=None, new_tokdict=None, cls=ParseResults):
    """Construct a modified ParseResults object from the given ParseResults object."""
    if new_toklist is None:
        if DEVELOP:  # avoid the overhead of the call if not develop
            internal_assert(new_tokdict is None, "if new_toklist is None, new_tokdict must be None", new_tokdict)
        new_toklist = old_tokens._ParseResults__toklist
        new_tokdict = old_tokens._ParseResults__tokdict
    # we have to pass name=None here and then set __name after otherwise
    #  the constructor might generate a new tokdict item we don't want;
    #  this also ensures that asList and modal don't matter, since they
    #  only do anything when you name is not None, so we don't pass them
    new_tokens = cls(new_toklist)
    new_tokens._ParseResults__name = old_tokens._ParseResults__name
    new_tokens._ParseResults__parent = old_tokens._ParseResults__parent
    new_tokens._ParseResults__accumNames.update(old_tokens._ParseResults__accumNames)
    if new_tokdict is not None:
        new_tokens._ParseResults__tokdict.update(new_tokdict)
    return new_tokens


def evaluate_tokens(tokens, **kwargs):
    """Evaluate the given tokens in the computation graph.
    Very performance sensitive."""
    # can't have these be normal kwargs to make evaluate_tokens a valid parse action
    is_final = kwargs.pop("is_final", False)
    evaluated_toklists = kwargs.pop("evaluated_toklists", ())
    if DEVELOP:  # avoid the overhead of the call if not develop
        internal_assert(not kwargs, "invalid keyword arguments to evaluate_tokens", kwargs)

    if not USE_COMPUTATION_GRAPH:
        return tokens
    final_evaluate_tokens.enabled = True  # special variable used by cached_parse

    if isinstance(tokens, ParseResults):

        # evaluate the list portion of the ParseResults
        old_toklist = tokens._ParseResults__toklist
        new_toklist = None
        for eval_old_toklist, eval_new_toklist in evaluated_toklists:
            if old_toklist == eval_old_toklist:
                new_toklist = eval_new_toklist
                break
        if new_toklist is None:
            new_toklist, exc_node = evaluate_all_tokens(old_toklist, is_final=is_final, evaluated_toklists=evaluated_toklists)
            if exc_node is not None:
                return exc_node
            # overwrite evaluated toklists rather than appending, since this
            #  should be all the information we need for evaluating the dictionary
            evaluated_toklists = ((old_toklist, new_toklist),)

        # evaluate the dictionary portion of the ParseResults
        new_tokdict = {}
        for name, occurrences in tokens._ParseResults__tokdict.items():
            new_occurrences = []
            for value, position in occurrences:
                if value is None:  # fake value created by build_new_toks_for
                    new_value = None
                else:
                    new_value = evaluate_tokens(value, is_final=is_final, evaluated_toklists=evaluated_toklists)
                    if isinstance(new_value, ExceptionNode):
                        return new_value
                new_occurrences.append(_ParseResultsWithOffset(new_value, position))
            new_tokdict[name] = new_occurrences

        new_tokens = make_modified_tokens(tokens, new_toklist, new_tokdict)

        if DEVELOP:  # avoid the overhead of the call if not develop
            internal_assert(set(tokens._ParseResults__tokdict.keys()) <= set(new_tokens._ParseResults__tokdict.keys()), "evaluate_tokens on ParseResults failed to maintain tokdict keys", (tokens, "->", new_tokens))

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

        # base cases (performance sensitive; should be in likelihood order):
        if isinstance(tokens, (str, bool)) or tokens is None:
            return tokens

        elif isinstance(tokens, ComputationNode):
            result = tokens.evaluate()
            if is_final and isinstance(result, ExceptionNode):
                result.evaluate()
            elif isinstance(result, ParseResults):
                return make_modified_tokens(result, cls=MergeNode)
            elif isinstance(result, list):
                if len(result) == 1:
                    return result[0]
                else:
                    return MergeNode(result)
            else:
                return result

        elif isinstance(tokens, list):
            result, exc_node = evaluate_all_tokens(tokens, is_final=is_final, evaluated_toklists=evaluated_toklists)
            return result if exc_node is None else exc_node

        elif isinstance(tokens, tuple):
            result, exc_node = evaluate_all_tokens(tokens, expand_inner=False, is_final=is_final, evaluated_toklists=evaluated_toklists)
            return tuple(result) if exc_node is None else exc_node

        elif isinstance(tokens, ExceptionNode):
            if is_final:
                tokens.evaluate()
            return tokens

        elif isinstance(tokens, DeferredNode):
            return tokens

        else:
            raise CoconutInternalException("invalid computation graph tokens", tokens)


class MergeNode(ParseResults):
    """A special type of ParseResults object that should be merged into outer tokens."""
    __slots__ = ()


def build_new_toks_for(tokens, new_toklist, unchanged=False):
    """Build new tokens from tokens to return just new_toklist."""
    if USE_COMPUTATION_GRAPH and not isinstance(new_toklist, ExceptionNode):
        keep_names = [
            n for n in tokens._ParseResults__tokdict
            if n.startswith(always_keep_parse_name_prefix) or unchanged and n.startswith(keep_if_unchanged_parse_name_prefix)
        ]
        if tokens._ParseResults__name is not None and (
            tokens._ParseResults__name.startswith(always_keep_parse_name_prefix)
            or unchanged and tokens._ParseResults__name.startswith(keep_if_unchanged_parse_name_prefix)
        ):
            keep_names.append(tokens._ParseResults__name)
        if keep_names:
            new_tokens = make_modified_tokens(tokens, new_toklist)
            for name in keep_names:
                new_tokens[name] = None
            return new_tokens
    return new_toklist


cached_trim_arity = memoize()(_trim_arity)


class ComputationNode(pickleable_obj):
    """A single node in the computation graph."""
    __slots__ = ("action", "original", "loc", "tokens", "trim_arity")
    pprinting = False
    override_original = None
    add_to_loc = 0

    @classmethod
    @contextmanager
    def using_overrides(cls):
        override_original, cls.override_original = cls.override_original, None
        add_to_loc, cls.add_to_loc = cls.add_to_loc, 0
        try:
            yield
        finally:
            cls.override_original = override_original
            cls.add_to_loc = add_to_loc

    def __new__(cls, action, original, loc, tokens, trim_arity=True, ignore_no_tokens=False, ignore_one_token=False, greedy=False):
        """Create a ComputionNode to return from a parse action.

        If ignore_no_tokens, then don't call the action if there are no tokens.
        If ignore_one_token, then don't call the action if there is only one token.
        If greedy, then never defer the action until later."""
        if test_computation_graph_pickling:
            with CombineToNode.enable_pickling():
                try:
                    pickle.dumps(action, protocol=pickle.HIGHEST_PROTOCOL)
                except Exception:
                    raise ValueError("unpickleable action in ComputationNode: " + repr(action))
        if ignore_no_tokens and len(tokens) == 0 or ignore_one_token and len(tokens) == 1:
            # could be a ComputationNode, so we can't have an __init__
            return build_new_toks_for(tokens, tokens, unchanged=True)
        else:
            self = super(ComputationNode, cls).__new__(cls)
            self.action = action
            self.original = original
            self.loc = loc
            self.tokens = tokens
            self.trim_arity = trim_arity
            if greedy:
                return self.evaluate()
            else:
                return self

    def __reduce__(self):
        """Get pickling information."""
        return (self.__class__, (self.action, self.original, self.loc, self.tokens, self.trim_arity))

    @property
    def name(self):
        """Get the name of the action."""
        name = getattr(self.action, "__name__", None)
        # repr(action) not defined for all actions, so must only be evaluated if getattr fails
        return name if name is not None else repr(self.action)

    def evaluate(self):
        """Get the result of evaluating the computation graph at this node.

        Very performance sensitive."""
        # note that this should never cache, since if a greedy Wrap that doesn't add to the packrat context
        #  hits the cache, it'll get the same ComputationNode object, but since it's greedy that object needs
        #  to actually be reevaluated
        if logger.tracing and not final_evaluate_tokens.enabled:
            logger.log_tag("cached_parse invalidated by", self)

        if self.trim_arity:
            using_action = cached_trim_arity(self.action)
        else:
            using_action = self.action
        using_original = self.original if self.override_original is None else self.override_original
        using_loc = self.loc + self.add_to_loc
        evaluated_toks = evaluate_tokens(self.tokens)

        if logger.tracing:  # avoid the overhead of the call if not tracing
            logger.log_trace(self.name, using_original, using_loc, evaluated_toks, self.tokens)
        if isinstance(evaluated_toks, ExceptionNode):
            return evaluated_toks  # short-circuit if we got an ExceptionNode
        try:
            result = using_action(
                using_original,
                using_loc,
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

        out = build_new_toks_for(evaluated_toks, result)
        if logger.tracing:  # avoid the overhead if not tracing
            dropped_keys = set(self.tokens._ParseResults__tokdict.keys())
            if isinstance(out, ParseResults):
                dropped_keys -= set(out._ParseResults__tokdict.keys())
            if dropped_keys:
                logger.log_tag(self.name, "DROP " + repr(dropped_keys), wrap=False)
        return out

    def __repr__(self):
        """Get a representation of the entire computation graph below this node."""
        if not logger.tracing:
            logger.warn_err(CoconutInternalException("ComputationNode.__repr__ called when not tracing"))
        inner_repr = "\n".join("\t" + line for line in repr(self.tokens).splitlines())
        if self.pprinting:
            return '("' + self.name + '",\n' + inner_repr + "\n)"
        else:
            return self.name + "(\n" + inner_repr + "\n)"


class DeferredNode(object):
    """A node in the computation graph that has had its evaluation explicitly deferred."""
    __slots__ = ("original", "loc", "tokens")

    def __init__(self, original, loc, tokens):
        self.original = original
        self.loc = loc
        self.tokens = tokens

    def evaluate(self):
        """Evaluate the deferred computation."""
        return unpack(self.tokens)


class ExceptionNode(object):
    """A node in the computation graph that stores an exception that will be raised upon final evaluation."""
    __slots__ = ("exception_maker",)

    def __init__(self, exception_maker):
        if not USE_COMPUTATION_GRAPH:
            raise exception_maker()
        self.exception_maker = exception_maker

    def evaluate(self):
        """Raise the stored exception."""
        raise self.exception_maker()


class CombineToNode(Combine, pickleable_obj):
    """Modified Combine to work with the computation graph."""
    __slots__ = ()
    validation_dict = None
    pickling_enabled = False

    def _combine(self, original, loc, tokens):
        """Implement the parse action for Combine."""
        combined_tokens = super(CombineToNode, self).postParse(original, loc, tokens)
        if DEVELOP:  # avoid the overhead of the call if not develop
            internal_assert(len(combined_tokens) == 1, "Combine produced multiple tokens", combined_tokens)
        return combined_tokens[0]

    @override
    def postParse(self, original, loc, tokens):
        """Create a ComputationNode for Combine."""
        return ComputationNode(self._combine, original, loc, tokens, ignore_no_tokens=True, ignore_one_token=True, trim_arity=False)

    def __reduce__(self):
        if self.pickling_enabled:
            return (identifier_to_parse_elem, (parse_elem_to_identifier(self, self.validation_dict),))
        else:
            return super(CombineToNode, self).__reduce__()

    @classmethod
    @contextmanager
    def enable_pickling(cls, validation_dict=None):
        """Context manager to enable pickling for CombineToNode."""
        old_validation_dict, cls.validation_dict = cls.validation_dict, validation_dict
        old_pickling_enabled, cls.pickling_enabled = cls.pickling_enabled, True
        try:
            yield
        finally:
            cls.pickling_enabled = old_pickling_enabled
            cls.validation_dict = old_validation_dict


if USE_COMPUTATION_GRAPH:
    combine = CombineToNode
else:
    combine = Combine


def add_action(item, action, make_copy=None):
    """Add a parse action to the given item."""
    if make_copy is None:
        item = maybe_copy_elem(item, "attach")
    elif make_copy:
        item = item.copy()
    return item.addParseAction(action)


def get_func_args(func):
    """Inspect a function to determine its argument names."""
    if PY2:
        return inspect.getargspec(func)[0]
    else:
        return inspect.getfullargspec(func)[0]


def should_trim_arity(func):
    """Determine if we need to call _trim_arity on func."""
    annotation = getattr(func, "trim_arity", None)
    if annotation is not None:
        return annotation
    try:
        func_args = get_func_args(func)
    except TypeError:
        return True
    if not func_args:
        return True
    if func_args[0] == "self":
        func_args.pop(0)
    if func_args[:3] == ["original", "loc", "tokens"]:
        return False
    return True


def attach(item, action, ignore_no_tokens=None, ignore_one_token=None, ignore_arguments=None, trim_arity=None, make_copy=None, **kwargs):
    """Set the parse action for the given item to create a node in the computation graph."""
    if ignore_arguments is None:
        ignore_arguments = getattr(action, "ignore_arguments", False)
    # if ignore_arguments, then we can just pass in the computation graph and have it be ignored
    if not ignore_arguments and USE_COMPUTATION_GRAPH:
        # use the action's annotations to generate the defaults
        if ignore_no_tokens is None:
            ignore_no_tokens = getattr(action, "ignore_no_tokens", False)
        if ignore_one_token is None:
            ignore_one_token = getattr(action, "ignore_one_token", False)
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
    return add_action(item, action, make_copy)


def final_evaluate_tokens(tokens):
    """Same as evaluate_tokens but should only be used once a parse is assured."""
    if not final_evaluate_tokens.enabled:  # handled by cached_parse
        return tokens
    result = evaluate_tokens(tokens, is_final=True)
    # clear packrat cache after evaluating tokens so error creation gets to see the cache
    clear_packrat_cache()
    return result


final_evaluate_tokens.enabled = True


def final(item):
    """Collapse the computation graph upon parsing the given item."""
    # evaluate_tokens expects a computation graph, so we just call add_action directly
    return add_action(trace(item), final_evaluate_tokens)


def defer(item):
    """Defers evaluation of the given item.
    Only does any actual deferring if USE_COMPUTATION_GRAPH is True."""
    return add_action(item, DeferredNode)


def unpack(tokens):
    """Evaluate and unpack the given computation graph."""
    logger.log_tag("unpack", tokens)
    tokens = final_evaluate_tokens(tokens)
    if isinstance(tokens, ParseResults) and len(tokens) == 1:
        tokens = tokens[0]
    return tokens


def in_incremental_mode():
    """Determine if we are using incremental parsing mode."""
    return ParserElement._incrementalEnabled and not ParserElement._incrementalWithResets


def force_reset_packrat_cache():
    """Forcibly reset the packrat cache and all packrat stats."""
    if ParserElement._incrementalEnabled:
        ParserElement._incrementalEnabled = False
        ParserElement.enableIncremental(
            incremental_mode_cache_size if in_incremental_mode() else default_incremental_cache_size,
            **ParserElement.getIncrementalInfo()  # no comma for py2
        )
    else:
        ParserElement._packratEnabled = False
        ParserElement.enablePackrat(packrat_cache_size)


@contextmanager
def parsing_context(inner_parse=None):
    """Context to manage the packrat cache across parse calls."""
    current_cache_matters = (
        inner_parse is not False
        and ParserElement._packratEnabled
    )
    new_cache_matters = (
        inner_parse is not True
        and ParserElement._incrementalEnabled
        and not ParserElement._incrementalWithResets
    )
    will_clear_cache = (
        not ParserElement._incrementalEnabled
        or ParserElement._incrementalWithResets
    )
    if (
        current_cache_matters
        and new_cache_matters
        and ParserElement._incrementalWithResets
    ):
        incrementalWithResets, ParserElement._incrementalWithResets = ParserElement._incrementalWithResets, False
        try:
            yield
        finally:
            ParserElement._incrementalWithResets = incrementalWithResets
            dehybridize_cache()
    elif (
        current_cache_matters
        and will_clear_cache
    ):
        # store old packrat cache
        old_cache = ParserElement.packrat_cache
        old_cache_stats = ParserElement.packrat_cache_stats[:]

        # give inner parser a new packrat cache
        force_reset_packrat_cache()
        try:
            yield
        finally:
            ParserElement.packrat_cache = old_cache
            if logger.verbose:
                ParserElement.packrat_cache_stats[0] += old_cache_stats[0]
                ParserElement.packrat_cache_stats[1] += old_cache_stats[1]
    elif not will_clear_cache:
        try:
            yield
        finally:
            dehybridize_cache()
    else:
        yield


class StartOfStrGrammar(object):
    """A container object that denotes grammars that should always be parsed at the start of the string."""
    __slots__ = ("grammar", "parse_element_index", "__weakref__")
    start_marker = StringStart()

    def __init__(self, grammar):
        self.grammar = grammar
        if all_parse_elements is not None:
            self.parse_element_index = len(all_parse_elements)
            all_parse_elements.append(wkref(self))

    def with_start_marker(self):
        """Get the grammar with the start marker."""
        internal_assert(not CPYPARSING, "StartOfStrGrammar.with_start_marker() should only be necessary without cPyparsing")
        return self.start_marker + self.grammar

    def apply(self, grammar_transformer):
        """Apply a function to transform the grammar."""
        self.grammar = grammar_transformer(self.grammar)

    @property
    def name(self):
        return get_name(self.grammar)

    def setName(self, *args, **kwargs):
        """Equivalent to .grammar.setName."""
        return self.grammar.setName(*args, **kwargs)


def prep_grammar(grammar, for_scan, streamline=False, add_unpack=False):
    """Prepare a grammar item to be used as the root of a parse."""
    if isinstance(grammar, StartOfStrGrammar):
        if for_scan:
            grammar = grammar.with_start_marker()
        else:
            grammar = grammar.grammar
    if add_unpack:
        grammar = add_action(grammar, unpack)
    grammar = trace(grammar)
    if streamline:
        grammar.streamlined = False
        grammar.streamline()
    else:
        grammar.streamlined = True
    return grammar.parseWithTabs()


def parse(grammar, text, inner=None, eval_parse_tree=True, **kwargs):
    """Parse text using grammar."""
    with parsing_context(inner):
        result = prep_grammar(grammar, for_scan=False).parseString(text, **kwargs)
        if eval_parse_tree:
            result = unpack(result)
        return result


def all_matches(grammar, text, inner=None, eval_parse_tree=True):
    """Find all matches for grammar in text."""
    kwargs = {}
    if CPYPARSING and isinstance(grammar, StartOfStrGrammar):
        grammar = grammar.grammar
        kwargs["maxStartLoc"] = 0
    with parsing_context(inner):
        for tokens, start, stop in prep_grammar(grammar, for_scan=True).scanString(text, **kwargs):
            if eval_parse_tree:
                tokens = unpack(tokens)
            yield tokens, start, stop


def cached_parse(
    computation_graph_cache,
    grammar,
    text,
    inner=None,
    eval_parse_tree=True,
    scan_string=False,
    include_tokens=True,
    cache_prefixes=False,
):
    """Version of parse that caches the result when it's a pure ComputationNode."""
    if not include_tokens:
        eval_parse_tree = False
    if not CPYPARSING:  # caching is only supported on cPyparsing
        if scan_string:
            for tokens, start, stop in all_matches(grammar, text, inner, eval_parse_tree):
                return tokens, start, stop
            return None, None, None
        else:
            return parse(grammar, text, inner)

    # only iterate over keys, not items, so we don't mark everything as alive
    for key in computation_graph_cache:
        prefix, is_at_end = key
        if DEVELOP:  # avoid overhead
            internal_assert(cache_prefixes or is_at_end, "invalid computation graph cache item", key)
        # the assumption here is that if the prior parse didn't make it to the end,
        #  then we can freely change the text after the end of where it made it,
        #  but if it did make it to the end, then we can't add more text after that
        if (
            is_at_end and text == prefix
            or not is_at_end and text.startswith(prefix)
        ):
            if scan_string:
                tokens, start, stop = computation_graph_cache[key]
            else:
                tokens = computation_graph_cache[key]
            if DEVELOP:
                logger.record_stat("cached_parse", True)
                logger.log_tag("cached_parse hit", (prefix, text[len(prefix):], tokens))
            break
    else:  # no break
        # disable token evaluation by final() to allow us to get a ComputationNode;
        #  this makes long parses very slow, however, so once a greedy parse action
        #  is hit such that evaluate_tokens gets called, evaluate_tokens will set
        #  final_evaluate_tokens.enabled back to True, which speeds up the rest of the
        #  parse and tells us that something greedy happened so we can't cache
        final_evaluate_tokens.enabled = False
        try:
            if scan_string:
                for tokens, start, stop in all_matches(grammar, text, inner, eval_parse_tree=False):
                    break
                else:  # no break
                    tokens = start = stop = None
            else:
                stop, tokens = parse(grammar, text, inner, eval_parse_tree=False, returnLoc=True)
            if not include_tokens:
                tokens = bool(tokens)
            if not final_evaluate_tokens.enabled:
                is_at_end = True if stop is None else stop >= len(text)
                if cache_prefixes or is_at_end:
                    prefix = text if stop is None else text[:stop + 1]
                    if scan_string:
                        computation_graph_cache[(prefix, is_at_end)] = tokens, start, stop
                    else:
                        computation_graph_cache[(prefix, is_at_end)] = tokens
        finally:
            if DEVELOP:
                logger.record_stat("cached_parse", False)
                logger.log_tag(
                    "cached_parse miss " + ("-> stored" if not final_evaluate_tokens.enabled else "(not stored)"),
                    text,
                    multiline=True,
                )
            final_evaluate_tokens.enabled = True

    if include_tokens and eval_parse_tree:
        tokens = unpack(tokens)
    if scan_string:
        return tokens, start, stop
    else:
        return tokens


def try_parse(grammar, text, inner=None, eval_parse_tree=True):
    """Attempt to parse text using grammar else None."""
    try:
        return parse(grammar, text, inner, eval_parse_tree)
    except ParseBaseException:
        return None


def cached_try_parse(cache, grammar, text, inner=None, eval_parse_tree=True, **kwargs):
    """Cached version of try_parse."""
    if not CPYPARSING:  # scan_string on StartOfStrGrammar is only fast on cPyparsing
        return try_parse(grammar, text, inner, eval_parse_tree)
    if not isinstance(grammar, StartOfStrGrammar):
        grammar = StartOfStrGrammar(grammar)
    tokens, start, stop = cached_parse(cache, grammar, text, inner, eval_parse_tree, scan_string=True, **kwargs)
    return tokens


def does_parse(grammar, text, inner=None):
    """Determine if text can be parsed using grammar."""
    return try_parse(grammar, text, inner, eval_parse_tree=False)


def cached_does_parse(cache, grammar, text, inner=None, **kwargs):
    """Cached version of does_parse."""
    return cached_try_parse(cache, grammar, text, inner, include_tokens=False, **kwargs)


def parse_where(grammar, text, inner=None):
    """Determine where the first parse is."""
    for tokens, start, stop in all_matches(grammar, text, inner, eval_parse_tree=False):
        return start, stop
    return None, None


def cached_parse_where(cache, grammar, text, inner=None, **kwargs):
    """Cached version of parse_where."""
    tokens, start, stop = cached_parse(cache, grammar, text, inner, scan_string=True, include_tokens=False, **kwargs)
    return start, stop


def match_in(grammar, text, inner=None):
    """Determine if there is a match for grammar anywhere in text."""
    start, stop = parse_where(grammar, text, inner)
    internal_assert((start is None) == (stop is None), "invalid parse_where results", (start, stop))
    return start is not None


def cached_match_in(cache, grammar, text, inner=None, **kwargs):
    """Cached version of match_in."""
    start, stop = cached_parse_where(cache, grammar, text, inner, **kwargs)
    internal_assert((start is None) == (stop is None), "invalid cached_parse_where results", (start, stop))
    return start is not None


def transform(grammar, text, inner=None):
    """Transform text by replacing matches to grammar."""
    kwargs = {}
    if CPYPARSING and isinstance(grammar, StartOfStrGrammar):
        grammar = grammar.grammar
        kwargs["maxStartLoc"] = 0
    with parsing_context(inner):
        result = prep_grammar(grammar, add_unpack=True, for_scan=True).transformString(text, **kwargs)
        if result == text:
            result = None
        return result


# -----------------------------------------------------------------------------------------------------------------------
# TARGETS:
# -----------------------------------------------------------------------------------------------------------------------

on_new_python = False

raw_sys_target = str(sys.version_info[0]) + str(sys.version_info[1])
if raw_sys_target in pseudo_targets:
    sys_target = pseudo_targets[raw_sys_target]
elif raw_sys_target in specific_targets:
    sys_target = raw_sys_target
elif sys.version_info > supported_py3_vers[-1]:
    sys_target = "".join(str(i) for i in supported_py3_vers[-1])
    on_new_python = True
elif sys.version_info < supported_py2_vers[0]:
    sys_target = "".join(str(i) for i in supported_py2_vers[0])
elif sys.version_info < (3,):
    sys_target = "".join(str(i) for i in supported_py2_vers[-1])
else:
    sys_target = "".join(str(i) for i in supported_py3_vers[0])


def get_psf_target():
    """Get the oldest PSF-supported Python version target."""
    now = dt.datetime.now()
    for ver, eol in py_vers_with_eols:
        if now < eol:
            break
    return pseudo_targets.get(ver, ver)


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
    """
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
    else:
        raise CoconutInternalException("unknown get_target_info_smart mode", mode)


# -----------------------------------------------------------------------------------------------------------------------
# PARSING INTROSPECTION:
# -----------------------------------------------------------------------------------------------------------------------

# incremental lookup indices
_lookup_elem = 0
_lookup_orig = 1
_lookup_loc = 2
# _lookup_bools = 3
# _lookup_context = 4
assert _lookup_elem == 0, "lookup must start with elem"

# incremental value indices
_value_exc_loc_or_ret = 0
# _value_furthest_loc = 1
_value_useful = -1
assert _value_exc_loc_or_ret == 0, "value must start with exc loc / ret"
assert _value_useful == -1, "value must end with usefullness obj"


def maybe_copy_elem(item, name):
    """Copy the given grammar element if it's referenced somewhere else."""
    item_ref_count = sys.getrefcount(item) if CPYTHON and not on_new_python else float("inf")
    internal_assert(lambda: item_ref_count >= temp_grammar_item_ref_count, "add_action got item with too low ref count", (item, type(item), item_ref_count))
    if item_ref_count <= temp_grammar_item_ref_count:
        if DEVELOP:
            logger.record_stat("maybe_copy_" + name, False)
        return item
    else:
        if DEVELOP:
            logger.record_stat("maybe_copy_" + name, True)
        return item.copy()


def hasaction(elem):
    """Determine if the given grammar element has any actions associated with it."""
    return (
        MODERN_PYPARSING
        or elem.parseAction
        or elem.resultsName is not None
        or elem.debug
    )


@contextmanager
def using_fast_grammar_methods():
    """Enables grammar methods that modify their operands when they aren't referenced elsewhere."""
    if MODERN_PYPARSING:
        yield
        return

    def fast_add(self, other):
        if hasaction(self):
            return old_add(self, other)
        self = maybe_copy_elem(self, "add")
        self += other
        return self
    old_add, And.__add__ = And.__add__, fast_add

    def fast_or(self, other):
        if hasaction(self):
            return old_or(self, other)
        self = maybe_copy_elem(self, "or")
        self |= other
        return self
    old_or, MatchFirst.__or__ = MatchFirst.__or__, fast_or

    try:
        yield
    finally:
        And.__add__ = old_add
        MatchFirst.__or__ = old_or


def get_func_closure(func):
    """Get variables in func's closure."""
    if PY2:
        varnames = func.func_code.co_freevars
        cells = func.func_closure
    else:
        varnames = func.__code__.co_freevars
        cells = func.__closure__
    return {v: c.cell_contents for v, c in zip(varnames, cells)}


def get_pyparsing_cache():
    """Extract the underlying pyparsing packrat cache."""
    packrat_cache = ParserElement.packrat_cache
    if isinstance(packrat_cache, dict):  # if enablePackrat is never called
        return packrat_cache
    elif CPYPARSING:
        return packrat_cache.cache  # cPyparsing adds this
    else:  # on pyparsing we have to do this
        try:
            # this is sketchy, so errors should only be complained
            #  use .set instead of .get for the sake of MODERN_PYPARSING
            return get_func_closure(packrat_cache.set.__func__)["cache"]
        except Exception as err:
            complain(err)
            return {}


def should_clear_cache(force=False):
    """Determine if we should be clearing the packrat cache."""
    if force:
        return True
    elif not ParserElement._packratEnabled:
        return False
    elif ParserElement._incrementalEnabled:
        if not in_incremental_mode():
            return repeatedly_clear_incremental_cache
        if (
            incremental_cache_limit is not None
            and len(ParserElement.packrat_cache) > incremental_cache_limit
        ):
            return "smart"
        return False
    else:
        return True


def add_packrat_cache_items(new_items, clear_first=False):
    """Add the given items to the packrat cache."""
    if clear_first:
        ParserElement.packrat_cache.clear()
    if new_items:
        if PY2 or not CPYPARSING:
            for lookup, value in new_items:
                ParserElement.packrat_cache.set(lookup, value)
        else:
            ParserElement.packrat_cache.update(new_items)


def execute_clear_strat(clear_cache):
    """Clear PyParsing cache using clear_cache."""
    orig_cache_len = None
    if clear_cache is True:
        # clear cache without resetting stats
        ParserElement.packrat_cache.clear()
    elif clear_cache == "smart":
        orig_cache_len = execute_clear_strat("useless")
        cleared_frac = (orig_cache_len - len(get_pyparsing_cache())) / orig_cache_len
        if cleared_frac < require_cache_clear_frac:
            logger.log("Packrat cache pruning using 'useless' strat failed; falling back to 'second half' strat.")
            execute_clear_strat("second half")
    else:
        internal_assert(CPYPARSING, "unsupported clear_cache strategy", clear_cache)
        cache = get_pyparsing_cache()
        orig_cache_len = len(cache)
        if clear_cache == "useless":
            keys_to_del = []
            for lookup, value in cache.items():
                if not value[_value_useful][0]:
                    keys_to_del.append(lookup)
            for del_key in keys_to_del:
                del cache[del_key]
        elif clear_cache == "second half":
            all_keys = tuple(cache.keys())
            for del_key in all_keys[len(all_keys) // 2: len(all_keys)]:
                del cache[del_key]
        else:
            raise CoconutInternalException("invalid clear_cache strategy", clear_cache)
    return orig_cache_len


def dehybridize_cache():
    """Dehybridize any hybrid entries in the incremental parsing cache."""
    if (
        CPYPARSING
        # if we're not in incremental mode, we just throw away the cache
        #  after every parse, so no need to dehybridize it
        and in_incremental_mode()
        and ParserElement.getIncrementalInfo()["hybrid_mode"]
    ):
        cache = get_pyparsing_cache()
        new_entries = {}
        for lookup, value in cache.items():
            cached_item = value[0]
            if cached_item is not True and not isinstance(cached_item, int):
                new_entries[lookup] = (True,) + value[1:]
        cache.update(new_entries)


def clear_packrat_cache(force=False):
    """Clear the packrat cache if applicable.
    Very performance-sensitive for incremental parsing mode."""
    clear_cache = should_clear_cache(force=force)
    if clear_cache:
        if DEVELOP:
            start_time = get_clock_time()
        orig_cache_len = execute_clear_strat(clear_cache)
        # always dehybridize after cache clear so we're dehybridizing the fewest items
        dehybridize_cache()
        if DEVELOP and orig_cache_len is not None:
            logger.log("Pruned packrat cache from {orig_len} items to {new_len} items using {strat!r} strategy ({time} secs).".format(
                orig_len=orig_cache_len,
                new_len=len(get_pyparsing_cache()),
                strat=clear_cache,
                time=get_clock_time() - start_time,
            ))
    return clear_cache


def get_cache_items_for(original, only_useful=False, exclude_stale=True):
    """Get items from the pyparsing cache filtered to only be from parsing original."""
    cache = get_pyparsing_cache()
    for lookup, value in cache.items():
        got_orig = lookup[_lookup_orig]
        internal_assert(lambda: isinstance(got_orig, (bytes, str)), "failed to look up original in pyparsing cache item", (lookup, value))
        if ParserElement._incrementalEnabled:
            (is_useful,) = value[_value_useful]
            if only_useful and not is_useful:
                continue
            if exclude_stale and is_useful >= 2:
                continue
        if got_orig == original:
            yield lookup, value


def get_highest_parse_loc(original):
    """Get the highest observed parse location.
    Note that there's no point in filtering for successes/failures, since we always see both at the same locations."""
    highest_loc = 0
    for lookup, _ in get_cache_items_for(original):
        loc = lookup[_lookup_loc]
        if loc > highest_loc:
            highest_loc = loc
    return highest_loc


def enable_incremental_parsing(reason="explicit enable_incremental_parsing call"):
    """Enable incremental parsing mode where prefix/suffix parses are reused."""
    if not SUPPORTS_INCREMENTAL:
        return False
    if in_incremental_mode():  # incremental mode is already enabled
        return True
    ParserElement._incrementalEnabled = False
    try:
        ParserElement.enableIncremental(
            incremental_mode_cache_size,
            still_reset_cache=False,
            cache_successes=incremental_mode_cache_successes,
            hybrid_mode=incremental_mode_cache_successes and incremental_use_hybrid,
        )
    except ImportError as err:
        raise CoconutException(str(err))
    logger.log("Incremental parsing mode enabled due to {reason}.".format(reason=reason))
    return True


def disable_incremental_parsing():
    """Properly disable incremental parsing mode."""
    if in_incremental_mode():
        ParserElement._incrementalEnabled = False
        ParserElement._incrementalWithResets = False
        force_reset_packrat_cache()


def parse_elem_to_identifier(elem, validation_dict=None):
    """Get the identifier for the given parse element."""
    identifier = elem.parse_element_index
    internal_assert(lambda: elem == all_parse_elements[identifier](), "failed to look up parse element by identifier", lambda: (elem, all_parse_elements[identifier]()))
    if validation_dict is not None:
        validation_dict[identifier] = elem.__class__.__name__
    return identifier


def identifier_to_parse_elem(identifier, validation_dict=None):
    """Get the parse element for the given identifier."""
    if identifier < len(all_parse_elements):
        maybe_elem = all_parse_elements[identifier]()
        if maybe_elem is not None:
            if validation_dict is not None:
                internal_assert(maybe_elem.__class__.__name__ == validation_dict[identifier], "parse element pickle-unpickle inconsistency", (maybe_elem, validation_dict[identifier]))
            return maybe_elem
    return None


# -----------------------------------------------------------------------------------------------------------------------
# PARSE ELEMENTS:
# -----------------------------------------------------------------------------------------------------------------------

class MatchAny(MatchFirst):
    """Version of MatchFirst that always uses adaptive parsing."""
    all_match_anys = []

    def __init__(self, *args, **kwargs):
        super(MatchAny, self).__init__(*args, **kwargs)
        self.all_match_anys.append(weakref.ref(self))

    def __or__(self, other):
        if isinstance(other, MatchAny):
            self = maybe_copy_elem(self, "any_or")
            return self.append(other)
        else:
            return MatchFirst([self, other])

    @override
    def copy(self):
        self = super(MatchAny, self).copy()
        self.all_match_anys.append(weakref.ref(self))
        return self

    if not use_fast_pyparsing_reprs:
        def __str__(self):
            return self.__class__.__name__ + ":" + super(MatchAny, self).__str__()


if SUPPORTS_ADAPTIVE:
    MatchAny.setAdaptiveMode(True)


def any_of(*exprs, **kwargs):
    """Build a MatchAny of the given MatchFirst."""
    use_adaptive = kwargs.pop("use_adaptive", use_adaptive_any_of) and SUPPORTS_ADAPTIVE
    reverse = reverse_any_of
    if DEVELOP:
        reverse = kwargs.pop("reverse", reverse)
    internal_assert(not kwargs, "excess keyword arguments passed to any_of", kwargs)

    AnyOf = MatchAny if use_adaptive else MatchFirst

    flat_exprs = []
    for e in exprs:
        if (
            # don't merge MatchFirsts when we're reversing
            not (reverse and not use_adaptive)
            and e.__class__ == AnyOf
            and not hasaction(e)
        ):
            flat_exprs.extend(e.exprs)
        else:
            flat_exprs.append(e)

    if reverse:
        flat_exprs = reversed([trace(e) for e in exprs])

    return AnyOf(flat_exprs)


class Wrap(ParseElementEnhance):
    """PyParsing token that wraps the given item in the given context manager."""
    global_instance_counter = 0
    inside = False

    def __init__(self, item, wrapper, greedy=False, include_in_packrat_context=True):
        super(Wrap, self).__init__(item)
        self.wrapper = wrapper
        self.greedy = greedy
        self.include_in_packrat_context = SUPPORTS_PACKRAT_CONTEXT and include_in_packrat_context
        self.identifier = Wrap.global_instance_counter
        Wrap.global_instance_counter += 1

    @property
    def wrapped_name(self):
        return get_name(self.expr) + " (Wrapped)"

    @contextmanager
    def wrapped_context(self):
        """Context manager that edits the packrat_context.

        Required to allow the packrat cache to distinguish between wrapped
        and unwrapped parses. Only supported natively on cPyparsing."""
        was_inside, self.inside = self.inside, True
        if self.include_in_packrat_context:
            old_packrat_context = ParserElement.packrat_context
            new_packrat_context = old_packrat_context | frozenset((self.identifier,))
            ParserElement.packrat_context = new_packrat_context
        try:
            yield
        finally:
            if self.include_in_packrat_context:
                internal_assert(ParserElement.packrat_context == new_packrat_context, "invalid popped Wrap identifier", self.identifier)
                ParserElement.packrat_context = old_packrat_context
            self.inside = was_inside

    @override
    def parseImpl(self, original, loc, *args, **kwargs):
        """Wrapper around ParseElementEnhance.parseImpl."""
        if logger.tracing:  # avoid the overhead of the call if not tracing
            logger.log_trace(self.wrapped_name, original, loc)
        with logger.indent_tracing():
            reparse = False
            parse_loc = None
            while parse_loc is None:  # lets wrapper catch errors to trigger a reparse
                with self.wrapper(original, loc, self, **(dict(reparse=True) if reparse else {})):
                    with self.wrapped_context():
                        parse_loc, tokens = super(Wrap, self).parseImpl(original, loc, *args, **kwargs)
                        if self.greedy:
                            if logger.tracing and not final_evaluate_tokens.enabled:
                                logger.log_tag("cached_parse invalidated by", self)
                            tokens = evaluate_tokens(tokens)
                if reparse and parse_loc is None:
                    raise CoconutInternalException("illegal double reparse in", self)
                reparse = True
        if logger.tracing:  # avoid the overhead of the call if not tracing
            logger.log_trace(self.wrapped_name, original, loc, tokens)
        return parse_loc, tokens

    def __str__(self):
        return self.wrapped_name

    def __repr__(self):
        return self.wrapped_name


def manage(item, manager, include_in_packrat_context, greedy=True):
    """Attach a manager to the given parse item."""
    return Wrap(item, manager, include_in_packrat_context=include_in_packrat_context, greedy=greedy)


def handle_and_manage(item, handler, manager, **kwargs):
    """Attach a handler and a manager to the given parse item."""
    return manage(attach(item, handler), manager, **kwargs)


def disable_inside(item, *elems, **kwargs):
    """Prevent elems from matching inside of item.

    Returns (item with elems disabled, *new versions of elems).
    """
    _invert = kwargs.pop("_invert", False)
    internal_assert(not kwargs, "excess keyword arguments passed to disable_inside", kwargs)

    level = [0]  # number of wrapped items deep we are; in a list to allow modification

    @contextmanager
    def manage_item(original, loc, self):
        level[0] += 1
        try:
            yield
        finally:
            level[0] -= 1

    yield Wrap(item, manage_item, include_in_packrat_context=True)

    @contextmanager
    def manage_elem(original, loc, self):
        if level[0] == 0 if not _invert else level[0] > 0:
            yield
        else:
            raise ParseException(original, loc, self.errmsg, self)

    for elem in elems:
        yield Wrap(elem, manage_elem)


def disable_outside(item, *elems):
    """Prevent elems from matching outside of item.

    Returns (item with elems enabled, *new versions of elems).
    """
    for wrapped in disable_inside(item, *elems, _invert=True):
        yield wrapped


@memoize()
def labeled_group(item, label):
    """A labeled pyparsing Group."""
    return Group(item(label))


def fake_labeled_group_handle(label, tokens):
    """Pickleable handler for fake_labeled_group."""
    internal_assert(label in tokens, "failed to label with " + repr(label) + " for tokens", tokens)
    [item], = tokens
    return item


def fake_labeled_group(item, label):
    """Apply a label to an item in a group and then destroy the group.
    Only useful with special labels that stick around."""
    return attach(labeled_group(item, label), partial(fake_labeled_group_handle, label))


def add_labels(tokens):
    """Parse action to gather all the attached labels."""
    item, = tokens
    return (item, tokens._ParseResults__tokdict.keys())


def invalid_syntax_handle(msg, original, loc, tokens):
    """Pickleable handler for invalid_syntax."""
    raise CoconutDeferredSyntaxError(msg, loc)


invalid_syntax_handle.trim_arity = False  # fixes pypy issue


def invalid_syntax(item, msg, **kwargs):
    """Mark a grammar item as an invalid item that raises a syntax err with msg."""
    if isinstance(item, str):
        item = Literal(item)
    elif isinstance(item, tuple):
        item = reduce(lambda a, b: a | b, map(Literal, item))
    return attach(item, partial(invalid_syntax_handle, msg), ignore_arguments=True, **kwargs)


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


@memoize(64)
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
    return attach(item, const([output]), ignore_arguments=True)


def addspace(item):
    """Condense and adds space to the tokenized output."""
    return attach(item, " ".join, ignore_no_tokens=True, ignore_one_token=True)


def condense(item):
    """Condense the tokenized output."""
    return attach(item, "".join, ignore_no_tokens=True, ignore_one_token=True)


@memoize()
def maybeparens(lparen, item, rparen, prefer_parens=False):
    """Wrap an item in optional parentheses, only applying them if necessary."""
    if prefer_parens:
        return lparen.suppress() + item + rparen.suppress() | item
    else:
        return item | lparen.suppress() + item + rparen.suppress()


def interleaved_tokenlist(required_item, other_item, sep, allow_trailing=False, at_least_two=False, multi_group=True):
    """Create a grammar to match interleaved required_items and other_items,
    where required_item must show up at least once."""
    sep = sep.suppress()

    def one_or_more_group(item):
        return Group(OneOrMore(item)) if multi_group else OneOrMore(Group(item))

    if at_least_two:
        out = (
            # required sep other (sep other)*
            Group(required_item)
            + one_or_more_group(sep + other_item)
            # other (sep other)* sep required (sep required)*
            | (
                Group(other_item + ZeroOrMore(sep + other_item))
                if multi_group else
                Group(other_item) + ZeroOrMore(Group(sep + other_item))
            ) + one_or_more_group(sep + required_item)
            # required sep required (sep required)*
            | (
                Group(required_item + OneOrMore(sep + required_item))
                if multi_group else
                Group(required_item) + OneOrMore(Group(sep + required_item))
            )
        )
    else:
        out = (
            Optional(one_or_more_group(other_item + sep))
            + (
                Group(required_item + ZeroOrMore(sep + required_item))
                if multi_group else
                Group(required_item) + ZeroOrMore(Group(sep + required_item))
            ) + Optional(one_or_more_group(sep + other_item))
        )
    out += ZeroOrMore(
        one_or_more_group(sep + required_item)
        | one_or_more_group(sep + other_item)
    )
    if allow_trailing:
        out += Optional(sep)
    return out


@memoize()
def tokenlist(item, sep, suppress=True, allow_trailing=True, at_least_two=False, require_sep=False, suppress_trailing=False):
    """Create a list of tokens matching the item."""
    if suppress:
        sep = sep.suppress()
    if suppress_trailing:
        trailing_sep = sep.suppress()
    else:
        trailing_sep = sep
    if not require_sep:
        out = item + (OneOrMore if at_least_two else ZeroOrMore)(sep + item)
        if allow_trailing:
            out += Optional(trailing_sep)
    elif not allow_trailing:
        out = item + OneOrMore(sep + item)
    elif at_least_two:
        out = item + OneOrMore(sep + item) + Optional(trailing_sep)
    elif suppress_trailing:
        out = item + OneOrMore(sep + item) + Optional(trailing_sep) | item + trailing_sep
    else:
        out = OneOrMore(item + sep) + Optional(item)
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


def itemlist(item, sep, suppress_trailing=True, **kwargs):
    """Create a list of items separated by seps with comma-like spacing added.
    A trailing sep is allowed."""
    return attach(
        tokenlist(item, sep, suppress=False, suppress_trailing=suppress_trailing, **kwargs),
        add_list_spacing,
    )


def exprlist(expr, op, **kwargs):
    """Create a list of exprs separated by ops with plus-like spacing added.
    No trailing op is allowed."""
    return addspace(tokenlist(expr, op, suppress=False, allow_trailing=False, **kwargs))


def stores_loc_action(loc, tokens):
    """Action that just parses to loc."""
    internal_assert(len(tokens) == 0, "invalid store loc tokens", tokens)
    return str(loc)


always_match = Empty()
stores_loc_item = attach(always_match, stores_loc_action)


def disallow_keywords(kwds, with_suffix=""):
    """Prevent the given kwds from matching."""
    to_disallow = (
        k + r"\b" + re.escape(with_suffix)
        for k in kwds
    )
    return regex_item(r"(?!" + "|".join(to_disallow) + r")").suppress()


def disambiguate_literal(literal, not_literals, fixesto=None):
    """Get an item that matchesl literal and not any of not_literals."""
    item = regex_item(
        r"(?!" + "|".join(re.escape(s) for s in not_literals) + ")"
        + re.escape(literal)
    )
    if fixesto is not None:
        item = fixto(item, fixesto)
    return item


def any_keyword_in(kwds):
    """Match any of the given keywords."""
    return regex_item(r"|".join(k + r"\b" for k in kwds))


def base_keyword(name, explicit_prefix=False, require_whitespace=False):
    """Construct a grammar which matches name as a Python keyword."""
    base_kwd = regex_item(name + r"\b" + (r"(?=\s)" if require_whitespace else ""))
    if explicit_prefix and name in reserved_vars + allow_explicit_keyword_vars:
        return combine(Optional(explicit_prefix.suppress()) + base_kwd)
    else:
        return base_kwd


boundary = regex_item(r"\b")


def any_len_perm_with_one_of_each_group(*groups_and_elems):
    """Matches any len permutation of elems that contains at least one of each group."""
    elems = []
    groups = defaultdict(list)
    for item in groups_and_elems:
        if isinstance(item, tuple):
            g, e = item
        else:
            g, e = None, item
        elems.append(e)
        if g is not None:
            groups[g].append(e)

    out = None
    allow_none = False
    ordered_subsets = list(ordered_powerset(elems))
    # reverse to ensure that prefixes are matched last
    ordered_subsets.reverse()
    for ord_subset in ordered_subsets:
        allow = True
        for grp in groups.values():
            if not any(e in ord_subset for e in grp):
                allow = False
                break
        if allow:
            if ord_subset:
                ord_subset_item = reduce(lambda x, y: x + y, ord_subset)
                if out is None:
                    out = ord_subset_item
                else:
                    out |= ord_subset_item
            else:
                allow_none = True
    if allow_none:
        out = Optional(out)
    return out


def any_len_perm(*optional, **kwargs):
    """Any length permutation of optional and required."""
    required = kwargs.pop("required", ())
    internal_assert(not kwargs, "invalid any_len_perm kwargs", kwargs)

    groups_and_elems = []
    groups_and_elems.extend(optional)
    groups_and_elems.extend(enumerate(required))
    return any_len_perm_with_one_of_each_group(*groups_and_elems)


def any_len_perm_at_least_one(*elems, **kwargs):
    """Any length permutation of elems that includes at least one of the elems and all the required."""
    required = kwargs.pop("required", ())
    internal_assert(not kwargs, "invalid any_len_perm kwargs", kwargs)

    groups_and_elems = []
    groups_and_elems.extend((-1, e) for e in elems)
    groups_and_elems.extend(enumerate(required))
    return any_len_perm_with_one_of_each_group(*groups_and_elems)


def caseless_literal(literalstr, suppress=False, disambiguate=False):
    """Version of CaselessLiteral that always parses to the given literalstr."""
    out = CaselessLiteral(literalstr)
    if suppress:
        out = out.suppress()
    else:
        out = fixto(out, literalstr)
    if disambiguate:
        out = disallow_keywords(k for k in all_keywords if k.startswith((literalstr[0].lower(), literalstr[0].upper()))) + out
    return out


# -----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
# -----------------------------------------------------------------------------------------------------------------------


def ordered(items):
    """Return the items in a deterministic order."""
    if PY2:
        return sorted(items)
    else:
        return items


def pprint_tokens(tokens):
    """Pretty print tokens."""
    pprinting, ComputationNode.pprinting = ComputationNode.pprinting, True
    try:
        pprint(eval(repr(tokens)))
    finally:
        ComputationNode.pprinting = pprinting


def getline(loc, original):
    """Get the line at loc in original."""
    return _line(loc, original.replace(non_syntactic_newline, "\n"))


def powerset(items, min_len=0):
    """Return the powerset of the given items."""
    return itertools.chain.from_iterable(
        itertools.combinations(items, comb_len) for comb_len in range(min_len, len(items) + 1)
    )


def ordered_powerset(items, min_len=0):
    """Return all orderings of each subset in the powerset of the given items."""
    return itertools.chain.from_iterable(
        itertools.permutations(items, perm_len) for perm_len in range(min_len, len(items) + 1)
    )


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
    return itertools.chain(iterator, (last_val,))


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


def paren_change(inputstr, opens=open_chars, closes=close_chars):
    """Determine the parenthetical change of level (num closes - num opens)."""
    count = 0
    for c in inputstr:
        if c in opens:  # open parens/brackets/braces
            count -= 1
        elif c in closes:  # close parens/brackets/braces
            count += 1
    return count


def close_char_for(open_char):
    """Get the close char for the given open char."""
    return close_chars[open_chars.index(open_char)]


def open_char_for(close_char):
    """Get the open char for the given close char."""
    return open_chars[close_chars.index(close_char)]


def ind_change(inputstr):
    """Determine the change in indentation level (num opens - num closes)."""
    return inputstr.count(openindent) - inputstr.count(closeindent)


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


def tuple_str_of_str(argstr, add_parens=True):
    """Make a tuple repr of the given comma-delimited argstr."""
    out = argstr + ("," if argstr else "")
    if add_parens:
        out = "(" + out + ")"
    return out


def dict_to_str(inputdict, quote_keys=False, quote_values=False):
    """Convert a dictionary of code snippets to a dict literal."""
    return "{" + ", ".join(
        (repr(key) if quote_keys else str(key)) + ": " + (repr(value) if quote_values else str(value))
        for key, value in ordered(inputdict.items())
    ) + "}"


def split_comment(line, move_indents=False):
    """Split line into base and comment."""
    if move_indents:
        line, indent = split_trailing_indent(line, handle_comments=False)
    else:
        indent = ""
    for i, c in enumerate(append_it(line, None)):
        if c in comment_chars:
            break
    return line[:i] + indent, line[i:]


def extract_line_num_from_comment(line, default=None):
    """Extract the line number from a line with a line number comment, else return default."""
    _, all_comments = split_comment(line)
    for comment in all_comments.split("#"):
        words = comment.strip().split(None, 1)
        if words:
            first_word = words[0].strip(":")
            try:
                return int(first_word)
            except ValueError:
                pass
    logger.log("failed to extract line num comment from", line)
    return default


def rem_comment(line):
    """Remove a comment from a line."""
    base, comment = split_comment(line)
    return base


def get_comment(line):
    """Extract a comment from a line if it has one."""
    base, comment = split_comment(line)
    return comment


def should_indent(code):
    """Determines whether the next line should be indented."""
    last_line = rem_comment(code.splitlines()[-1])
    return last_line.endswith((":", "=", "\\")) or paren_change(last_line) < 0


def split_leading_comments(inputstr):
    """Split into leading comments and rest."""
    comments = ""
    indent, base = split_leading_indent(inputstr)

    while base.startswith(comment_chars):
        comment_line, rest = base.split("\n", 1)

        got_comment, got_indent = split_trailing_indent(comment_line)
        comments += got_comment + "\n"
        indent += got_indent

        got_indent, base = split_leading_indent(rest)
        indent += got_indent

    return comments, indent + base


def split_trailing_comment(inputstr):
    """Split into rest and trailing comment."""
    parts = inputstr.rsplit("\n", 1)
    if len(parts) == 1:
        return parts[0], ""
    else:
        rest, last_line = parts
        last_line, comment = split_comment(last_line)
        return rest + "\n" + last_line, comment


def split_leading_indent(inputstr, max_indents=None):
    """Split inputstr into leading indent and main."""
    indents = []
    while (
        (max_indents is None or max_indents > 0)
        and inputstr.startswith(indchars)
    ) or inputstr.lstrip() != inputstr:
        got_ind, inputstr = inputstr[0], inputstr[1:]
        # max_indents only refers to openindents/closeindents, not all indchars
        if max_indents is not None and got_ind in (openindent, closeindent):
            max_indents -= 1
        indents.append(got_ind)
    return "".join(indents), inputstr


def split_trailing_indent(inputstr, max_indents=None, handle_comments=True):
    """Split inputstr into leading indent and main."""
    indents_from_end = []
    while (
        (max_indents is None or max_indents > 0)
        and inputstr.endswith(indchars)
    ) or inputstr.rstrip() != inputstr:
        inputstr, got_ind = inputstr[:-1], inputstr[-1]
        # max_indents only refers to openindents/closeindents, not all indchars
        if max_indents is not None and got_ind in (openindent, closeindent):
            max_indents -= 1
        indents_from_end.append(got_ind)
    if handle_comments:
        inputstr, comment = split_trailing_comment(inputstr)
        inputstr, inner_indent = split_trailing_indent(inputstr, max_indents, handle_comments=False)
        inputstr = inputstr + comment
        indents_from_end.append(inner_indent)
    return inputstr, "".join(reversed(indents_from_end))


def split_leading_trailing_indent(line, symmetric=False, **kwargs):
    """Split leading and trailing indent."""
    leading_indent, line = split_leading_indent(line, **kwargs)
    if symmetric:
        kwargs["max_indents"] = leading_indent.count(openindent)
    line, trailing_indent = split_trailing_indent(line, **kwargs)
    return leading_indent, line, trailing_indent


def rem_and_count_indents(inputstr):
    """Removes and counts the ind_change (opens - closes)."""
    no_opens = inputstr.replace(openindent, "")
    num_opens = len(inputstr) - len(no_opens)
    no_indents = no_opens.replace(closeindent, "")
    num_closes = len(no_opens) - len(no_indents)
    return no_indents, num_opens - num_closes


def rem_and_collect_indents(inputstr):
    """Removes and collects all indents into (non_indent_chars, indents)."""
    non_indent_chars, change_in_level = rem_and_count_indents(inputstr)
    if change_in_level == 0:
        indents = ""
    elif change_in_level < 0:
        indents = closeindent * (-change_in_level)
    else:
        indents = openindent * change_in_level
    return non_indent_chars, indents


def collapse_indents(indentation):
    """Removes all openindent-closeindent pairs."""
    non_indent_chars, indents = rem_and_collect_indents(indentation)
    return non_indent_chars + indents


def is_blank(line):
    """Determine whether a line is blank."""
    line, _ = rem_and_count_indents(rem_comment(line))
    return not line or line.isspace()


def final_indentation_level(code):
    """Determine the final indentation level of the given code."""
    level = 0
    for line in literal_lines(code):
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


def handle_indentation(inputstr, add_newline=False, extra_indent=0):
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
    if extra_indent:
        out = openindent * extra_indent + out + closeindent * extra_indent
    internal_assert(lambda: out.count(openindent) == out.count(closeindent), "failed to properly handle indentation in", out)
    return out


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


def sequential_split(inputstr, splits):
    """Slice off parts of inputstr by sequential splits."""
    out = [inputstr]
    for s in splits:
        out += out.pop().split(s, 1)
    return out


def normalize_indent_markers(lines):
    """Normalize the location of indent markers to the earliest equivalent location."""
    new_lines = lines[:]
    for i in range(1, len(new_lines)):
        indent, line = split_leading_indent(new_lines[i])
        if indent:
            j = i - 1  # the index to move the initial indent to
            while j > 0:
                if is_blank(new_lines[j]):
                    new_lines[j], indent = rem_and_collect_indents(new_lines[j] + indent)
                    j -= 1
                else:
                    break
            new_lines[j] += indent
            new_lines[i] = line
    return new_lines


def add_int_and_strs(int_part=0, str_parts=(), parens=False):
    """Get an int/str that adds the int part and str parts."""
    if not str_parts:
        return int_part
    if int_part:
        str_parts.append(str(int_part))
    if len(str_parts) == 1:
        return str_parts[0]
    out = " + ".join(str_parts)
    if parens:
        out = "(" + out + ")"
    return out


def base_move_loc(original, loc, chars_to_move_forwards):
    """Move loc in original in accordance with chars_to_move_forwards."""
    visited_locs = set()
    while 0 <= loc <= len(original) - 1:
        c = original[loc]
        for charset, forwards in chars_to_move_forwards.items():
            if c in charset:
                break
        else:  # no break
            break
        if forwards:
            if loc >= len(original) - 1:
                break
            next_loc = loc + 1
        else:
            if loc <= 1:
                break
            next_loc = loc - 1
        if next_loc in visited_locs:
            loc = next_loc
            break
        visited_locs.add(next_loc)
        loc = next_loc
    return loc


def move_loc_to_non_whitespace(original, loc, backwards=False):
    """Move the given loc in original to the closest non-whitespace in the given direction.
    Won't ever move far enough to set loc to 0 or len(original)."""
    return base_move_loc(
        original,
        loc,
        chars_to_move_forwards={
            # for loc, move backwards on newlines/indents, which we can do safely without removing anything from the error
            indchars: False,
            default_whitespace_chars: not backwards,
        },
    )


def move_endpt_to_non_whitespace(original, loc, backwards=False):
    """Same as base_move_loc but for endpoints specifically."""
    return base_move_loc(
        original,
        loc,
        chars_to_move_forwards={
            # for endpt, ignore newlines/indents to avoid introducing unnecessary lines into the error
            default_whitespace_chars: not backwards,
            # always move forwards on unwrapper to ensure we don't cut wrapped objects in the middle
            unwrapper: True,
        },
    )


def sub_all(inputstr, regexes, replacements):
    """Sub all regexes for replacements in inputstr."""
    for key, regex in regexes.items():
        inputstr = regex.sub(lambda match: replacements[key], inputstr)
    return inputstr


# -----------------------------------------------------------------------------------------------------------------------
# EXTRAS:
# -----------------------------------------------------------------------------------------------------------------------


class FixPytestNames(ast.NodeTransformer):
    """Renames invalid names added by pytest assert rewriting."""

    def fix_name(self, name):
        """Make the given pytest name a valid but non-colliding identifier."""
        return name.replace("@", reserved_prefix + "_pytest_")

    def visit_Name(self, node):
        """Special method to visit ast.Names."""
        node.id = self.fix_name(node.id)
        return node

    def visit_alias(self, node):
        """Special method to visit ast.aliases."""
        node.asname = self.fix_name(node.asname)
        return node


def pytest_rewrite_asserts(code, module_name=reserved_prefix + "_pytest_module"):
    """Uses pytest to rewrite the assert statements in the given code."""
    from _pytest.assertion.rewrite import rewrite_asserts  # hidden since it's not always available

    module_name = module_name.encode("utf-8")
    tree = ast.parse(code)
    rewrite_asserts(tree, module_name)
    fixed_tree = ast.fix_missing_locations(FixPytestNames().visit(tree))
    return ast.unparse(fixed_tree)


@contextmanager
def adaptive_manager(original, loc, item, reparse=False):
    """Manage the use of MatchFirst.setAdaptiveMode."""
    if reparse:
        cleared_cache = clear_packrat_cache()
        if cleared_cache is not True:
            item.include_in_packrat_context = True
        MatchFirst.setAdaptiveMode(False, usage_weight=10)
        try:
            yield
        finally:
            MatchFirst.setAdaptiveMode(False, usage_weight=1)
            if cleared_cache is not True:
                item.include_in_packrat_context = False
    else:
        MatchFirst.setAdaptiveMode(True)
        try:
            yield
        except Exception as exc:
            if DEVELOP:
                logger.log("reparsing due to:", exc)
                logger.record_stat("adaptive", False)
        else:
            if DEVELOP:
                logger.record_stat("adaptive", True)
        finally:
            MatchFirst.setAdaptiveMode(False)
