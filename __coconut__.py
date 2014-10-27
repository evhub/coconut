#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# CoconutScript Header: --------------------------------------------------------

class __coconut__(object):
    """Built-In Coconut Functions."""
    import operator
    import functools
    curry = functools.partial
    fold = functools.reduce
    def inv(item):
        """Inversion (!True)."""
        if isinstance(item, bool):
            return not item
        else:
            return ~item
    def infix(a, func, b):
        """Infix Calling (5 \\mod\\ 6)."""
        return func(a, b)
    def pipe(*args):
        """Pipelining (x |> func)."""
        out = args[0]
        for func in args[1:]:
            out = func(out)
        return out
    def loop(*args):
        """Looping (a~ func)."""
        lists = list(args)
        func = lists.pop()
        while lists:
            new_lists = []
            items = []
            for series, step in lists:
                items += series[:step]
                series = series[step:]
                if series:
                    new_lists.append((series, step))
            if items:
                yield func(*items)
            else:
                break
            lists = new_lists
    def compose(f, g):
        """Composing (f..g)."""
        def _composed(*args, **kwargs):
            """Function Composition Wrapper."""
            return f(g(*args, **kwargs))
        return _composed
    def zipwith(func, *args):
        """Functional Zipping."""
        lists = list(args)
        while lists:
            new_lists = []
            items = []
            for series in lists:
                items.append(series[0])
                series = series[1:]
                if series:
                    new_lists.append(series)
            if items:
                yield func(*items)
            else:
                break
            lists = new_lists
    def recursive(func):
        """Tail Recursion Elimination."""
        state = [True, None]
        recurse = object()
        def _tailed(*args, **kwargs):
            """Tail Recursion Wrapper."""
            if state[0]:
                state[0] = False
                try:
                    while True:
                        result = func(*args, **kwargs)
                        if result is recurse:
                            args, kwargs = state[1]
                            state[1] = None
                        else:
                            return result
                finally:
                    state[0] = True
            else:
                state[1] = args, kwargs
                return recurse
        return _tailed

fold = __coconut__.fold
zipwith = __coconut__.zipwith
recursive = __coconut__.recursive

# Compiled CoconutScript: ------------------------------------------------------

