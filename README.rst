Coconut
=======

Coconut is a simple, modern, developer-friendly scripting language that compiles to Python, built for functional programming.

Installation
------------

::pip install coconut

Usage
-----

usage:
  coconut [-h] [-v] [-s] [-r] [-n] [-i] [-d] [-c ...] [--autopep8 ...] [path [path ...]]

positional arguments:
  :path:              names of files/directories to compile

optional arguments:
  -h, --help          show this help message and exit

  -v, --version       print the coconut version

  -s, --strict        enforce code cleanliness standards

  -r, --run           run files after compiling them

  -n, --nowrite       disable writing of compiled code

  -i, --interact      start the interpreter after compiling files

  -d, --debug         show compiled python being executed

  -c, --code          run code passed in as string

  --autopep8          use autopep8 to format compiled code

Syntax
------

Coconut is based on Python 3 syntax and compiles to Python 3 code. Coconut makes significant changes from Python 3 syntax, however:

- New operators:
    - compose: ``..`` (in-place: ``..=``)
    - partial: ``$``
    - pipeline: ``|>`` (in-place: ``=>``)
    - lambda: ``->``
    - chain: ``::`` (in-place: ``::=``)
- New syntax:
    - infix function calling: new ``6 `mod` 3`` syntax
    - operator functions: new ``(+)`` syntax
    - function definition: alternative ``f(x) = x`` syntax
    - non-decimal integers: alternative ``10110_2`` syntax
- Changed syntax:
    - unicode symbols: supports unicode alternatives for most symbols
    - lambda keyword: removed (use the lambda operator instead)
- New built-ins:
    - right reduce: ``reduce``
    - zip with function: ``zipwith``
    - tail recursion elimination: ``recursive``
- New constructs: (planned)
    - operator [re]definition
    - pattern matching
