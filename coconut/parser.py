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

from .util import *
from pyparsing import *

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# HEADERS:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

headers = {

"none": '',

"top":

r'''#!/usr/bin/env python

# Coconut Header: --------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division
try:
    from future_builtins import *
except ImportError:
    pass
''',

"import":

r'''
import sys as _coconut_sys
import os.path as _coconut_os_path
_coconut_sys.path.append(_coconut_os_path.dirname(_coconut_os_path.abspath(__file__)))
import __coconut__
''',

"class":

r'''
class __coconut__(object):
    """Built-In Coconut Functions."""
    import operator
    import functools
    partial = functools.partial
    reduce = functools.reduce
    import itertools
    chain = itertools.chain
    slice = itertools.islice
    takewhile = itertools.takewhile
    import collections
    data = staticmethod(collections.namedtuple)
    @staticmethod
    def compose(f, g):
        """Composing (f..g)."""
        def _composed(*args, **kwargs):
            """Function Composition Wrapper."""
            return f(g(*args, **kwargs))
        return _composed
    @staticmethod
    def infix(a, func, b):
        """Infix Calling (5 `mod` 6)."""
        return func(a, b)
    @staticmethod
    def pipe(*args):
        """Pipelining (x |> func)."""
        out = args[0]
        for func in args[1:]:
            out = func(out)
        return out
    @staticmethod
    def recursive(func):
        """Tail Call Optimizer."""
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
''',

"body":

r'''
"""Built-In Coconut Functions."""

import operator

import functools
partial = functools.partial
reduce = functools.reduce

import itertools
chain = itertools.chain
slice = itertools.islice
takewhile = itertools.takewhile

import collections
data = collections.namedtuple

def compose(f, g):
    """Composing (f..g)."""
    def _composed(*args, **kwargs):
        """Function Composition Wrapper."""
        return f(g(*args, **kwargs))
    return _composed

def infix(a, func, b):
    """Infix Calling (5 `mod` 6)."""
    return func(a, b)

def pipe(*args):
    """Pipelining (x |> func)."""
    out = args[0]
    for func in args[1:]:
        out = func(out)
    return out

def recursive(func):
    """Tail Call Optimizer."""
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
''',

"funcs":

r'''
reduce = __coconut__.reduce
takewhile = __coconut__.takewhile
recursive = __coconut__.recursive
''',

"bottom":

r'''
# Compiled Coconut: ------------------------------------------------------------

'''
}

headers["package"] = headers["top"] + headers["body"]
headers["code"] = headers["top"] + headers["class"] + headers["funcs"]
headers["file"] = headers["code"] + headers["bottom"]
headers["module"] = headers["top"] + headers["import"] + headers["funcs"] + headers["bottom"]

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CoconutException(ParseFatalException):
    """Base Coconut Exception."""
    def __init__(self, value):
        """Creates The Coconut Exception."""
        self.value = value
    def __repr__(self):
        """Displays The Coconut Exception."""
        return self.value
    def __str__(self):
        """Wraps repr."""
        return repr(self)

def attach(item, action):
    """Attaches A Parse Action To An Item."""
    return item.copy().addParseAction(action)

def fixto(item, output):
    """Forces An Item To Result In A Specific Output."""
    return attach(item, replaceWith(output))

def addspace(item):
    """Condenses And Adds Space To The Tokenized Output."""
    def callback(tokens):
        """Callback Function Constructed By addspace."""
        return " ".join(tokens)
    return attach(item, callback)

def condense(item):
    """Condenses The Tokenized Output."""
    def callback(tokens):
        """Callback Function Constructed By condense."""
        return "".join(tokens)
    return attach(item, callback)

def parenwrap(lparen, item, rparen):
    """Wraps An Item In Optional Parentheses."""
    return condense(lparen.suppress() + item + rparen.suppress() | item)

class tracer(object):
    """Debug Tracer."""
    show = print

    def __init__(self, on=False):
        """Creates The Tracer."""
        self.debug(on)

    def debug(self, on=True):
        """Changes The Tracer's State."""
        self.on = on

    def trace(self, original, location, tokens, message=None):
        """Tracer Parse Action."""
        if self.on:
            original = str(original)
            location = int(location)
            out = ""
            if message is not None:
                out += "["+message+"] "
            if len(tokens) == 1:
                out += repr(tokens[0])
            else:
                out += str(tokens)
            out += " (line "+str(lineno(location, original))+", col "+str(col(location, original))+")"
            self.show(out)
        return tokens

    def bind(self, item, message=None):
        """Traces A Parse Element."""
        if message is None:
            callback = self.trace
        else:
            def callback(original, location, tokens):
                """Callback Function Constructed By tracer."""
                return self.trace(original, location, tokens, message)
        return attach(item, callback)

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PROCESSORS:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def anyint_proc(tokens):
    """Replaces Underscored Integers."""
    if len(tokens) == 1:
        item, base = tokens[0].split("_")
        return 'int("'+item+'", '+base+")"
    else:
        raise CoconutException("invalid anyint token")

def list_proc(tokens):
    """Properly Formats Lists."""
    out = []
    for x in range(0, len(tokens)):
        if x%2 == 0:
            out.append(tokens[x])
        else:
            out[-1] += tokens[x]
    return " ".join(out)

def itemlist(item, sep):
    """Creates A List Containing An Item."""
    return attach(item + ZeroOrMore(sep + item) + Optional(sep).suppress(), list_proc)

def item_proc(tokens):
    """Processes Items."""
    out = tokens.pop(0)
    for trailer in tokens:
        if isinstance(trailer, str):
            out += trailer
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
                            elif x == 1:
                                arg = "len("+out+")"
                            elif x == 3:
                                arg = "1"
                        args.append(arg)
                    out = "__coconut__.slice("+out
                    if len(args) == 1:
                        out += ", "+args[0]+", ("+args[0]+")+1)"
                        out = "next("+out+")"
                    else:
                        for arg in args:
                            out += ", "+arg
                        out += ")"
                else:
                    raise CoconutException("invalid isplit args: "+repr(trailer[1]))
            elif trailer[0] == "..":
                out = "__coconut__.compose("+out+", "+trailer[1]+")"
            else:
                raise CoconutException("invalid special trailer: "+repr(trailer[0]))
        else:
            raise CoconutException("invalid trailer tokens: "+repr(trailer))
    return out

def chain_proc(tokens):
    """Processes Chain Calls."""
    if len(tokens) == 1:
        return tokens[0]
    else:
        return "__coconut__.chain("+", ".join(tokens)+")"

def infix_proc(tokens):
    """Processes Infix Calls."""
    if len(tokens) == 1:
        return tokens[0]
    else:
        return "__coconut__.infix("+infix_proc(tokens[:-2])+", "+tokens[-2]+", "+tokens[-1]+")"

def pipe_proc(tokens):
    """Processes Pipe Calls."""
    if len(tokens) == 1:
        return tokens[0]
    else:
        return "__coconut__.pipe("+", ".join(tokens)+")"

def lambda_proc(tokens):
    """Processes Lambda Calls."""
    if len(tokens) == 2:
        return "lambda "+tokens[0]+": "+tokens[1]
    else:
        raise CoconutException("invalid lambda tokens: "+repr(tokens))

def assign_proc(tokens):
    """Processes Assignments."""
    if len(tokens) == 3:
        if tokens[1] == "|>=":
            return tokens[0]+" = __coconut__.pipe("+tokens[0]+", ("+tokens[2]+"))"
        elif tokens[1] == "..=":
            return tokens[0]+" = __coconut__.compose("+tokens[0]+", ("+tokens[2]+"))"
        elif tokens[1] == "::=":
            return tokens[0]+" = __coconut__.chain("+tokens[0]+", ("+tokens[2]+"))"
        else:
            return tokens
    else:
        raise CoconutException("invalid assignment tokens: "+repr(tokens))

def func_proc(tokens):
    """Processes Mathematical Function Definitons."""
    if len(tokens) == 2:
        return "def "+tokens[0]+": return "+tokens[1]
    else:
        raise CoconutException("invalid mathematical function definition tokens: "+repr(tokens))

def data_proc(tokens):
    """Processes Data Blocks."""
    if len(tokens) == 2:
        return "class "+tokens[0]+"(__coconut__.data('"+tokens[0]+"', '"+tokens[1]+"'))"
    else:
        raise CoconutException("invalid data tokens: "+repr(tokens))

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PARSER:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class processor(object):
    """The Coconut Processor."""
    TRACER = tracer()
    trace = TRACER.bind
    debug = TRACER.debug
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
    verbosity = 20

    def __init__(self, strict=False):
        """Creates A New Processor."""
        self.strict = strict
        self.string_ref <<= self.trace(attach(self.string_marker, self.string_repl), "string_ref")
        self.comment <<= self.trace(attach(self.comment_marker, self.comment_repl), "comment")
        self.setup()
        self.clean()

    def setup(self):
        """Initializes The Processor."""
        self.preprocs = [self.prepare, self.strproc, self.indproc]
        self.postprocs = [self.reindproc, self.headerproc]

    def clean(self):
        """Resets References."""
        self.indchar = None
        self.refs = []

    def wrapstr(self, text, strchar, multiline):
        """Wraps A String."""
        self.refs.append((text, strchar, multiline))
        return '"'+str(len(self.refs)-1)+'"'

    def wrapcomment(self, text):
        """Wraps A Comment."""
        self.refs.append(text)
        return "#"+str(len(self.refs)-1)

    def getpart(self, iterstring, point):
        """Gets A Part Of A String For An Error Message."""
        out = ""
        i = point-self.verbosity
        while i < point+self.verbosity:
            if i >= 0 and i < len(iterstring):
                out += iterstring[i]
            i += 1
        return "..."+repr(out)+"..."

    def prepare(self, inputstring, strip=False, **kwargs):
        """Prepares A String For Processing."""
        if strip:
            return inputstring.strip()
        else:
            return inputstring

    def strproc(self, inputstring, **kwargs):
        """Processes Strings."""
        out = []
        found = None
        hold = None
        x = 0
        while x <= len(inputstring):
            if x == len(inputstring):
                c = self.linebreak
            else:
                c = inputstring[x]
            if hold is not None:
                if len(hold) == 1:
                    if c in self.endline:
                        out.append(self.wrapcomment(hold[0])+c)
                        hold = None
                    else:
                        hold[0] += c
                elif hold[2] is not None:
                    if c == self.escape:
                        hold[0] += hold[2]+c
                        hold[2] = None
                    elif c == hold[1][0]:
                        hold[2] += c
                    elif len(hold[2]) > len(hold[1]):
                        raise CoconutException("invalid number of string closes in "+self.getpart(inputstring, x))
                    elif hold[2] == hold[1]:
                        out.append(self.wrapstr(hold[0], hold[1][0], True))
                        hold = None
                        x -= 1
                    else:
                        hold[0] += hold[2]+c
                        hold[2] = None
                elif hold[0].endswith(self.escape) and not hold[0].endswith(self.escape*2):
                    hold[0] += c
                elif c == hold[1]:
                    out.append(self.wrapstr(hold[0], hold[1], False))
                    hold = None
                elif c == hold[1][0]:
                    hold[2] = c
                else:
                    hold[0] += c
            elif found is not None:
                if c == found[0]:
                    found += c
                elif len(found) == 1:
                    hold = [c, found, None]
                    found = None
                elif len(found) == 2:
                    out.append(self.wrapstr("", found[0], False))
                    found = None
                    x -= 1
                elif len(found) == 3:
                    hold = [c, found, None]
                    found = None
                else:
                    raise CoconutException("invalid number of string starts in "+self.getpart(inputstring, x))
            elif c in self.startcomment:
                hold = [""]
            elif c in self.holds:
                found = c
            else:
                out.append(c)
            x += 1
        if hold is not None or found is not None:
            raise CoconutException("unclosed string in "+self.getpart(inputstring, x))
        return "".join(out)

    def leading(self, inputstring):
        """Counts Leading Whitespace."""
        count = 0
        for c in inputstring:
            if c not in self.white:
                break
            elif self.indchar is None:
                self.indchar = c
            elif self.indchar != c:
                raise CoconutException("illegal mixing of tabs and spaces in "+repr(inputstring))
            count += 1
        return count

    def change(self, inputstring):
        """Determines The Parenthetical Change Of Level."""
        count = 0
        hold = None
        for c in inputstring:
            if hold:
                if c == self.escape:
                    hold[1] = not hold[1]
                elif hold[1]:
                    hold[1] = False
                elif c == hold[0]:
                    hold = None
            elif c in self.startcomment:
                break
            elif c in self.holds:
                hold = [c, False]
            elif c in self.downs:
                count -= 1
            elif c in self.ups:
                count += 1
        return count

    def indproc(self, inputstring, **kwargs):
        """Processes Indentation."""
        lines = inputstring.splitlines()
        new = []
        levels = []
        count = 0
        current = None
        for line in lines:
            if not line or line.lstrip().startswith(self.startcomment):
                new.append(line)
                continue
            if line[-1] in self.white:
                if self.strict:
                    raise CoconutException("[strict] found trailing whitespace in "+repr(line))
                else:
                    line = line.rstrip()
            if line.endswith("\\"):
                if self.strict:
                    raise CoconutException("[strict] found backslash continuation in "+repr(line))
                else:
                    new[-1] += " "+line[:-1]
            elif count < 0:
                new[-1] += " "+line
            else:
                check = self.leading(line)
                if current is None:
                    if check:
                        raise CoconutException("illegal initial indent in "+repr(line))
                    else:
                        current = 0
                elif check > current:
                    levels.append(current)
                    current = check
                    line = self.openstr+line
                elif check in levels:
                    point = levels.index(check)+1
                    line = self.closestr*(len(levels[point:])+1)+line
                    levels = levels[:point]
                    current = levels.pop()
                elif current != check:
                    raise CoconutException("illegal dedent to unused indentation level in "+repr(line))
                new.append(line)
            count += self.change(line)
        if count != 0:
            raise CoconutException("unclosed parenthetical in "+repr(new[-1]))
        new.append(self.closestr*len(levels))
        return self.linebreak.join(new)

    def reindent(self, inputstring):
        """Reconverts Indent Tokens Into Indentation."""
        out = []
        level = 0
        hold = None
        for line in inputstring.splitlines():
            if hold is None and not line.startswith(self.startcomment):
                while line.startswith(self.openstr) or line.startswith(self.closestr):
                    if line[0] == self.openstr:
                        level += 1
                    elif line[0] == self.closestr:
                        level -= 1
                    line = line[1:]
                line = " "*self.tablen*level + line
            for c in line:
                if hold:
                    if c == self.escape:
                        hold[1] = not hold[1]
                    elif hold[1]:
                        hold[1] = False
                    elif c == hold[0]:
                        hold = None
                elif c in self.holds:
                    hold = [c, False]
            if hold is None:
                line = line.rstrip()
            out.append(line)
        return self.linebreak.join(out)

    def pre(self, inputstring, **kwargs):
        """Performs Pre-Processing."""
        out = str(inputstring)
        for proc in self.preprocs:
            out = proc(out, **kwargs)
        return out

    def reindproc(self, inputstring, strip=True, **kwargs):
        """Reformats Indentation."""
        out = inputstring
        if strip:
            out = out.strip()
        out = self.reindent(out)
        if strip:
            out = out.strip()
        out += self.linebreak
        return out

    def headerproc(self, inputstring, header="file", **kwargs):
        """Adds The Header."""
        return headers[header]+inputstring

    def post(self, tokens, **kwargs):
        """Performs Post-Processing."""
        if len(tokens) == 1:
            out = tokens[0]
            for proc in self.postprocs:
                out = proc(out, **kwargs)
            return out
        else:
            raise CoconutException("multiple tokens leftover: "+repr(tokens))

    def autopep8(self, arglist=[]):
        """Enables autopep8 Integration."""
        import autopep8
        args = autopep8.parse_args([""]+arglist)
        def pep8_fixer(code, **kwargs):
            """Automatic PEP8 Fixer."""
            return autopep8.fix_code(code, options=args)
        self.postprocs.append(pep8_fixer)

    def string_repl(self, tokens):
        """Replaces String References."""
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
                raise CoconutException("string marker points to comment")
        else:
            raise CoconutException("invalid string marker")

    def comment_repl(self, tokens):
        """Replaces Comment References."""
        if len(tokens) == 1:
            ref = self.refs[int(tokens[0])]
            if isinstance(ref, tuple):
                raise CoconutException("comment marker points to string")
            else:
                return "#"+ref
        else:
            raise CoconutException("invalid comment marker")

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# GRAMMAR:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    ParserElement.setDefaultWhitespaceChars(white)

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
    dubslash = fixto(Literal("//") | Literal("\u20eb"), "//")
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

    mul_star = fixto(star | ~Literal("\xd7\xd7")+Literal("\xd7"), "*")
    exp_dubstar = fixto(dubstar | Literal("\xd7\xd7") | Literal("\u2191"), "**")
    neg_minus = fixto(minus | Literal("\u207b"), "-")
    sub_minus = fixto(minus | Literal("\u2212"), "-")
    div_slash = fixto((slash | Literal("\xf7"))+~slash, "/")
    div_dubslash = fixto(dubslash | Combine(Literal("\xf7")+slash), "//")

    NAME = Regex("(?![0-9])\\w+")
    dotted_name = condense(NAME + ZeroOrMore(dot + NAME))

    integer = Word(nums)
    binint = Word("01")
    octint = Word("01234567")
    hexint = Word(hexnums)
    anyint = Word(nums, alphanums)

    basenum = Combine(integer + dot + Optional(integer)) | integer
    sci_e = CaselessLiteral("e") | fixto(Literal("\u23e8"), "E")
    numitem = Combine(basenum + sci_e + integer) | basenum

    NUMBER = (attach(Combine(anyint + underscore + integer), anyint_proc)
              | Combine(CaselessLiteral("0b") + binint)
              | Combine(CaselessLiteral("0o") + octint)
              | Combine(CaselessLiteral("0x") + hexint)
              | numitem
              )

    string_ref = Forward()
    comment = Forward()

    string_marker = Combine(Literal('"').suppress() + integer + Literal('"').suppress())
    comment_marker = Combine(pound.suppress() + integer)

    bit_b = Optional(CaselessLiteral("b"))
    raw_r = Optional(CaselessLiteral("r"))
    STRING = Combine((bit_b + raw_r | raw_r + bit_b) + string_ref)
    lineitem = Combine(Optional(comment) + Literal(linebreak))
    NEWLINE = condense(OneOrMore(lineitem))
    STARTMARKER = StringStart()
    ENDMARKER = StringEnd()
    INDENT = Literal(openstr)
    DEDENT = Literal(closestr)

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

    vardef = NAME
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
    dictorsetmaker = addspace(condense(test + colon) + test + comp_for
                      ^ itemlist(condense(test + colon) + test, comma)
                      ^ test + comp_for
                      ^ testlist
                      )

    op_atom = lparen + (
        fixto(pipeline, "__coconut__.pipe")
        | fixto(dotdot, "__coconut__.compose")
        | fixto(dubcolon, "__coconut__.chain")
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
        ) + rparen

    func_atom = NAME | op_atom | condense(lparen + Optional(yield_expr | testlist_comp) + rparen)
    keyword_atom = Keyword("None") | Keyword("True") | Keyword("False")
    atom = (keyword_atom
            | ellipses
            | condense(lbrack + Optional(testlist_comp) + rbrack)
            | condense(lbrace + Optional(dictorsetmaker) + rbrace)
            | NUMBER
            | OneOrMore(STRING)
            | func_atom
            )
    slicetest = Optional(test)
    sliceop = condense(colon + slicetest)
    subscript = condense(slicetest + sliceop + Optional(sliceop)) | test
    subscriptlist = itemlist(subscript, comma)
    slicetestgroup = Optional(test, default="")
    sliceopgroup = colon.suppress() + slicetestgroup
    subscriptgroup = Group(slicetestgroup + sliceopgroup + Optional(sliceopgroup) | test)
    simple_trailer = condense(lbrack + subscriptlist + rbrack) | condense(dot + NAME)
    trailer = (Group(condense(dollar + lparen) + callargslist + rparen.suppress())
               | condense(lparen + callargslist + rparen)
               | Group(dotdot + func_atom)
               | Group(condense(dollar + lbrack) + subscriptgroup + rbrack.suppress())
               | simple_trailer
               )

    assignlist = Forward()
    assign_item = NAME + ZeroOrMore(simple_trailer) | lparen + assignlist + rparen | lbrack + assignlist + rbrack
    assignlist <<= itemlist(Optional(star) + assign_item, comma)

    atom_item = trace(attach(atom + ZeroOrMore(trailer), item_proc), "atom_item")

    factor = Forward()
    power = trace(condense(atom_item + Optional(exp_dubstar + factor)), "power")
    unary = plus | neg_minus | tilde

    factor <<= trace(condense(unary + factor) | power, "factor")

    mulop = mul_star | div_slash | div_dubslash | percent
    term = addspace(factor + ZeroOrMore(mulop + factor))
    arith = plus | sub_minus
    arith_expr = addspace(term + ZeroOrMore(arith + term))

    shift = lshift | rshift
    shift_expr = addspace(arith_expr + ZeroOrMore(shift + arith_expr))
    and_expr = addspace(shift_expr + ZeroOrMore(amp + shift_expr))
    xor_expr = addspace(and_expr + ZeroOrMore(caret + and_expr))
    or_expr = addspace(xor_expr + ZeroOrMore(bar + xor_expr))

    chain_expr = attach(or_expr + ZeroOrMore(dubcolon.suppress() + or_expr), chain_proc)

    infix_expr = attach(chain_expr + ZeroOrMore(backtick.suppress() + test + backtick.suppress() + chain_expr), infix_proc)

    pipe_expr = attach(infix_expr + ZeroOrMore(pipeline.suppress() + infix_expr), pipe_proc)

    expr <<= trace(pipe_expr, "expr")
    comparison = addspace(expr + ZeroOrMore(comp_op + expr))
    not_test = addspace(ZeroOrMore(Keyword("not")) + comparison)
    and_test = addspace(not_test + ZeroOrMore(Keyword("and") + not_test))
    or_test = addspace(and_test + ZeroOrMore(Keyword("or") + and_test))
    test_item = or_test
    test_nocond = Forward()
    lambdef_params = lparen.suppress() + varargslist + rparen.suppress()

    lambdef = trace(attach(lambdef_params + arrow.suppress() + test, lambda_proc), "lambdef")
    lambdef_nocond = trace(attach(lambdef_params + arrow.suppress() + test_nocond, lambda_proc), "lambdef_nocond")

    test <<= lambdef | trace(addspace(test_item + Optional(Keyword("if") + test_item + Keyword("else") + test)), "test")
    test_nocond <<= lambdef_nocond | trace(test_item, "test_item")
    exprlist = itemlist(star_expr | expr, comma)

    suite = Forward()

    argument = condense(NAME + equals + test) | addspace(NAME + Optional(comp_for))
    classdef = condense(addspace(Keyword("class") + NAME) + Optional(condense(lparen + Optional(testlist) + rparen)) + suite)
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

    dotted_as_name = addspace(dotted_name + Optional(Keyword("as") + NAME))
    import_as_name = addspace(NAME + Optional(Keyword("as") + NAME))
    import_as_names = itemlist(import_as_name, comma)
    dotted_as_names = itemlist(dotted_as_name, comma)
    import_name = addspace(Keyword("import") + parenwrap(lparen, dotted_as_names, rparen))
    import_from = addspace(Keyword("from") + condense(ZeroOrMore(dot) + dotted_name | OneOrMore(dot))
                   + Keyword("import") + (star | parenwrap(lparen, import_as_names, rparen)))
    import_stmt = import_from | import_name

    namelist = parenwrap(lparen, itemlist(NAME, comma), rparen)
    global_stmt = addspace(Keyword("global") + namelist)
    nonlocal_stmt = addspace(Keyword("nonlocal") + namelist)
    del_stmt = addspace(Keyword("del") + namelist)
    with_item = addspace(test + Optional(Keyword("as") + NAME))
    assert_stmt = addspace(Keyword("assert") + parenwrap(lparen, testlist, rparen))
    else_stmt = condense(Keyword("else") + suite)
    if_stmt = condense(addspace(Keyword("if") + condense(test + suite))
                       + ZeroOrMore(addspace(Keyword("elif") + condense(test + suite)))
                       + Optional(else_stmt)
                       )
    while_stmt = addspace(Keyword("while") + condense(test + suite + Optional(else_stmt)))
    for_stmt = addspace(Keyword("for") + exprlist + Keyword("in") + condense(testlist + suite + Optional(else_stmt)))
    except_clause = addspace(Keyword("except") + test + Optional(Keyword("as") + NAME))
    try_stmt = condense(Keyword("try") + suite + (
        Keyword("finally") + suite
        | (
            OneOrMore(except_clause + suite) + Optional(Keyword("except") + suite)
            | Keyword("except") + suite
            ) + Optional(else_stmt) + Optional(Keyword("finally") + suite)
        ))
    with_stmt = addspace(Keyword("with") + condense(parenwrap(lparen, itemlist(with_item, comma), rparen) + suite))

    base_funcdef = addspace(condense(NAME + parameters) + Optional(arrow + test))
    funcdef = addspace(Keyword("def") + condense(base_funcdef + suite))

    datadef = condense(attach(Keyword("data").suppress() + NAME + lparen.suppress() + itemlist(NAME, comma) + rparen.suppress(), data_proc) + suite)

    decorator = condense(at + test + NEWLINE)
    decorators = OneOrMore(decorator)
    decorated = condense(decorators + (classdef | funcdef | datadef))

    compound_stmt = trace(if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | datadef | decorated, "compound_stmt")

    expr_stmt = trace(addspace(attach(assignlist + augassign + (yield_expr | testlist), assign_proc)
                         | attach(base_funcdef + equals.suppress() + (yield_expr | testlist_star_expr), func_proc)
                         | ZeroOrMore(assignlist + equals) + (yield_expr | testlist_star_expr)
                         ), "expr_stmt")

    keyword_stmt = del_stmt | pass_stmt | flow_stmt | import_stmt | global_stmt | nonlocal_stmt | assert_stmt
    small_stmt = trace(keyword_stmt ^ expr_stmt, "small_stmt")
    simple_stmt = trace(condense(itemlist(small_stmt, semicolon) + NEWLINE), "simple_stmt")
    stmt = trace(compound_stmt | simple_stmt, "stmt")
    suite <<= trace(condense(colon + NEWLINE + INDENT + OneOrMore(stmt) + DEDENT) | addspace(colon + simple_stmt), "suite")

    single_input = trace(NEWLINE | stmt, "single_input")
    file_input = trace(condense(ZeroOrMore(single_input)), "file_input")
    eval_input = trace(condense(testlist + NEWLINE), "eval_input")

    single_parser = condense(STARTMARKER + single_input + ENDMARKER)
    file_parser = condense(STARTMARKER + file_input + ENDMARKER)
    eval_parser = condense(STARTMARKER + eval_input + ENDMARKER)

    def parse_single(self, inputstring):
        """Parses Console Input."""
        out = self.post(self.single_parser.parseString(self.pre(inputstring)), header="none")
        self.clean()
        return out

    def parse_file(self, inputstring):
        """Parses File Input."""
        out = self.post(self.file_parser.parseString(self.pre(inputstring)), header="file")
        self.clean()
        return out

    def parse_module(self, inputstring):
        """Parses Module Input."""
        out = self.post(self.file_parser.parseString(self.pre(inputstring)), header="module")
        self.clean()
        return out

    def parse_block(self, inputstring):
        """Parses Block Text."""
        out = self.post(self.file_parser.parseString(self.pre(inputstring)), header="none")
        self.clean()
        return out

    def parse_eval(self, inputstring):
        """Parses Eval Input."""
        out = self.post(self.eval_parser.parseString(self.pre(inputstring, strip=True)), header="none")
        self.clean()
        return out

    def parse_debug(self, inputstring):
        """Parses Debug Input."""
        out = self.post(self.file_parser.parseString(self.pre(inputstring, strip=True)), header="none")
        self.clean()
        return out
