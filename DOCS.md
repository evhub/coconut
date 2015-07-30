# Coconut Documentation

This documentation will cover all the technical details of the [Coconut](https://github.com/evhub/coconut) programming language. This documentation is not intended as a tutorialized introduction, only a technical specification. For a full introduction and tutorial of the Coconut programming language, see the [HELP](https://github.com/evhub/coconut/blob/master/HELP.md) file.

- [I. Command Line](#i-command-line)
    - [Usage](#usage)
    - [Positional Arguments](#positional-arguments)
    - [Optional Arguments](#optional-arguments)
    - [Python Versions](#python-versions)
    - [Compiled Files](#compiled-files)
    - [strict Mode](#strict-mode)
    - [IPython](#ipython)
- [II. Syntax](#ii-syntax)
    - [Lambdas](#lambdas)
    - [Backtick Calling](#backtick-calling)
    - [Function Definition](#function-definition)
    - [Operator Functions](#operator-functions)
    - [Enhanced Set Literals](#enhanced-set-literals)
    - [Non-Decimal Integers](#non-decimal-integers)
    - [Enhanced Decorators](#enhanced-decorators)
    - [Enhanced Else Statements](#enhanced-else-statements)
    - [Unicode Alternatives](#unicode-alternatives)
    - [Code Passthrough](#code-passthrough)
- [III. Operators](#iii-operators)
    - [Compose](#compose)
    - [Pipe Forward](#pipe-forward)
    - [Chain](#chain)
    - [Partial](#partial)
    - [Iterator Slice](#iterator-slice)
- [IV. Built-Ins](#iv-built-ins)
    - [reduce](#reduce)
    - [itemgetter](#itemgetter)
    - [attrgetter](#attrgetter)
    - [methodcaller](#methodcaller)
    - [takewhile](#takewhile)
    - [dropwhile](#dropwhile)
    - [tee](#tee)
    - [recursive](#recursive)
- [V. Keywords](#v-keywords)
    - [data](#data)
    - [match](#match)
    - [case](#case)
    - [Backslash Escaping](#backslash-escaping)
- [VI. Coconut Module](#vi-coconut-module)
    - [coconut.convenience](#coconutconvenience)

## I. Command Line

### Usage

```
coconut [-h] [source] [dest] [-v] [-s] [-p] [-r] [-n] [-i] [-q] [-d] [-c code] [--autopep8 ...]
```

### Positional Arguments

```
source                path to the coconut file/folder to compile
dest                  destination directory for compiled files (defaults to the source directory)
```

### Optional Arguments

```
-h, --help            show this help message and exit
-v, --version         print coconut and python version information
-s, --strict          enforce code cleanliness standards
-p, --print           print the compiled source
-r, --run             run the compiled source
-n, --nowrite         disable writing the compiled source
-i, --interact        force the interpreter to start (otherwise starts if no other command is given)
-q, --quiet           suppress all informational output
-d, --debug           enable printing debug output
-c, --code            run a line of coconut passed in as a string (can also be accomplished with a pipe)
--autopep8            use autopep8 to format compiled code (remaining args passed to autopep8)
```

### Python Versions

The primary target for Coconut is Python 3, but the compiler will run on Python 2 or 3, and, unless constructs are used that are only present in Python 3, will attempt to produce universal code that will run like it does in Python 3 in Python 2. The officially supported versions are `2.7`, `3.3`, `3.4`, and `3.5`.

### Compiled Files

Files compiled by the `coconut` command-line utility will vary based on compilation parameters. If an entire folder of files is compiled, a `__coconut__.py` file will be created to house necessary functions, whereas if only a single file is compiled, that information will be stored within a header inside the file. Regardless of which method is used, each `.coc` file found will compile to another file with the same name, except with `.py` instead of `.coc`, which will hold the compiled code.

If an extension other than `.py` is desired for the compiled files, such as `.pyde` for [Python Processing](http://py.processing.org/), then that extension can be put before `.coc` in the source file name, and it will be used instead of `.py` for the compiled files. For example, `name.coc` will compile to `name.py`, whereas `name.pyde.coc` will compile to `name.pyde`.

### `--strict` Mode

If the `--strict` or `-s` flag is enabled, Coconut will throw errors on various style problems. These are:
- Mixing of tabs and spaces
- Use of the Python-style `lambda` statement
- Use of backslash continuations
- Trailing whitespace

It is recommended that you use the `--strict` flag if you are starting a new Coconut project.

### IPython

If you prefer [IPython](http://ipython.org/) to the normal Python shell, coconut can also be used as an IPython extension. The code `%load_ext coconut` will provide access to the `%coconut` and `%%coconut` magics. The `%coconut` magic will run a line of Coconut with default parameters, whereas the `%%coconut` magic will take command-line arguments on the first line, and run any coconut code provided in the rest of the cell with those parameters.

## II. Syntax

### Lambdas

Coconut provides an alternative to Python's `lambda` statements in favor of a simple, Coffee-style `->` operator. The operator has the same precedence as the old statement.

##### Python Docs

Lambda forms (lambda expressions) have the same syntactic position as expressions. They are a shorthand to create anonymous functions; the expression `(arguments) -> expression` yields a function object. The unnamed object behaves like a function object defined with:
```
def <lambda>(arguments):
    return expression
```
Note that functions created with lambda forms cannot contain statements or annotations.

##### Example

Coconut:
```
(x, y) -> 2*(x+y)
```

Python:
```
lambda x, y: 2*(x+y)
```

### Backtick Calling

Coconut allows for Haskell-style infix calling, where a function is surrounded by backticks and then can have arguments placed in front of or behind it. Backtick calling has a precedence in-between chaining and piping.

##### Example

Coconut:
```
(x `mod` 2) `f` == 1
```

Python:
```
f(mod(x, 2)) == 1
```

### Function Definition

Coconut allows for math-style in-line function definition, where the body of the function is assigned directly to the function call. The function call that is assinged to can be parenthesis-style or backtick-style.

##### Example

Coconut:
```
exp(x, b=2) = b**x
```

Python:
```
def exp(x, b=2): return b**x
```

### Operator Functions

Coconut uses Haskell-style operator function short-hand, where the operator placed within parentheses can be used as a function. The full list of operator functions is as follows:
```
(|>)        => (<lambda>)
(..)        => (<lambda>)
(::)        => (__coconut__.chain)
($)         => (__coconut__.partial)
[$]         => (__coconut__.islice)
(+)         => (__coconut__.operator.__add__)
[+]         => (__coconut__.operator.__concat__)
(-)         => (__coconut__.operator.__sub__)
(\u207b)    => (__coconut__.operator.__neg__)
(*)         => (__coconut__.operator.__mul__)
(**)        => (__coconut__.operator.__pow__)
(/)         => (__coconut__.operator.__truediv__)
(//)        => (__coconut__.operator.__floordiv__)
(%)         => (__coconut__.operator.__mod__)
(&)         => (__coconut__.operator.__and__)
(^)         => (__coconut__.operator.__xor__)
(|)         => (__coconut__.operator.__or__)
(<<)        => (__coconut__.operator.__lshift__)
(>>)        => (__coconut__.operator.__rshift__)
(<)         => (__coconut__.operator.__lt__)
(>)         => (__coconut__.operator.__gt__)
(==)        => (__coconut__.operator.__eq__)
(<=)        => (__coconut__.operator.__le__)
(>=)        => (__coconut__.operator.__ge__)
(!=)        => (__coconut__.operator.__ne__)
(~)         => (__coconut__.operator.__inv__)
(not)       => (__coconut__.operator.__not__)
(and)       => (<lambda>)
(or)        => (<lambda>)
(is)        => (__coconut__.operator.is_)
(in)        => (__coconut__.operator.__contains__)
```

##### Example

Coconut:
```
prod = reduce((*), items)
```

Python:
```
import operator
prod = reduce(operator.__mul__, items)
```

### Enhanced Set Literals

In addition to Python's normal set literals using curly braces, Coconut supports a special `s` (for `set`) or `f` (for `frozenset`) in front of a Python-like set literal to ensure it is a set literal of the specified type even when it otherwise would not be, such as when it is empty, or if a `frozenset` is desired.

#### Example

Coconut:
```
empty_frozen_set = f{}
```

Python:
```
empty_frozen_set = frozenset()
```

### Non-Decimal Integers

In addition to Python's normal binary, octal, and hexadecimal integer syntax, Coconut also supports its own universal non-decimal integer syntax, where the base is put after an underscore at the end.

##### Python Docs

A base-n literal consists of the digits 0 to n-1, with `a` to `z` (or `A` to `Z`) having values 10 to 35. The default base is 10. The allowed values are 0 and 2-36. Base 0 means to interpret exactly as a code literal, so that the actual base is 2, 8, 10, or 16, and so that `010`, `010_0`, and `010_8` are 8, while `10`, `10_0`, and `010_10` are 10.

##### Example

Coconut:
```
10A_12 == 154
```

Python:
```
int("10A", 12) == 154
```

### Enhanced Decorators

Unlike Python, which only supports a single variable or function call in a decorator, Coconut supports any expression.

##### Example

Coconut:
```
@ wrapper1 .. wrapper2 $(arg)
func(x) = x**2
```

Python:
```
def wrapper(func):
    return wrapper1(wrapper2(arg, func))
@wrapper
def func(x):
    return x**2
```

### Enhanced Else Statements

Coconut supports the compound statements `try`, `if`, and `match` on the end of an `else` statement like any simple statement would be. This is most useful for mixing `match` and `if` statements together, but also allows for compound `try` statements.

##### Example

Coconut:
```
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
```
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

### Unicode Alternatives

Coconut supports unicode alternatives to many different symbols. The full list of symbols is as follows:
```
→ (\u2192)                  => "->"
↦ (\u21a6)                  => "|>"
⇒ (\u21d2)                  => "|>="
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

Coconut supports the ability to pass arbitrary code through the compiler without being touched, for compatibility with other variants of Python, such as [Cython](http://cython.org/). Anything placed between `\(` and the corresponding close paren will be passed through, as well as any line starting with `\\`, which will have the additional effect of allowing indentation under it.

##### Example

Coconut:
```
\\cdef f(x):
    return x |> g
```

Python:
```
cdef f(x):
    return g(x)
```

## III. Operators

### Compose

Coconut uses the `..` operator for function composition. It has a precedence in-between subscription and exponentiation. The in-place operator is `..=`.

##### Example

Coconut:
```
fog = f..g
```

Python:
```
fog = lambda *args, **kwargs: f(g(*args, **kwargs))
```

### Pipe Forward

Coconut uses the FSharp-style pipe forward operator `|>` for reverse function application. It has a precedence in-between backtick calls and comparisons. The in-place operator is `|>=`.

##### Example

Coconut:
```
ans = 5 |> f |> g
```

Python:
```
ans = g(f(5))
```

### Chain

Coconut uses the FSharp-style concatenation operator `::` for iterator chaining. It has a precedence in-between bitwise or and backtick calls. The in-place operator is `::=`.

##### Python Docs

Make an iterator that returns elements from the first iterable until it is exhausted, then proceeds to the next iterable, until all of the iterables are exhausted. Used for treating consecutive sequences as a single sequence. Equivalent to:
```
def chain(*iterables):
    # chain('ABC', 'DEF') --> A B C D E F
    for it in iterables:
        for element in it:
            yield element
```

##### Example

Coconut:
```
combined = range(0,5) :: range(10,15)
```

Python:
```
import itertools
combined = itertools.chain(range(0,5), range(10,15))
```

### Partial

Coconut uses a `$` sign right after a function before a function call to perform partial application. It has the same precedence as subscription.

##### Python Docs

Return a new `partial` object which when called will behave like _func_ called with the positional arguments _args_ and keyword arguments _keywords_. If more arguments are supplied to the call, they are appended to _args_. If additional keyword arguments are supplied, they extend and override _keywords_. Roughly equivalent to:
```
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
```
pow2 = pow$(2)
```

Python:
```
import functools
pow2 = functools.partial(pow, 2)
```

### Iterator Slice

Coconut uses a `$` sign right after an iterator before a slice to perform iterator slicing. It works just like sequence slicing, with the exception that no guarantee that the original iterator be preserved is made (to preserve the original iterator, use Coconut's `tee` function). It has the same precedence as subscription.

##### Python Docs

Make an iterator that returns selected elements from the _iterable_. If _start_ is non-zero, then elements from the _iterable_ are skipped until _start_ is reached. Afterward, elements are returned consecutively unless _step_ is set higher than one which results in items being skipped. If _stop_ is `None`, then iteration continues until the iterator is exhausted, if at all; otherwise, it stops at the specified position. Unlike regular slicing, iterator slicing does not support negative values for _start_, _stop_, or _step_. Can be used to extract related fields from data where the internal structure has been flattened (for example, a multi-line report may list a name field on every third line). Equivalent to:
```
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
```
selection = map(f, iteritem)$[5:10]
```

Python:
```
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
```
prod = reduce((*), items)
```

Python:
```
import functools
prod = functools.reduce(operator.__mul__, items)
```

### `itemgetter`

Coconut provides `operator.itemgetter` as a built-in under the name `itemgetter`.

##### Python Docs

**itemgetter**(_\*items_)

Return a callable object that fetches _items_ from its operand using the operand’s `__getitem__()` method. If multiple items are specified, returns a tuple of lookup values. For example:

- After `f = itemgetter(2)`, the call `f(r)` returns `r[2]`.
- After `g = itemgetter(2, 5, 3)`, the call `g(r)` returns `(r[2], r[5], r[3])`.

Equivalent to:
```
def itemgetter(*items):
    if len(items) == 1:
        item = items[0]
        def g(obj):
            return obj[item]
    else:
        def g(obj):
            return tuple(obj[item] for item in items)
    return g
```

The items can be any type accepted by the operand’s `__getitem__` method. Dictionaries accept any hashable value. Lists, tuples, and strings accept an index or a slice.

##### Example

Coconut:
```
letters = "ABCDEFG" |> itemgetter(1, 3, 5) |> reduce$([+])
```

Python:
```
import operator
letters = functools.reduce(operator.__concat__, operator.itemgetter(1, 3, 5)("ABCDEFG"))
```

### `attrgetter`

Coconut provides `operator.attrgetter` as a built-in under the name `attrgetter`.

##### Python Docs

**attrgetter**(_\*attrs_)

Return a callable object that fetches _attrs_ from its operand. If more than one attribute is requested, returns a tuple of attributes. The attribute names can also contain dots. For example:

- After `f = attrgetter('name')`, the call `f(b)` returns `b.name`.
- After `f = attrgetter('name', 'date')`, the call `f(b)` returns `(b.name, b.date)`.
- After `f = attrgetter('name.first', 'name.last')`, the call `f(b)` returns `(b.name.first, b.name.last)`.

Equivalent to:
```
def attrgetter(*items):
    if any(not isinstance(item, str) for item in items):
        raise TypeError('attribute name must be a string')
    if len(items) == 1:
        attr = items[0]
        def g(obj):
            return resolve_attr(obj, attr)
    else:
        def g(obj):
            return tuple(resolve_attr(obj, attr) for attr in items)
    return g

def resolve_attr(obj, attr):
    for name in attr.split("."):
        obj = getattr(obj, name)
    return obj
```

##### Example

Coconut:
```
coords = point |> attrgetter("x", "y")
```

Python:
```
import operator
coords = operator.attrgetter("x", "y")(point)
```

### `methodcaller`

Coconut provides `operator.methodcaller` as a built-in under the name `methodcaller`.

##### Python Docs

**methodcaller**(_name_**[**_, args..._**]**)

Return a callable object that calls the method _name- on its operand. If additional arguments and/or keyword arguments are given, they will be given to the method as well. For example:

- After `f = methodcaller('name')`, the call `f(b)` returns `b.name()`.
- After `f = methodcaller('name', 'foo', bar=1)`, the call `f(b)` returns `b.name('foo', bar=1)`.

Equivalent to:
```
def methodcaller(name, *args, **kwargs):
    def caller(obj):
        return getattr(obj, name)(*args, **kwargs)
    return caller
```

##### Example

Coconut:
```
clean = map(methodcaller("strip"), unclean)
```

Python:
```
import operator
clean = map(operator.methodcaller("strip"), unclean)
```

### `takewhile`

Coconut provides `functools.takewhile` as a built-in under the name `takewhile`.

##### Python Docs

**takewhile**(_predicate, iterable_)

Make an iterator that returns elements from the _iterable_ as long as the _predicate_ is true. Equivalent to:
```
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
```
negatives = takewhile(numiter, (x) -> x<0)
```

Python:
```
import functools
negatives = functools.takewhile(numiter, lambda x: x<0)
```

### `dropwhile`

Coconut provides `functools.dropwhile` as a built-in under the name `dropwhile`.

##### Python Docs

**dropwhile**(_predicate, iterable_)

Make an iterator that drops elements from the _iterable_ as long as the _predicate_ is true; afterwards, returns every element. Note: the iterator does not produce any output until the predicate first becomes false, so it may have a lengthy start-up time. Equivalent to:
```
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
```
positives = dropwhile(numiter, (x) -> x<0)
```

Python:
```
import functools
positives = functools.dropwhile(numiter, lambda x: x<0)
```

### `tee`

Coconut provides `itertools.tee` as a built-in under the name `tee`.

##### Python Docs

**tee**(_iterable, n=2_)

Return _n_ independent iterators from a single iterable. Equivalent to:
```
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
```
original, temp = tee(original)
sliced = temp$[5:]
```

Python:
```
import itertools
original, temp = itertools.tee(original)
sliced = itertools.islice(temp, 5, None)
```

### `recursive`

Coconut provides a `recursive` decorator to perform tail recursion optimization on a function written in a tail-recursive style, where it directly returns all calls to itself. Do not use this decorator on a function not written in a tail-recursive style or you will get strange errors.

##### Example

Coconut:
```
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

## V. Keywords

### `data`

Coconut provides `data` blocks for the creation of immutable classes derived from `collections.namedtuple`. Coconut data statement syntax looks like:
```
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
```
data triangle(a, b, c):
    def is_right(self):
        return self.a**2 + self.b**2 == self.c**2
```

Python:
```
import collections
class triangle(collections.namedtuple("triangle", "a, b, c")):
    def is_right(self):
        return self.a**2 + self.b**2 == self.c**2
```

### `match`

Coconut provides `match` statements to allow for Haskell-style pattern-matching. Coconut match statement syntax looks like:
```
match <pattern> in <value> [if <cond>]:
    <body>
[else:
    <body>]
```
`<value>` is the item to match against, `<cond>` is an optional additional check, and `<body>` is simply code that is executed if the header above it succeeds. `<pattern>` follows its own, special syntax, defined roughly like so:
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
    | "{" pattern_pairs "}"         # dictionaries
    | ["s"] "{" pattern_consts "}"  # sets
    | (                             # head-tail splits
        "(" patterns ")"                # tuples
        | "[" patterns "]"              # lists
      ) (
        "+"                             # for a tuple/list
        | "::"                          # for an iterator
      ) pattern
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
- Lists (`[<patterns>]`) or Tuples (`(<patterns>)`): will only match a sequence (`collections.abc.Sequence`) of the same length, and will check the contents against `<patterns>`.
- Dicts (`{<pairs>}`): will only match a mapping (`collections.abc.Mapping`) of the same length, and will check the contents against `<pairs>`.
- Sets (`{<constants>}`): will only match a set (`collections.abc.Set`) of the same length and contents.
- List/Tuple Splits (`<list/tuple> + <var>`): will match the beginning of the [im]mutable sequence against the `<list/tuple>`, then bind the rest to `<var>`, and call `list` or `tuple` on it, depending on which construct was used.
- Iterator Splits (`<list/tuple> :: <var>`): will match the beginning of an iterable (`collections.abc.Iterable`) against the `<list/tuple>`, then bind the rest to `<var>`.

##### Example

Coconut:
```
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

_Can't be done._

### `case`

Coconut's `case` statements are an extension of Coconut's `match` statements for use when many matches are to be attempted against one object, and only one should succeed. Each pattern in a case block is checked until a match is found, and then the corresponding body is executed, and the case block terminated. The syntax for case blocks is:
```
case <value>:
    match <pattern> [if <cond>]:
        <body>
    match <pattern> [if <cond>]:
        <body>
    ...
[else:
    <body>]
```
`<pattern>` is any `match` pattern, `<value>` is the item to match against, `<cond>` is an optional additional check, and `<body>` is simply code that is executed if the header above it succeeds.

##### Example

Coconut:
```
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

_Can't be done._

### Backslash Escaping

To allow access to the valid Python variable names `data`, `match`, and `case` in Coconut, those keywords may be backslash-escaped to turn them into the variables instead. Additionally, to provide more seamless integration with Python 3.5, the variable names `async` and `await` must also be backslash-escaped.

##### Example

Coconut:
```
\data = 5
print(\data)
```

Python:
```
data = 5
print(data)
```

## VI. Coconut Module

### `coconut.convenience`

The recommended way to use Coconut as a module is to use `from coconut.convenience import` and import whatever convenience functions you'll be using. Specifications of the different convenience functions are as follows.

#### `coconut.convenience.parse`

**parse**(_code,_ **[**_mode_**]**)

Likely the most useful of the convenience functions, `parse` takes Coconut code as input and outputs the equivalent compiled Python code. The second argument, _mode_, is used to indicate the context for the parsing. Possible values of _mode_ are:

- `"file"`: a stand-alone file (the default)
- `"single"`: a single line of code
- `"module"`: a file in a folder or module
- `"block"`: many lines of code
- `"eval"`: a single expression

#### `coconut.convenience.cmd`

**cmd**(_args_, **[**_interact_**]**)

Executes the given _args_ as if they were fed to `coconut` on the command-line, with the exception that unless _interact_ is true or `-i` is passed, the interpreter will not be started.

#### `coconut.convenience.version`

**version**(**[**_which_**]**)

Retrieves a string containing information about the Coconut version. The optional argument _which_ is the type of version information desired. Possible values of _which_ are:

- `"num"`: the numerical version (the default)
- `"name"`: the version codename
- `"full"`: the numerical version with the codename attached
- `"-v"`: the full string printed by `coconut -v`
