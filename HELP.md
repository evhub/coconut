# Coconut Tutorial

<!-- MarkdownTOC -->

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Starting Out](#starting-out)
    1. [Using the Interpreter](#using-the-interpreter)
    2. [Using the Compiler](#using-the-compiler)
4. [Case Studies](#case-studies)
5. [Case Study 1: Factorial](#case-study-1-factorial)
    1. [Imperative Method](#imperative-method)
    2. [Recursive Method](#recursive-method)
    3. [Iterative Method](#iterative-method)
6. [Case Study 2: Quick Sort](#case-study-2-quick-sort)
7. [Case Study 3: Vectors](#case-study-3-vectors)
8. [Case Study 4: Vector Fields](#case-study-4-vector-fields)

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
```bash
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

## Case Studies

Because Coconut is built to be fundamentally _useful_, the best way to demo it is to show it in action. To that end, the majority of this tutorial will be showing how to apply Coconut to solve particular problems, which we'll call case studies.

These case studies are not intended to provide a complete picture of all of Coconut's features. For that, see Coconut's excellent [documentation](http://coconut.readthedocs.org/en/master/DOCS.html). Instead, they are intended to show how Coconut can actually be used to solve practical programming problems.

## Case Study 1: Factorial

In the first case study we will be defining a `factorial` function, that is, a function that computes `n!` where `n` is an integer `>= 0`. This is somewhat of a toy example, since Python can fairly easily do this, but it will serve as a good showcase of some of the basic features of Coconut and how they can be used to great effect.

To start off with, we're going to have to decide what sort of an implementation of `factorial` we want. There are many different ways to tackle this problem, but for the sake of concision we'll split them into three major categories: imperative, recursive, and iterative.

### Imperative Method

The imperative approach is the way you'd write `factorial` in a language like C. In pure Python, it looks something like this:

```python
def factorial(n):
    """Compute n! where n is an integer >= 0."""
    if isinstance(n, int) and n >= 0:
        acc = 1
        for x in range(1, n+1):
            acc *= x
        return acc
    else:
        raise TypeError("the argument to factorial must be an integer >= 0")

```

Although the imperative approach is a fundamentally ugly method, Python does a spectacularly good job of making it look nice, and that's why this is mostly a toy example. But let's take a look at the recursive method.

### Recursive Method

```python
def factorial(n):
    """Compute n! where n is an integer >= 0."""
    case n:
        match 0:
            return 1
        match n is int if n > 0:
            return n * factorial(n-1)
    else:
        raise TypeError("the argument to factorial must be an integer >= 0")
```

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
        match n is int if n > 0:
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
