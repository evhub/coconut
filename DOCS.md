# Coconut Documentation

This documentation will cover all the technical details of the [Coconut](https://github.com/evhub/coconut) programming language. This documentation is not intended as a tutorialized introduction, only a technical specification. For a full introduction and tutorial of the Coconut programming language see the [HELP](https://github.com/evhub/coconut/blob/master/HELP.md) file.

### Overview

Coconut is based on Python 3 syntax and compiles to Python 3 code. Coconut makes significant changes from Python 3 syntax, however:

- New operators:
    x- lambda: `->`
    - compose: `..` (in-place: `..=`)
    - pipe forward: `|>` (in-place: `|>=`)
    - chain: `::` (in-place: `::=`)
    - partial and islice: `$`
- New syntax:
    - infix function calling: new ``6 `mod` 3`` syntax
    - operator functions: new `(+)` syntax
    - function definition: alternative `f(x) = x` syntax
    - non-decimal integers: alternative `10110_2` syntax
- New blocks:
    - immutable named-tuple-derived classes: `data`
- Changed syntax:
    - unicode symbols: supports unicode alternatives for most symbols
    - lambda keyword: removed (use the lambda operator instead)
- New built-ins:
    - right reduce: `reduce`
    - iterator take while: `takewhile`
    - tail recursion elimination: `recursive`
- New constructs: (planned)
    - operator [re]definition
    - pattern matching


## I. Command Line

Usage:
```
coconut [-h] [source] [dest] [-v] [-s] [-p] [-r] [-n] [-i] [-q] [-d [level]] [-c code] --autopep8 ...]
```

Positional Arguments:
```
source                path to the coconut file/folder to compile
dest                  destination directory for compiled files (defaults to the source directory)
```

Optional Arguments:
```
-h, --help            show this help message and exit
-v, --version         print coconut and python version information
-s, --strict          enforce code cleanliness standards
-p, --print           print the compiled source
-r, --run             run the compiled source
-n, --nowrite         disable writing the compiled source
-i, --interact        force the interpreter to start (otherwise starts if no other command is given)
-q, --quiet           suppress all info and debug output
-d, --debug           enable debug output (0 is off, no arg defaults to 1, max is 2)
-c, --code            run a line of coconut passed in as a string
--autopep8            use autopep8 to format compiled code (remaining args passed to autopep8)
```

## II. Syntax

### Lambdas

Python's `lambda` statements are removed in Coconut in favor of a simple, Coffee-style `->` operator. The operator has the same precedence as the old statement.

#### Python Docs

Lambda forms (lambda expressions) have the same syntactic position as expressions. They are a shorthand to create anonymous functions; the expression `(arguments) -> expression` yields a function object. The unnamed object behaves like a function object defined with:
```
def <lambda>(arguments):
    return expression
```
See section _Function definitions_ for the syntax of parameter lists. Note that functions created with lambda forms cannot contain statements or annotations.

#### Example

Coconut:
```
(x, y) -> 2*(x+y)
```

Python:
```
lambda x, y: 2*(x+y)
```

### Infix Calling

Coconut uses Haskell-style infix calling, where the infix function is surrounded by backticks and placed between its two operands. Infix calling has a precedence in-between chaining and piping.

#### Example

Coconut:
```
x `mod` 2 == 1
```

Python:
```
mod(x, 2) == 1
```

### Function Definition

Coconut allows for math-style in-line function definition, where the body of the function is assigned directly to the function call.

#### Example

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
(|>)        => (__coconut__.pipe)
(..)        => (__coconut__.compose)
(::)        => (__coconut__.chain)
(`)         => (__coconut__.infix)
($)         => (__coconut__.partial)
[$]         => (__coconut__.slice)
(+)         => (__coconut__.operator.__add__)
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
(is)        => (__coconut__.operator.is_)
(and)       => (__coconut__.bool_and)
(or)        => (__coconut__.bool_or)
```

### Non-Decimal Integers

In addition to Python's normal binary, octal, and hexadecimal integer syntax, Coconut also supports its own universal non-decimal integer syntax, where the base is put after an underscore at the end.

#### Python Docs

A base-n literal consists of the digits 0 to n-1, with `a` to `z` (or `A` to `Z`) having values 10 to 35. The default base is 10. The allowed values are 0 and 2-36. Base 0 means to interpret exactly as a code literal, so that the actual base is 2, 8, 10, or 16, and so that `int('010', 0)` is not legal, while `int('010')` is, as well as `int('010', 8)`.

#### Example

Coconut:
```
10A_12 == 154
```

Python:
```
int("10A", 12) == 154
```

### Unicode Alternatives

Python supports unicode alternatives to many different symbols. The full list of symbols is as follows:
```
→ (\u2192)                  => "->"
↦ (\u21a6)                  => "|>"
⇒ (\u21d2)                  => "|>="
× (\xd7)                    => "*"
↑ (\u2191) or ×× (\xd7\xd7) => "**"
÷ (\xf7)                    => "/"
÷/ (\xf7/)                  => "//"
− (\u2212)                  => "-" (only subtraction)
⁻ (\u207b)                  => "-" (only negation)
¬ (\xac)                    => "~"
¬= (\xac=)                  => "!="
∧ (\u2227) or ∩ (\u2229)    => "&"
∨ (\u2228) or ∪ (\u222a)    => "|"
⊻ (\u22bb) or ⊕ (\u2295)    => "^"
« (\xab)                    => "<<"
» (\xbb)                    => ">>"
… (\u2026)                  => "..."
```

## III. Operators

### Compose

Coconut uses the `..` operator for function composition. It has a precedence in-between subscription and exponentiation. The in-place operator is `..=`.

#### Example

Coconut:
```
fog = f..g
```

Python:
```
fog = lambda *args, **kwargs: f(g(*args, **kwargs))
```

### Pipe Forward

Coconut uses the FSharp-style pipe forward operator `|>` for reverse function application. It has a precedence in-between infix calls and comparisons. The in-place operator is `|>=`.

#### Example

Coconut:
```
ans = 5 |> f |> g
```

Python:
```
ans = g(f(5))
```

### Chain

Coconut uses the FSharp-style concatenation operator `::` for iterator chaining. It has a precedence in-between bitwise or and infix calls. The in-place operator is `::=`.

#### Python Docs

Make an iterator that returns elements from the first iterable until it is exhausted, then proceeds to the next iterable, until all of the iterables are exhausted. Used for treating consecutive sequences as a single sequence. Equivalent to:
```
def chain(*iterables):
    # chain('ABC', 'DEF') --> A B C D E F
    for it in iterables:
        for element in it:
            yield element
```

#### Example

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

#### Python Docs

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

#### Example

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

Coconut uses a `$` sign right after an iterator before a slice to perform iterator slicing. It works just like sequence slicing, with the exception that no guarantee that the original iterator be preserved is made. It has the same precedence as subscription.

#### Python Docs

Make an iterator that returns selected elements from the iterable. If _start_ is non-zero, then elements from the iterable are skipped until _start_ is reached. Afterward, elements are returned consecutively unless _step_ is set higher than one which results in items being skipped. If _stop_ is `None`, then iteration continues until the iterator is exhausted, if at all; otherwise, it stops at the specified position. Unlike regular slicing, iterator slicing does not support negative values for _start_, _stop_, or _step_. Can be used to extract related fields from data where the internal structure has been flattened (for example, a multi-line report may list a name field on every third line). Equivalent to:
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

#### Example

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

#### Python Docs

*reduce*(_function, iterable_*[*_, initializer_*]*)

Apply _function_ of two arguments cumulatively to the items of _sequence_, from left to right, so as to reduce the sequence to a single value. For example, `reduce((x, y) -> x+y, [1, 2, 3, 4, 5])` calculates `((((1+2)+3)+4)+5)`. The left argument, _x_, is the accumulated value and the right argument, _y_, is the update value from the _sequence_. If the optional _initializer_ is present, it is placed before the items of the sequence in the calculation, and serves as a default when the sequence is empty. If _initializer_ is not given and _sequence_ contains only one item, the first item is returned.

#### Example

Coconut:
```
prod = reduce((*), items)
```

Python:
```
import functools
prod = functools.reduce(operator.__mul__, items)
```

### `takewhile`

Coconut provides `functools.takewhile` as a built-in under the name `takewhile`.

#### Python Docs

*takewhile*(_predicate, iterable_)

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

#### Example

Coconut:
```
positives = takewhile(numiter, (x) -> x>0)
```

Python:
```
import functools
positives = functools.takewhile(numiter, lambda x: x>0)
```

### `recursive`

Coconut provides a `recursive` decorator to perform tail recursion optimization on a function written in a tail-recursive style.

#### Example

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

Coconut provides `data` blocks for the creation of immutable classes derived from `collections.namedtuple`.

#### Python Docs

Returns a new tuple subclass. The new subclass is used to create tuple-like objects that have fields accessible by attribute lookup as well as being indexable and iterable. Instances of the subclass also have a helpful docstring (with typename and field_names) and a helpful `__repr__()` method which lists the tuple contents in a `name=value` format.

Any valid Python identifier may be used for a field name except for names starting with an underscore. Valid identifiers consist of letters, digits, and underscores but do not start with a digit or underscore and cannot be a keyword such as _class, for, return, global, pass, or raise_.

Named tuple instances do not have per-instance dictionaries, so they are lightweight and require no more memory than regular tuples.

#### Example

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
