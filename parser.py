#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# INFO:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Author: Evan Hubinger
# Date Created: 2014
# Description: The CoconutScript parser.

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# DATA:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

from __future__ import with_statement, print_function, absolute_import, unicode_literals, division

from rabbit.carrot.root import *
from pyparsing import *

header = '''#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# CoconutScript Header: --------------------------------------------------------

class __coconut__(object):
    """Built-In Coconut Functions."""
    import functools
    fold = functools.reduce
    def inv(item):
        """Inversion."""
        if isinstance(item, bool):
            return not item
        else:
            return ~item
    def infix(a, func, b):
        """Infix Calling."""
        return func(a, b)
    def pipe(*args):
        """Pipelining."""
        out = args[0]
        for func in args[1:]:
            out = func(out)
        return out
    def loop(*args):
        """Looping."""
        func = args.pop()
        lists = args
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
    def curry(func, *args):
        """Currying."""
        return functools.partial(func, *args)
    def compose(f, g):
        """Composing."""
        return lambda x: f(g(x))
    def zipwith(func, *args):
        """Functional Zipping."""
        lists = args
        while lists:
            new_lists = []
            items = []
            for series in lists:
                items += series[0]
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
        @functools.wraps(func)
        def _optimized(*args, **kwargs):
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
        return _recursive

fold = __coconut__.fold
zipwith = __coconut__.zipwith
recursive = __coconut__.recursive

# Compiled CoconutScript: ------------------------------------------------------

'''
start = "\u2402"
openstr = "\u204b"
closestr = "\xb6"
end = "\u2403"
linebreak = "\n"
white = " \t\f"

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# GRAMMAR:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

refs = None

class processor(object):
    """The CoconutScript Pre-Processor."""
    verbosity = 10
    downs = "([{"
    ups = ")]}"
    holds = "'\"`"
    raw = "`"
    comment = "#"
    endline = "\n\r"
    escape = "\\"
    tablen = 4
    indchar = None

    def __init__(self):
        """Creates A New Pre-Processor."""
        self.refs = []
        global refs
        refs = self.refs

    def pre(self, inputstring):
        """Performs Pre-Processing."""
        return start + self.indproc(self.strproc(inputstring)) + end

    def wrapstr(self, text, raw, multiline):
        """Wraps A String."""
        self.refs.append((text, raw, multiline))
        return '"'+str(len(refs)-1)+'"'

    def wrapcomment(self, text):
        """Wraps A String."""
        self.refs.append(text)
        return "#"+str(len(refs)-1)

    def getpart(self, iterstring, point):
        """Gets A Part Of A String For An Error Message."""
        out = ""
        i = point-self.verbosity
        while i < point+self.verbosity:
            if i and i < len(iterstring):
                out += iterstring[i]
            i += 1
        return "..."+repr(out)+"..."

    def strproc(self, inputstring):
        """Processes Strings."""
        out = []
        found = None
        hold = None
        x = 0
        while x <= len(inputstring):
            if x == len(inputstring):
                c = linebreak
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
                        raise ParseFatalException("Invalid number of string closes in "+self.getpart(inputstring, x))
                    elif hold[2] == hold[1]:
                        out.append(self.wrapstr(hold[0], hold[1][0] in self.raw, True))
                        hold = None
                        x -= 1
                    else:
                        hold[0] += hold[2]+c
                        hold[2] = None
                elif hold[0].endswith(self.escape):
                    hold[0] += c
                elif c == hold[1]:
                    out.append(self.wrapstr(hold[0], hold[1] in self.raw, False))
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
                    out.append(self.wrapstr("", False, False))
                    found = None
                    x -= 1
                elif len(found) == 3:
                    hold = [c, found, None]
                    found = None
                else:
                    raise ParseFatalException("Invalid number of string starts in "+self.getpart(inputstring, x))
            elif c in self.comment:
                hold = [""]
            elif c in self.holds:
                found = c
            else:
                out.append(c)
            x += 1
        if hold is not None or found is not None:
            raise ParseFatalException("Unclosed string in "+self.getpart(inputstring, x))
        return "".join(out)

    def leading(self, inputstring):
        """Counts Leading Whitespace."""
        count = 0
        for c in inputstring:
            if c not in white:
                break
            elif self.indchar is None:
                self.indchar = c
            elif self.indchar != c:
                raise ParseFatalException("Illegal mixing of tabs and spaces in "+repr(inputstring))
            count += 1
        return count

    def change(self, inputstring):
        """Determines The Parenthetical Change Of Level."""
        count = 0
        hold = None
        for c in inputstring:
            if hold:
                if c == hold:
                    hold = None
            elif c in self.comment:
                break
            elif c in self.holds:
                hold = c
            elif c in self.downs:
                count -= 1
            elif c in self.ups:
                count += 1
        return count

    def indproc(self, inputstring):
        """Processes Indentation."""
        lines = inputstring.splitlines()
        new = []
        levels = []
        count = 0
        for x in xrange(0, len(lines)):
            if lines[x] and lines[x][-1] in white:
                raise ParseFatalException("Illegal trailing whitespace in "+repr(lines[x]))
            elif count < 0:
                new[-1] += lines[x]
            else:
                check = self.leading(lines[x])
                if not x:
                    if check:
                        raise ParseFatalException("Illegal initial indent in "+repr(lines[x]))
                    else:
                        current = 0
                elif check > current:
                    levels.append(current)
                    current = check
                    lines[x] = openstr+lines[x]
                elif check in levels:
                    point = levels.index(check)+1
                    lines[x] = closestr*(len(levels[point:])+1)+lines[x]
                    levels = levels[:point]
                    current = levels.pop()
                elif current != check:
                    raise ParseFatalException("Illegal dedent to unused indentation level in "+repr(lines[x]))
                new.append(lines[x])
            count += self.change(lines[x])
        new.append(closestr*(len(levels)-1))
        return linebreak.join(new)

    def reindent(self, inputstring):
        """Reconverts Indent Tokens Into Indentation."""
        out = []
        level = 0
        hold = None
        for line in inputstring.splitlines():
            if hold is None:
                while line.startswith(openstr) or line.startswith(closestr):
                    if line[0] == openstr:
                        level += 1
                    elif line[0] == closestr:
                        level -= 1
                    line = line[1:]
                line = " "*self.tablen*level + line
            for c in line:
                if hold:
                    if hold == c:
                        hold = None
                elif c in self.holds:
                    hold = c
            if hold is None:
                line = line.rstrip()
            out.append(line)
        return linebreak.join(out)

    def post(self, tokens):
        """Performs Post-Processing."""
        if len(tokens) == 1:
            return header+self.reindent(tokens[0].strip()).strip()+linebreak
        else:
            raise ParseFatalException("Multiple tokens leftover: "+repr(tokens))

ParserElement.setDefaultWhitespaceChars(white)

def fixto(item, output):
    """Forces An Item To Result In A Specific Output."""
    return item.setParseAction(replaceWith(output))

def addspace(item):
    """Condenses And Adds Space To The Tokenized Output."""
    return item.setParseAction(lambda tokens: " ".join(tokens))

def condense(item):
    """Condenses The Tokenized Output."""
    return item.setParseAction(lambda tokens: "".join(tokens))

comma = Literal(",")
dot = Literal(".")
star = Literal("*")
dubstar = Literal("**")
lparen = Literal("(")
rparen = Literal(")")
at = Literal("@")
arrow = fixto(Literal("->") | Literal("\u2192"), "->")
heavy_arrow = fixto(Literal("=>") | Literal("\u21d2"), "=>")
colon = Literal(":")
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
dotdot = Literal("..")
dollar = Literal("$")
ellipses = fixto(Literal("...") | Literal("\u2026"), "...")
lshift = fixto(Literal("<<") | Literal("\xab"), "<<")
rshift = fixto(Literal(">>") | Literal("\xbb"), ">>")
tilde = Literal("~")
underscore = Literal("_")
pound = Literal("#")
backslash = Literal("\\")

mul_star = fixto(star | Literal("\xd7"), "*")
exp_dubstar = fixto(star | Literal("\xd7\xd7"), "**")
neg_minus = fixto(minus | Literal("\xaf"), "-")
sub_minus = fixto(minus | Literal("\u2212"), "-")
div_slash = fixto(slash | Literal("\xf7"), "/")
div_dubslash = fixto(dubslash | Combine(Literal("\xf7"), slash), "//")
inv_bang = fixto(bang, "~")
mod_percent = percent

NAME = Regex(r"(?![0-9])\w")
dotted_name = condense(NAME + ZeroOrMore(dot + NAME))

integer = Word(nums)
binint = Word("01")
octint = Word("01234567")
hexint = Word(hexnums)
anyint = Word(nums, alphanums)

basenum = Combine(integer + dot + Optional(integer)) | integer
sci_e = CaselessLiteral("e") | fixto(Literal("\u23e8"), "E")
numitem = Combine(basenum + sci_e + integer) | basenum

def anyint_proc(tokens):
    """Replaces Underscored Integers."""
    if len(tokens) == 1:
        item, base = tokens[0].split("_")
        tokens[0] = 'int("'+item+'", '+base+")"
        return tokens
    else:
        raise ParseFatalException("Invalid anyint token")

NUMBER = (Combine(anyint + underscore + integer).setParseAction(anyint_proc)
          | Combine(CaselessLiteral("0b"), binint)
          | Combine(CaselessLiteral("0o"), octint)
          | Combine(CaselessLiteral("0x"), hexint)
          | numitem
          )

def string_repl(tokens):
    """Replaces String References."""
    if len(tokens) == 1:
        tokens[0] = refs[int(tokens[0])]
        if isinstance(tokens[0], tuple):
            tokens[0], raw, multiline = tokens[0]
            if tokens[0]:
                if tokens[0][-1] == '"':
                    tokens[0] = tokens[:-1]+'\\"'
                if tokens[0][0] == '"':
                    tokens[0] = "\\"+tokens[0]
            if multiline:
                tokens[0] = '"""'+tokens[0]+'"""'
            else:
                tokens[0] = '"'+tokens[0]+'"'
            if raw:
                tokens[0] = "r"+tokens[0]
            return tokens
        else:
            raise ParseFatalException("String marker points to comment")
    else:
        raise ParseFatalException("Invalid string marker")

def comment_repl(tokens):
    """Replaces Comment References."""
    if len(tokens) == 1:
        tokens[0] = refs[int(tokens[0])]
        if isinstance(tokens[0], tuple):
            raise ParseFatalException("Comment marker points to string")
        else:
            return tokens
    else:
        raise ParseFatalException("Invalid comment marker")

string_ref = Combine(Literal('"').suppress() + integer + Literal('"').suppress()).setParseAction(string_repl)
comment = Combine(pound.suppress() + integer).setParseAction(comment_repl)
bit_b = CaselessLiteral("b")
STRING = Combine(Optional(bit_b) + string_ref)
NEWLINE = Combine(Optional(comment) + Literal(linebreak))
STARTMARKER = Literal(start).suppress()
ENDMARKER = Literal(end).suppress()
INDENT = Literal(openstr)
DEDENT = Literal(closestr) + Optional(NEWLINE)

augassign = (heavy_arrow # In-place pipeline
             | Combine(plus + equals)
             | Combine(sub_minus + equals)
             | Combine(mul_star + equals)
             | Combine(exp_dubstar + equals)
             | Combine(div_slash + equals)
             | Combine(mod_percent + equals)
             | Combine(amp + equals)
             | Combine(bar + equals)
             | Combine(caret + equals)
             | Combine(lshift + equals)
             | Combine(rshift + equals)
             | Combine(div_dubslash + equals)
             | Combine(OneOrMore(tilde) + equals)
             | Combine(dotdot + equals)
             )

comp_op = (Literal("<")
           | Literal(">")
           | Literal("==")
           | fixto(
               Literal(">=")
               | Literal("\u2265"), ">="
               )
           | fixto(
               Literal("<=")
               | Literal("\u2264"), "<="
               )
           | fixto(
               Combine(bang, equals)
               | Literal("\u2260"), "!="
               )
           | addspace(Keyword("not") + Keyword("in"))
           | Keyword("in")
           | addspace(Keyword("is") + Keyword("not"))
           | Keyword("is")
           )

test = Forward()
expr = Forward()
comp_for = Forward()

def itemlist(item, sep=comma):
    """Creates A List Containing An Item."""
    return addspace(ZeroOrMore(condense(item + sep)) + item + Optional(sep).suppress())

def parenwrap(item):
    """Wraps An Item In Optional Parentheses."""
    return condense(lparen.suppress() + item + rparen.suppress() | item)

tfpdef = condense(NAME + Optional(colon + test))
default = Optional(condense(equals + test))
argslist = addspace((
    ZeroOrMore(condense(tfpdef + default + comma)) + condense(tfpdef + default)
     | OneOrMore(condense(tfpdef + default + comma)) + (
         condense(star + tfpdef)
         | condense(star + Optional(tfpdef) + comma) + (
             ZeroOrMore(condense(tfpdef + default + comma)) + (
                 condense(tfpdef + default)
                 | condense(dubstar + tfpdef)
                 )
             )
         )
    ) + Optional(comma).suppress())
parameters = condense(lparen + argslist + rparen)

testlist = itemlist(test)
yield_arg = addspace(Keyword("from") + test) | testlist
yield_expr = addspace(Keyword("yield") + Optional(yield_arg))
star_expr = condense(star + expr)
test_star_expr = test | star_expr
testlist_star_expr = itemlist(test_star_expr)
testlist_comp = addspace(test_star_expr + comp_for) | testlist_star_expr
dictorsetmaker = addspace(condense(test + colon) + test + comp_for
                  | itemlist(condense(test + colon) + test)
                  | test + comp_for
                  | testlist
                  )
func_atom = NAME | condense(lparen + Optional(yield_expr | testlist_comp) + rparen)
atom = (func_atom
        | condense(lbrack + Optional(testlist_comp) + rbrack)
        | condense(lbrace + Optional(dictorsetmaker) + rbrace)
        | ellipses
        | Keyword("None")
        | Keyword("True")
        | Keyword("False")
        | NUMBER
        | OneOrMore(STRING)
        )
sliceop = condense(colon + Optional(test))
subscript = test | condense(Optional(test) + sliceop + Optional(sliceop))
subscriptlist = itemlist(subscript)
trailer = (Group(dollar + lparen.suppress() + Optional(argslist) + rparen.suppress())
           | condense(lparen + Optional(argslist) + rparen)
           | condense(lbrack + subscriptlist + rbrack)
           | Group(dotdot + func_atom)
           | condense(dot + NAME)
           )

def item_proc(tokens):
    """Processes Items."""
    out = tokens.pop(0)
    for trailer in tokens:
        if isinstance(trailer, str):
            out += trailer
        elif len(trailer) == 2:
            if trailer[0] == "$":
                out = "__coconut__.curry("+out+", "+trailer[1]+")"
            elif trailer[0] == "..":
                out = "__coconut__.compose("+out+", "+trailer[1]+")"
            else:
                raise ParseFatalException("Invalid special trailer: "+repr(trailer[0]))
        else:
            raise ParseFatalException("Invalid trailer tokens: "+repr(trailer))
item = (atom + ZeroOrMore(trailer)).setParseAction(item_proc)

factor = Forward()
power = condense(item + Optional(exp_dubstar + factor))
unary = plus | neg_minus

def inv_proc(tokens):
    """Processes Inversions."""
    if len(tokens) == 1:
        return "__coconut__.inv("+tokens[0]+")"
    else:
        raise ParseFatalException("Invalid inversion tokens: "+repr(tokens))
factor <<= condense(unary + factor) | (inv_bang.suppress() + factor).setParseAction(inv_proc) | power

mulop = mul_star | div_slash | div_dubslash | mod_percent
term = addspace(factor + ZeroOrMore(mulop + factor))
arith = plus | sub_minus
arith_expr = addspace(term + ZeroOrMore(arith + term))

def infix_proc(tokens):
    """Processes Infix Calls."""
    if len(tokens) == 1:
        return tokens[0]
    else:
        return "__coconut__.infix("+infix_proc(tokens[:-2])+", "+tokens[-2]+", "+tokens[-1]+")"
infix_expr = (arith_expr + ZeroOrMore(backslash.suppress() + test + backslash.suppress() + arith_expr)).setParseAction(infix_proc)

def loop_proc(tokens):
    """Processes Loop Calls."""
    if len(tokens) == 1:
        return tokens[0]
    else:
        out = "__coconut__.loop("+tokens[-1]
        for loop_list, loop_step in tokens[:-1]:
            out += ", ("+loop_list+", "+loop_step+")"
        return out+")"
loop_expr = (ZeroOrMore(Group(infix_expr + OneOrMore(tilde))) + infix_expr).setParseAction(loop_proc)

shift = lshift | rshift
shift_expr = addspace(loop_expr + ZeroOrMore(shift + loop_expr))
and_expr = addspace(shift_expr + ZeroOrMore(amp + shift_expr))
xor_expr = addspace(and_expr + ZeroOrMore(caret + and_expr))
or_expr = addspace(xor_expr + ZeroOrMore(bar + xor_expr))

def pipe_proc(tokens):
    """Processes Pipe Calls."""
    if len(tokens) == 1:
        return tokens[0]
    else:
        return "__coconut__.pipe("+", ".join(tokens)+")"
pipe_expr = (or_expr + ZeroOrMore(pipeline.suppress() + or_expr)).setParseAction(pipe_proc)

expr <<= pipe_expr
comparison = addspace(expr + ZeroOrMore(comp_op + expr))
not_test = addspace(ZeroOrMore(Keyword("not")) + comparison)
and_test = addspace(not_test + ZeroOrMore(Keyword("and") + not_test))
or_test = addspace(and_test + ZeroOrMore(Keyword("or") + and_test))
test_item = or_test
test_nocond = Forward()

def lambda_proc(tokens):
    """Processes Lambda Calls."""
    if len(tokens) == 2:
        return "lambda "+tokens[0]+": "+tokens[1]
    else:
        raise ParseFatalException("Invalid lambda tokens: "+repr(tokens))
lambdef = (lparen.suppress() + argslist + rparen.suppress() + arrow.suppress() + test).setParseAction(lambda_proc)

lambdef_nocond = addspace(parameters + arrow + test_nocond)
test <<= lambdef | addspace(test_item + Optional(Keyword("if") + test_item + Keyword("else") + test))
test_nocond <<= lambdef_nocond | test_item
exprlist = itemlist(star_expr | expr)

suite = Forward()

argument = condense(NAME + equals + test) | addspace(NAME + Optional(comp_for))
arglist = addspace(
    ZeroOrMore(condense(argument + comma))
    + (
        condense(dubstar + test)
        | star + condense(test + comma) + (
            OneOrMore(condense(argument + comma)) + (
                argument + Optional(comma).suppress()
                | condense(dubstar + test)
                )
            )
        | star + test + Optional(comma).suppress()
        | argument + Optional(comma).suppress()
        )
    )
classdef = condense(addspace(Keyword("class") + condense(NAME + Optional(lparen + Optional(arglist) + rparen) + colon)) + suite)
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
import_as_names = itemlist(import_as_name)
dotted_as_names = itemlist(dotted_as_name)
import_name = addspace(Keyword("import") + parenwrap(dotted_as_names))
import_from = addspace(Keyword("from") + condense(ZeroOrMore(dot) + dotted_name | OneOrMore(dot))
               + Keyword("import") + (star | parenwrap(import_as_names)))
import_stmt = import_name | import_from

namelist = parenwrap(itemlist(NAME))
global_stmt = addspace(Keyword("global") + namelist)
nonlocal_stmt = addspace(Keyword("nonlocal") + namelist)
del_stmt = addspace(Keyword("del") + namelist)
with_item = addspace(test + Optional(Keyword("as") + NAME))
assert_stmt = addspace(Keyword("assert") + parenwrap(testlist))
else_stmt = condense(Keyword("else") + colon + suite)
if_stmt = condense(addspace(Keyword("if") + condense(test + colon + suite))
                   + ZeroOrMore(addspace(Keyword("elif") + condense(test + colon + suite)))
                   + Optional(else_stmt)
                   )
while_stmt = addspace(Keyword("while") + condense(test + colon + suite + Optional(else_stmt)))
for_stmt = addspace(Keyword("for") + exprlist + Keyword("in") + condense(testlist + colon + suite + Optional(else_stmt)))
except_clause = addspace(Keyword("except") + test + Optional(Keyword("as") + NAME))
try_stmt = condense(Keyword("try") + colon + suite + (
    Keyword("finally") + colon + suite
    | (
        OneOrMore(except_clause + colon + suite) + Optional(Keyword("except") + colon + suite)
        | Keyword("except") + colon + suite
        ) + Optional(else_stmt) + Optional(Keyword("finally") + colon + suite)
    ))
with_stmt = addspace(Keyword("with") + condense(parenwrap(itemlist(with_item)) + colon + suite))

decorator = condense(at + test + NEWLINE)
decorators = OneOrMore(decorator)
funcdef = addspace(Keyword("def") + condense(NAME + parameters + Optional(arrow + test) + colon + suite))
decorated = condense(decorators + (classdef | funcdef))

compound_stmt = if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated
expr_stmt = addspace(testlist_star_expr + (augassign + (yield_expr | testlist) | ZeroOrMore(equals + (yield_expr | testlist_star_expr))))
small_stmt = del_stmt | pass_stmt | flow_stmt | import_stmt | global_stmt | nonlocal_stmt | assert_stmt | expr_stmt
simple_stmt = itemlist(small_stmt, semicolon) + NEWLINE
stmt = compound_stmt | simple_stmt
suite <<= condense(NEWLINE + INDENT + OneOrMore(stmt) + DEDENT) | simple_stmt

single_input = NEWLINE | condense(compound_stmt + NEWLINE) | simple_stmt
file_input = condense(ZeroOrMore(NEWLINE | stmt))
eval_input = condense(testlist + NEWLINE)

single_parser = condense(OneOrMore(STARTMARKER + single_input + ENDMARKER))
file_parser = condense(OneOrMore(STARTMARKER + file_input + ENDMARKER))
eval_parser = condense(OneOrMore(STARTMARKER + eval_input + ENDMARKER))

def parsewith(parser, item):
    """Tests Parsing With A Parser."""
    return (StringStart() + parser + StringEnd()).parseString(item)

def parse_single(inputstring):
    """Processes Console Input."""
    proc = processor()
    return proc.post(single_parser.parseString(proc.pre(inputstring)))

def parse_file(inputstring):
    """Processes File Input."""
    proc = processor()
    return proc.post(file_parser.parseString(proc.pre(inputstring)))

def parse_eval(inputstring):
    """Processes Eval Input."""
    proc = processor()
    return proc.post(eval_parser.parseString(proc.pre(inputstring.strip())))

if __name__ == "__main__":
    print(parse_file(open(__file__, "rb").read()))
