# Coconut Tutorial

This tutorial will teach you how to write clean, functional, Pythonic code using the [Coconut](https://github.com/evhub/coconut) programming language. It is assumed that the reader knows some basic Python, but no other prior knowledge or experience is required.

## I. Getting Started

### 1. Install Coconut

The first thing you're going to need to do is install Coconut. Since Coconut is hosted on the [Python Package Index](https://pypi.python.org/pypi/coconut), it can be installed easily using `pip`. Simply install [Python](https://www.python.org/downloads/), open up a command line prompt, and enter the following:
```
python -m pip install coconut
```

To test that `coconut` is working, make sure the Coconut command-line help appears when you enter into the command line:
```
coconut -h
```

### 2. Set Up a Workspace

Now that you've installed Coconut, it's time to create your first Coconut program. Open up your favorite text editor and save a new file named `tutorial.coc`. It is recommended that you tell your text editor to treat all `.coc` files as Python source files for the purpose of syntax highlighting (Coconut and Python are close enough that this will work). All Coconut files should use the extension `.coc` so they can be recognized as such when compiling folders of many different files.

### 3. Start Coding!

If you're familiar with Python, then you're already familiar with most of Coconut. Coconut is nearly a strict superset of Python 3 syntax, with the sole exception of `lambda` statements, which will be later in this tutorial. For now, let's start with a simple `hello, world!` program. Put this code inside your `tutorial.coc`:
```
print("hello, world!")
```

Now it's time to compile the file and run it to test that it works. Open up your command line and enter in:
```
cd <tutorial.coc directory>
coconut tutorial.coc
python tutorial.py
```

If everything is working properly, you should see something like this:
```
$ coconut tutorial.coc
Coconut: Compiling '<tutorial.coc directory>'...
Coconut: Compiled '<tutorial.py directory>'.
$ python tutorial.py
hello, world!
```

### 4. Understanding Compiled Code

If you look in your `tutorial.coc` directory, you should notice that a new file, `tutorial.py` was created when you ran the compiler. That file contains the compiled Python code, which was why you had to enter `python tutorial.py` instead of `python tutorial.coc` to run it.

Open `tutorial.py` and look inside. You should see two sections, `Coconut Header` and `Compiled Coconut`. The `Coconut Header` section contains code inserted into all compiled coconut files, whereas the `Compiled Coconut` section contains the specific code the compiler produced from your source file.

### 5. Understanding Compiled Folders

You might have noticed that the `Coconut Header` section in `tutorial.py` is somewhat large (while Coconut tries to keep the size small, there's only so much it can do). This is because that section contains all the code necessary to set up the Coconut environment. Because Coconut needs to set up that environment in every file, it puts a header at the top.

It would be rather innefficient, however, if Coconut put that entire header in every file of a module (or other folder of files that are intended to stay together). Instead, when compiling a folder, Coconut puts all of that code in a `__coconut__.py` file in the folder directory.

### 6. Compile a Folder!

To compile a folder this way, simply call the `coconut` command with the folder directory as the first argument. Go ahead and try it on the `tutorial.coc` directory:
```
coconut <tutorial.coc directory>
cd <tutorial.coc directory>
python tutorial.py
```
If everything is working properly, you should see exactly the same output as before.

If you now go into the `tutorial.coc` directory, however, you should see a new file, `__coconut__.py`, which contains the header from earlier in non-class form, and if you now open the `tutorial.py` file, you should see a significantly shortened header that imports the larger header file.

_Note: When compiling modules, one will often want to compile to a different location than the source. To accomplish this, simply pass the destination directory as the second argument to `coconut`, like so:_
```
coconut <source directory> <destination directory>
```

### 7. Play Around!

As this tutorial starts introducing new concepts, it'll be useful to be able to enter Coconut code and have it compiled and run on the fly. To do this, you can start the Coconut interpreter by entering `coconut` into the console with no arguments.

## II. Functions

### 1. Lambdas

Now that you've gotten your feet wet with a simple `hello, world!` program, but before we delve into the special things Coconut can do that Python can't, we should cover the one exception to the rule of Coconut being a strict superset of Python: lambdas.

In Python, lambdas are ugly and bulky, requiring the entire word `lambda` to be written out every time one is constructed. This is fine if in-line functions are very rarely needed, but in functional programming in-line functions are an essential tool, and so Coconut substitues in a much simpler lambda syntax: the `->` operator.

Just to demonstrate the lambda syntax, try modifying your `hello, world!` program by adding a function defined with a lambda that prints `"hello, "+arg+"!"`, and call it with `"lambdas"` as the `arg`:
```
hello = (arg="world") -> print("hello, "+arg+"!")   # Coconut still supports Python's "def" blocks,
hello("lambdas")                                    #  but we're trying to demonstrate lambdas here
```

Then run it and test that it works:
```
$ coconut tutorial.coc
...
$ python tutorial.py
hello, lambdas!
```

### 2. Partial Application

Partial application, or currying, is a mainstay of functional programming, and for good reason: it allows the dynamic customization of functions to fit the needs of where they are being used. Partial application allows a new function to be created out of an old function with some of its arguments pre-specified. In Coconut, partial application is done by putting a `$` in-between a function and its arguments when calling it.

Here's an example of the power of partial application in Coconut:
```
nums = range(0, 5)
expnums = map(pow$(2), nums)
print(list(expnums))
```
Try to predict what you think will be printed, then either use the interpreter or put this code in `tutorial.coc` and compile and run it to check if you were right.

### 3. Function Composition

Another mainstay of functional programming, one very common in mathematics, is function composition, the ability to combine multiple functions into one. In Coconut, function composition is done by the `..` operator.

Here's an example of function composition:
```
zipsum = map$(sum)..zip
print(list(zipsum([1,2,3], [10,20,30])))
```
Try again to predict what you think will be printed, then test it to see if you were right.

### 4. Pipe Forward

Another useful functional programming operator is pipe forward, which makes pipeline-style programming, where a value is fed from function to function, transformed at each step, much easier and more elegant. In Coconut, pipe forward is done by the `|>` operator.

Here's an example:
```
sq = (x) -> x**2
plus1 = (x) -> x+1
3 |> plus1 |> sq |> print
```
For all of the examples in this tutorial you should try predicting and then testing to check.

### 5. Operator Functions

A very common thing to do in functional programming is to make use of function versions of built-in operators, currying them, composing them, and piping them. To make this easy, Coconut provides a short-hand syntax to access operator functions, where the operator is simply surrounded by parentheses to retrieve the function.

Here's an example:
```
5 |> (-)$(2) |> (*)$(2) |> print
```
_Note: If you've been dutifully guessing and checking, you probablly guessed `6` for this and were surprised to find that the actual answer was `-6`. This happens because partial application always starts with the first argument, and the first argument to `(-)` is the thing you're subtracting from, not the thing you're subtracting!_

### 6. Function Definition

Up until now, we've been using assignment to a lambda for function one-liners. While this works fine, it has some disadvantages, namely that the function will appear unnamed in any tracebacks, and both the `=` and `->` operators have to be typed out each time. To fix both of these problems, Coconut allows for mathematical function definition.

Here's an example:
```
f(x) = x**2 + x
5 |> f |> print
```

### 7. Infix Calling

Another common idiom in functional programming is to write functions that are intended to behave somewhat like operators. To assist with this, Coconut provies infix calling, where a two-argument function can be called by surrounding it with backticks and placing it in-between its two arguments.

Here's an example:
```
mod = (%)
print(5 `mod` 3)
```

### 8. `reduce`

A Python 2 built-in that was removed in Python 3, Coconut re-introduces `reduce`, as it can be very useful for functional programming.

Here's an example:
```
prod = reduce$((*))
range(1, 5) |> prod |> print
```

### 9. `recursive`

Tail-recursion is a common functional programming construct that, while automatically optimized in many programming languages, is not in Python. Coconut provides a way around this with the `recursive` decorator.

Here's an example:
```
@recursive
def next_mul_of(n, x):
    if x % n == 0:
        return x
    else:
        return next_mul_of(n, x+1)

12 |> next_mul_of $(5) |> print
```
_Note: Only use this decorator if your function is written in a tail-recursive style, where it directly returns any calls to itself. If `recursive` is used on a function that is not written in a tail-recursive style, you will get strange errors._

## III. Iterators

### 1. Slicing

Another mainstay of functional programming is lazy evaluation, where sequences are only evaluated when their contents are requested, allowing for things like infinite sequences. In Python, this can be done via iterators. Unfortunately, many of the tools necessary for working with iterators just like one would work with sequences are absent.

Coconut aims to fix this, and the first part of that is Coconut's iterator slicing. Coconut's iterator slicing works much the same as Python's sequence slicing, and looks much the same as Coconut's partial application, but with brackets instead of parentheses.

Here's an example:
```
def N():
    x = 0
    while True:
        yield x # the yield statement is Python's way of constructing iterators
        x += 1

N()$[10:15] |> list |> print
```
_Note: Unlike Python's sequence slicing, Coconut's iterator slicing makes no guarantee that the original iterator be preserved._

### 2. Chaining

Another useful tool to make working with iterators as easy as working with sequences is the ability to combine multiple iterators together. This operation is called chain, and is equivalent to addition with sequences. In Coconut, chaining is done by the `::` operator.

Here's an example:
```
(range(-10, 0) :: N())$[5:15] |> list |> print
```

### 3. `takewhile`

A useful built-in for working with iterators, `takewhile` will slice the iterator up to the point where the condition fails.

Here's an example:
```
N() |> takewhile$((>)$(5)) |> list |> print
```

## IV. Values

### `data`

The final mainstay of functional programming that Coconut improves in Python is the use of values, or immutable data. Immutable data can be very useful for the same reason that tuples can, but in Python creating custom immutable data types is difficult. Coconut makes it very easy by providing `data` blocks.

Here's an example:
```
data vector(x, y):
    def __abs__(self):
        return (self.x**2 + self.y**2)**.5

vector(3, 4) |> abs |> print
```

## V. Further Reading

This tutorial was too short to be able to fully cover all the features provided by the Coconut programming language. For the full documentation, see the [DOCS](https://github.com/evhub/coconut/blob/master/DOCS.md) file.
