#!/usr/bin/python

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

header = """#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# CoconutScript Header:

# Compiled CoconutScript:

"""
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

class pre(object):
    """The CoconutScript Pre-Processor."""
    downs="([{"
    ups=")]}"
    holds="'\"`"
    raw="`"
    comment="#"
    endline="\n\r"
    escape="\\"
    indchar = None

    def __init__(self):
        """Creates A New Pre-Processor."""
        self.refs = []
        global refs
        refs = self.refs

    def proc(self, inputstring):
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
                        raise ParseFatalException("Invalid number of string closes in char #"+x)
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
                    raise ParseFatalException("Invalid number of string starts in char #"+x)
            elif c in self.comment:
                hold = [""]
            elif c in self.holds:
                found = c
            else:
                out.append(c)
            x += 1
        if hold is not None or found is not None:
            raise ParseFatalException("Unclosed string in char #"+x)
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
                raise ParseFatalException("Illegal mixing of tabs and spaces in line "+inputstring)
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
                raise ParseFatalException("Illegal trailing whitespace in line "+lines[x]+" (#"+str(x)+")")
            elif count < 0:
                new[-1] += lines[x]
            else:
                check = self.leading(lines[x])
                if not x:
                    if check:
                        raise ParseFatalException("Illegal initial indent in line "+lines[x]+" (#"+str(x)+")")
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
                    raise ParseFatalException("Illegal dedent to unused indentation level in line "+lines[x]+" (#"+str(x)+")")
                new.append(lines[x])
            count += self.change(lines[x])
        new.append(closestr*(len(levels)-1))
        return linebreak.join(new)

ParserElement.setDefaultWhitespaceChars(white)

def fixto(item, output):
    """Forces An Item To Result In A Specific Output."""
    return item.setParseAction(replaceWith(output))

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
mod_percent = percent

NAME = Regex(r"(?![0-9])\w")
dotted_name = NAME + ZeroOrMore(dot + NAME)

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
NEWLINE = Optional(comment) + Literal(linebreak)
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
           | Keyword("not") + Keyword("in")
           | Keyword("in")
           | Keyword("is") + Keyword("not")
           | Keyword("is")
           )

test = Forward()
expr = Forward()
comp_for = Forward()

tfpdef = NAME + Optional(colon + test)
default = Optional(equals + test)
argslist = (
    tfpdef + default + ZeroOrMore(comma + tfpdef + default)
    + Optional(comma + Optional(star + Optional(tfpdef)
    + ZeroOrMore(comma + tfpdef + default) + Optional(comma
    + dubstar + tfpdef) | dubstar + tfpdef))
    | star + Optional(tfpdef) + ZeroOrMore(comma + tfpdef + default)
    + Optional(comma + dubstar + tfpdef) | dubstar + tfpdef
    )
parameters = lparen + argslist + rparen

testlist = test + ZeroOrMore(comma + test) + Optional(comma).suppress()
yield_arg = Keyword("from") + test | testlist
yield_expr = Keyword("yield") + Optional(yield_arg)
star_expr = star + expr
testlist_star_expr = (test | star_expr) + ZeroOrMore(comma + (test | star_expr)) + Optional(comma).suppress()
testlist_comp = (test | star_expr) + (comp_for | ZeroOrMore(comma + (test | star_expr)) + Optional(comma).suppress())
dictorsetmaker = ((test + colon + test + (comp_for | ZeroOrMore(comma + test + colon + test) + Optional(comma).suppress()))
                  | (test + (comp_for | ZeroOrMore(comma + test) + Optional(comma).suppress())))
func_atom = NAME | lparen + Optional(yield_expr | testlist_comp) + rparen
atom = (func_atom
        | lbrack + Optional(testlist_comp) + rbrack
        | lbrace + Optional(dictorsetmaker) + rbrace
        | ellipses
        | Keyword("None")
        | Keyword("True")
        | Keyword("False")
        | NUMBER
        | OneOrMore(STRING)
        )
sliceop = colon + Optional(test)
subscript = test | Optional(test) + colon + Optional(test) + Optional(sliceop)
subscriptlist = subscript + ZeroOrMore(comma + subscript) + Optional(comma).suppress()
trailer = Optional(dollar) + lparen + Optional(argslist) + rparen | lbrack + subscriptlist + rbrack | dotdot + func_atom | dot + NAME
item = atom + ZeroOrMore(trailer)
factor = Forward()
power = item + Optional(exp_dubstar + factor)
unary = plus | neg_minus | bang
factor <<= unary + factor | power
mulop = mul_star | div_slash | div_dubslash | mod_percent
term = factor + ZeroOrMore(mulop + factor)
arith = plus | sub_minus
arith_expr = term + ZeroOrMore(arith + term)
infix_expr = arith_expr + ZeroOrMore(backslash + test + backslash + arith_expr) # Infix
loop_expr = ZeroOrMore(infix_expr + OneOrMore(tilde)) + infix_expr # Loop
shift = lshift | rshift
shift_expr = loop_expr + ZeroOrMore(shift + loop_expr)
and_expr = shift_expr + ZeroOrMore(amp + shift_expr)
xor_expr = and_expr + ZeroOrMore(caret + and_expr)
or_expr = xor_expr + ZeroOrMore(bar + xor_expr)
pipe_expr = or_expr + ZeroOrMore(pipeline + or_expr) # Pipe
expr <<= pipe_expr
comparison = expr + ZeroOrMore(comp_op + expr)
not_test = ZeroOrMore(Keyword("not")) + comparison
and_test = not_test + ZeroOrMore(Keyword("and") + not_test)
or_test = and_test + ZeroOrMore(Keyword("or") + and_test)
test_item = or_test
test_nocond = Forward()
lambdef = parameters + arrow + test
lambdef_nocond = parameters + arrow + test_nocond
test <<= test_item + Optional(Keyword("if") + test_item + Keyword("else") + test) | lambdef
test_nocond <<= test_item | lambdef_nocond
exprlist = (star_expr | expr) + ZeroOrMore(comma + (star_expr | expr)) + Optional(comma).suppress()

suite = Forward()

argument = NAME + equals + test | NAME + Optional(comp_for)
arglist = ZeroOrMore(argument + comma) + ( dubstar + test
                                          | star + test + ZeroOrMore(comma + argument) + Optional(comma + dubstar + test)
                                          | argument + Optional(comma))
classdef = Keyword("class") + NAME + Optional(lparen + Optional(arglist) + rparen) + colon + suite
comp_iter = Forward()
comp_for <<= Keyword("for") + exprlist + Keyword("in") + test_item + Optional(comp_iter)
comp_if = Keyword("if") + test_nocond + Optional(comp_iter)
comp_iter <<= comp_for | comp_if

pass_stmt = Keyword("pass")
break_stmt = Keyword("break")
continue_stmt = Keyword("continue")
return_stmt = Keyword("return") + Optional(testlist)
yield_stmt = yield_expr
raise_stmt = Keyword("raise") + Optional(test + Optional(Keyword("from") + test))
flow_stmt = break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt

def parenwrap(item):
    """Wraps An Item In Optional Parentheses."""
    return lparen.suppress() + item + rparen.suppress() | item

dotted_as_name = dotted_name + Optional(Keyword("as") + NAME)
import_as_name = NAME + Optional(Keyword("as") + NAME)
import_as_names = import_as_name + ZeroOrMore(comma + import_as_name) + Optional(comma).suppress()
dotted_as_names = dotted_as_name + ZeroOrMore(comma + dotted_as_name) + Optional(comma).suppress()
import_name = Keyword("import") + parenwrap(dotted_as_names)
import_from = (Keyword("from") + (ZeroOrMore(dot) + dotted_name | OneOrMore(dot))
               + Keyword("import") + (star | parenwrap(import_as_names)))
import_stmt = import_name | import_from

global_stmt = Keyword("global") + parenwrap(NAME + ZeroOrMore(comma + NAME) + Optional(comma).suppress())
nonlocal_stmt = Keyword("nonlocal") + parenwrap(NAME + ZeroOrMore(comma + NAME) + Optional(comma).suppress())
del_stmt = Keyword("del") + parenwrap(NAME + ZeroOrMore(comma + NAME) + Optional(comma).suppress())
with_item = test + Optional(Keyword("as") + NAME)
assert_stmt = Keyword("assert") + parenwrap(test + Optional(comma + test))
if_stmt = Keyword("if") + test + colon + suite + ZeroOrMore(Keyword("elif") + test + colon + suite) + Optional(Keyword("else") + colon + suite)
while_stmt = Keyword("while") + test + colon + suite + Optional(Keyword("else") + colon + suite)
for_stmt = Keyword("for") + exprlist + Keyword("in") + testlist + colon + suite + Optional(Keyword("else") + colon + suite)
except_clause = Keyword("except") + test + Optional(Keyword("as") + NAME)
try_stmt = Keyword("try") + colon + suite + (((OneOrMore(except_clause + colon + suite)
                                             + Optional(Keyword("except") + colon + suite))
                                             | Keyword("except") + colon + suite)
                                             + Optional(Keyword("else") + colon + suite)
                                             + Optional(Keyword("finally") + colon + suite)
                                             | Keyword("finally") + colon + suite)
with_stmt = Keyword("with") + parenwrap(with_item + ZeroOrMore(comma + with_item)) + colon + suite

decorator = at + test + NEWLINE
decorators = OneOrMore(decorator)
funcdef = Keyword("def") + NAME + parameters + Optional(arrow + test) + colon + suite
decorated = decorators + (classdef | funcdef)

compound_stmt = if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated
expr_stmt = testlist_star_expr + (augassign + (yield_expr | testlist) | ZeroOrMore(equals + (yield_expr | testlist_star_expr)))
small_stmt = del_stmt | pass_stmt | flow_stmt | import_stmt | global_stmt | nonlocal_stmt | assert_stmt | expr_stmt
simple_stmt = small_stmt + ZeroOrMore(semicolon + small_stmt) + Optional(semicolon).suppress() + NEWLINE
stmt = compound_stmt | simple_stmt
suite <<= NEWLINE + INDENT + OneOrMore(stmt) + DEDENT | simple_stmt

single_input = NEWLINE | compound_stmt + NEWLINE | simple_stmt
file_input = ZeroOrMore(NEWLINE | stmt)
eval_input = testlist + Optional(comment)

single_parser = OneOrMore(STARTMARKER + single_input + ENDMARKER)
file_parser = OneOrMore(STARTMARKER + file_input + ENDMARKER)
eval_parser = OneOrMore(STARTMARKER + eval_input + ENDMARKER)

def parsewith(parser, item):
    """Tests Parsing With A Parser."""
    return (StringStart() + parser + StringEnd()).parseString(item)

def parse_single(inputstring):
    """Processes Console Input."""
    return single_parser.parseString(pre().proc(inputstring))

def parse_file(inputstring):
    """Processes File Input."""
    return file_parser.parseString(pre().proc(inputstring))

def parse_eval(inputstring):
    """Processes Eval Input."""
    return eval_parser.parseString(pre().proc(inputstring.strip()))

if __name__ == "__main__":
    print(parse_file(open(__file__, "rb").read()))
