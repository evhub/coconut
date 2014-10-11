CoconutScript
=============

CoconutScript is a modern, developer-friendly scripting language that compiles to Python, built for functional programming.

CoconutScript is based on Python 3 syntax, but will compile to either Python 3 or Python 2. CoconutScript does make significant changes from Python 3 syntax, however. The major differences from Python 3 are:

* Changed operators:
	* unary negation: `!` (instead of `~`)
* New operators:
	* compose: `..` (in-place: `..=`)
	* curry: `$`
	* loop: `~` (in-place: `~=`)
	* pipeline: `|>` (in-place: `=>`)
	* lambda: `->`
	* set equal: `:=` (operator version of `=`)
* Changed syntax:
	* strings: only `b` prefix is allowed, raw strings use `` ` ``
	* functions: support alternative `f(x) = x` syntax
	* lambda keyword: removed
	* non-decimal integers: entered as integer`_`base
	* decorators: support all types of expressions
	* variable lists (for `global`, `nonlocal`, `del`): can be wrapped in parentheses
	* backslash continuations: removed
	* trailing whitespace: disallowed
* New Built-Ins:
	* right fold: `fold`
	* zip with: `zipwith`
	* tail recursion elimination: `recursive`
* New Constructs (Planned):
	* operator [re]definition
	* lazy evaluation
	* pattern matching

CoconutScript is still in the early stages of development, and no stable release is currently available. If CoconutScript sounds interesting to you, however, we recommend you check back later when a stable release is available, or check out CoconutScript's spiritual predecessor, [Rabbit](https://github.com/evhub/rabbit).
