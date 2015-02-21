Coconut
=======

Coconut is a modern, developer-friendly scripting language that compiles to Python, built for functional programming.

### Usage

`python coconut.py -h`

### Syntax

Coconut is based on Python 3 syntax and compiles to Python 3 code. Coconut makes significant changes from Python 3 syntax, however. The major differences from Python 3 are:

* New operators:
	* compose: `..` (in-place: `..=`)
	* curry: `$`
	* pipeline: `|>` (in-place: `=>`)
	* lambda: `->`
	* chain: `::` (in-place: `::=`)
* New syntax:
	* infix function calling: new `6 \mod\ 3` syntax
	* operator functions: new `(+)` syntax
	* function definition: alternative `f(x) = x` syntax
	* unicode symbols: supports unicode alternatives for most symbols
	* non-decimal integers: alternative `10110_2` syntax
* Changed syntax:
	* strings: only `b` prefix is allowed, raw strings use `` `string` `` syntax
	* lambda keyword: removed (use the operator instead)
	* backslash continuations: removed (use expanded parenthetical continuations instead)
* New built-ins:
	* right fold: `fold`
	* zip with: `zipwith`
	* tail recursion elimination: `recursive`
* New constructs (planned):
	* operator [re]definition
	* lazy evaluation
	* pattern matching
