# Coconut Tutorial

<!-- MarkdownTOC -->

1. [Introduction](#introduction)
    1. [Installation](#installation)
2. [Starting Out](#starting-out)
    1. [Using the Interpreter](#using-the-interpreter)
    2. [Using the Compiler](#using-the-compiler)
    3. [Using IPython / Jupyter](#using-ipython--jupyter)
    4. [Case Studies](#case-studies)
3. [Case Study 1: Factorial](#case-study-1-factorial)
    1. [Imperative Method](#imperative-method)
    2. [Recursive Method](#recursive-method)
    3. [Iterative Method](#iterative-method)
4. [Case Study 2: Quick Sort](#case-study-2-quick-sort)
5. [Case Study 3: Vectors](#case-study-3-vectors)
6. [Case Study 4: Vector Fields](#case-study-4-vector-fields)
7. [Filling in the Gaps](#filling-in-the-gaps)

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

### Installation

At its very core, Coconut is a compiler that turns Coconut code into Python code. That means that anywhere where you can use a Python script, you can also use a compiled Coconut script. To access that core compiler, Coconut comes with a command-line utility, which can:
- compile single Coconut files or entire Coconut projects
- interpret Coconut code on-the-fly
- hook into existing Python applications like IPython / Jupyter

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

That means supporting IPython / Jupyter, as modern Python programming, particularly in the sciences, has gravitated towards the use of [IPython](http://ipython.org/) (the python kernel for the [Jupyter](http://jupyter.org/) framework) instead of the classic Python shell. Coconut supports being used both as a kernel for Jupyter notebooks and consoles, and as an extension inside of the IPython kernel.

To launch a Jupyter notebook with Coconut as the kernel, use the command
```bash
coconut --jupyter notebook
```
and to launch a Jupyter console, use the command
```bash
coconut --jupyter console
```
or equivalently, `--ipython` can be substituted for `--jupyter` in either command.

To use Coconut as an extension inside of the IPython kernel, type the code
```python
%load_ext coconut
```
into your IPython notebook or console, and then to run Coconut code, use
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

The imperative approach is the way you'd write `factorial` in a language like C. Imperative approaches involve lots of state change, where variables are regularly modified and loops are liberally used. In Coconut, the imperative approach to the `factorial` problem looks like this:
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

# Test cases:
-1 |> factorial |> print # TypeError
0.5 |> factorial |> print # TypeError
0 |> factorial |> print # 1
3 |> factorial |> print # 6
```
Before we delve into what exactly is happening here, let's give it a run and make sure the test cases check out. If we were really writing a Coconut program, we'd want to save and compile an actual file, but since we're just playing around, let's try copy-pasting into the interpreter. Here, you should get `1`, `6`, and then two `TypeError`s.

Now that we've verified it works, let's take a look at what's going on. Since the imperative approach is a fundamentally non-functional method, Coconut can't help us improve this example very much. Even here, though, the use of Coconut's infix notation (where the function is put in-between its arguments, surrounded in backticks) in `` n `isinstance` int `` makes the code slightly cleaner and easier to read.

### Recursive Method

The recursive approach is the first of the fundamentally functional approaches, in that it doesn't involve the state change and loops of the imperative approach. Recursive approaches avoid the need to change variables by making that variable change implicit in the recursive function call. Here's the recursive approach to the `factorial` problem in Coconut:
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

# Test cases:
-1 |> factorial |> print # TypeError
0.5 |> factorial |> print # TypeError
0 |> factorial |> print # 1
3 |> factorial |> print # 6
```

Copy, paste! You should get the same test results as you got for the imperative version--but you can probably tell there's quite a lot more going on here than there. That's intentional: Coconut is intended for functional programming, not imperative programminng, and so its new features are built to be most useful when programming in a functional style.

Let's take a look at the specifics of the syntax in this example. The first thing we see is `case n`. This statement starts a `case` block, in which only `match` statements can occur. Each `match` statement will attempt to match its given pattern against the value in the `case` block. Only the first successful match inside of any given `case` block will be executed. When a match is successful, any variable bindings in that match will also be performed. Additionally, as is true in this case, `match` statements can also have `if` guards that will check the given condition before the match is considered final. Finally, after the `case` block, an `else` statement is allowed, which will only be excectued if no `match` statement is.

Specifically, in this example, the first `match` statement checks whether `n` matches to `0`. If it does, it executes `return 1`. Then the second `match` statement checks whether `n` matches to `_ is int`, which performs an `isinstance` check on `n` against `int`, then checks whether `n > 0`, and if those are true, executes `return n * factorial(n-1)`. If neither of those two statements are executed, the `else` statement triggers and executes `raise TypeError("the argument to factorial must be an integer >= 0")`.

Although this example is very basic, pattern-matching is both one of Coconut's most powerful and most complicated features. As a general intuitive guide, it is helpful to think _assignment_ whenever you see the keyword `match`. A good way to showcase this is that all `match` statements can be converted into equivalent destructuring assignment statements, which are also valid Coconut. In this case, the destructuring assignment equivalent to the `factorial` function above, in Coconut, would be:
```python
def factorial(n):
    """Compute n! where n is an integer >= 0."""
    try:
        0 = n # destructuring assignment
    except MatchError:
        try:
            _ is int = n # also destructuring assignment
        except MatchError:
            pass
        else: if n > 0: # in Coconut, if, match, and try are allowed after else
            return n * factorial(n-1)
    else:
        return 1
    raise TypeError("the argument to factorial must be an integer >= 0")

# Test cases:
-1 |> factorial |> print # TypeError
0.5 |> factorial |> print # TypeError
0 |> factorial |> print # 1
3 |> factorial |> print # 6
```

Copy, paste! While this destructuring assignment equivalent should work, it is much more cumbersome than `match` statements when you expect that they'll fail, which is why `match` statement syntax exists. But the destructuring assignment equivalent illuminates what exactly the pattern-matching is doing, by making it clear that `match` statements are really just fancy destructuring assignment statements, which _are really just fancy normal assignment statements_. In fact, to be explicit about using destructuring assignment instead of normal assignment, the `match` keyword can be put before a destructuring assignment statement to signify it as such.

It will be helpful to, as we continue to use Coconut's pattern-matching and destructuring assignment statements in further examples, think _assignment_ whenever you see the keyword `match`.

Up until now, for the recursive method, we have only dealt with pattern-matching, but there's actually another way that Coconut allows us to improve our `factorial` function: by writing it in a tail-recursive style, where it directly returns all calls to itself, and using Coconut's `recursive` decorator, like so:
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

# Test cases:
-1 |> factorial |> print # TypeError
0.5 |> factorial |> print # TypeError
0 |> factorial |> print # 1
3 |> factorial |> print # 6
```

Copy, paste! This version is exactly equivalent to the original version, with the exception that it will never raise a `MaximumRecursionDepthError`, because Coconut's `recursive` decorator will optimize away the tail recursion into a `while` loop.

### Iterative Method

The final, and other functional, approach, is the iterative one. Iterative approaches avoid the need for state change and loops by using higher-order functions, those that take other functions as their arguments, like `map` and `reduce`, to abstract out the basic operations being performed. In Coconut, the iterative appraoch to the `factorial` problem is:
```python
def factorial(n):
    """Compute n! where n is an integer >= 0."""
    case n:
        match 0:
            return 1
        match _ is int if n > 0:
            return range(1, n+1) |> reduce$((*))
    else:
        raise TypeError("the argument to factorial must be an integer >= 0")

# Test cases:
-1 |> factorial |> print # TypeError
0.5 |> factorial |> print # TypeError
0 |> factorial |> print # 1
3 |> factorial |> print # 6
```

Copy, paste! This definition differs from the recursive definition only by one line. That's intentional: because both the iterative and recursive approaches are functional approaches, Coconut can provide a great assist in making the code cleaner and more readable. The one line that differs is this one:
```python
return range(1, n+1) |> reduce$((*))
```

Let's break down what's happening on this line. First, the `range` function constructs an iterator of all the numbers that need to be multiplied together. Then, it is piped into the function `reduce$((*))`, which does that multiplication. But how? What is `reduce$((*))`.

We'll start with the base, the `reduce` function. `reduce` used to exist as a built-in in Python 2, and Coconut brings it back. `reduce` is a higher-order function that takes a function on two arguments as its first argument, and an iterator as its second argument, and applies that function to the given iterator by starting with the first element, and calling the function on the accumulated call so far and the next element, until the iterator is exhausted. Here's a visual representation:
```python
reduce(f, (a, b, c, d))

acc                 iter
                    (a, b, c, d)
a                   (b, c, d)
f(a, b)             (c, d)
f(f(a, b), c)       (d)
f(f(f(a, b), c), d)

return acc
```

Now let's take a look at what we do to `reduce` to make it multiply all the numbers we feed into it together. The Coconut code that we saw for that was `reduce$((*))`. There are two different Coconut constructs being used here: the operator function for multiplication in the form of `(*)`, and partial application in the form of `$`.

First, the operator function. In Coconut, a function form of any operator can be retrieved by surrounding that operator in parentheses. In this case, `(*)` is roughly equivalent to `lambda x, y: x*y`, but much cleaner and neater. In Coconut's lambda syntax, `(*)` is also equivalent to `(x, y) -> x*y`, which we will use from now on for all lambdas, even though both are legal Coconut, because Python's `lambda` statement is too ugly and bulky to use regularly. In fact, if Coconut's `--strict` mode is enabled, it will raise an error whenever Python `lambda` statements are used.

Second, the partial application. In Coconut, if a function call is prefixed by a `$`, like in this example, instead of actually performing the function call, a new function is returned with the given arguments already provided to it, so that when it is then called, it will be called with both the partially-applied arguments and the new arguments, in that order. In this case, `reduce$((*))` is equivalent to `(*args, **kwargs) -> reduce((*), *args, **kwargs)`.

Putting it all together, we can see how the single line of code
```python
range(1, n+1) |> reduce$((*))
```
is able to compute the proper factorial, without using any state or loops, only higher-order functions, in true functional style. By supplying the tools we use here like partial application (`$`), pipeline-style programming (`|>`), higher-order functions (`reduce`), and operator functions (`(*)`), Coconut enables this sort of functional programming to be done cleanly, neatly, and easily.

## Case Study 2: Quick Sort

In the second case study, we will be implementing the quick sort algorithm. Our `quick_sort` function will take in an iterator, and output an iterator that is the sorted version of that iterator.

Our method for tackling this problem is going to be a combination of the recursive and iterative approaches we used for the `factorial` problem, in that we're going to be lazily building up an iterator, and we're going to be doing it recursively. Here's the code, in Coconut:
```python
def quick_sort(l):
    """Return a sorted iterator of l, using the quick sort algorithm, and without using any data until necessary."""
    match [head] :: tail in l:
        tail, tail_ = tee(tail)
        yield from (quick_sort((x for x in tail if x <= head))
            :: (head,)
            :: quick_sort((x for x in tail_ if x > head))
            )

# Test cases:
[] |> quick_sort |> list |> print # []
[3] |> quick_sort |> list |> print # [3]
[0,1,2,3,4] |> quick_sort |> list |> print # [0,1,2,3,4]
[4,3,2,1,0] |> quick_sort |> list |> print # [0,1,2,3,4]
[3,0,4,2,1] |> quick_sort |> list |> print # [0,1,2,3,4]
```
Copy, paste! This `quick_sort` algorithm works uses a bunch of new constructs, so let's go over them.

First, the `::` operator, which appears here both in pattern-matching and by itself. In essence, the `::` operator is `+` for iterators. On its own, it takes two iterators and concatenates, or chains, them together. In pattern-matching, it inverts that operation, destructuring the beginning of an iterator into a pattern, and binding the rest of that iterator to a variable.

Which brings us to the second new thing, `match ... in ...` notation. The notation
```python
match pattern in item:
    <body>
else:
    <else>
```
is shorthand for
```python
case item:
    match pattern:
        <body>
else:
    <else>
```
that avoids the need for an additional level of indentation when only one `match` is being performed.

The third new construct is the built-in function `tee`. `tee` solves a problem for functional programming created by the implementation of Python's iterators: whenever an element of an iterator is accessed, it's lost. `tee` solves this problem by splitting an iterator in two (or more if the optional argument `n` is passed) independent iterators that both use the same underlying iterator to access their data, thus when an element of one is accessed, it isn't lost in the other.

Finally, although it's not a new construct, since it exists in Python 3, the use of `yield from` here deserves a mention. In Python, `yield` is the statement used to construct iterators, functioning much like `return`, with the exception that multiple `yield`s can be encountered, and each one will produce another element. `yield from` is very similar, except instead of adding a single element to the produced iterator, it adds another whole iterator.

Putting it all together, here's our `quick_sort` function again:
```python
def quick_sort(l):
    """Return a sorted iterator of l, using the quick sort algorithm, and without using any data until necessary."""
    match [head] :: tail in l:
        tail, tail_ = tee(tail)
        yield from (quick_sort((x for x in tail if x <= head))
            :: (head,)
            :: quick_sort((x for x in tail_ if x > head))
            )
```

The function first attempts to split `l` into an initial element and a remaining iterator. If `l` is the empty iterator, that match will fail, and it will fall through, yielding the empty iterator. Otherwise, we make a copy of the rest of the iterator, and yield the join of (the quick sort of all the remaining elements less than the initial element), (the initial element), and (the quick sort of all the remaining elements greater than the initial element).

The advantages of the basic approach used here, heavy use of iterators and recursion, as opposed to the classical imperative approach, are numerous. First, our approach is more clear and more readable, since it is describing _what_ `quick_sort` is instead of _how_ `quick_sort` could be implemented. Second, our approach is _lazy_ in that our `quick_sort` won't evaluate any data until it needs it. Finally, and although this isn't relevant for `quick_sort` it is relevant in many other cases, an example of which we'll see later in this tutorial, our approach allows for working with _infinite_ series just like they were finite.

And Coconut makes programming in such an advantageous functional approach significantly easier. In this example, Coconut's pattern-matching lets us easily split the given iterator, and Coconut's `::` iterator joining operator lets us easily put it back together again in sorted order.

## Case Study 3: Vectors

In the next case study, we'll be doing something slightly different--instead of defining a function, we'll be creating an object. Specifically, we're going to try to implement an immutable n-vector that supports all the basic vector operations.

In functional programming, it is often very desirable to define _immutable_ objects, those that can't be changed once created--like Python's strings or tuples. Like strings and tuples, immutable objects are useful for a wide variety of reasons: they're easier to reason about, since you can be guaranteed they won't change; they're hashable and pickleable, so they can be used as keys and serialized; and when combined with pattern-matching, they can be used as what are called _algebraic data types_ to build up and then deconstruct large, complicated data structures very easily.

Coconut's `data` statement brings the power and utility of _immutable, algebraic data types_ to Python, and it is this that we will be using to construct our `vector` type. The demonstrate the syntax of `data` statements, we'll start by defining a simple 2-vector:
```python
data vector2(x, y):
    """Immutable 2-vector."""
    def __abs__(self):
        """Return the magnitude of the 2-vector."""
        return (self.x**2 + self.y**2)**0.5

# Test cases:
vector2(1, 2) |> print # vector2(x=1, y=2)
vector2(3, 4) |> abs |> print # 5
v = vector2(2, 3)
v.x = 7 # AttributeError
```

Copy, paste!

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

## Filling in the Gaps
