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

start = "\u2402"
openstr = "\u204b"
closestr = "\u00b6"
end = "\u2403"

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# GRAMMAR:
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def leading(inputstring):
    """Counts Leading Whitespace."""
    count = 0
    for c in str(inputstring):
        if c == " ":
            count += 1
        elif c == "\t":
            count += 4
        else:
            break
    return count

def change(inputstring, downs="([{", ups=")]}", holds="'"+'"'):
    """Determines The Parenthetical Change Of Level."""
    count = 0
    hold = None
    for c in inputstring:
        if hold:
            if c == hold:
                hold = None
        elif c in holds:
            hold = c
        elif c in downs:
            count -= 1
        elif c in ups:
            count += 1
    return count

def preproc(inputstring):
    """Performs Pre-Processing."""
    lines = str(inputstring).splitlines()
    new = []
    levels = []
    count = 0
    for x in xrange(0, len(lines)):
        if count < 0:
            new[-1] += lines[x]
        else:
            check = leading(lines[x])
            if not x:
                current = check
            elif check > current:
                levels.append(current)
                current = check
                lines[x] = openstr+lines[x]
            elif check in levels:
                point = levels.index(check)+1
                new[-1] += closestr*(len(levels[point:])+1)
                levels = levels[:point]
                current = levels.pop()
            elif current != check:
                raise ParseException("Illegal dedent to unused indentation level in line "+lines[x]+" (#"+str(x)+")")
            new.append(lines[x])
        count += change(lines[x])
    new[-1] += closestr*(len(levels)-1)
    return start + "\n".join(new) + end

ParserElement.setDefaultWhitespaceChars(" \t")

comma = Literal(",")
dot = Literal(".")
star = Literal("*")
dubstar = Literal("**")
lparen = Literal("(")
rparen = Literal(")")
at = Literal("@")
arrow = Literal("->")
colon = Literal(":")
semicolon = Literal(";")
equals = Literal("=")
lbrack = Literal("[")
rbrack = Literal("]")
lbrace = Literal("{")
rbrace = Literal("}")
plus = Literal("+")
minus = Literal("-")
bang = Literal("!")
slash = Literal("/")
dubslash = Literal("//")
pipeline = Literal("|>")
amp = Literal("&")
caret = Literal("^")
bar = Literal("|")
percent = Literal("%")
dotdot = Literal("..")
dollar = Literal("$")
dotdotdot = Literal("...")
lshift = Literal("<<")
rshift = Literal(">>")
tilde = Literal("~")

NAME = Word(alphas, alphanums+"_")
dotted_name = NAME + ZeroOrMore(dot + NAME)

integer = Word(nums)
hexint = Word(hexnums)

basenum = integer | Combine(integer, dot, Optional(integer))

sci_e = Literal("e") | Literal("E")
numitem = basenum | Combine(basenum, sci_e, integer)
hexitem = hexint | Combine(hexint, sci_e, hexint)

NUMBER = numitem | Combine(Literal("0"), (Literal("b") | Literal("o") | Literal("x")), hexitem)

STRING = Optional(Literal("b")) + (QuotedString('"', "\\", unquoteResults=False)
                                   | QuotedString("'", "\\", unquoteResults=False)
                                   | QuotedString("`", "\\", unquoteResults=False)
                                   | QuotedString('"""', "\\", multiline=True, unquoteResults=False)
                                   | QuotedString("'''", "\\", multiline=True, unquoteResults=False)
                                   | QuotedString("```", "\\", multiline=True, unquoteResults=False)
                                   )
NEWLINE = OneOrMore(Literal("\n"))
STARTMARKER = Literal(start).suppress()
ENDMARKER = Literal(end).suppress()
INDENT = Literal(openstr)
DEDENT = Literal(closestr)

augassign = (Literal("+=")
             | Literal("-=")
             | Literal("*=")
             | Literal("**=")
             | Literal("/=")
             | Literal("%=")
             | Literal("&=")
             | Literal("|=")
             | Literal("^=")
             | Literal("<<=")
             | Literal(">>=")
             | Literal("//=")
             | Combine(OneOrMore(tilde), equals)
             | Literal("..=")
             | Literal("=>") # In-place pipeline
             )

comp_op = (Literal("<")
           | Literal(">")
           | Literal("==")
           | Literal(">=")
           | Literal("<=")
           | Literal("!=")
           | Keyword("in")
           | Keyword("not") + Keyword("in")
           | Keyword("is")
           | Keyword("is") + Keyword("not")
           )

test = Forward()
expr = Forward()
comp_for = Forward()

tfpdef = NAME + Optional(colon + test)
default = Optional(equals + test)
argslist = Group(
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
testlist_comp = (test | star_expr) + (comp_for | ZeroOrMore(comma + (test | star_expr)) + Optional(comma).suppress())
dictorsetmaker = ((test + colon + test + (comp_for | ZeroOrMore(comma + test + colon + test) + Optional(comma).suppress()))
                  | (test + (comp_for | ZeroOrMore(comma + test) + Optional(comma).suppress())))
atom = (lparen + Group(Optional(yield_expr | testlist_comp)) + rparen
        | lbrack + Group(Optional(testlist_comp)) + rbrack
        | lbrace + Group(Optional(dictorsetmaker)) + rbrace
        | NAME
        | NUMBER
        | OneOrMore(STRING)
        | dotdotdot
        | Keyword("None")
        | Keyword("True")
        | Keyword("False")
        )
sliceop = colon + Optional(test)
subscript = test | Optional(test) + colon + Optional(test) + Optional(sliceop)
subscriptlist = Group(subscript + ZeroOrMore(comma + subscript) + Optional(comma).suppress())
trailer = Optional(dollar) + lparen + Optional(argslist) + rparen | lbrack + subscriptlist + rbrack | dot + NAME | dotdot + atom
item = Group(atom + ZeroOrMore(trailer))
factor = Forward()
power = Group(item + Optional(dubstar + factor))
unary = plus | minus | bang
factor <<= Group(unary + factor | power)
mulop = star | slash | percent | dubslash
term = Group(factor + ZeroOrMore(mulop + factor))
arith = plus | minus
arith_expr = Group(term + ZeroOrMore(arith + term))
shift = lshift | rshift
shift_expr = Group(arith_expr + ZeroOrMore(shift + arith_expr))
and_expr = Group(shift_expr + ZeroOrMore(amp + shift_expr))
xor_expr = Gorup(and_expr + ZeroOrMore(caret + and_expr))
or_expr = Group(xor_expr + ZeroOrMore(bar + xor_expr))
loop_expr = Group(or_expr + ZeroOrMore(OneOrMore(tilde) + or_expr))
pipe_expr = Group(loop_expr + ZeroOrMore(pipeline + loop_expr))
expr <<= pipe_expr
comparison = Group(expr + ZeroOrMore(comp_op + expr))
not_test = Forward()
not_test <<= Group(Keyword("not") + not_test | comparison)
and_test = Group(not_test + ZeroOrMore(Keyword("and") + not_test))
or_test = Group(and_test + ZeroOrMore(Keyword("or") + and_test))
test_nocond = Forward()
lambdef = parameters + arrow + test
lambdef_nocond = parameters + arrow + test_nocond
test <<= or_test + Optional(Keyword("if") + or_test + Keyword("else") + test) | lambdef
test_nocond <<= or_test | lambdef_nocond
exprlist = (expr | star_expr) + ZeroOrMore(comma + (expr | star_expr)) + Optional(comma).suppress()

suite = Forward()

argument = NAME + Optional(comp_for) | NAME + equals + test
arglist = ZeroOrMore(argument + comma) + (argument + Optional(comma)
                                          | star + test + ZeroOrMore(comma + argument) + Optional(comma + dubstar + test)
                                          | dubstar + test)
classdef = Keyword("class") + NAME + Optional(lparen + Optional(arglist) + rparen) + colon + suite
comp_iter = Forward()
comp_for <<= Keyword("for") + exprlist + Keyword("in") + or_test + Optional(comp_iter)
comp_if = Keyword("if") + test_nocond + Optional(comp_iter)
comp_iter <<= comp_for | comp_if

pass_stmt = Keyword("pass")
break_stmt = Keyword("break")
continue_stmt = Keyword("continue")
return_stmt = Keyword("return") + Optional(testlist)
yield_stmt = yield_expr
raise_stmt = Keyword("raise") + Optional(test + Optional(Keyword("from") + test))
flow_stmt = break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt

def paren_wrap(item):
    """Wraps An Item In Optional Parentheses."""
    return Group(item | lparen.suppress() + item + rparen.suppress())

dotted_as_name = dotted_name + Optional(Keyword("as") + NAME)
import_as_name = NAME + Optional(Keyword("as") + NAME)
import_as_names = import_as_name + ZeroOrMore(comma + import_as_name) + Optional(comma).suppress()
dotted_as_names = dotted_as_name + ZeroOrMore(comma + dotted_as_name) + Optional(comma).suppress()
import_name = Keyword("import") + dotted_as_names
import_from = (Keyword("from") + (ZeroOrMore(dot) + dotted_name | OneOrMore(dot))
               + Keyword("import") + (star | paren_wrap(import_as_names)))
import_stmt = import_name | import_from

global_stmt = Keyword("global") + parenwrap(NAME + ZeroOrMore(comma + NAME) + Optional(comma).suppress())
nonlocal_stmt = Keyword("nonlocal") + parenwrap(NAME + ZeroOrMore(comma + NAME) + Optional(comma).suppress())
del_stmt = Keyword("del") + parenwrap(NAME + ZeroOrMore(comma + NAME) + Optional(comma).suppress())
with_item = test + Optional(Keyword("as") + NAME)
assert_stmt = Keyword("assert") + test + Optional(comma + test)
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
with_stmt = Keyword("with") + with_item + ZeroOrMore(comma + with_item) + colon + suite

decorator = at + test + NEWLINE
decorators = OneOrMore(decorator)
funcdef = Keyword("def") + NAME + parameters + Optional(arrow + test) + colon + suite
decorated = decorators + (classdef | funcdef)

compound_stmt = if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated
testlist_star_expr = (test|star_expr) + ZeroOrMore(comma + (test | star_expr)) + Optional(comma).suppress()
expr_stmt = testlist_star_expr + (augassign + (yield_expr | testlist) | ZeroOrMore(equals + (yield_expr | testlist_star_expr)))
small_stmt = expr_stmt | del_stmt | pass_stmt | flow_stmt | import_stmt | global_stmt | nonlocal_stmt | assert_stmt
simple_stmt = small_stmt + ZeroOrMore(semicolon + small_stmt) + Optional(semicolon).suppress() + NEWLINE
stmt = simple_stmt | compound_stmt
suite <<= simple_stmt | NEWLINE + INDENT + OneOrMore(stmt) + DEDENT

single_input = NEWLINE | simple_stmt | compound_stmt + NEWLINE
file_input = ZeroOrMore(NEWLINE | stmt)
eval_input = testlist + ZeroOrMore(NEWLINE)

single_parser = STARTMARKER + single_input + ENDMARKER
file_parser = STARTMARKER + file_input + ENDMARKER
eval_parser = STARTMARKER + eval_input + ENDMARKER

single_parser.ignore(pythonStyleComment)
file_parser.ignore(pythonStyleComment)
eval_parser.ignore(pythonStyleComment)

def parse_single(inputstring):
    """Processes Console Input."""
    return single_parser.parseString(preproc(inputstring))

def parse_file(inputstring):
    """Processes File Input."""
    return file_parser.parseString(preproc(inputstring))

def parse_eval(inputstring):
    """Processes Eval Input."""
    return eval_parser.parseString(preproc(inputstring))

if __name__ == "__main__":
    selfstr = open("parser.py", "rb").read()
    print(parse_file(selfstr))
