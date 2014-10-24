CoconutScript
=============

CoconutScript is a modern, developer-friendly scripting language that compiles to Python, built for functional programming.

CoconutScript is based on Python 3 syntax, but will compile to either Python 3 or Python 2. CoconutScript does make significant changes from Python 3 syntax, however. The major differences from Python 3 are:

* New operators:
	* compose: `..` (in-place: `..=`)
	* curry: `$`
	* loop: `~` (in-place: `~=`)
	* pipeline: `|>` (in-place: `=>`)
	* lambda: `->`
* Changed operators:
	* unary negation: `!` (replaces `~`, only difference is it negates `bool`)
* New syntax:
	* infix function calling: new `6 \mod\ 3` syntax
	* operator functions: alternative `(+)` syntax
	* function definition: alternative `f(x) = x` syntax
	* unicode symbols: supports unicode alternatives for most symbols
	* non-decimal integers: alternative `10110_2` syntax
* Changed syntax:
	* strings: only `b` prefix is allowed, raw strings use `` `string` `` syntax
	* lambda keyword: removed (use the operator instead)
	* decorators: support all types of expressions
	* all statement arguments: can be wrapped in parentheses
	* backslash continuations: removed
	* trailing whitespace: disallowed
* New built-ins:
	* right fold: `fold`
	* zip with: `zipwith`
	* tail recursion elimination: `recursive`
* New constructs (planned):
	* operator [re]definition
	* lazy evaluation
	* pattern matching

CoconutScript is still in the early stages of development, and no stable release is currently available. If CoconutScript sounds interesting to you, however, I recommend you check back later when a stable release is available, or check out CoconutScript's spiritual predecessor, [Rabbit](https://github.com/evhub/rabbit).
