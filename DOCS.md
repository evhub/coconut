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
coconut [-h] [-v] [-s] [-r] [-i] [-d [level]] [-c code] [--autopep8 ...] [source] [dest]
```

Positional Arguments:
```
source                path to the coconut file/module to compile
dest                  destination directory for compiled files (defaults to the source directory)
```

Optional Arguments:
```
-h, --help            show this help message and exit
-v, --version         print coconut and python version information
-s, --strict          enforce code cleanliness standards
-r, --run             run the compiled source instead of writing it
-i, --interact        force the interpreter to start (otherwise starts if no other command is given)
-d, --debug           enable debug output (0 is off, no arg defaults to 1, max is 2)
-c, --code            run a line of coconut passed in as a string
--autopep8            use autopep8 to format compiled code (remaining args passed to autopep8)
```

## II. Syntax

### Lambdas

Python's `lambda` statements are removed in Coconut in favor of a simple `->` operator.

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
map((/), divlist)
```

Python:
```
import operator
map(operator.__div__, divlist)
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

### Pipe Forward

### Chain

### Partial

### iSlice

## IV. Built-Ins

### `reduce`

### `takewhile`

### `recursive`

## V. Keywords

### `data`
