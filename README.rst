Coconut
=======

Coconut is a simple, modern, developer-friendly scripting language that compiles to Python, built for functional programming. Coconut can be found on: GitHub_, PyPI_.

.. _GitHub: https://github.com/evhub/coconut
.. _PyPI: https://pypi.python.org/pypi/coconut

Installation
------------

Enter in console::

    pip install coconut

Command Line
------------

Usage::

  coconut [-h] [-v] [-s] [-r] [-i] [-d [level]] [-c code] [--autopep8 ...] [source] [dest]

Positional Arguments::

  source                path to the coconut file/module to compile
  dest                  destination directory for compiled files (defaults to the source directory)

Optional Arguments::

  -h, --help            show this help message and exit
  -v, --version         print coconut and python version information
  -s, --strict          enforce code cleanliness standards
  -r, --run             run the compiled source instead of writing it
  -i, --interact        force the interpreter to start (otherwise starts if no other command is given)
  -d, --debug           enable debug output (0 is off, no arg defaults to 1, max is 2)
  -c, --code            run a line of coconut passed in as a string
  --autopep8            use autopep8 to format compiled code (remaining args passed to autopep8)

Overview
--------

Coconut is based on Python 3 syntax and compiles to Python 3 code. Coconut makes significant changes from Python 3 syntax, however:

- New operators:
    - lambda: ``->``
    - compose: ``..`` (in-place: ``..=``)
    - pipe forward: ``|>`` (in-place: ``|>=``)
    - chain: ``::`` (in-place: ``::=``)
    - partial and islice: ``$``
- New syntax:
    - infix function calling: new ``6 `mod` 3`` syntax
    - operator functions: new ``(+)`` syntax
    - function definition: alternative ``f(x) = x`` syntax
    - non-decimal integers: alternative ``10110_2`` syntax
- New blocks:
    - immutable named-tuple-derived classes: ``data``
- Changed syntax:
    - unicode symbols: supports unicode alternatives for most symbols
    - lambda keyword: removed (use the lambda operator instead)
- New built-ins:
    - right reduce: ``reduce``
    - iterator take while: ``takewhile``
    - tail recursion elimination: ``recursive``
- New constructs: (planned)
    - operator [re]definition
    - pattern matching

Tutorial
--------

A full introduction and tutorial of the Coconut progamming language can be found in the HELP_ file.

.. _HELP: https://github.com/evhub/coconut/blob/master/HELP.md
