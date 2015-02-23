Coconut
=======

Coconut is a simple, modern, developer-friendly scripting language that compiles to Python, built for functional programming.

Usage
-----

usage: coconut [-h] [-c ...] [-r] [-n] [-i] [-d] [--autopep8 ...]
               [path [path ...]]

positional arguments:
  path:               names of files to compile

optional arguments:
  -h, --help          show this help message and exit
  
  -c, --code          run code passed in as string
  
  -r, --run           run files after compiling them
  
  -n, --nowrite       disable writing of compiled code
  
  -i, --interact      start the interpreter after compiling files
  
  -d, --debug         shows compiled python being executed
  
  --autopep8          use autopep8 to format compiled code

Syntax
------

Coconut is based on Python 3 syntax and compiles to Python 3 code. Coconut makes significant changes from Python 3 syntax, however:

* New operators:
	* compose: ``..`` (in-place: ``..=``)
	* curry: ``$``
	* pipeline: ``|>`` (in-place: ``=>``)
	* lambda: ``->``
	* join: ``::`` (in-place: ``::=``)
* New syntax:
	* infix function calling: new ``6 \mod\ 3`` syntax
	* operator functions: new ``(+)`` syntax
	* function definition: alternative ``f(x) = x`` syntax
	* unicode symbols: supports unicode alternatives for most symbols
	* non-decimal integers: alternative ``10110_2`` syntax
* Changed syntax:
	* strings: only ``b`` prefix is allowed, raw strings use ```string``` syntax
	* lambda keyword: removed (use the operator instead)
	* backslash continuations: removed (use improved parenthetical continuations instead)
* New built-ins:
	* right fold: ``fold``
	* zip with: ``zipwith``
	* tail recursion elimination: ``recursive``
* New constructs: (planned)
	* operator [re]definition
	* pattern matching
