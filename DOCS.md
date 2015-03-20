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
-x New syntax:
    - infix function calling: new ``6 `mod` 3`` syntax
    - operator functions: new `(+)` syntax
    - function definition: alternative `f(x) = x` syntax
    - non-decimal integers: alternative `10110_2` syntax
- New blocks:
    - immutable named-tuple-derived classes: `data`
-x Changed syntax:
    - unicode symbols: supports unicode alternatives for most symbols
    - lambda keyword: removed (use the lambda operator instead)
-x New built-ins:
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

Python's `lambda` statements are removed in Coconut in favor of a simple, Coffee-style `->` operator.

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

Coconut uses Haskell-style infix calling, where the infix function is surrounded by backticks and placed between its two operands.

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

Coconut uses Haskell-style operator function short-hand, where the operator placed within parentheses can be used as a function.

#### Example

Coconut:
```
divprod = reduce((/), divlist)
```

Python:
```
import operator
divprod = reduce(operator.__div__, divlist)
```

### Non-Decimal Integers

In addition to Python's normal binary, octal, and hexadecimal integer syntax, Coconut also supports its own universal non-decimal integer syntax, where the base is put after an underscore at the end.

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

Coconut uses the `..` operator for function composition. The in-place operator is `..=`.

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

Coconut uses the FSharp-style pipe forward operator `|>` for reverse function application. The in-place operator is `|>=`.

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

Coconut uses the FSharp-style concatenation operator `::` for iterator chaining. The in-place operator is `::=`.

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

Coconut uses a `$` sign right after a function before a function call to perform partial application.

#### Example

Coconut:
```
root2 = sqrt$(2)
```

Python:
```
import functools
root2 = functools.partial(sqrt, 2)
```

### iSlice

Coconut uses a `$` sign right after an iterator before a slice to perform iterator slicing.

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

#### Example

Coconut:
```
expfold = reduce((**), explist)
```

Python:
```
import functools
expfold = functools.reduce(operator.__pow__, explist)
```

### `takewhile`

Coconut provides `functools.takewhile` as a built-in under the name `takewhile`.

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

Coconut provides `data` blocks for the creation on immutable classes derived from `collections.namedtuple`.

#### Example

Coconut:
```
data vector(x, y):
    def __abs__(self):
        return (self.x**2 + self.y**2)**.5
```

Python:
```
import collections
class vector(collections.namedtuple("vector", "x, y")):
    def __abs__(self):
        return (self.x**2 + self.y**2)**.5
```
