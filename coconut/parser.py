#!/usr/bin/env python

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# INFO:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
Date Created: 2014
Description: The Coconut Parser.
"""

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division

from .root import *
from pyparsing import *

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# HEADERS:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def headers(which, version=None):
    if which == "none":
        return ""
    elif which == "initial":
        if version is None:
            header = "#!/usr/bin/env python"
        elif version == "2":
            header = "#!/usr/bin/python2"
        elif version == "3":
            header = "#!/usr/bin/python3"
        else:
            raise CoconutException("invalid Python version: "+repr(version))
        header += r'''

# Compiled with Coconut version '''+VERSION_STR+'''

'''
    else:
        header = r'''

# Coconut Header: --------------------------------------------------------------
        '''
        if version is None:
            header += r'''
from __future__ import with_statement, print_function, absolute_import, unicode_literals, division
try: from future_builtins import *
except ImportError: pass
try: xrange
except NameError: pass
else:
    range = xrange
try: ascii
except NameError: ascii = repr
try: unichr
except NameError: unichr = chr
_coconut_encoding = "utf8"
try: unicode
except NameError: pass
else:
    bytes, str = str, unicode
    _coconut_print = print
    def print(*args, **kwargs):
        """Wraps _coconut_print."""
        return _coconut_print(*(str(x).encode(_coconut_encoding) for x in args), **kwargs)
try: raw_input
except NameError: pass
else:
    _coconut_input = raw_input
    def input(*args, **kwargs):
        """Wraps _coconut_input."""
        return _coconut_input(*args, **kwargs).decode(_coconut_encoding)
'''
        elif version == "2":
            header += r'''
from __future__ import with_statement, print_function, absolute_import, unicode_literals, division
from future_builtins import *
range = xrange
ascii = repr
unichr = chr
_coconut_encoding = "utf8"
bytes, str = str, unicode
_coconut_print = print
def print(*args, **kwargs):
    """Wraps _coconut_print."""
    return _coconut_print(*(str(x).encode(_coconut_encoding) for x in args), **kwargs)
_coconut_input = raw_input
def input(*args, **kwargs):
    """Wraps _coconut_input."""
    return _coconut_input(*args, **kwargs).decode(_coconut_encoding)
'''
        if which == "package":
            header += r'''
"""Built-in Coconut Functions."""

import functools
partial = functools.partial
reduce = functools.reduce

import operator
itemgetter = operator.itemgetter
attrgetter = operator.attrgetter
methodcaller = operator.methodcaller

import itertools
chain = itertools.chain
islice = itertools.islice
takewhile = itertools.takewhile
dropwhile = itertools.dropwhile
tee = itertools.tee

import collections
data = collections.namedtuple

try:
    import collections.abc as abc
except ImportError:
    abc = collections

def recursive(func):
    """Tail Call Optimizer."""
    state = [True, None]
    recurse = object()
    @functools.wraps(func)
    def tailed_func(*args, **kwargs):
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
    return tailed_func
'''
        else:
            if which == "module":
                header += r'''
import sys as _coconut_sys
import os.path as _coconut_os_path
_coconut_sys.path.append(_coconut_os_path.dirname(_coconut_os_path.abspath(__file__)))
import __coconut__
'''
            elif which == "code" or which == "file":
                header += r'''
class __coconut__(object):
    """Built-in Coconut Functions."""
    import functools
    partial = functools.partial
    reduce = functools.reduce
    import operator
    itemgetter = operator.itemgetter
    attrgetter = operator.attrgetter
    methodcaller = operator.methodcaller
    import itertools
    chain = itertools.chain
    islice = itertools.islice
    takewhile = itertools.takewhile
    dropwhile = itertools.dropwhile
    tee = itertools.tee
    import collections
    data = staticmethod(collections.namedtuple)
    try:
        import collections.abc as abc
    except ImportError:
        abc = collections
    @staticmethod
    def recursive(func):
        """Tail Call Optimizer."""
        state = [True, None]
        recurse = object()
        @functools.wraps(func)
        def tailed_func(*args, **kwargs):
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
        return tailed_func
'''
            else:
                raise CoconutException("invalid header type: "+repr(which))
            header += r'''
reduce = __coconut__.reduce
itemgetter = __coconut__.itemgetter
attrgetter = __coconut__.attrgetter
methodcaller = __coconut__.methodcaller
takewhile = __coconut__.takewhile
dropwhile = __coconut__.dropwhile
tee = __coconut__.tee
recursive = __coconut__.recursive
'''
            if which != "code":
                header += r'''
# Compiled Coconut: ------------------------------------------------------------

'''
    return header

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

ParserElement.enablePackrat()

openstr = "\u204b"
closestr = "\xb6"
linebreak = "\n"
white = " \t\f"
downs = "([{"
ups = ")]}"
holds = "'\""
startcomment = "#"
endline = "\n\r"
escape = "\\"
tablen = 4
decorator_var = "_coconut_decorator"
match_to_var = "_coconut_match_to"
match_check_var = "_coconut_match_check"
match_iter_var = "_coconut_match_iter"
wildcard = "_"
const_vars = ["True", "False", "None"]
reserved_vars = ["data", "match", "case", "async", "await"]

ParserElement.setDefaultWhitespaceChars(white)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

coconut_error = ParseFatalException, ParseException

class CoconutException(ParseFatalException):
    """Base Coconut exception."""
    def __init__(self, value):
        """creates the Coconut exception."""
        self.value = value
    def __repr__(self):
        """Displays the Coconut exception."""
        return self.value
    def __str__(self):
        """Wraps repr."""
        return repr(self)

class CoconutSyntaxError(CoconutException):
    """Coconut SyntaxError."""
    def __init__(self, message, source, point=None):
        """Creates the Coconut SyntaxError."""
        self.value = message
        if point is None:
            self.value += linebreak + "  " + source
        else:
            if point >= len(source):
                point = len(source)-1
            part = source.splitlines()[lineno(point, source)-1]
            self.value += linebreak + "  " + part + linebreak + "  "
            for x in range(0, col(point, source)):
                if part[x] in white:
                    self.value += part[x]
                else:
                    self.value += " "
            self.value += "^"

class CoconutStyleError(CoconutSyntaxError):
    """Coconut --strict error."""
    def __init__(self, message, source, point=None):
        """Creates the --strict Coconut error."""
        message += " (disable --strict to dismiss)"
        CoconutSyntaxError.__init__(self, message, source, point)

def attach(item, action):
    """Attaches a parse action to an item."""
    return item.copy().addParseAction(action)

def fixto(item, output):
    """Forces an item to result in a specific output."""
    return attach(item, replaceWith(output))

def addspace(item):
    """Condenses and adds space to the tokenized output."""
    def callback(tokens):
        """Callback function constructed by addspace."""
        return " ".join(tokens)
    return attach(item, callback)

def condense(item):
    """Condenses the tokenized output."""
    def callback(tokens):
        """Callback function constructed by condense."""
        return "".join(tokens)
    return attach(item, callback)

def parenwrap(lparen, item, rparen):
    """Wraps an item in optional parentheses."""
    return condense(lparen.suppress() + item + rparen.suppress() ^ item)

class tracer(object):
    """Debug tracer."""
    show = print

    def __init__(self, on=False):
        """Creates the tracer."""
        self.debug(on)

    def debug(self, on=True):
        """Changes the tracer's state."""
        self.on = on

    def trace(self, original, location, tokens, message=None):
        """Tracer parse action."""
        if self.on:
            original = str(original)
            location = int(location)
            out = ""
            if message is not None:
                out += "["+message+"] "
            if len(tokens) == 1 and isinstance(tokens[0], str):
                out += repr(tokens[0])
            else:
                out += str(tokens)
            out += " (line "+str(lineno(location, original))+", col "+str(col(location, original))+")"
            self.show(out)
        return tokens

    def bind(self, item, message=None):
        """Traces a parse element."""
        if message is None:
            callback = self.trace
        else:
            def callback(original, location, tokens):
                """Callback function constructed by tracer."""
                return self.trace(original, location, tokens, message)
        bound = attach(item, callback)
        if message is not None:
            bound.setName(message)
        return bound

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PROCESSORS:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def anyint_proc(tokens):
    """Replaces underscored integers."""
    if len(tokens) == 1:
        item, base = tokens[0].split("_")
        return 'int("'+item+'", '+base+")"
    else:
        raise CoconutException("invalid anyint tokens: "+repr(toknes))

def list_proc(tokens):
    """Properly formats lists."""
    out = []
    for x in range(0, len(tokens)):
        if x%2 == 0:
            out.append(tokens[x])
        else:
            out[-1] += tokens[x]
    return " ".join(out)

def itemlist(item, sep):
    """Creates a list containing an item."""
    return attach(item + ZeroOrMore(sep + item) + Optional(sep), list_proc)

def item_proc(tokens):
    """Processes items."""
    out = tokens.pop(0)
    for trailer in tokens:
        if isinstance(trailer, str):
            out += trailer
        elif len(trailer) == 1:
            raise CoconutSyntaxError("an argument is required", trailer[0])
        elif len(trailer) == 2:
            if trailer[0] == "$(":
                out = "__coconut__.partial("+out+", "+trailer[1]+")"
            elif trailer[0] == "$[":
                if 0 < len(trailer[1]) <= 3:
                    args = []
                    for x in range(0, len(trailer[1])):
                        arg = trailer[1][x]
                        if not arg:
                            if x == 0:
                                arg = "0"
                            else:
                                arg = "None"
                        args.append(arg)
                    out = "__coconut__.islice("+out
                    if len(args) == 1:
                        out += ", "+args[0]+", ("+args[0]+") + 1)"
                        out = "next("+out+")"
                    else:
                        for arg in args:
                            out += ", "+arg
                        out += ")"
                else:
                    raise CoconutException("invalid iterator slice args: "+repr(trailer[1]))
            elif trailer[0] == "..":
                out = "(lambda *args, **kwargs: ("+out+")(("+trailer[1]+")(*args, **kwargs)))"
            else:
                raise CoconutException("invalid special trailer: "+repr(trailer[0]))
        else:
            raise CoconutException("invalid trailer tokens: "+repr(trailer))
    return out

def chain_proc(tokens):
    """Processes chain calls."""
    if len(tokens) == 1:
        return tokens[0]
    else:
        return "__coconut__.chain("+", ".join(tokens)+")"

def infix_proc(tokens):
    """Processes infix calls."""
    if len(tokens) < 3:
        raise CoconutException("invalid infix tokens: "+repr(tokens))
    else:
        items = []
        for item in tokens[0]:
            items.append(item)
        for item in tokens[2]:
            items.append(item)
        if len(tokens) > 3:
            items.append(infix_proc([[]]+tokens[3:]))
        args = []
        for arg in items:
            if arg:
                args.append(arg)
        return tokens[1] + "(" + ", ".join(args) + ")"

def pipe_proc(tokens):
    """Processes pipe calls."""
    if len(tokens) == 1:
        return tokens[0]
    else:
        func = tokens.pop()
        return func+"("+pipe_proc(tokens)+")"

def lambda_proc(tokens):
    """Processes lambda calls."""
    if len(tokens) == 1:
        return "lambda: "+tokens[0]
    elif len(tokens) == 2:
        return "lambda "+tokens[0]+": "+tokens[1]
    else:
        raise CoconutException("invalid lambda tokens: "+repr(tokens))

def assign_proc(tokens):
    """Processes assignments."""
    if len(tokens) == 3:
        name, op, item = tokens
        out = ""
        if op == "|>=":
            out += name+" = ("+item+")("+name+")"
        elif op == "..=":
            out += name+" = (lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs)))("+name+", "+item+")"
        elif op == "::=":
            out += name+" = __coconut__.chain("+name+", ("+item+"))"
        else:
            out += name+" "+op+" "+item
        return out
    else:
        raise CoconutException("invalid assignment tokens: "+repr(tokens))

def func_proc(tokens):
    """Processes mathematical function definitons."""
    if len(tokens) == 2:
        return "def "+tokens[0]+": return "+tokens[1]
    else:
        raise CoconutException("invalid mathematical function definition tokens: "+repr(tokens))

def data_proc(tokens):
    """Processes data blocks."""
    if len(tokens) == 2:
        return "class "+tokens[0]+"(__coconut__.data('"+tokens[0]+"', '"+tokens[1]+"'))"
    elif len(tokens) == 1:
        return "class "+tokens[0]+"(__coconut__.data('"+tokens[0]+"', ''))"
    else:
        raise CoconutException("invalid data tokens: "+repr(tokens))

def decorator_proc(tokens):
    """Processes decorators."""
    defs = []
    decorates = []
    for x in range(0, len(tokens)):
        varname = decorator_var + "_" + str(x)
        defs.append(varname+" = "+tokens[x])
        decorates.append("@"+varname)
    return linebreak.join(defs + decorates) + linebreak

def else_proc(tokens):
    """Processes compound else statements."""
    if len(tokens) == 1:
        return linebreak + openstr + tokens[0] + closestr
    else:
        raise CoconutException("invalid compound else statement tokens: "+repr(tokens))

def set_proc(tokens):
    """Processes set literals."""
    if len(tokens) == 1:
        set_type = tokens[0]
        if set_type == "s":
            return "set()"
        elif set_type == "f":
            return "frozenset()"
        else:
            raise CoconutException("invalid set type: "+str(set_type))
    elif len(tokens) == 2:
        set_type, set_maker = tokens
        if set_type == "s":
            return "set(["+set_maker+"])"
        elif set_type == "f":
            return "frozenset(["+set_maker+"])"
        else:
            raise CoconutException("invalid set type: "+str(set_type))
    else:
        raise CoconutException("invalid set literal tokens: "+repr(tokens))

def class_proc(tokens):
    """Processes class inheritance lists."""
    if len(tokens) == 0:
        return "(object)"
    elif len(tokens) == 1:
        return "("+tokens[0]+")"
    else:
        raise CoconutException("invalid class inheritance tokens: "+repr(tokens))

class matcher(object):
    """Pattern-matching processor."""
    position = 0
    iter_index = 0

    def __init__(self, checkvar, checkdefs=None, names=None):
        """Creates the matcher."""
        self.checkvar = checkvar
        self.checkdefs = []
        if checkdefs is None:
            self.increment()
        else:
            for checks, defs in checkdefs:
                self.checkdefs.append([checks[:], defs[:]])
            self.checks = self.get_checks(-1)
            self.defs = self.get_defs(-1)
        if names is None:
            self.names = {}
        else:
            self.names = dict(names)
        self.others = []

    def duplicate(self):
        """Duplicates the matcher to others."""
        self.others.append(matcher(self.checkvar, self.checkdefs, self.names))
        self.others[-1].set_checks(0, ["not "+self.checkvar] + self.others[-1].get_checks(0))
        return self.others[-1]

    def get_checks(self, position):
        """Gets the checks at the position."""
        return self.checkdefs[position][0]

    def set_checks(self, position, checks):
        """Sets the checks at the position."""
        self.checkdefs[position][0] = checks

    def set_defs(self, position, defs):
        """Sets the defs at the position."""
        self.checkdefs[position][1] = defs

    def get_defs(self, position):
        """Gets the defs at the position."""
        return self.checkdefs[position][1]

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

    def set_position(self, position):
        """Sets the if-statement position."""
        if position < 0:
            raise CoconutException("invalid match index: "+str(position))
        while position >= len(self.checkdefs):
            self.checkdefs.append([[], []])
        self.checks = self.checkdefs[position][0]
        self.defs = self.checkdefs[position][1]
        self.position = position

    def increment(self, forall=False):
        """Advances the if-statement position."""
        self.set_position(self.position+1)
        if forall:
            for other in self.others:
                other.increment(True)

    def decrement(self, forall=False):
        """Decrements the if-statement position."""
        self.set_position(self.position-1)
        if forall:
            for other in self.others:
                other.decrement(True)

    def match(self, original, item):
        """Performs pattern-matching processing."""
        if "dict" in original:
            if len(original) == 1:
                match = original[0]
            else:
                raise CoconutException("invalid dict match tokens: "+repr(original))
            self.checks.append("isinstance("+item+", __coconut__.abc.Mapping)")
            self.checks.append("len("+item+") == "+str(len(match)))
            for x in range(0, len(match)):
                k,v = match[x]
                self.checks.append(k+" in "+item)
                self.match(v, item+"["+k+"]")
        elif "series" in original and (len(original) == 2 or (len(original) == 4 and original[2] == "+")):
            tail = None
            if len(original) == 2:
                series_type, match = original
            else:
                series_type, match, _, tail = original
            self.checks.append("isinstance("+item+", __coconut__.abc.Sequence)")
            if tail is None:
                self.checks.append("len("+item+") == "+str(len(match)))
            else:
                self.checks.append("len("+item+") >= "+str(len(match)))
                if series_type == "(":
                    self.defs.append(tail+" = tuple("+item+"["+str(len(match))+":])")
                elif series_type == "[":
                    self.defs.append(tail+" = list("+item+"["+str(len(match))+":])")
                else:
                    raise CoconutException("invalid series match type: "+repr(series_type))
            for x in range(0, len(match)):
                self.match(match[x], item+"["+str(x)+"]")
        elif "series" in original and len(original) == 4 and original[2] == "::":
            series_type, match, _, tail = original
            self.checks.append("isinstance("+item+", __coconut__.abc.Iterable)")
            itervar = match_iter_var + "_" + str(self.iter_index)
            self.iter_index += 1
            if series_type == "(":
                self.defs.append(itervar+" = tuple(__coconut__.islice("+item+", 0, "+str(len(match))+"))")
            elif series_type == "[":
                self.defs.append(itervar+" = list(__coconut__.islice("+item+", 0, "+str(len(match))+"))")
            else:
                raise CoconutException("invalid iterator match tokens: "+repr(original))
            self.defs.append(tail+" = "+item)
            self.increment()
            self.checks.append("len("+itervar+") >= "+str(len(match)))
            for x in range(0, len(match)):
                self.match(match[x], itervar+"["+str(x)+"]")
            self.decrement()
        elif "const" in original:
            (match,) = original
            if match in const_vars:
                self.checks.append(item+" is "+match)
            else:
                self.checks.append(item+" == "+match)
        elif "is" in original:
            match, type_check = original
            self.checks.append("isinstance("+item+", ("+type_check+"))")
            self.match(match, item)
        elif "var" in original:
            (setvar,) = original
            if setvar != wildcard:
                if setvar in self.names:
                    self.checks.append(self.names[setvar]+" == "+item)
                else:
                    self.defs.append(setvar+" = "+item)
                    self.names[setvar] = item
        elif "set" in original:
            if len(original) == 1:
                match = original[0]
            else:
                raise CoconutException("invalid set match tokens: "+repr(original))
            self.checks.append("isinstance("+item+", __coconut__.abc.Set)")
            self.checks.append("len("+item+") == "+str(len(match)))
            for const in match:
                self.checks.append(const+" in "+item)
        elif "data" in original:
            data_type, match = original
            self.checks.append("isinstance("+item+", "+data_type+")")
            for x in range(0, len(match)):
                self.match(match[x], item+"["+str(x)+"]")
        elif "paren" in original:
            (match,) = original
            self.match(match, item)
        elif "assign" in original:
            setvar, match = original
            if setvar in self.names:
                self.checks.append(self.names[setvar]+" == "+item)
            else:
                self.defs.append(setvar+" = "+item)
                if setvar != wildcard:
                    self.names[setvar] = item
            self.match(match, item)
        elif "and" in original:
            for match in original:
                self.match(match, item)
        elif "or" in original:
            for x in range(1, len(original)):
                self.duplicate().match(original[x], item)
            self.match(original[0], item)
        else:
            raise CoconutException("invalid inner match tokens: "+repr(original))

    def out(self):
        out = ""
        closes = 0
        for checks, defs in self.checkdefs:
            if checks:
                out += "if (" + ") and (".join(checks) + "):" + linebreak + openstr
                closes += 1
            if defs:
                out += linebreak.join(defs) + linebreak
        out += self.checkvar + " = True" + linebreak
        out += closestr * closes
        for other in self.others:
            out += other.out()
        return out

def match_proc(tokens):
    """Processes match blocks."""
    if len(tokens) == 3:
        matches, item, stmts = tokens
        cond = None
    elif len(tokens) == 4:
        matches, item, cond, stmts = tokens
    else:
        raise CoconutException("invalid top-level match tokens: "+repr(tokens))
    matching = matcher(match_check_var)
    matching.match(matches, match_to_var)
    if cond:
        matching.increment(True)
        matching.add_check(cond)
    out = match_check_var + " = False" + linebreak
    out += match_to_var + " = " + item + linebreak
    out += matching.out()
    out += "if "+match_check_var+":" + linebreak + openstr + "".join(stmts) + closestr
    return out

def case_to_match(tokens, item):
    """Converts case tokens to match tokens."""
    if len(tokens) == 2:
        matches, stmts = tokens
        return matches, item, stmts
    elif len(tokens) == 3:
        matches, cond, stmts = tokens
        return matches, item, cond, stmts
    else:
        raise CoconutException("invalid case match tokens: "+repr(tokens))

def case_proc(tokens):
    """Processes case blocks."""
    if len(tokens) == 2:
        item, cases = tokens
        default = None
    elif len(tokens) == 3:
        item, cases, default = tokens
    else:
        raise CoconutException("invalid top-level case tokens: "+repr(tokens))
    out = match_proc(case_to_match(cases[0], item))
    for case in cases[1:]:
        out += "if not "+match_check_var+":" + linebreak + openstr + match_proc(case_to_match(case, item)) + closestr
    if default is not None:
        out += "if not "+match_check_var+default
    return out

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PARSER:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class processor(object):
    """The Coconut processor."""
    TRACER = tracer()
    trace = TRACER.bind
    debug = TRACER.debug

    def __init__(self, strict=False):
        """Creates a new processor."""
        self.strict = strict
        self.string_ref <<= self.trace(attach(self.string_marker, self.string_repl), "string_ref")
        self.moduledoc <<= self.trace(attach(self.string_marker + self.newline, self.set_docstring), "moduledoc")
        self.comment <<= self.trace(attach(self.comment_marker, self.comment_repl), "comment")
        self.passthrough <<= self.trace(attach(self.passthrough_marker, self.passthrough_repl), "passthrough")
        self.passthrough_block <<= self.trace(attach(self.passthrough_block_marker, self.passthrough_repl), "passthrough_block")
        self.classic_lambdef_ref <<= attach(self.classic_lambdef, self.lambda_check)
        self.classic_lambdef_nocond_ref <<= attach(self.classic_lambdef_nocond, self.lambda_check)
        self.setup()
        self.clean()

    def setup(self):
        """Initializes the processor."""
        self.preprocs = [self.prepare, self.str_proc, self.passthrough_proc, self.ind_proc]
        self.postprocs = [self.reind_proc, self.header_proc]

    def clean(self):
        """Resets references."""
        self.indchar = None
        self.refs = []
        self.match_check_index = 0
        self.match_to_index = 0
        self.match_iter_index = 0
        self.docstring = ""

    def wrap_str(self, text, strchar, multiline):
        """Wraps a string."""
        self.refs.append((text, strchar, multiline))
        return '"'+str(len(self.refs)-1)+'"'

    def wrap_passthrough(self, text, multiline):
        """Wraps a passthrough."""
        if not multiline:
            text = text.lstrip()
        fulltext = ""
        found = None
        for c in text:
            if found is not None:
                if c == '"':
                    fulltext += self.string_repl([found])
                    found = None
                else:
                    found += c
            elif c == '"':
                found = ""
            else:
                fulltext += c
        self.refs.append(fulltext)
        if multiline:
            out = "\\"
        else:
            out = "\\\\"
        out += str(len(self.refs)-1)
        if not multiline:
            out += linebreak
        return out

    def wrap_comment(self, text):
        """Wraps a comment."""
        self.refs.append(text)
        return "#"+str(len(self.refs)-1)

    def prepare(self, inputstring, strip=False, **kwargs):
        """Prepares a string for processing."""
        if strip:
            return inputstring.strip()
        else:
            return inputstring

    def str_proc(self, inputstring, **kwargs):
        """Processes strings."""
        out = []
        found = None
        hold = None
        _comment = 0
        _char = 0
        _start = 1
        _store = 2
        x = 0
        while x <= len(inputstring):
            if x == len(inputstring):
                c = linebreak
            else:
                c = inputstring[x]
            if hold is not None:
                if len(hold) == 1:
                    if c in endline:
                        out.append(self.wrap_comment(hold[_comment])+c)
                        hold = None
                    else:
                        hold[_comment] += c
                elif hold[_store] is not None:
                    if c == escape:
                        hold[_char] += hold[_store]+c
                        hold[_store] = None
                    elif c == hold[_start][0]:
                        hold[_store] += c
                    elif len(hold[_store]) > len(hold[_start]):
                        raise CoconutSyntaxError("invalid number of string closes", inputstring, x)
                    elif hold[_store] == hold[_start]:
                        out.append(self.wrap_str(hold[_char], hold[_start][0], True))
                        hold = None
                        x -= 1
                    else:
                        hold[_char] += hold[_store]+c
                        hold[_store] = None
                elif hold[_char].endswith(escape) and not hold[_char].endswith(escape*2):
                    hold[_char] += c
                elif c == hold[_start]:
                    out.append(self.wrap_str(hold[_char], hold[_start], False))
                    hold = None
                elif c == hold[_start][0]:
                    hold[_store] = c
                elif len(hold[_start]) == 1 and c in endline:
                    raise CoconutSyntaxError("linebreak in non-multiline string", inputstring, x)
                else:
                    hold[_char] += c
            elif found is not None:
                if c == found[0]:
                    found += c
                elif len(found) == 1:
                    if c in endline:
                        raise CoconutSyntaxError("linebreak in non-multiline string", inputstring, x)
                    else:
                        hold = [c, found, None]
                        found = None
                elif len(found) == 2:
                    out.append(self.wrap_str("", found[0], False))
                    found = None
                    x -= 1
                elif len(found) == 3:
                    hold = [c, found, None]
                    found = None
                else:
                    raise CoconutSyntaxError("invalid number of string starts", inputstring, x)
            elif c in startcomment:
                hold = [""]
            elif c in holds:
                found = c
            else:
                out.append(c)
            x += 1
        if hold is not None or found is not None:
            raise CoconutSyntaxError("unclosed string", inputstring, x)
        else:
            return "".join(out)

    def passthrough_proc(self, inputstring, **kwargs):
        """Processes python passthroughs."""
        out = []
        found = None
        hold = None
        count = None
        multiline = None
        for x in range(0, len(inputstring)):
            c = inputstring[x]
            if hold is not None:
                count += self.change(c)
                if count >= 0 and c == hold:
                    out.append(self.wrap_passthrough(found, multiline))
                    found = None
                    hold = None
                    count = None
                    multiline = None
                else:
                    found += c
            elif found:
                if c == escape:
                    found = ""
                    hold = linebreak
                    count = 0
                    multiline = False
                elif c == "(":
                    found = ""
                    hold = ")"
                    count = -1
                    multiline = True
                else:
                    out.append(escape + c)
                    found = None
            elif c == escape:
                found = True
            else:
                out.append(c)
        if hold is not None or found is not None:
            raise CoconutSyntaxError("unclosed passthrough", inputstring, x)
        else:
            return "".join(out)

    def leading(self, inputstring):
        """Counts leading whitespace."""
        count = 0
        for x in range(0, len(inputstring)):
            if inputstring[x] == " ":
                if self.indchar is None:
                    self.indchar = " "
                count += 1
            elif inputstring[x] == "\t":
                if self.indchar is None:
                    self.indchar = "\t"
                count += tablen - x % tablen
            else:
                break
            if self.strict and self.indchar != inputstring[x]:
                raise CoconutStyleError("found mixing of tabs and spaces", inputstring, x)
        return count

    def change(self, inputstring):
        """Determines the parenthetical change of level."""
        count = 0
        for c in inputstring:
            if c in downs:
                count -= 1
            elif c in ups:
                count += 1
        return count

    def ind_proc(self, inputstring, **kwargs):
        """Processes indentation."""
        lines = inputstring.splitlines()
        new = []
        levels = []
        count = 0
        current = None
        for line in lines:
            if line and line[-1] in white:
                if self.strict:
                    raise CoconutStyleError("found trailing whitespace", line)
                else:
                    line = line.rstrip()
            if new:
                last = new[-1].split(startcomment, 1)[0].rstrip()
            else:
                last = None
            if not line or line.lstrip().startswith(startcomment):
                if count >= 0:
                    new.append(line)
            elif last is not None and last.endswith("\\"):
                if self.strict:
                    raise CoconutStyleError("found backslash continuation", last)
                else:
                    new[-1] = last[:-1]+" "+line
            elif count < 0:
                new[-1] = last+" "+line
            else:
                check = self.leading(line)
                if current is None:
                    if check:
                        raise CoconutSyntaxError("illegal initial indent", line)
                    else:
                        current = 0
                elif check > current:
                    levels.append(current)
                    current = check
                    line = openstr+line
                elif check in levels:
                    point = levels.index(check)+1
                    line = closestr*(len(levels[point:])+1)+line
                    levels = levels[:point]
                    current = levels.pop()
                elif current != check:
                    raise CoconutSyntaxError("illegal dedent to unused indentation level", line)
                new.append(line)
            count += self.change(line)
        if new:
            last = new[-1].split(startcomment, 1)[0].rstrip()
            if last.endswith("\\"):
                raise CoconutSyntaxError("illegal final backslash continuation", last)
            if count != 0:
                raise CoconutSyntaxError("unclosed parenthetical", new[-1])
        new.append(closestr*len(levels))
        return linebreak.join(new)

    def reindent(self, inputstring):
        """Reconverts indent tokens into indentation."""
        out = []
        level = 0
        hold = None
        _char = 0
        _escape = 1
        for line in inputstring.splitlines():
            if hold is None and not line.startswith(startcomment):
                while line.startswith(openstr) or line.startswith(closestr):
                    if line[0] == openstr:
                        level += 1
                    elif line[0] == closestr:
                        level -= 1
                    line = line[1:]
                line = " "*tablen*level + line
            for c in line:
                if hold:
                    if c == escape:
                        hold[_escape] = not hold[_escape]
                    elif hold[_escape]:
                        hold[_escape] = False
                    elif c == hold[_char]:
                        hold = None
                elif c in holds:
                    hold = [c, False]
            if hold is None:
                line = line.rstrip()
            out.append(line)
        return linebreak.join(out)

    def indebug(self):
        """Checks whether debug mode is active."""
        return self.TRACER.on

    def todebug(self, tag, code):
        """If debugging, prints a debug message."""
        if self.indebug():
            self.TRACER.show("["+str(tag)+"] "+repr(code))

    def pre(self, inputstring, **kwargs):
        """Performs pre-processing."""
        out = str(inputstring)
        for proc in self.preprocs:
            out = proc(out, **kwargs)
            self.todebug(proc.__name__, out)
        return out

    def reind_proc(self, inputstring, strip=True, **kwargs):
        """Reformats indentation."""
        out = inputstring
        if strip:
            out = out.strip()
        out = self.reindent(out)
        if strip:
            out = out.strip()
        out += linebreak
        return out

    def header_proc(self, inputstring, header="file", initial="initial", **kwargs):
        """Adds the header."""
        return headers(initial) + self.docstring + headers(header) + inputstring

    def post(self, tokens, **kwargs):
        """Performs post-processing."""
        if len(tokens) == 1:
            out = tokens[0]
            for proc in self.postprocs:
                out = proc(out, **kwargs)
                self.todebug(proc.__name__, out)
            return out
        else:
            raise CoconutException("multiple tokens leftover: "+repr(tokens))

    def autopep8(self, arglist=[]):
        """Enables autopep8 integration."""
        import autopep8
        args = autopep8.parse_args([""]+arglist)
        def pep8_fixer(code, **kwargs):
            """Automatic PEP8 fixer."""
            return autopep8.fix_code(code, options=args)
        self.postprocs.append(pep8_fixer)

    def string_repl(self, tokens):
        """Replaces string references."""
        if len(tokens) == 1:
            ref = self.refs[int(tokens[0])]
            if isinstance(ref, tuple):
                string, strchar, multiline = ref
                if multiline:
                    string = strchar*3+string+strchar*3
                else:
                    string = strchar+string+strchar
                return string
            else:
                raise CoconutException("string marker points to comment/passthrough")
        else:
            raise CoconutException("invalid string marker: "+repr(tokens))

    def set_docstring(self, tokens):
        """Sets the docstring."""
        if len(tokens) == 2:
            self.docstring = self.string_repl([tokens[0]])
            return tokens[1]
        else:
            raise CoconutException("invalid docstring tokens: "+repr(tokens))

    def comment_repl(self, tokens):
        """Replaces comment references."""
        if len(tokens) == 1:
            ref = self.refs[int(tokens[0])]
            if isinstance(ref, tuple):
                raise CoconutException("comment marker points to string")
            else:
                return "#"+ref
        else:
            raise CoconutException("invalid comment marker: "+repr(tokens))

    def passthrough_repl(self, tokens):
        """Replaces passthrough references."""
        if len(tokens) == 1:
            ref = self.refs[int(tokens[0])]
            if isinstance(ref, tuple):
                raise CoconutException("passthrough marker points to string")
            else:
                return ref
        else:
            raise CoconutException("invalid passthrough marker: "+repr(tokens))

    def lambda_check(self, tokens):
        """Checks for Python-style lambdas."""
        if len(tokens) != 1:
            raise CoconutException("invalid Python-style lambda tokens: "+repr(tokens))
        elif self.strict:
            raise CoconutStyleError("found Python-style lambda", tokens[0])
        else:
            return tokens[0]

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# GRAMMAR:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    comma = Literal(",")
    dot = ~Literal("..")+Literal(".")
    dubstar = Literal("**")
    star = ~dubstar+Literal("*")
    lparen = Literal("(")
    rparen = Literal(")")
    at = Literal("@")
    arrow = fixto(Literal("->") | Literal("\u2192"), "->")
    heavy_arrow = fixto(Literal("|>=") | Literal("\u21d2"), "|>=")
    dubcolon = Literal("::")
    colon = fixto(~dubcolon+Literal(":"), ":")
    semicolon = Literal(";")
    equals = Literal("=")
    lbrack = Literal("[")
    rbrack = Literal("]")
    lbrace = Literal("{")
    rbrace = Literal("}")
    plus = Literal("+")
    minus = Literal("-")
    bang = fixto(Literal("!") | Literal("\xac"), "!")
    slash = Literal("/")
    dubslash = Literal("//")
    pipeline = fixto(Literal("|>") | Literal("\u21a6"), "|>")
    amp = fixto(Literal("&") | Literal("\u2227") | Literal("\u2229"), "&")
    caret = fixto(Literal("^") | Literal("\u22bb") | Literal("\u2295"), "^")
    bar = fixto(Literal("|") | Literal("\u2228") | Literal("\u222a"), "|")
    percent = Literal("%")
    dotdot = ~Literal("...")+Literal("..")
    dollar = Literal("$")
    ellipses = fixto(Literal("...") | Literal("\u2026"), "...")
    lshift = fixto(Literal("<<") | Literal("\xab"), "<<")
    rshift = fixto(Literal(">>") | Literal("\xbb"), ">>")
    tilde = fixto(Literal("~") | Literal("\xac"), "~")
    underscore = Literal("_")
    pound = Literal("#")
    backtick = Literal("`")
    backslash = Literal("\\")
    dubbackslash = Literal("\\\\")

    mul_star = fixto(star | Literal("\u22c5"), "*")
    exp_dubstar = fixto(dubstar | Literal("\u2191"), "**")
    neg_minus = fixto(minus | Literal("\u207b"), "-")
    sub_minus = fixto(minus | Literal("\u2212"), "-")
    div_slash = fixto((slash | Literal("\xf7"))+~slash, "/")
    div_dubslash = fixto(dubslash | Combine(Literal("\xf7")+slash), "//")
    matrix_at = at | Literal("\xd7")

    name = (
        ~Keyword("and")
        + ~Keyword("as")
        + ~Keyword("assert")
        + ~Keyword("break")
        + ~Keyword("class")
        + ~Keyword("continue")
        + ~Keyword("def")
        + ~Keyword("del")
        + ~Keyword("elif")
        + ~Keyword("else")
        + ~Keyword("except")
        + ~Keyword("finally")
        + ~Keyword("for")
        + ~Keyword("from")
        + ~Keyword("global")
        + ~Keyword("if")
        + ~Keyword("import")
        + ~Keyword("in")
        + ~Keyword("is")
        + ~Keyword("lambda")
        + ~Keyword("nonlocal")
        + ~Keyword("not")
        + ~Keyword("or")
        + ~Keyword("pass")
        + ~Keyword("raise")
        + ~Keyword("return")
        + ~Keyword("try")
        + ~Keyword("while")
        + ~Keyword("with")
        + ~Keyword("yield")
        + Regex("(?![0-9])\\w+")
        )
    for k in const_vars + reserved_vars:
        name = ~Keyword(k) + name
    for k in reserved_vars:
        name |= fixto(backslash + Keyword(k), k)
    dotted_name = condense(name + ZeroOrMore(dot + name))

    integer = Word(nums)
    binint = Word("01")
    octint = Word("01234567")
    hexint = Word(hexnums)
    anyint = Word(nums, alphanums)

    basenum = Combine(integer + dot + Optional(integer) | Optional(integer) + dot + integer) | integer
    sci_e = CaselessLiteral("e")
    numitem = Combine(basenum + sci_e + integer) | basenum

    number = (attach(Combine(anyint + underscore + integer), anyint_proc)
              | Combine(CaselessLiteral("0b") + binint)
              | Combine(CaselessLiteral("0o") + octint)
              | Combine(CaselessLiteral("0x") + hexint)
              | numitem
              )

    string_ref = Forward()
    moduledoc = Forward()
    comment = Forward()
    passthrough = Forward()
    passthrough_block = Forward()

    string_marker = Combine(Literal('"').suppress() + integer + Literal('"').suppress())
    comment_marker = Combine(pound.suppress() + integer)
    passthrough_marker = Combine(backslash.suppress() + integer)
    passthrough_block_marker = Combine(dubbackslash.suppress() + integer)

    bit_b = Optional(CaselessLiteral("b"))
    raw_r = Optional(CaselessLiteral("r"))
    string = Combine((bit_b + raw_r | raw_r + bit_b) + string_ref)
    lineitem = Combine(Optional(comment) + Literal(linebreak))
    newline = condense(OneOrMore(lineitem))
    startmarker = StringStart() + condense(ZeroOrMore(lineitem) + Optional(moduledoc))
    endmarker = StringEnd()
    indent = Literal(openstr)
    dedent = Literal(closestr)

    augassign = (heavy_arrow
                 | Combine(dotdot + equals)
                 | Combine(dubcolon + equals)
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
                 )

    lt = ~Literal("<<")+Literal("<")
    gt = ~Literal(">>")+Literal(">")
    eq = Combine(equals + equals)
    le = fixto(Combine(lt + equals) | Literal("\u2264"), "<=")
    ge = fixto(Combine(gt + equals) | Literal("\u2265"), ">=")
    ne = fixto(Combine(bang + equals) | Literal("\u2260"), "!=")

    comp_op = (le | ge | ne | lt | gt | eq
               | addspace(Keyword("not") + Keyword("in"))
               | Keyword("in")
               | addspace(Keyword("is") + Keyword("not"))
               | Keyword("is")
               )

    test = Forward()
    expr = Forward()
    comp_for = Forward()

    vardef = name
    tfpdef = condense(vardef + Optional(colon + test))
    callarg = test
    default = Optional(condense(equals + test))

    argslist = Optional(itemlist(condense(dubstar + tfpdef | star + tfpdef | tfpdef + default), comma))
    varargslist = Optional(itemlist(condense(dubstar + vardef | star + vardef | vardef + default), comma))
    callargslist = Optional(itemlist(condense(dubstar + callarg | star + callarg | callarg + default), comma))

    parameters = condense(lparen + argslist + rparen)

    testlist = itemlist(test, comma)

    yield_arg = addspace(Keyword("from") + test) | testlist
    yield_expr = addspace(Keyword("yield") + Optional(yield_arg))
    star_expr = condense(star + expr)
    test_star_expr = star_expr | test
    testlist_star_expr = itemlist(test_star_expr, comma)
    testlist_comp = addspace(test_star_expr + comp_for) | testlist_star_expr
    setmaker = addspace(test + comp_for | testlist)
    dictmaker = addspace(
        condense(test + colon) + test + comp_for
        | itemlist(addspace(condense(test + colon) + test), comma)
        )

    op_atom = condense(
        lparen + (
            fixto(pipeline, "lambda *args: __coconut__.reduce(lambda x, f: f(x), args)")
            | fixto(dotdot, "lambda *args: reduce(lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs)), args)")
            | fixto(dubcolon, "__coconut__.chain")
            | fixto(dollar, "__coconut__.partial")
            | fixto(dot, "__coconut__.operator.attrgetter")
            | fixto(exp_dubstar, "__coconut__.operator.__pow__")
            | fixto(mul_star, "__coconut__.operator.__mul__")
            | fixto(div_dubslash, "__coconut__.operator.__floordiv__")
            | fixto(div_slash, "__coconut__.operator.__truediv__")
            | fixto(percent, "__coconut__.operator.__mod__")
            | fixto(plus, "__coconut__.operator.__add__")
            | fixto(sub_minus, "__coconut__.operator.__sub__")
            | fixto(neg_minus, "__coconut__.operator.__neg__")
            | fixto(amp, "__coconut__.operator.__and__")
            | fixto(caret, "__coconut__.operator.__xor__")
            | fixto(bar, "__coconut__.operator.__or__")
            | fixto(lshift, "__coconut__.operator.__lshift__")
            | fixto(rshift, "__coconut__.operator.__rshift__")
            | fixto(lt, "__coconut__.operator.__lt__")
            | fixto(gt, "__coconut__.operator.__gt__")
            | fixto(eq, "__coconut__.operator.__eq__")
            | fixto(le, "__coconut__.operator.__le__")
            | fixto(ge, "__coconut__.operator.__ge__")
            | fixto(ne, "__coconut__.operator.__ne__")
            | fixto(tilde, "__coconut__.operator.__inv__")
            | fixto(Keyword("not"), "__coconut__.operator.__not__")
            | fixto(Keyword("and"), "lambda a, b: a and b")
            | fixto(Keyword("or"), "lambda a, b: a or b")
            | fixto(Keyword("is"), "__coconut__.operator.is_")
            | fixto(Keyword("in"), "__coconut__.operator.__contains__")
        ) + rparen
        | fixto(lbrack, "(") + (
            fixto(dollar, "__coconut__.islice")
            | fixto(plus, "__coconut__.operator.__concat__")
        ) + fixto(rbrack, ")")
    )

    func_atom = name | op_atom | condense(lparen + Optional(yield_expr | testlist_comp) + rparen)
    keyword_atom = Keyword(const_vars[0])
    for x in range(1, len(const_vars)):
        keyword_atom |= Keyword(const_vars[x])
    string_atom = addspace(OneOrMore(string))
    passthrough_atom = addspace(OneOrMore(passthrough))
    set_s = fixto(CaselessLiteral("s"), "s")
    set_letter = set_s | fixto(CaselessLiteral("f"), "f")
    atom = (
        keyword_atom
        | ellipses
        | number
        | string_atom
        | passthrough_atom
        | condense(lbrack + Optional(testlist_comp) + rbrack)
        | condense(lbrace + Optional(dictmaker) + rbrace)
        | condense(fixto(lbrace, "set(") + Optional(setmaker) + fixto(rbrace, ")"))
        | attach(set_letter + lbrace.suppress() + Optional(setmaker) + rbrace.suppress(), set_proc)
        | func_atom
        )
    slicetest = Optional(test)
    sliceop = condense(colon + slicetest)
    subscript = condense(slicetest + sliceop + Optional(sliceop)) | test
    subscriptlist = itemlist(subscript, comma)
    slicetestgroup = Optional(test, default="")
    sliceopgroup = colon.suppress() + slicetestgroup
    subscriptgroup = Group(slicetestgroup + sliceopgroup + Optional(sliceopgroup) | test)
    simple_trailer = condense(lbrack + subscriptlist + rbrack) | condense(dot + name)
    trailer = (Group(condense(dollar + lparen) + callargslist + rparen.suppress())
               | condense(lparen + callargslist + rparen)
               | Group(dotdot + func_atom)
               | Group(condense(dollar + lbrack) + Optional(subscriptgroup) + rbrack.suppress())
               | simple_trailer
               )

    assignlist = Forward()
    simple_assign = condense(name + ZeroOrMore(simple_trailer))
    assign_item = condense(simple_assign | lparen + assignlist + rparen | lbrack + assignlist + rbrack)
    assignlist <<= itemlist(Optional(star) + assign_item, comma)

    atom_item = trace(attach(atom + ZeroOrMore(trailer), item_proc), "atom_item")

    factor = Forward()
    power = trace(condense(addspace(Optional(Keyword("await")) + atom_item) + Optional(exp_dubstar + factor)), "power")
    unary = plus | neg_minus | tilde

    factor <<= trace(condense(unary + factor) | power, "factor")

    mulop = mul_star | div_slash | div_dubslash | percent | matrix_at
    term = addspace(factor + ZeroOrMore(mulop + factor))
    arith = plus | sub_minus
    arith_expr = addspace(term + ZeroOrMore(arith + term))

    shift = lshift | rshift
    shift_expr = addspace(arith_expr + ZeroOrMore(shift + arith_expr))
    and_expr = addspace(shift_expr + ZeroOrMore(amp + shift_expr))
    xor_expr = addspace(and_expr + ZeroOrMore(caret + and_expr))
    or_expr = addspace(xor_expr + ZeroOrMore(bar + xor_expr))

    chain_expr = attach(or_expr + ZeroOrMore(dubcolon.suppress() + or_expr), chain_proc)

    infix_expr = Forward()
    infix_op = condense(fixto(backtick.suppress(), "(") + chain_expr + fixto(backtick.suppress(), ")"))
    infix_item = attach(Group(Optional(chain_expr)) + infix_op + Group(Optional(infix_expr)), infix_proc)
    infix_expr <<= infix_item | chain_expr

    pipe_expr = attach(infix_expr + ZeroOrMore(pipeline.suppress() + infix_expr), pipe_proc)

    expr <<= trace(pipe_expr, "expr")
    comparison = addspace(expr + ZeroOrMore(comp_op + expr))
    not_test = addspace(ZeroOrMore(Keyword("not")) + comparison)
    and_test = addspace(not_test + ZeroOrMore(Keyword("and") + not_test))
    or_test = addspace(and_test + ZeroOrMore(Keyword("or") + and_test))
    test_item = or_test
    test_nocond = Forward()
    classic_lambdef_params = parenwrap(lparen, varargslist, rparen)
    new_lambdef_params = lparen.suppress() + varargslist + rparen.suppress()

    classic_lambdef_ref = Forward()
    classic_lambdef = addspace(Keyword("lambda") + condense(classic_lambdef_params + colon) + test)
    new_lambdef = attach(new_lambdef_params + arrow.suppress() + test, lambda_proc)
    lambdef = trace(classic_lambdef_ref | new_lambdef, "lambdef")

    classic_lambdef_nocond_ref = Forward()
    classic_lambdef_nocond = addspace(Keyword("lambda") + condense(classic_lambdef_params + colon) + test_nocond)
    new_lambdef_nocond = attach(new_lambdef_params + arrow.suppress() + test_nocond, lambda_proc)
    lambdef_nocond = trace(classic_lambdef_nocond_ref | new_lambdef_nocond, "lambdef_nocond")

    test <<= lambdef | trace(addspace(test_item + Optional(Keyword("if") + test_item + Keyword("else") + test)), "test")
    test_nocond <<= lambdef_nocond | trace(test_item, "test_item")
    exprlist = itemlist(star_expr | expr, comma)

    simple_stmt = Forward()
    simple_compound_stmt = Forward()
    stmt = Forward()
    suite = Forward()
    nocolon_suite = Forward()

    argument = condense(name + equals + test) | addspace(name + Optional(comp_for))
    classlist = attach(Optional(lparen.suppress() + Optional(testlist) + rparen.suppress()), class_proc)
    classdef = condense(addspace(Keyword("class") + name) + classlist + suite)
    comp_iter = Forward()
    comp_for <<= addspace(Keyword("for") + exprlist + Keyword("in") + test_item + Optional(comp_iter))
    comp_if = addspace(Keyword("if") + test_nocond + Optional(comp_iter))
    comp_iter <<= comp_for | comp_if

    pass_stmt = Keyword("pass")
    break_stmt = Keyword("break")
    continue_stmt = Keyword("continue")
    return_stmt = addspace(Keyword("return") + Optional(testlist))
    yield_stmt = yield_expr
    raise_stmt = addspace(Keyword("raise") + Optional(test + Optional(Keyword("from") + test)))
    flow_stmt = break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt

    dotted_as_name = addspace(dotted_name + Optional(Keyword("as") + name))
    import_as_name = addspace(name + Optional(Keyword("as") + name))
    import_as_names = itemlist(import_as_name, comma)
    dotted_as_names = itemlist(dotted_as_name, comma)
    import_name = addspace(Keyword("import") + parenwrap(lparen, dotted_as_names, rparen))
    import_from = addspace(Keyword("from") + condense(ZeroOrMore(dot) + dotted_name | OneOrMore(dot))
                   + Keyword("import") + (star | parenwrap(lparen, import_as_names, rparen)))
    import_stmt = import_from | import_name

    namelist = parenwrap(lparen, itemlist(name, comma), rparen)
    global_stmt = addspace(Keyword("global") + namelist)
    nonlocal_stmt = addspace(Keyword("nonlocal") + namelist)
    del_stmt = addspace(Keyword("del") + itemlist(simple_assign, comma))
    with_item = addspace(test + Optional(Keyword("as") + name))

    match = Forward()
    matchlist_list = Group(Optional(match + ZeroOrMore(comma.suppress() + match) + Optional(comma.suppress())))
    matchlist_tuple = Group(Optional(match + OneOrMore(comma.suppress() + match) + Optional(comma.suppress()) | match + comma.suppress()))
    match_const = (
        keyword_atom
        | number
        | string_atom
        | condense(equals.suppress() + simple_assign)
        )
    matchlist_set = Group(Optional(match_const + ZeroOrMore(comma.suppress() + match_const) + Optional(comma.suppress())))
    match_pair = Group(match_const + colon.suppress() + match)
    matchlist_dict = Group(Optional(match_pair + ZeroOrMore(comma.suppress() + match_pair) + Optional(comma.suppress())))
    base_match = Group(
        (match_const)("const")
        | (lparen + matchlist_tuple + rparen.suppress() + Optional((plus | dubcolon) + name))("series")
        | (lparen.suppress() + match + rparen.suppress())("paren")
        | (lbrack + matchlist_list + rbrack.suppress() + Optional((plus | dubcolon) + name))("series")
        | (lbrace.suppress() + matchlist_dict + rbrace.suppress())("dict")
        | (Optional(set_s.suppress()) + lbrace.suppress() + matchlist_set + rbrace.suppress())("set")
        | (name + equals.suppress() + match)("assign")
        | (name + lparen.suppress() + matchlist_list + rparen.suppress())("data")
        | name("var")
        )
    matchlist_name = name | lparen.suppress() + itemlist(name, comma) + rparen.suppress()
    matchlist_is = base_match + Keyword("is").suppress() + matchlist_name
    is_match = Group(matchlist_is("is")) | base_match
    matchlist_and = is_match + OneOrMore(Keyword("and").suppress() + is_match)
    and_match = Group(matchlist_and("and")) | is_match
    matchlist_or = and_match + OneOrMore(Keyword("or").suppress() + and_match)
    or_match = Group(matchlist_or("or")) | and_match
    match <<= trace(or_match, "match")

    else_suite = condense(suite | colon + trace(attach(simple_compound_stmt, else_proc), "else_suite"))
    else_stmt = condense(Keyword("else") + else_suite)

    match_suite = colon.suppress() + Group((newline.suppress() + indent.suppress() + OneOrMore(stmt) + dedent.suppress()) | simple_stmt)
    full_match = trace(attach(
        Keyword("match").suppress() + match + Keyword("in").suppress() + test + Optional(Keyword("if").suppress() + test) + match_suite
        , match_proc), "full_match")
    match_stmt = condense(full_match + Optional(else_stmt))

    case_match = trace(Group(
        Keyword("match").suppress() + match + Optional(Keyword("if").suppress() + test) + match_suite
        ), "case_match")
    case_stmt = attach(
        Keyword("case").suppress() + test + colon.suppress() + newline.suppress()
        + indent.suppress() + Group(OneOrMore(case_match))
        + dedent.suppress() + Optional(Keyword("else").suppress() + else_suite)
        , case_proc)

    assert_stmt = addspace(Keyword("assert") + testlist)
    if_stmt = condense(addspace(Keyword("if") + condense(test + suite))
                       + ZeroOrMore(addspace(Keyword("elif") + condense(test + suite)))
                       + Optional(else_stmt)
                       )
    while_stmt = addspace(Keyword("while") + condense(test + suite + Optional(else_stmt)))
    for_stmt = addspace(Keyword("for") + exprlist + Keyword("in") + condense(testlist + suite + Optional(else_stmt)))
    except_clause = addspace(Keyword("except") + test + Optional(Keyword("as") + name))
    try_stmt = condense(Keyword("try") + suite + (
        Keyword("finally") + suite
        | (
            OneOrMore(except_clause + suite) + Optional(Keyword("except") + suite)
            | Keyword("except") + suite
            ) + Optional(else_stmt) + Optional(Keyword("finally") + suite)
        ))
    with_stmt = addspace(Keyword("with") + condense(itemlist(with_item, comma) + suite))

    name_funcdef = condense(name + parameters)
    op_funcdef_arg = condense(parenwrap(lparen.suppress(), tfpdef + Optional(default), rparen.suppress()))
    op_funcdef_name = backtick.suppress() + name + backtick.suppress()
    op_funcdef = attach(Group(Optional(op_funcdef_arg)) + op_funcdef_name + Group(Optional(op_funcdef_arg)), infix_proc)
    base_funcdef = addspace((op_funcdef | name_funcdef) + Optional(arrow + test))
    funcdef = addspace(Keyword("def") + condense(base_funcdef + suite))
    async_funcdef = addspace(Keyword("async") + funcdef)
    async_stmt = async_funcdef | addspace(Keyword("async") + (with_stmt | for_stmt))

    data_args = Optional(lparen.suppress() + Optional(itemlist(~underscore + name, comma)) + rparen.suppress())
    datadef = condense(attach(Keyword("data").suppress() + name + data_args, data_proc) + suite)

    decorators = attach(OneOrMore(at.suppress() + test + newline.suppress()), decorator_proc)
    decorated = condense(decorators + (classdef | funcdef | async_funcdef | datadef))

    passthrough_stmt = condense(passthrough_block + (nocolon_suite | newline))

    simple_compound_stmt <<= if_stmt | try_stmt | case_stmt | match_stmt | passthrough_stmt
    compound_stmt = trace(simple_compound_stmt | with_stmt | while_stmt | for_stmt | funcdef | classdef | datadef | decorated | async_stmt, "compound_stmt")

    expr_stmt = trace(addspace(
                      attach(simple_assign + augassign + (yield_expr | testlist), assign_proc)
                      | attach(base_funcdef + equals.suppress() + (yield_expr | testlist_star_expr), func_proc)
                      | ZeroOrMore(assignlist + equals) + (yield_expr | testlist_star_expr)
                      ), "expr_stmt")

    keyword_stmt = del_stmt | pass_stmt | flow_stmt | import_stmt | global_stmt | nonlocal_stmt | assert_stmt
    small_stmt = trace(keyword_stmt ^ expr_stmt, "small_stmt")
    simple_stmt <<= trace(condense(itemlist(small_stmt, semicolon) + newline), "simple_stmt")
    stmt <<= trace(compound_stmt | simple_stmt, "stmt")
    nocolon_suite <<= condense(newline + indent + OneOrMore(stmt) + dedent)
    suite <<= trace(condense(colon + nocolon_suite) | addspace(colon + simple_stmt), "suite")
    line = trace(newline | stmt, "line")

    single_input = trace(Optional(line), "single_input")
    file_input = trace(condense(ZeroOrMore(line)), "file_input")
    eval_input = trace(condense(testlist + Optional(newline)), "eval_input")

    single_parser = condense(startmarker + single_input + endmarker)
    file_parser = condense(startmarker + file_input + endmarker)
    eval_parser = condense(startmarker + eval_input + endmarker)

    def parse_single(self, inputstring):
        """Parses console input."""
        out = self.post(self.single_parser.parseString(self.pre(inputstring)), header="none", initial="none")
        self.clean()
        return out

    def parse_file(self, inputstring):
        """Parses file input."""
        out = self.post(self.file_parser.parseString(self.pre(inputstring)), header="file")
        self.clean()
        return out

    def parse_module(self, inputstring):
        """Parses module input."""
        out = self.post(self.file_parser.parseString(self.pre(inputstring)), header="module")
        self.clean()
        return out

    def parse_block(self, inputstring):
        """Parses block text."""
        out = self.post(self.file_parser.parseString(self.pre(inputstring)), header="none", initial="none")
        self.clean()
        return out

    def parse_eval(self, inputstring):
        """Parses eval input."""
        out = self.post(self.eval_parser.parseString(self.pre(inputstring, strip=True)), header="none", initial="none")
        self.clean()
        return out

    def parse_debug(self, inputstring):
        """Parses debug input."""
        out = self.post(self.file_parser.parseString(self.pre(inputstring, strip=True)), header="none", initial="none")
        self.clean()
        return out
