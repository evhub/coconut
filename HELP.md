# Coconut Tutorial

<!-- MarkdownTOC -->

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Starting Out](#starting-out)
    1. [Using the Interpreter](#using-the-interpreter)
    2. [Using the Compiler](#using-the-compiler)
    3. [Using IPython / Jupyter](#using-ipython--jupyter)
    4. [Case Studies](#case-studies)
4. [Case Study 1: Factorial](#case-study-1-factorial)
    1. [Imperative Method](#imperative-method)
    2. [Recursive Method](#recursive-method)
    3. [Iterative Method](#iterative-method)
5. [Case Study 2: Quick Sort](#case-study-2-quick-sort)
6. [Case Study 3: Vectors](#case-study-3-vectors)
7. [Case Study 4: Vector Fields](#case-study-4-vector-fields)

<!-- /MarkdownTOC -->

## Introduction

Welcome to the tutorial for the [Coconut Programming Language](http://evhub.github.io/coconut/)! If you're here, you've probably already seen Coconut's tagline: **simple, elegant, Pythonic functional programming**. But those are just words; what they mean in practice is that _all valid Python 3 is valid Coconut_ but Coconut builds on top of Python a suite of _simple, elegant utilities for functional programming_.

Why use Coconut? Coconut is built to be fundamentally _useful_. Coconut enhances the repetoire of Python programmers to include the tools of modern functional programming, in such a way that those tools are _easy_ and _fun_ to use; that is, _Coconut does to functional programming what Python did to imperative programming_. And Coconut code runs the same on _any Python version_, making the Python 2/3 split a thing of the past.

Specifically, Coconut adds to Python _built-in, syntactical support_ for:
- pattern-matching
- algebraic data types
- lazy lists
- destructuring assignment
- partial application
- function composition
- prettier lambdas
- infix notation
- pipeline-style programming
- operator functions

and much more!

## Installation

At its very core, Coconut is a compiler that turns Coconut code into Python code. That means that anywhere where you can use a Python script, you can also use a compiled Coconut script. To access that core compiler, Coconut comes with a command-line utility, which can:
- compile single Coconut files or entire Coconut projects
- interpret Coconut code on-the-fly
- launch IPython / Jupyter notebooks that use Coconut as the kernel

Installing Coconut, including all the features above, is drop-dead simple. Just
1. install [Python](https://www.python.org/downloads/),
2. open a command-line prompt,
3. and enter:
```bash
python -m pip install coconut
```

To check that your installation is functioning properly, try entering into the command-line
```bash
coconut -h
```
which should display Coconut's command-line help.

_Note: if you're having trouble installing Coconut, or if anything else mentioned in this tutorial doesn't seem to work for you, feel free to [open an issue](https://github.com/evhub/coconut/issues/new) and it'll be addressed as soon as possible._

## Starting Out

### Using the Interpreter

Now that you've got Coconut installed, the obvious first thing to do is to play around with it. To launch the Coconut interpreter, just go to the command-line and type
```bash
coconut
```
and you should see something like
```python
Coconut Interpreter:
(type "exit()" or press Ctrl-D to end)
>>>
```
which is Coconut's way of telling you you're ready to start entering code for it to evaluate. So let's do that!

In case you missed it earlier, _all valid Python 3 is valid Coconut_ (with one very minor [exception](http://coconut.readthedocs.org/en/master/DOCS.html#backslash-escaping)). That doesn't mean compiled Coconut will only run on Python 3—in fact, compiled Coconut will run the same on any Python version—but it does mean that only Python 3 code is guaranteed to compile as Coconut code.

That means that if you're familiar with Python, you're already familiar with a good deal of Coconut's core syntax and Coconut's entire standard library. To show that, let's try entering some basic Python into the Coconut interpreter.

```python
>>> print("hello, world!")
hello, world!
>>> 1 + 1
>>> print(1 + 1)
2
```

One thing you probably noticed here is that unlike the Python interpreter, the Coconut interpreter will not automatically print the result of a naked expression. This is a good thing, because it means your code will do exactly the same thing in the interpreter as it would anywhere else, but it might take some getting used to.

### Using the Compiler

Of course, while being able to interpret Coconut code on-the-fly is a great thing, it wouldn't be very useful without the ability to write and compile larger programs. To that end, it's time to write our first Coconut program: "hello, world!" Coconut-style.

First, we're going to need to create a file to put our code into. The file extension for Coconut source files is `.coc`, so let's create the new file `hello_world.coc`. After you do that, you should take the time now to tell your text editor to interpret `.coc` files as Python code; since all Python is valid Coconut, this should properly highlight a lot of your code, and highlight the rest well enough.

_Note: in Sublime Text, this is done by opening the `.coc` file, clicking on "Plain Text" at the bottom right, selecting "Open all with current extension as...", and then choosing "Python"._

Now let's put some code in our `hello_world.coc` file. Unlike in Python, where headers like
```python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import print_function, absolute_import, unicode_literals, division
```
are common and often very necessary, the Coconut compiler will automatically take care of all of that for you, so all you need to worry about is your own code. To that end, let's add the code for our "hello, world!" program.

In pure Python 3, "hello, world!" is
```python
print("hello, world!")
```
and while that will work in Coconut, equally as valid is to use a pipeline-style approach, which is what we'll do, and write
```python
"hello, world!" |> print
```
which should let you see very clearly how Coconut's `|>` operator enables pipeline-style programming: it allows an object to be passed along from function to function, with a different operation performed at each step. In this case, we are piping the object `"hello, world!"` into the operation `print`. Now let's save our simple "hello, world!" program, and try to run it.

Compiling Coconut files and projects with the Coconut command-line utility is incredibly simple. Just type
```bash
coconut /directory/to/hello_world.coc
```
where `/directory/to/` is the path from the current working directory to `hello_world.coc`. Running this command should yield the output
```bash
Coconut: Compiling       /directory/to/hello_world.coc ...
Coconut: Compiled to     /directory/to/hello_world.py .
```
which should deposit a new `hello_world.py` file in the same directory as the `hello_world.coc` file. You should then be able to run that file with
```bash
python /directory/to/hello_world.py
```
which should produce `hello, world!` as the output.

Compiling single files is not the only way to use the Coconut command-line utility, however. We can also compile all the Coconut files in a given directory simply by passing that directory as the first argument, which will get rid of the need to run the same Coconut header code in each file by storing it in a `__coconut__.py` file in the same directory.

The Coconut  compiler supports a large variety of different compilation options, the help for which can always be accessed by entering `coconut -h` into the command-line. One of the most useful of these is `--strict` (or `-s` for short), which will force you to make your source code obey certain cleanliness standards.

### Using IPython / Jupyter

Although all different types of programming can benefit from using more functional techniques, scientific computing, perhaps more than any other field, lends itself very well to functional programming, an observation the case studies in this tutorial are very good examples of. To that end, Coconut aims to provide extensive support for the established tools of scientific computing in Python.

That means supporting IPython, as modern Python programming, particularly in the sciences, has gravitated towards the use of [IPython](http://ipython.org/) (the python kernel for the [Jupyter](http://jupyter.org/) framework) instead of the classic Python shell. Coconut supports being used both as a kernel for IPython notebooks and consoles, and as an extension inside of the Python kernel.

To launch an IPython notebook with Coconut as the kernel, use the command
```bash
coconut --ipython notebook
```
and for launching an IPython console, use the command
```bash
coconut --ipython console
```
or equivalently, `--jupyter` can be substituted for `--ipython` in either command.

To use Coconut as an extension inside of the Python kernel, add the code
```python
%load_ext coconut
```
and then to run Coconut code, use
```python
%coconut <code>
```
or
```python
%%coconut <command-line-args>
<code>
```

### Case Studies

Because Coconut is built to be fundamentally _useful_, the best way to demo it is to show it in action. To that end, the majority of this tutorial will be showing how to apply Coconut to solve particular problems, which we'll call case studies.

These case studies are not intended to provide a complete picture of all of Coconut's features. For that, see Coconut's comprehensive [documentation](http://coconut.readthedocs.org/en/master/DOCS.html). Instead, they are intended to show how Coconut can actually be used to solve practical programming problems.

## Case Study 1: Factorial

In the first case study we will be defining a `factorial` function, that is, a function that computes `n!` where `n` is an integer `>= 0`. This is somewhat of a toy example, since Python can fairly easily do this, but it will serve as a good showcase of some of the basic features of Coconut and how they can be used to great effect.

To start off with, we're going to have to decide what sort of an implementation of `factorial` we want. There are many different ways to tackle this problem, but for the sake of concision we'll split them into three major categories: imperative, recursive, and iterative.

### Imperative Method

The imperative approach is the way you'd write `factorial` in a language like C. In Coconut, it looks something like this:
```python
def factorial(n):
    """Compute n! where n is an integer >= 0."""
    if n `isinstance` int and n >= 0:
        acc = 1
        for x in range(1, n+1):
            acc *= x
        return acc
    else:
        raise TypeError("the argument to factorial must be an integer >= 0")

```

Since the imperative approach is a fundamentally non-functional method, Coconut can't help us improve this example very much. Even here, though, the use of Coconut's infix notation in `` n `isinstance` int `` makes the code slightly clearer and easier to read.

### Recursive Method

Recursion is one of the most fundamental tools of functional programming, and is thus a place where Coconut can really help clear up confusing code. Here's the recursive approach in Coconut:
```python
def factorial(n):
    """Compute n! where n is an integer >= 0."""
    case n:
        match 0:
            return 1
        match _ is int if n > 0:
            return n * factorial(n-1)
    else:
        raise TypeError("the argument to factorial must be an integer >= 0")
```

Already, you can tell there's a lot more going on here than with the imperative method. That's intentional: Coconut is intended for functional programming, not imperative programminng, and so its new features are built to be most useful when programming in a functional style.

Let's take a look at the specifics of the syntax in this example. The first thing we see is `case n`. This statement starts a `case` block, in which only `match` statements can occur. Each `match` statement will attempt to match its given pattern against the value in the `case` block. Only the first successful match inside of any given `case` block will be executed. When a match is successful, any variable bindings in that match will also be performed. Additionally, as is true in this case, `match` statements can also have `if` guards that will check the given condition before the match is considered final. Finally, after the `case` block, an `else` statement is allowed, which will only be excectued if no `match` statement is.

Specifically, in this example, the first `match` statement checks whether `n` matches to `0`. If it does, it executes `return 1`. Then the second `match` statement checks whether `n` matches to `_ is int`, which performs an `isinstance` check on `n` against `int`, then checks whether `n > 0`, and if those are true, executes `return n * factorial(n-1)`. If neither of those two statements are executed, the `else` statement triggers and executes `raise TypeError("the argument to factorial must be an integer >= 0")`.

Although this example is very basic, pattern-matching is both one of Coconut's most powerful and most complicated features. As a general intuitive guide, it is helpful to think _assignment_ whenever you see the keyword `match`. A good way to showcase this is that all `match` statements can be converted into equivalent destructuring assignment statements, which are also valid Coconut. In this case, the destructuring assignment equivalent to the `factorial` function above, in Coconut, would be:
```python
def factorial(n):
    """Compute n! where n is an integer >= 0."""
    match_success = False
    try:
        match 0 = n
    except MatchError:
        try:
            match _ is int = n
        except MatchError:
            pass
        else:
            if n > 0:
                match_success = True
                return n * factorial(n-1)
    if not match_success:
        raise TypeError("the argument to factorial must be an integer >= 0")
```

As you can see, the destructuring assignment equivalent is much more cumbersome when you expect that the `match` might fail, which is why `match` statement syntax exists. But the destructuring assignment equivalent illuminates what exactly the pattern-matching is doing, by making it clear that `match` statements, and destructuring assignment statements, _are relly just fancy normal assignment statements_. In fact, the `match` keyword before the destructuring assignment statements in this example is optional. Exactly equivalent to the above would be:
```python
def factorial(n):
    """Compute n! where n is an integer >= 0."""
    match_success = False
    try:
        0 = n
    except MatchError:
        try:
            _ is int = n
        except MatchError:
            pass
        else:
            if n > 0:
                match_success = True
                return n * factorial(n-1)
    if not match_success:
        raise TypeError("the argument to factorial must be an integer >= 0")
```

It will be helpful to, as we continue to use Coconut's pattern-matching and destructuring assignment statements in further examples, think _assignment_ whenever you see the keyword `match`.

Up until now, for the recursive method, we have only dealt with pattern-matching, but there's actually another way that Coconut allows us to improve our `factorial` function: by writing it in a tail-recursive style and using Coconut's `recursive` decorator, like so:
```python
@recursive
def factorial(n, acc=1):
    """Compute n! where n is an integer >= 0."""
    case n:
        match 0:
            return acc
        match _ is int if n > 0:
            return factorial(n-1, acc*n)
    else:
        raise TypeError("the argument to factorial must be an integer >= 0")
```

This version is exactly equivalent to the original version, with the exception that it will never raise a `MaximumRecursionDepthError`, because Coconut's `recursive` decorator will optimize away the tail recursion into a `while` loop.

### Iterative Method

```python
product = reduce$((*))
```

```python
def factorial(n):
    """Compute n! where n is an integer >= 0."""
    case n:
        match 0:
            return 1
        match _ is int if n > 0:
            return range(1, n+1) |> product
    else:
        raise TypeError("the argument to factorial must be an integer >= 0")
```

## Case Study 2: Quick Sort

```python
def quick_sort(l):
    """Return sorted(l) where l is any iterator, using the quick sort algorithm."""
    match [head] :: tail in l:
        tail, tail_ = tee(tail)
        return (quick_sort((x for x in tail if x <= head))
            :: (head,)
            :: quick_sort((x for x in tail_ if x > head))
            )
    else:
        return iter()
```

## Case Study 3: Vectors

```python
data vector(pts):
    """Immutable n-vector."""
    def __new__(cls, *pts):
        """Create a new vector from the given pts."""
        if len(pts) == 1 and pts[0] `isinstance` vector:
            return pts[0] # vector(v) where v is a vector should return v
        else:
            return pts |> tuple |> datamaker(cls)
    def __abs__(self):
        """Return the magnitude of the vector."""
        return self.pts |> map$((x) -> x**2) |> sum |> ((s) -> s**0.5)
    def __eq__(self, other):
        """Compare whether two vectors are equal."""
        match vector(=self.pts) in other:
            return True
        else:
            return False
    def __add__(self, other):
        """Add two vectors together."""
        match vector(pts) in other if len(pts) == len(self.pts):
            return map((+), self.pts, pts) |*> vector
        else:
            raise TypeError("vectors can only be added to other vectors of the same length")
    def __mul__(self, other):
        """Scalar multiplication and dot product."""
        match vector(pts) in other:
            if len(pts) == len(self.pts):
                return map((*), self.pts, pts) |> sum # dot product
            else:
                raise TypeError("cannot dot product vector by other vector of different length")
        else:
            return self.pts |> map$((*)$(other)) |*> vector # scalar multiplication
    def __neg__(self):
        """Retrieve the negative of the vector."""
        return self.pts |> map$((-)) |*> vector
    def __sub__(self, other):
        """Subtract one vector from another."""
        match vector(pts) in other if len(pts) == len(self.pts):
            return map((-), self.pts, pts) |*> vector
        else:
            raise TypeError("vectors can only have other vectors of the same length subtracted from them")
```

## Case Study 4: Vector Fields

```python
def diagonal_line(x):
    y = 0
    while y <= x:
        yield x-y, y
        y += 1
def linearized_plane(n=0):
    return diagonal_line(n) :: linearized_plane(n+1)
def vector_field():
    return linearized_plane() |> map$((xy)-> vector(*xy))
def magnitude_field():
    return vector_field |> map$(abs)
```
