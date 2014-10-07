CoconutScript
=============

CoconutScript is a modern, developer-friendly scripting language that compiles to Python, built for functional programming.

CoconutScript is based on Python 3 syntax, but will compile to either Python 3 or Python 2. CoconutScript does make significant changes from Python 3 syntax, however. The major differences from Python 3 are:

* Changed operators:
	* unary negation: `!` (instead of `~`)
* New operators:
	* compose: `..`
	* curry: `$`
	* loop: `~`
	* pipeline: `|>`
	* lambda: `->`
* Changed syntax:
	* lambda keyword: removed
	* backslash continuations: removed
	* trailing whitespace: disallowed
	* decorators: support all types of expressions
	* variable lists: can be wrapped in parentheses
	* strings: only `b` prefix is allowed, raw strings use `` ` ``
* New Constructs:
	* operator [re]definition
	* lazy evaluation
* Improved Built-Ins:
	* right fold: `fold` (instead of `reduce`)
	* zip: `zip`
	* zip with: `zipwith`
	* tail recursion elimination: `recursive`

CoconutScript is still in the early stages of development, and no stable release is currently available. If CoconutScript sounds interesting to you, however, we recommend you check back later when a stable release is available, or check out CoconutScript's spiritual predecessor, [Rabbit](https://github.com/evhub/rabbit).
