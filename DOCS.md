# Coconut Documentation

This documentation will cover all the technical details of the [Coconut](https://github.com/evhub/coconut) programming language. This documentation is not intended as a tutorialized introduction, only a technical specification. For a full introduction and tutorial of the Coconut programming language, see the [HELP](https://github.com/evhub/coconut/blob/master/HELP.md) file.

- [I. Command Line](#i-command-line)
    - [Usage](#usage)
    - [Positional Arguments](#positional-arguments)
    - [Optional Arguments](#optional-arguments)
    - [Python Versions](#python-versions)
    - [Compiled Files](#compiled-files)
    - [--strict Mode](#--strict-mode)
    - [IPython](#ipython)
- [II. Syntax](#ii-syntax)
    - [Lambdas](#lambdas)
    - [Lazy Lists](#lazy-lists)
    - [Backtick Calling](#backtick-calling)
    - [Mathematical Function Definition](#mathematical-function-definition)
    - [Operator Functions](#operator-functions)
    - [Destructuring Assignment](#destructuring-assignment)
    - [Pattern-Matching Function Definition](#pattern-matching-function-definition)
    - [Implicit Partial Application](#implicit-partial-application)
    - [Enhanced Set Literals](#enhanced-set-literals)
    - [Enhanced Imaginary Literals](#enhanced-imaginary-literals)
    - [Non-Decimal Integers](#non-decimal-integers)
    - [Enhanced Decorators](#enhanced-decorators)
    - [Enhanced `else` Statements](#enhanced-else-statements)
    - [Enhanced `except` Statements](#enhanced-except-statements)
    - [Enhanced Variable Lists](#enhanced-variable-lists)
    - [Unicode Alternatives](#unicode-alternatives)
    - [Code Passthrough](#code-passthrough)
- [III. Operators](#iii-operators)
    - [Compose](#compose)
    - [Pipeline](#pipeline)
    - [Chain](#chain)
    - [Partial Application](#partial-application)
    - [Iterator Slice](#iterator-slice)
- [IV. Built-Ins](#iv-built-ins)
    - [`reduce`](#reduce)
    - [`takewhile`](#takewhile)
    - [`dropwhile`](#dropwhile)
    - [`tee`](#tee)
    - [`consume`](#consume)
    - [`datamaker`](#datamaker)
    - [`recursive`](#recursive)
    - [`__coconut_version__`](#__coconut_version__)
- [V. Keywords](#v-keywords)
    - [`data`](#data)
    - [`match`](#match)
    - [`case`](#case)
    - [Backslash Escaping](#backslash-escaping)
    - [Reserved Variables](#reserved-variables)
- [VI. Coconut Module](#vi-coconut-module)
    - [`coconut.convenience`](#coconutconvenience)
    - [`coconut.convenience.parse`](#coconutconvenienceparse)
    - [`coconut.convenience.setup`](#coconutconveniencesetup)
    - [`coconut.convenience.cmd`](#coconutconveniencecmd)
    - [`coconut.convenience.version`](#coconutconvenienceversion)
    - [`coconut.convenience.CoconutException`](#coconutconveniencecoconutexception)

## I. Command Line

### Usage

```
coconut [-h] [-v] [source] [dest] [-t version] [-s] [-p] [-f] [-r] [-n] [-i] [-q] [-d] [-c code] [--autopep8 ...]
```

### Positional Arguments

```
source                path to the coconut file/folder to compile
dest                  destination directory for compiled files (defaults to the source directory)
```

### Optional Arguments

```
-h, --help            show this help message and exit
-v, --version         print Coconut and Python version information
-t, --target          specify target Python version
-s, --strict          enforce code cleanliness standards
-p, --print           print the compiled Python
-f, --force           force overwriting of compiled Python (otherwise only overwrites when the source changes)
-r, --run             run the compiled Python
-n, --nowrite         disable writing the compiled Python
-i, --interact        force the interpreter to start (otherwise starts if no other command is given)
-q, --quiet           suppress all informational output
-d, --debug           print verbose debug output
-c, --code            run a line of Coconut passed in as a string (can also be accomplished with a pipe)
--autopep8            use autopep8 to format compiled code (remaining args passed to autopep8)
```

### Python Versions

While Coconut syntax is based off of Python 3, the compiler should run on any Python version `>= 2.6` on the `2.x` branch or `>= 3.2` on the `3.x` branch, and will attempt to produce universal code that will run like it does on Python 3 in Python 2.

_Note: While the compiler should run under any Python implementation of any version `>= 2.6` on the `2.x` branch or `>= 3.2` on the `3.x` branch, the tested against implementations are [CPython](https://www.python.org/) `2.6, 2.7, 3.3, 3.4, 3.5` and [PyPy](http://pypy.org/) `2.7`._

If the version of Python that the compiled code will be running on is known ahead of time, one of `2` (for the `2.x` branch) or `3` (for the `3.x` branch) should be specified as the `--target`. The given target will only affect the compiled code and whether or not Python-3-specific syntax is allowed. Where Python 3 and Python 2 syntax standards differ, Coconut syntax will always follow Python 3 accross all targets. Coconut will not, however, change any imports, variable names, or library interfaces. Universal compatibility with those must still be done manually.

Coconut will, however, add in new Python 3 built-ins and overwrite Python 2 built-ins to use the Python 3 versions where possible. If access to the Python 2 versions is desired, the old builtins can be retrieved by prefixing them with `py2_`. The old built-ins available are:
- `py2_filter`
- `py2_hex`
- `py2_map`
- `py2_oct`
- `py2_zip`
- `py2_range`
- `py2_int`
- `py2_chr`
- `py2_str`
- `py2_open`
- `py2_print`
- `py2_input`

### Compiled Files

Files compiled by the `coconut` command-line utility will vary based on compilation parameters. If an entire folder of files is compiled, a `__coconut__.py` file will be created to house necessary functions, whereas if only a single file is compiled, that information will be stored within a header inside the file. Regardless of which method is used, each `.coc` file found will compile to another file with the same name, except with `.py` instead of `.coc`, which will hold the compiled code.

If an extension other than `.py` is desired for the compiled files, such as `.pyde` for [Python Processing](http://py.processing.org/), then that extension can be put before `.coc` in the source file name, and it will be used instead of `.py` for the compiled files. For example, `name.coc` will compile to `name.py`, whereas `name.pyde.coc` will compile to `name.pyde`.

### `--strict` Mode

If the `--strict` or `-s` flag is enabled, Coconut will throw errors on various style problems. These are:
- Mixing of tabs and spaces (otherwise would show a warning)
- Use of the Python-style `lambda` statement
- Use of `u` to denote Unicode strings
- Use of backslash continuations (implicit continuations are preferred)
- Trailing whitespace at the end of lines

It is recommended that you use the `--strict` or `-s` flag if you are starting a new Coconut project, as it will help you write cleaner code.

### IPython

If you prefer [IPython](http://ipython.org/) to the normal Python shell, Coconut can also be used as an IPython extension. The line magic `%load_ext coconut` will provide access to the `%coconut` and `%%coconut` magics. The `%coconut` line magic will run a line of Coconut with default parameters, whereas the `%%coconut` block magic will take command-line arguments on the first line, and run any Coconut code provided in the rest of the cell with those parameters.

## II. Syntax

### Lambdas

Coconut provides an alternative to Python's `lambda` statements in favor of a simple, Coffee-style `->` operator. The operator has the same precedence as the old statement.

##### Python Docs

Lambda forms (lambda expressions) have the same syntactic position as expressions. They are a shorthand to create anonymous functions; the expression `(arguments) -> expression` yields a function object. The unnamed object behaves like a function object defined with:
```python
def <lambda>(arguments):
    return expression
```
Note that functions created with lambda forms cannot contain statements or annotations.

##### Example

Coconut:
```python
(x, y) -> 2*(x+y)
```

Python:
```python
lambda x, y: 2*(x+y)
```

### Lazy Lists

Coconut supports the creation of lazy lists, where the contents in the list will be treated as a Python iterator and not evaluated until they are needed. Lazy lists can be created in Coconut simply by simply surrounding a comma-seperated list of items with `(|` and `|)` instead of `[` and `]` for a list or `(` and `)` for a tuple.

##### Example

Coconut:
```python
nums = (| -3, -1, 1 |) :: range(2,10)
```

Python:
_Can't be done without a complicated iterator comprehension in place of the lazy list. See the compiled code for the Python syntax._

### Backtick Calling

Coconut allows for Haskell-style infix calling, where a function is surrounded by backticks and then can have arguments placed in front of or behind it. Backtick calling has a precedence in-between chaining and piping.

##### Example

Coconut:
```python
(x `mod` 2) `f` == 1
```

Python:
```python
f(mod(x, 2)) == 1
```

### Mathematical Function Definition

Coconut allows for math-style in-line function definition, where the body of the function is assigned directly to the function call. The syntax for in-line function definition is
```
"def" (
    <name> "(" <args> ")"
    | "(" <arg1> ")" "`" <name> "`" "(" <arg2> ")"
) "=" <body>
```
where `<name>` is the name of the function and `<args>` are the functions arguments. Additionally, backtick-style definition is also allowed in normal Python block function definition statements.

##### Example

Coconut:
```python
def exp(x, b=2) = b**x
def a `mod` b = a % b
```

Python:
```python
def exp(x, b=2): return b**x
def mod(a, b): return a % b
```

### Operator Functions

Coconut uses Haskell-style operator function short-hand, where the operator placed within parentheses can be used as a function. The full list of operator functions is as follows:
```
(|>)        => (<lambda>) # pipe forward
(|*>)       => (<lambda>) # multi-arg pipe forward
(<|)        => (<lambda>) # pipe backward
(|*>)       => (<lambda>) # multi-arg pipe backward
(..)        => (<lambda>) # function composition
(.)         => (getattr)
(::)        => (itertools.chain) # will not evaluate its arguments lazily
($)         => (functools.partial)
(+)         => (operator.__add__)
(-)         => (<lambda>) # 1 arg: operator.__neg__, 2 args: operator.__sub__
(*)         => (operator.__mul__)
(**)        => (operator.__pow__)
(/)         => (operator.__truediv__)
(//)        => (operator.__floordiv__)
(%)         => (operator.__mod__)
(&)         => (operator.__and__)
(^)         => (operator.__xor__)
(|)         => (operator.__or__)
(<<)        => (operator.__lshift__)
(>>)        => (operator.__rshift__)
(<)         => (operator.__lt__)
(>)         => (operator.__gt__)
(==)        => (operator.__eq__)
(<=)        => (operator.__le__)
(>=)        => (operator.__ge__)
(!=)        => (operator.__ne__)
(~)         => (operator.__inv__)
(@)         => (operator.__matmul__)
(not)       => (operator.__not__)
(and)       => (<lambda>) # boolean and
(or)        => (<lambda>) # boolean or
(is)        => (operator.is_)
(in)        => (operator.__contains__)
```

##### Example

Coconut:
```python
prod = reduce((*), items)
```

Python:
```python
import operator
prod = reduce(operator.__mul__, items)
```

### Destructuring Assignment

Coconut supports significantly enhanced destructuring assignment, similar to Python's tuple/list destructuring, but much more powerful. The syntax for Coconut's destructuring assignment is
```
["match"] <pattern> = <value>
```
where `<value>` is any expression and `<pattern>` is defined by Coconut's [`match` statement](#match). The `match` keyword at the beginning is optional, but is sometimes necessary to disambiguate destructuring assignment from normal assignment, which will always take precedence. Coconut's destructuring assignment is equivalent to a match statement that follows the syntax:
```python
match <pattern> in <value>:
    pass
else:
    err = MatchError(<error message>)
    err.pattern = "<pattern>"
    err.value = <value>
    raise err
```
If a destructuring assignment statement fails, then instead of continuing on as if a `match` block had failed, a `MatchError` object will be raised describing the failure.

##### Example

Coconut:
```python
def last_two(l):
    _ + [a, b] = l
    return a, b
```

Python:

_Can't be done without a long series of checks in place of the destructuring assignment statement. See the compiled code for the Python syntax._

### Pattern-Matching Function Definition

Coconut supports pattern-matching / destructuring assignment syntax inside of function definition. The syntax for pattern-matching function definition is
```
[match] def <name>(<match>, <match>, ...):
    <body>
```
where `<name>` is the name of the function, `<body>` is the body of the function, and `<pattern>` is defined by Coconut's [`match` statement](#match). The `match` keyword at the beginning is optional, but is sometimes necessary to disambiguate pattern-matching function definition from normal function definition, which will always take precedence. Coconut's pattern-matching function definition is equivalent to a destructuring assignment statement that looks like:
```
def <name>(*args):
    match [<match>, <match>, ...] = args
    <body>
```
If pattern-matching function definition fails, it will raise a `MatchError` object just like destructuring assignment.

##### Example

Coconut:
```python
def last_two(_ + [a, b]):
    return a, b
```

Python:

_Can't be done without a long series of checks at the top of the function. See the compiled code for the Python syntax._

### Implicit Partial Application

Coconut supports a number of different syntactical aliases for common partial application use cases. These are:
```
.name       =>      operator.attrgetter("name")
obj.        =>      functools.partial(getattr, obj)
func$       =>      functools.partial(functools.partial, func)
series[]    =>      functools.partial(operator.__getitem__, series)
series$[]   =>      <lambda> # the equivalent of series[] for iterators
```

##### Example

Coconut:
```python
1 |> "123"[]
mod$ <| 5 <| 3
```

Python:
```python
"123"[1]
mod(5, 3)
```

### Enhanced Set Literals

In addition to Python's normal set literals using curly braces, Coconut supports a special `s` (for `set`) or `f` (for `frozenset`) in front of a Python-like set literal to ensure it is a set literal of the specified type even when it otherwise would not be, such as when it is empty, or if a `frozenset` is desired.

#### Example

Coconut:
```python
empty_frozen_set = f{}
```

Python:
```python
empty_frozen_set = frozenset()
```

### Enhanced Imaginary Literals

In addition to Python's `<num>j` or `<num>J` notation for imaginary literals, Coconut also supports `<num>i` or `<num>I`.

##### Python Docs

Imaginary literals are described by the following lexical definitions:
```
imagnumber ::=  (floatnumber | intpart) ("j" | "J" | "i" | "I")
```
An imaginary literal yields a complex number with a real part of 0.0. Complex numbers are represented as a pair of floating point numbers and have the same restrictions on their range. To create a complex number with a nonzero real part, add a floating point number to it, e.g., `(3+4i)`. Some examples of imaginary literals:
```
3.14i   10.i    10i     .001i   1e100i  3.14e-10i
```

##### Example

Coconut:
```
3 + 4i |> abs
```

Python:
```
abs(3 + 4j)
```

### Non-Decimal Integers

In addition to Python's normal binary, octal, and hexadecimal integer syntax, Coconut also supports its own universal non-decimal integer syntax `<base>"_"<number>`.

##### Python Docs

A base-n literal consists of the digits 0 to n-1, with `a` to `z` (or `A` to `Z`) having values 10 to 35. The default base is 10. The allowed values are 0 and 2-36. Base 0 means to interpret exactly as a code literal, so that the actual base is 2, 8, 10, or 16, and so that `010`, `0_010`, and `8_010` are 8, while `10`, `0_10`, and `10_010` are 10.

##### Example

Coconut:
```python
12_10A == 154
```

Python:
```python
int("10A", 12) == 154
```

### Enhanced Decorators

Unlike Python, which only supports a single variable or function call in a decorator, Coconut supports any expression.

##### Example

Coconut:
```python
@ wrapper1 .. wrapper2 $(arg)
def func(x) = x**2
```

Python:
```python
def wrapper(func):
    return wrapper1(wrapper2(arg, func))
@wrapper
def func(x):
    return x**2
```

### Enhanced `else` Statements

Coconut supports the compound statements `try`, `if`, and `match` on the end of an `else` statement like any simple statement would be. This is most useful for mixing `match` and `if` statements together, but also allows for compound `try` statements.

##### Example

Coconut:
```python
try:
    unsafe_1()
except MyError:
    handle_1()
else: try:
    unsafe_2()
except MyError:
    handle_2()
```

Python:
```python
try:
    unsafe_1()
except MyError:
    handle_1()
else:
    try:
        unsafe_2()
    except MyError:
        handle_2()
```

### Enhanced `except` Statements

Python 3 requires that if multiple exceptions are to be caught, they must be placed inside of parentheses, so as to disallow Python 2's use of a comma instead of `as`. Coconut allows commas in except statements to translate to catching multiple exceptions without the need for parentheses.

##### Example

Coconut:
```python
try:
    unsafe_func(arg)
except SyntaxError, ValueError as err:
    handle(err)
```

Python:
```python
try:
    unsafe_func(arg)
except (SyntaxError, ValueError) as err:
    handle(err)
```

### Enhanced Variable Lists

Coconut allows for the more elegant parenthetical continuation instead of the less elegant backslash continuation in `import`, `del`, `global`, and `nonlocal` statements.

##### Example

Coconut:
```python
global (really_long_global_variable_name_the_first_one,
        really_long_global_variable_name_the_second_one)
```

Python:
```python
global really_long_global_variable_name_the_first_one, \
        really_long_global_variable_name_the_second_one
```

### Unicode Alternatives

Coconut supports unicode alternatives to many different symbols. The full list of symbols is as follows:
```
→ (\u2192)                  => "->"
↦ (\u21a6)                  => "|>"
*↦ (*\u21a6)                => "|*>"
↤ (\u21a4)                  => "<|"
↤* (\u21a4*)                => "<*|"
⋅ (\u22c5)                  => "*"
↑ (\u2191)                  => "**"
÷ (\xf7)                    => "/"
÷/ (\xf7/)                  => "//"
− (\u2212)                  => "-" (only subtraction)
⁻ (\u207b)                  => "-" (only negation)
¬ (\xac)                    => "~"
≠ (\u2260) or ¬= (\xac=)    => "!="
≤ (\u2264)                  => "<="
≥ (\u2265)                  => ">="
∧ (\u2227) or ∩ (\u2229)    => "&"
∨ (\u2228) or ∪ (\u222a)    => "|"
⊻ (\u22bb) or ⊕ (\u2295)    => "^"
« (\xab)                    => "<<"
» (\xbb)                    => ">>"
… (\u2026)                  => "..."
× (\xd7)                    => "@" (only matrix multiplication)
```

### Code Passthrough

Coconut supports the ability to pass arbitrary code through the compiler without being touched, for compatibility with other variants of Python, such as [Cython](http://cython.org/) or [Mython](http://mython.org/). Anything placed between `\(` and the corresponding close paren will be passed through, as well as any line starting with `\\`, which will have the additional effect of allowing indentation under it.

##### Example

Coconut:
```
\\cdef f(x):
    return x |> g
```

Python:
```python
cdef f(x):
    return g(x)
```

## III. Operators

### Compose

Coconut uses the `..` operator for function composition. It has a precedence in-between subscription and exponentiation. The in-place operator is `..=`.

##### Example

Coconut:
```python
fog = f..g
```

Python:
```python
fog = lambda *args, **kwargs: f(g(*args, **kwargs))
```

### Pipeline

Coconut uses the FSharp-style pipe operators for pipeline-style function application. All the operators have a precedence in-between backtick calls and comparisons and are left-associative. All operators also support in-place versions. The different operators are:
```
(|>)    => pipe forward
(|*>)   => multiple-argument pipe forward
(<|)    => pipe backward
(<*|)   => multiple-argument pipe backward
```

##### Example

Coconut:
```python
ans = 5 |> f |*> g
```

Python:
```python
ans = g(*f(5))
```

### Chain

Coconut uses the FSharp-style concatenation operator `::` for iterator chaining. Coconut's iterator chaining is done lazily, in that the arguments are not evaluated until they are needed. It has a precedence in-between bitwise or and backtick calls. The in-place operator is `::=`.

##### Python Docs

Make an iterator that returns elements from the first iterable until it is exhausted, then proceeds to the next iterable, until all of the iterables are exhausted. Used for treating consecutive sequences as a single sequence. Chained inputs are evaluated lazily. Roughly equivalent to:
```python
def chain(*iterables):
    # chain('ABC', 'DEF') --> A B C D E F
    for it in iterables:
        for element in it:
            yield element
```

##### Example

Coconut:
```python
combined = range(0, 5) :: range(10, 15)
```

Python:
```python
import itertools
combined = itertools.chain(range(0, 5), range(10, 15))
```

### Partial Application

Coconut uses a `$` sign right after a function before a function call to perform partial application. It has the same precedence as subscription.

##### Python Docs

Return a new `partial` object which when called will behave like _func_ called with the positional arguments _args_ and keyword arguments _keywords_. If more arguments are supplied to the call, they are appended to _args_. If additional keyword arguments are supplied, they extend and override _keywords_. Roughly equivalent to:
```python
def partial(func, *args, **keywords):
    def newfunc(*fargs, **fkeywords):
        newkeywords = keywords.copy()
        newkeywords.update(fkeywords)
        return func(*(args + fargs), **newkeywords)
    newfunc.func = func
    newfunc.args = args
    newfunc.keywords = keywords
    return newfunc
```
The `partial` object is used for partial function application which “freezes” some portion of a function’s arguments and/or keywords resulting in a new object with a simplified signature.

##### Example

Coconut:
```python
pow2 = pow$(2)
```

Python:
```python
import functools
pow2 = functools.partial(pow, 2)
```

### Iterator Slice

Coconut uses a `$` sign right after an iterator before a slice to perform iterator slicing. It works just like sequence slicing, with the exception that negative indices are not allowed and no guarantee is made that the original iterator be preserved (to preserve the original iterator, use Coconut's [`tee` function](#tee)). For dynamically determining the slice parameters, iterator slicing supports slicing with a `slice` object in the same way as can be done with normal slicing. It has the same precedence as subscription.

##### Python Docs

Make an iterator that returns selected elements from the _iterable_. If _start_ is non-zero, then elements from the _iterable_ are skipped until _start_ is reached. Afterward, elements are returned consecutively unless _step_ is set higher than one which results in items being skipped. If _stop_ is `None`, then iteration continues until the iterator is exhausted, if at all; otherwise, it stops at the specified position. Unlike regular slicing, iterator slicing does not support negative values for _start_, _stop_, or _step_. Can be used to extract related fields from data where the internal structure has been flattened (for example, a multi-line report may list a name field on every third line). Equivalent to:
```python
def islice(iterable, *args):
    # islice('ABCDEFG', 2) --> A B
    # islice('ABCDEFG', 2, 4) --> C D
    # islice('ABCDEFG', 2, None) --> C D E F G
    # islice('ABCDEFG', 0, None, 2) --> A C E G
    s = slice(*args)
    it = iter(range(s.start or 0, s.stop or sys.maxsize, s.step or 1))
    nexti = next(it)
    for i, element in enumerate(iterable):
        if i == nexti:
            yield element
            nexti = next(it)
```
If _start_ is `None`, then iteration starts at zero. If _step_ is `None`, then the step defaults to one.

##### Example

Coconut:
```python
selection = map(f, iteritem)$[5:10]
```

Python:
```python
import itertools
selection = itertools.islice(map(f, iteritem), 5, 10)
```

## IV. Built-Ins

### `reduce`

Coconut re-introduces Python 2's `reduce` built-in, using the `functools.reduce` version.

##### Python Docs

**reduce**(_function, iterable_**[**_, initializer_**]**)

Apply _function_ of two arguments cumulatively to the items of _sequence_, from left to right, so as to reduce the sequence to a single value. For example, `reduce((x, y) -> x+y, [1, 2, 3, 4, 5])` calculates `((((1+2)+3)+4)+5)`. The left argument, _x_, is the accumulated value and the right argument, _y_, is the update value from the _sequence_. If the optional _initializer_ is present, it is placed before the items of the sequence in the calculation, and serves as a default when the sequence is empty. If _initializer_ is not given and _sequence_ contains only one item, the first item is returned.

##### Example

Coconut:
```python
prod = reduce((*), items)
```

Python:
```python
import functools
prod = functools.reduce(operator.__mul__, items)
```

### `takewhile`

Coconut provides `functools.takewhile` as a built-in under the name `takewhile`.

##### Python Docs

**takewhile**(_predicate, iterable_)

Make an iterator that returns elements from the _iterable_ as long as the _predicate_ is true. Equivalent to:
```python
def takewhile(predicate, iterable):
    # takewhile(lambda x: x<5, [1,4,6,4,1]) --> 1 4
    for x in iterable:
        if predicate(x):
            yield x
        else:
            break
```

##### Example

Coconut:
```python
negatives = takewhile(numiter, (x) -> x<0)
```

Python:
```python
import functools
negatives = functools.takewhile(numiter, lambda x: x<0)
```

### `dropwhile`

Coconut provides `functools.dropwhile` as a built-in under the name `dropwhile`.

##### Python Docs

**dropwhile**(_predicate, iterable_)

Make an iterator that drops elements from the _iterable_ as long as the _predicate_ is true; afterwards, returns every element. Note: the iterator does not produce any output until the predicate first becomes false, so it may have a lengthy start-up time. Equivalent to:
```python
def dropwhile(predicate, iterable):
    # dropwhile(lambda x: x<5, [1,4,6,4,1]) --> 6 4 1
    iterable = iter(iterable)
    for x in iterable:
        if not predicate(x):
            yield x
            break
    for x in iterable:
        yield x
```

##### Example

Coconut:
```python
positives = dropwhile(numiter, (x) -> x<0)
```

Python:
```python
import functools
positives = functools.dropwhile(numiter, lambda x: x<0)
```

### `tee`

Coconut provides `itertools.tee` as a built-in under the name `tee`.

##### Python Docs

**tee**(_iterable, n=2_)

Return _n_ independent iterators from a single iterable. Equivalent to:
```python
def tee(iterable, n=2):
    it = iter(iterable)
    deques = [collections.deque() for i in range(n)]
    def gen(mydeque):
        while True:
            if not mydeque:             # when the local deque is empty
                newval = next(it)       # fetch a new value and
                for d in deques:        # load it to all the deques
                    d.append(newval)
            yield mydeque.popleft()
    return tuple(gen(d) for d in deques)
```
Once `tee()` has made a split, the original _iterable_ should not be used anywhere else; otherwise, the _iterable_ could get advanced without the tee objects being informed.

This itertool may require significant auxiliary storage (depending on how much temporary data needs to be stored). In general, if one iterator uses most or all of the data before another iterator starts, it is faster to use `list()` instead of `tee()`.

##### Example

Coconut:
```python
original, temp = tee(original)
sliced = temp$[5:]
```

Python:
```python
import itertools
original, temp = itertools.tee(original)
sliced = itertools.islice(temp, 5, None)
```

### `consume`

Coconut provides the `consume` function to efficiently exhaust an iterator and thus perform any lazy evaluation contained within it. `consume` takes one optional argument, `keep_last`, that defaults to 0 and specifies how many, if any, items from the end to return as an iterable (`None` will keep all elements). Equivalent to:
```python
def consume(iterable, keep_last=0):
    """Fully exhaust iterable and return the last keep_last elements."""
    return collections.deque(iterable, maxlen=keep_last)
```

##### Example

Coconut:
```python
range(10) |> map$((x) -> x**2) |> map$(print) |> consume
```

Python:
```python
collections.deque(map(print, map(lambda x: x**2, range(10))), maxlen=0)
```

### `datamaker`

Coconut provides the `datamaker` function to allow direct access to the base constructor of data types created with the Coconut `data` statement. This is particularly useful when writing alternative constructors for data types by overwriting `__new__`. Equivalent to:
```python
def datamaker(data_type):
    """Returns base data constructor of data_type."""
    return super(data, data_type).__new__$(data_type)
```

##### Example

Coconut:
```python
data trilen(h):
    def __new__(cls, a, b):
        return (a**2 + b**2)**0.5 |> datamaker(cls)
```

Python:
```python
import collections
class trilen(collections.namedtuple("trilen", "h")):
    __slots__ = ()
    def __new__(cls, a, b):
        return super(cls, cls).__new__(cls, (a**2 + b**2)**0.5)
```

### `recursive`

Coconut provides a `recursive` decorator to perform tail recursion optimization on a function written in a tail-recursive style, where it directly returns all calls to itself. Do not use this decorator on a function not written in a tail-recursive style or the function will likely break.

##### Example

Coconut:
```python
@recursive
def collatz(n):
    if n == 1:
        return True
    elif n%2 == 0:
        return collatz(n/2)
    else:
        return collatz(3*n+1)
```

Python:

_Can't be done without a long decorator definition. The full definition of the decorator in Python can be found in the Coconut header._

### `__coconut_version__`

Coconut provides the built-in double-underscore constant variable `__coconut_version__` to allow direct access to the version of Coconut that the code was compiled in.

## V. Keywords

### `data`

Coconut provides `data` blocks for the creation of immutable classes derived from `collections.namedtuple` and made immutable with `__slots__`. Coconut data statement syntax looks like:
```python
data <name>(<args>):
    <body>
```
`<name>` is the name of the new data type, `<args>` are the arguments to its constructor as well as the names of its attributes, and `<body>` contains the data type's methods.

##### Python Docs

Returns a new tuple subclass. The new subclass is used to create tuple-like objects that have fields accessible by attribute lookup as well as being indexable and iterable. Instances of the subclass also have a helpful docstring (with type names and field names) and a helpful `__repr__()` method which lists the tuple contents in a `name=value` format.

Any valid Python identifier may be used for a field name except for names starting with an underscore. Valid identifiers consist of letters, digits, and underscores but do not start with a digit or underscore and cannot be a keyword such as _class, for, return, global, pass, or raise_.

Named tuple instances do not have per-instance dictionaries, so they are lightweight and require no more memory than regular tuples.

##### Example

Coconut:
```python
data triangle(a, b, c):
    def is_right(self):
        return self.a**2 + self.b**2 == self.c**2
```

Python:
```python
import collections
class triangle(collections.namedtuple("triangle", "a, b, c")):
    __slots__ = ()
    def is_right(self):
        return self.a**2 + self.b**2 == self.c**2
```

### `match`

Coconut provides `match` statements to allow for Haskell-style pattern-matching. Coconut match statement syntax is
```python
match <pattern> in <value> [if <cond>]:
    <body>
[else:
    <body>]
```
where `<value>` is the item to match against, `<cond>` is an optional additional check, and `<body>` is simply code that is executed if the header above it succeeds. `<pattern>` follows its own, special syntax, defined roughly like so:
```
pattern := (
    "(" pattern ")"                 # parentheses
    | "None" | "True" | "False"     # constants
    | "=" NAME                      # check
    | NUMBER                        # numbers
    | STRING                        # strings
    | NAME ["=" pattern]            # capture
    | NAME "(" patterns ")"         # data types
    | "(" patterns ")"              # tuples
    | "[" patterns "]"              # lists
    | "(|" patterns "|)"            # lazy lists
    | "{" pattern_pairs "}"         # dictionaries
    | ["s"] "{" pattern_consts "}"  # sets
    | (                             # head-tail splits
        "(" patterns ")"                # tuples
        | "[" patterns "]"              # lists
      ) "+" pattern
    | pattern "+" (                 # init-last splits
        "(" patterns ")"                # tuples
        | "[" patterns "]"              # lists
      )
    | (                             # head-last splits
        "(" patterns ")"                # tuples
        | "[" patterns "]"              # lists
      ) "+" pattern "+" (
        "(" patterns ")"                # this match must be the same
        | "[" patterns "]"              #  construct as the first match
      )
    | (                             # iterator splits
        "(" patterns ")"                # tuples
        | "[" patterns "]"              # lists
        | "(|" patterns "|)"            # lazy lists
      ) "::" pattern
    | pattern "is" names            # type-checking
    | pattern "and" pattern         # match all
    | pattern "or" pattern          # match any
    )
```

`match` statements will take this pattern and attempt to "match" against it, performing the checks and deconstructions on the arguments as specified by the pattern. The different constructs that can be specified in a pattern, and their function, are:
- Constants, Numbers, and Strings: will only match to the same constant, number, or string in the same position in the arguments.
- Variables: will match to anything, and will be bound to whatever they match to, with some exceptions:
 * If the same variable is used multiple times, a check will be performed that each use match to the same value.
 * If the variable name `_` is used, nothing will be bound and everything will always match to it.
- Explicit Bindings (`<var>=<pattern>`): will bind `<var>` to `<pattern>`.
- Checks (`=<var>`): will check that whatever is in that position is equal to the previously defined variable `<var>`.
- Type Checks (`<var> is <types>`): will check that whatever is in that position is of type(s) `<types>` before binding the `<var>`.
- Data Types (`<name>(<args>)`): will check that whatever is in that position is of data type `<name>` and will match the attributes to `<args>`.
- Lists (`[<patterns>]`), Tuples (`(<patterns>)`), or Lazy lists (`(|<patterns>|)`): will only match a sequence (`collections.abc.Sequence`) of the same length, and will check the contents against `<patterns>`.
- Dicts (`{<pairs>}`): will only match a mapping (`collections.abc.Mapping`) of the same length, and will check the contents against `<pairs>`.
- Sets (`{<constants>}`): will only match a set (`collections.abc.Set`) of the same length and contents.
- Head-Tail Splits (`<list/tuple> + <var>`): will match the beginning of the sequence against the `<list/tuple>`, then bind the rest to `<var>`, and make it the type of the construct used.
- Init-Last Splits (`<var> + <list/tuple>`): exactly the same as head-tail splits, but on the end instead of the beginning of the sequence.
- Head-Last Splits (`<list/tuple> + <var> + <list/tuple>`): the combination of a head-tail and an init-last split.
- Iterator Splits (`<list/tuple/lazy list> :: <var>`, or `<lazy list>`): will match the beginning of an iterable (`collections.abc.Iterable`) against the `<list/tuple/lazy list>`, then bind the rest to `<var>` or check that the iterable is done.

##### Example

Coconut:
```python
def factorial(value):
    match 0 in value:
        return 1
    match n is int in value if n > 0:
        return n * factorial3(n-1)
    match [] in value:
        return []
    match [head] + tail in value:
        return [factorial(head)] + factorial(tail)
```

Python:

_Can't be done without a long series of checks for each `match` statement. See the compiled code for the Python syntax._

### `case`

Coconut's `case` statements are an extension of Coconut's `match` statements for use when many matches are to be attempted against one object, and only one should succeed. Each pattern in a case block is checked until a match is found, and then the corresponding body is executed, and the case block terminated. The syntax for case blocks is
```python
case <value>:
    match <pattern> [if <cond>]:
        <body>
    match <pattern> [if <cond>]:
        <body>
    ...
[else:
    <body>]
```
where `<pattern>` is any `match` pattern, `<value>` is the item to match against, `<cond>` is an optional additional check, and `<body>` is simply code that is executed if the header above it succeeds.

##### Example

Coconut:
```python
def classify_sequence(value):
    out = ""        # unlike with normal matches, only one of the patterns
    case value:     #  will match, and out will only get appended to once
        match ():
            out += "empty"
        match (_,):
            out += "singleton"
        match (x,x):
            out += "duplicate pair of "+str(x)
        match (_,_):
            out += "pair"
    else:
        raise TypeError()
    return out
```

Python:

_Can't be done without a long series of checks for each `match` statement. See the compiled code for the Python syntax._

### Backslash Escaping

To allow access to the valid Python variable names `data`, `match`, and `case` in Coconut, those keywords may be backslash-escaped to turn them into the variables instead. Additionally, to provide more seamless integration with Python 3.5, the variable names `async` and `await` must be backslash-escaped, and to provide backwards compatibility with Python 2, the variable name `nonlocal` must be backslash-escaped.

##### Example

Coconut:
```
\data = 5
print(\data)
```

Python:
```python
data = 5
print(data)
```

### Reserved Variables

The Coconut compiler will modify and reference certain variables with the assumption that the code being compiled does not modify them in any way. If your code does modify any of these variables, your code is unlikely to work properly. These reserved variables are:
- the single variable name `__coconut__`
- all variable names of the form `_coconut_name`

## VI. Coconut Module

### `coconut.convenience`

The recommended way to use Coconut as a module is to use `from coconut.convenience import` and import whatever convenience functions you'll be using. Specifications of the different convenience functions are as follows.

#### `coconut.convenience.parse`

**parse**(_code,_ **[**_mode_**]**)

Likely the most useful of the convenience functions, `parse` takes Coconut code as input and outputs the equivalent compiled Python code. The second argument, _mode_, is used to indicate the context for the parsing. Possible values of _mode_ are:

- `"exec"`: code for use in `exec` (the default)
- `"file"`: a stand-alone file
- `"single"`: a single line of code
- `"module"`: a file in a folder or module
- `"block"`: any number of lines of code
- `"eval"`: a single expression
- `"debug"`: lines of code with no header

#### `coconut.convenience.setup`

**setup**(**[[[**_target_**]**_, strict_**]**_, quiet_**]**)

If `--target`, `--strict`, or `--quiet` are desired for `parse`, the three arguments to `setup`, _target_, _strict_, and _quiet_, will each set the value of the corresponding flag. The possible values for each flag are:

- _target_: `None` (default), `"2"`, or `"3"`
- _strict_: `False` (default) or `True`
- _quiet_: `False` (default) or `True`

#### `coconut.convenience.cmd`

**cmd**(_args_, **[**_interact_**]**)

Executes the given _args_ as if they were fed to `coconut` on the command-line, with the exception that unless _interact_ is true or `-i` is passed, the interpreter will not be started. Additionally, since `parse` and `cmd` share the same convenience parsing object, any changes made to the parsing with `cmd` will work just as if they were made with `setup`.

#### `coconut.convenience.version`

**version**(**[**_which_**]**)

Retrieves a string containing information about the Coconut version. The optional argument _which_ is the type of version information desired. Possible values of _which_ are:

- `"num"`: the numerical version (the default)
- `"name"`: the version codename
- `"spec"`: the numerical version with the codename attached
- `"-v"`: the full string printed by `coconut -v`

#### `coconut.convenience.CoconutException`

If an error is encountered in a convenience function, a `CoconutException` instance may be raised. `coconut.convenience.CoconutException` is provided to allow catching such errors.
