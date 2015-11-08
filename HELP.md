# Coconut Tutorial

This tutorial will teach you how to write elegant, Pythonic code in a functional style using the [Coconut Programming Language](https://github.com/evhub/coconut). It is assumed that the reader knows some basic Python, but no other prior knowledge or experience is required.

- [I. Getting Started](#i-getting-started)
    - [Install Coconut](#install-coconut)
    - [Set Up a Workspace](#set-up-a-workspace)
    - [Start Coding!](#start-coding)
    - [Understanding Compiled Code](#understanding-compiled-code)
    - [Understanding Compiled Folders](#understanding-compiled-folders)
    - [Compile a Folder!](#compile-a-folder)
    - [Play Around!](#play-around)
- [II. Functions](#ii-functions)
    - [Lambdas](#lambdas)
    - [Partial Application](#partial-application)
    - [Function Composition](#function-composition)
    - [Pipe Forward](#pipe-forward)
    - [Operator Functions](#operator-functions)
    - [Backtick Calling](#backtick-calling)
    - [Function Definition](#function-definition)
    - [`reduce`](#reduce)
- [III. Iterators](#iii-iterators)
    - [Lazy Lists](#lazy-lists)
    - [Slicing](#slicing)
    - [Chaining](#chaining)
- [IV. Values](#iv-values)
    - [`data`](#data)
    - [`match`](#match)
    - [`case`](#case)
- [V. Advanced Features](#v-advanced-features)
    - [`takewhile` and `dropwhile`](#takewhile-and-dropwhile)
    - [`recursive`](#recursive)
    - [Implicit Partial Application](#implicit-partial-application)
    - [Set Literals](#set-literals)
    - [Non-Decimal Integers](#non-decimal-integers)
    - [Imaginary Literals](#imaginary-literals)
- [VI. Further Reading](#vi-further-reading)

## I. Getting Started

### Install Coconut

The first thing you're going to need to do is install Coconut. Since Coconut is hosted on the [Python Package Index](https://pypi.python.org/pypi/coconut), it can be installed easily using `pip`. Simply install [Python](https://www.python.org/downloads/), open up a command line prompt, and enter the following:
```
python -m pip install coconut
```

To test that `coconut` is working, make sure the Coconut command-line help appears when you enter into the command line:
```
coconut -h
```

### Set Up a Workspace

Now that you've installed Coconut, it's time to create your first Coconut program. Open up your favorite text editor and save a new file named `tutorial.coc`. It is recommended that you tell your text editor to treat all `.coc` files as Python source files for the purpose of syntax highlighting (Coconut and Python are close enough that this will work). All Coconut files should use the extension `.coc` so they can be recognized as such when compiling folders of many different files.

### Start Coding!

If you're familiar with Python, then you're already familiar with most of Coconut: Coconut is a strict superset of Python 3 syntax. Before we get into Coconut's unique features, though, let's start with a simple `hello, world!` program. Put this code inside your `tutorial.coc`:
```python
print("hello, world!")
```

Now it's time to compile the file and run it to test that it works. Open up your command line and enter in:
```
cd <tutorial.coc directory>
coconut tutorial.coc
python tutorial.py
```

If everything is working properly, you should see something like this:

`coconut tutorial.coc`
```
Coconut: Compiling <tutorial.coc directory>...
Coconut: Compiled <tutorial.py directory>.
```
`python tutorial.py`
```
hello, world!
```

### Understanding The Compiler

If you look in your `tutorial.coc` directory, you should notice that a new file, `tutorial.py` was created when you ran the compiler. That file contains the compiled Python code, which was why you had to enter `python tutorial.py` instead of `python tutorial.coc` to run it.

When compiling large projects, one will often want to compile all the code at once, and then have it transfered to a different location than the source. To accomplish this, simply pass the destination directory as the second argument to `coconut`, like so:
```
coconut <source directory> <destination directory>
```

_Note: The full documentation for all of the compiler's features can be found in the [DOCS](https://github.com/evhub/coconut/blob/master/DOCS.md)._

### Play Around!

As this tutorial starts introducing new concepts, it'll be useful to be able to enter Coconut code and have it compiled and run on the fly. To do this, you can start the Coconut interpreter by entering `coconut` into the console with no arguments.

## II. Functions

### Lambdas

In Python, lambdas are ugly and bulky, requiring the entire word `lambda` to be written out every time one is constructed. This is fine if in-line functions are very rarely needed, but in functional programming in-line functions are an essential tool, and so Coconut substitues in a much simpler lambda syntax: the `->` operator.

Just to demonstrate the lambda syntax, try modifying your `hello, world!` program by adding a function defined with a lambda that prints `"hello, "+arg+"!"`, and call it with `"lambdas"` as the `arg`:
```python
hello = (arg="world") -> print("hello, "+arg+"!") # Coconut still supports Python's "def" blocks,
hello("lambdas")                                  #  but we're trying to demonstrate lambdas here
```

Then run it and test that it works:

`coconut tutorial.coc`
```
...
```
`python tutorial.py`
```
hello, lambdas!
```

### Partial Application

Partial application, or currying, is a mainstay of functional programming, and for good reason: it allows the dynamic customization of functions to fit the needs of where they are being used. Partial application allows a new function to be created out of an old function with some of its arguments pre-specified. In Coconut, partial application is done by putting a `$` in-between a function and its arguments when calling it.

Here's an example of the power of partial application in Coconut:
```python
nums = range(0, 5)
expnums = map(pow$(2), nums)
print(list(expnums))
```
Try to predict what you think will be printed, then either use the interpreter or put this code in `tutorial.coc` and compile and run it to check if you were right.

### Function Composition

Another mainstay of functional programming, one very common in mathematics, is function composition, the ability to combine multiple functions into one. In Coconut, function composition is done with the `..` operator.

Here's an example of function composition:
```python
zipsum = map$(sum)..zip
print(list(zipsum([1,2,3], [10,20,30])))
```
Try again to predict what you think will be printed, then test it to see if you were right.

### Pipe Forward

Another useful functional programming operator is pipe forward, which makes pipeline-style programming, where a value is fed from function to function, transformed at each step, much easier and more elegant. In Coconut, pipe forward is done with the `|>` operator (or `|*>` for multiple arguments).

_Note: Pipe backwards is also available, and accessed by the `<|` operator (or `<*|` for multiple arguments), although it is usually less useful._

Here's an example:
```python
sq = (x) -> x**2
plus1 = (x) -> x+1
3 |> plus1 |> sq |> print
```
For all of the examples in this tutorial you should try predicting and then testing to check.

### Operator Functions

A very common thing to do in functional programming is to make use of function versions of built-in operators: currying them, composing them, and piping them. To make this easy, Coconut provides a short-hand syntax to access operator functions, where the operator is simply surrounded by parentheses to retrieve the function.

Here's an example:
```python
5 |> (-)$(2) |> (*)$(2) |> print
```
_Note: If you've been dutifully guessing and checking, you probablly guessed `6` for this and were surprised to find that the actual answer was `-6`. This happens because partial application always starts with the first argument, and the first argument to `(-)` is the thing you're subtracting from, not the thing you're subtracting!_

### Backtick Calling

Another common idiom in functional programming is to write functions that are intended to behave somewhat like operators. To assist with this, Coconut provides backtick calling, where a function can be called by surrounding it with backticks, and then its arguments placed around it.

Here's an example:
```python
mod = (%)
(5 `mod` 3) `print`
```

### Function Definition

Up until now, we've been using assignment to a lambda for function one-liners. While this works fine, it has some disadvantages, namely that the function will appear unnamed in any tracebacks, and both the `=` and `->` operators have to be typed out each time. To fix both of these problems, Coconut allows for mathematical function definition.

Here's an example:
```
def f(x) = x**2 + x # note the = instead of the :
5 |> f |> print
```

Coconut also supports backtick calling syntax in mathematical or normal function definition, like so:
```
def (a) `mod` (b) = a % b
```

### `reduce`

A Python 2 built-in that was removed in Python 3, Coconut re-introduces `reduce`, as it can be very useful for functional programming.

Here's an example:
```python
prod = reduce$((*))
range(1, 5) |> prod |> print
```

## III. Iterators

### Lazy Lists

Another mainstay of functional programming is lazy evaluation, where sequences are only evaluated when their contents are requested, allowing for things like infinite sequences. In Python, this can be done via iterators. Unfortunately, many of the tools necessary for working with iterators just like one would work with lists are absent.

Coconut aims to fix this, and the first part of that is Coconut's lazy lists. Coconut's lazy lists look, and work, much like normal lists or tuples, but are really represented as iterators, and thus can support lazy evaluation.

The syntax for lazy lists is simply to use so-called "banana brackets" (`(|` and `|)`) instead of normal brackets or parentheses to surround the list.

Here's an example:
```python
hello = (| print("hello,"), print("world!") |)
list(items)
```

### Slicing

Once you have constructed iterators using Python's `yield` statement or Coconut's lazy list syntax, you need to be able to work with those iterators in the same way you would work with lists.

Coconut provides the tools to do this, and the first part of that is Coconut's iterator slicing. Coconut's iterator slicing works much the same as Python's sequence slicing, and looks much the same as Coconut's partial application, but with brackets instead of parentheses.

Here's an example:
```python
def N():
    x = 0
    while True:
        yield x # the yield statement is Python's way of constructing iterators
        x += 1

N()$[10:15] |> list |> print
```
_Note: Unlike Python's sequence slicing, Coconut's iterator slicing makes no guarantee that the original iterator be preserved (to preserve the original iterator, use Coconut's `tee` function)._

### Chaining

Another useful tool to make working with iterators as easy as working with sequences is the ability to lazily combine multiple iterators together. This operation is called chain, and is equivalent to addition with sequences, except that nothing gets evaluated until it is needed. In Coconut, chaining is done with the `::` operator.

Here's an example:
```python
def N(n=0):
    return (0,) :: N(n+1) # no infinite loop because :: is lazy

(range(-10, 0) :: N())$[5:15] |> list |> print
```

## IV. Values

### `data`

Another  mainstay of functional programming that Coconut improves in Python is the use of values, or immutable data types. Immutable data can be very useful because it guarantees that once you have some data it won't change, but in Python creating custom immutable data types is difficult. Coconut makes it very easy by providing `data` blocks.

The syntax for `data` blocks is a cross between the syntax for functions and the syntax for classes. The first line looks like a function definition (`data name(args):`), but the rest of the body looks like a class, usually containing method definitions. This is because while `data` blocks actually end up as classes in Python, Coconut automatically creates a special, immutable constructor based on the given `args`.

Here's an example:
```python
data vector(x, y):
    def __abs__(self):
        return (self.x**2 + self.y**2)**.5

v = vector(3, 4)
v |> print # all data types come with a built-in __repr__
v |> abs |> print
v.x = 2 # this will fail because data objects are immutable
```

### `match`

While not only useful for working with values, pattern-matching is tailored to them, allowing the ability to check and deconstruct values. Coconut provides fully-featured pattern-matching through its `match` statements. Since `match` statements are complicated and don't have an equivalent in pure Python, it's best to simply jump right in and get a feel for them. Once you do, you'll see they make a lot of sense.

We'll start with a simple factorial function, implemented using match statements:
```python
def factorial(value):
    match 0 in value:
        return 1
    match n is int in value:
        if n > 0:
            return n * factorial(n-1)
    raise TypeError("invalid argument to factorial of: "+repr(value))

3 |> factorial |> print
```
You should now be able to see the basic syntax that match statements follow: `match <pattern> in <value>`. The match statement will attempt to match the value against the pattern, and if successful, bind any variables in the pattern to whatever is in the same position in the value, and execute the code below the match statement.

What is allowed in the match statement's pattern is the thing with no equivalent in Python. The factorial function gives you a couple of examples, though: constants (`0`), variables (`n`), and optional type checks appended to variables (`is int`).

Match statements also support, in their basic syntax, an `if <cond>` that will check the condition as well as the match before executing the code below. Knowing this, we can slightly simplify our factorial function from earlier:
```python
def factorial(value):
    match 0 in value:
        return 1
    match n is int in value if n > 0:
        return n * factorial(n-1)
    raise TypeError("invalid argument to factorial of: "+repr(value))

3 |> factorial |> print
```

Match statements are also very useful when working with lists or tuples, as they allow them to be easily deconstructed. Here's an example:
```python
def classify_sequence(value):
    match [] in value:
        return "empty"
    match [_] in value:
        return "empty"
    match [x,x] in value:
        return "duplicate pair of "+str(x)
    match [_,_] in value:
        return "pair"

[] |> classify_sequence |> print
() |> classify_sequence |> print
[1] |> classify_sequence |> print
(1,1) |> classify_sequence |> print
(1,2) |> classify_sequence |> print
(1,1,1) |> classify_sequence |> print
```
There are a couple of new things here that deserve attention:

First, the use of normal list notation to access and check against the contents of the sequence. Tuple notation can also be used, and both lists and tuples will match either.

Second, the use of the wildcard, `_`. Unlike other variables, like `x` in this example, `_` will never be bound to a value, and can be repeated multiple times without requiring the repeats to be the same value. Making sure all uses of the same variable are equal, however, like in `(x,x)` , is actually a very useful feature of match statements, as can be seen from this example.

Third, the use of an `else` statement on the end. This works much like else statements in other parts of Python: the code under it is only executed if the corresponding match fails.

Next, I mentioned earlier that match statements played nicely with values. Here's an example of that:
```python
data point(x, y):
    def transform(self, other):
        match point(x, y) in other:
            return point(self.x + x, self.y + y)
        else:
            raise TypeError("arg to transform must be a point")
    def __eq__(self, other):
        match point(=self.x, =self.y) in other:
            return True
        else:
            return False

point(1,2) |> point(3,4).transform |> print
point(1,2) |> point(1,2).__eq__ |> print
```
As you can see, matching to data types can be very useful. Values defined by the user with the `data` statement can be matched against and their contents accessed by specifically referencing arguments to the data type's constructor.

Additionally, this example demonstrates checks against predefined variables, which can be done by prefixing the variable name with an equals sign.

This combination of data types and match statements can be used to powerful effect to replicate the usage of algebraic data types in functional programming. Here's an example:
```python
data empty(): pass
data leaf(n): pass
data node(l, r): pass
tree = (empty, leaf, node)

def depth(t):
    match tree() in t:
        return 0
    match tree(n) in t:
        return 1
    match tree(l, r) in t:
        return 1 + max([depth(l), depth(r)])

empty() |> depth |> print
leaf(5) |> depth |> print
node(leaf(2), node(empty(), leaf(3))) |> depth |> print
```

Even more common, however, are head-tail list or tuple deconstructions. Here's an example:
```python
def duplicate_first(value):
    match l=([x] + xs) in value:
        return [x] + l
    else:
        raise TypeError()

[1,2,3] |> duplicate_first |> print
```
There are another couple new things here that deserve attention:

First, in addition to implicit bindings with variables, match statements also support explicit bindings with the equals sign.

Second, match statements allow a `+ <var>` (or `:: <var>` for any iterable) at the end of a list or tuple literal to match the rest of the sequence.

Additionally, all of the match syntax that you have learned up to this point can also be used in simple assignment statements, like so:
```python
def dictpoint(value):
    {"x":x is int, "y":y is int} = value
    return x, y

{"x":1, "y":2} |> dictpoint |> print
```
This example shows how match statement syntax can be used in a simple assignment statement, much like Python's destructuring assignment for lists and tuples. In this case, a dictionary is being destructured, which is another type of pattern, in addition to set literals, that can be matched against.

This example could also be rewritten more cleanly using Coconut's pattern-matching function definition, like so:
```python
def dictpoint({"x":x is int, "y":y is int}):
    return x, y

{"x":1, "y":2} |> dictpoint |> print
```

If a pattern-matching assignment statement or function definition fails, then instead of continuing on as if a `match` block had failed, a `MatchError` object will be raised describing the failure.

_Note: If you would like to be more explicit in your pattern-matching assignment or function definition statements, you can optionally place a `match` at the beginning of the line._

### `case`

`case` statements are simply a convenience for doing multiple `match` statements against the same value, where only one of them should succeed. They look like this:
```python
def factorial(value):
    case value:
        match 0:
            return 1
        match n is int if n > 0:
            return n * factorial(n-1)
    else:
        raise TypeError("invalid argument to factorial of: "+repr(value))
```
Note the absence of an `in` in the `match` statements: that's because the `value` in `case value` is taking its place. Additionally, unlike lone match statements, only one match statement inside of a case block will ever succeed, so you should put more general matches below more specific ones.

## V. Advanced Features

### `takewhile` and `dropwhile`

Coconut adds the new built-in functions `takewhile` and `dropwhile`. Both take a condition as the first argument, and an iterable as the second, and either take from, or drop from, that iterable while the condition is true.

_Note: The full documentation for both of these functions can be found in the [DOCS](https://github.com/evhub/coconut/blob/master/DOCS.md)._

### `recursive`

Coconut adds the new built-in decorator `recursive`, which optimizes any function written in a tail-recursive style, where it directly returns all calls to itself. Do not use this decorator on a function not written in a tail-recursive style or you will get strange errors.

### Implicit Partial Application

Coconut allows for commonly-used partial applications to be shorthanded like so:
* `.name` = `operator.attrgetter$("name")`
* `obj.` = `getattr$(obj)`
* `func$` = `($)$(func)`
* `series[]` = `operator.__getitem__$(series)`
* `series$[]` = the equivalent of `series[]` for iterators

### Set Literals

Coconut allows an optional `s` to be prepended in front of Python set literals. While in most cases this does nothing, in the case of the empty set it lets Coconut know that it is an empty set and not an empty dictionary. Additionally, an `f` is also supported, in which case a Python `frozenset` will be generated instead of a normal set.

### Non-Decimal Integers

Coconut allows non-decimal integers to be written in the form `base_num`. In many cases this is more readable than Python's default C-style notation.

### Imaginary Literals

Coconut allows imaginary number literals to be written with an `i` or `I` instead of a `j` or `J`, to make it more readable if used in a mathematical context.

## VI. Further Reading

This tutorial was too short to be able to fully cover all the features provided by the Coconut programming language. For the full documentation, see the [DOCS](https://github.com/evhub/coconut/blob/master/DOCS.md) file.
