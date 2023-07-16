# Coconut Tutorial

```{contents}
---
local:
---
```

## Introduction

Welcome to the tutorial for the [Coconut Programming Language](http://evhub.github.io/coconut/)! Coconut is a variant of [Python](https://www.python.org/) built for **simple, elegant, Pythonic functional programming**. But those are just words; what they mean in practice is that _all valid Python 3 is valid Coconut_ but Coconut builds on top of Python a suite of _simple, elegant utilities for functional programming_.

Why use Coconut? Coconut is built to be useful. Coconut enhances the repertoire of Python programmers to include the tools of modern functional programming, in such a way that those tools are _easy_ to use and immensely _powerful;_ that is, Coconut does to functional programming what Python did to imperative programming. And Coconut code runs the same on _any Python version_, making the Python 2/3 split a thing of the past.

Specifically, Coconut adds to Python _built-in, syntactical support_ for:
- pattern-matching
- algebraic data types
- destructuring assignment
- partial application
- lazy lists
- function composition
- prettier lambdas
- infix notation
- pipeline-style programming
- operator functions
- tail call optimization
- where statements

and much more!

### Interactive Tutorial

This tutorial is non-interactive. To get an interactive tutorial instead, check out [Coconut's interactive tutorial](https://hmcfabfive.github.io/coconut-tutorial).

Note, however, that the interactive tutorial is less up-to-date than this one and thus may contain old, deprecated syntax (though Coconut will let you know if you encounter such a situation) as well as outdated idioms (meaning that the example code in the interactive tutorial is likely to be much less elegant than the example code here).

### Installation

At its very core, Coconut is a compiler that turns Coconut code into Python code. That means that anywhere where you can use a Python script, you can also use a compiled Coconut script. To access that core compiler, Coconut comes with a command-line utility, which can
- compile single Coconut files or entire Coconut projects,
- interpret Coconut code on-the-fly, and
- hook into existing Python applications like IPython/Jupyter and MyPy.

Installing Coconut, including all the features above, is drop-dead simple. Just

1. install [Python](https://www.python.org/downloads/),
2. open a command-line prompt,
3. and enter:
```
pip install coconut
```

_Note: If you are having trouble installing Coconut, try following the debugging steps in the [installation section of Coconut's documentation](./DOCS.md#installation)._

To check that your installation is functioning properly, try entering into the command line
```
coconut -h
```
which should display Coconut's command-line help.

_Note: If you're having trouble, or if anything mentioned in this tutorial doesn't seem to work for you, feel free to [ask for help on Gitter](https://gitter.im/evhub/coconut) and somebody will try to answer your question as soon as possible._

## Starting Out

### Using the Interpreter

Now that you've got Coconut installed, the obvious first thing to do is to play around with it. To launch the Coconut interpreter, just go to the command line and type
```
coconut
```
and you should see something like
```coconut
Coconut Interpreter vX.X.X:
(enter 'exit()' or press Ctrl-D to end)
>>>
```
which is Coconut's way of telling you you're ready to start entering code for it to evaluate. So let's do that!

In case you missed it earlier, _all valid Python 3 is valid Coconut_. That doesn't mean compiled Coconut will only run on Python 3—in fact, compiled Coconut will run the same on any Python version—but it does mean that only Python 3 code is guaranteed to compile as Coconut code.

That means that if you're familiar with Python, you're already familiar with a good deal of Coconut's core syntax and Coconut's entire standard library. To show that, let's try entering some basic Python into the Coconut interpreter. For example:
```coconut_pycon
>>> "hello, world!"
'hello, world!'
>>> 1 + 1
2
```

### Writing Coconut Files

Of course, while being able to interpret Coconut code on-the-fly is a great thing, it wouldn't be very useful without the ability to write and compile larger programs. To that end, it's time to write our first Coconut program: "hello, world!" Coconut-style.

First, we're going to need to create a file to put our code into. The file extension for Coconut source files is `.coco`, so let's create the new file `hello_world.coco`. After you do that, you should take the time now to set up your text editor to properly highlight Coconut code. For instructions on how to do that, see the documentation on [Coconut syntax highlighting](./DOCS.md#syntax-highlighting).

Now let's put some code in our `hello_world.coco` file. Unlike in Python, where headers like
```coconut_python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import print_function, absolute_import, unicode_literals, division
```
are common and often very necessary, the Coconut compiler will automatically take care of all of that for you, so all you need to worry about is your own code. To that end, let's add the code for our "hello, world!" program.

In pure Python 3, "hello, world!" is
```coconut_python
print("hello, world!")
```
and while that will work in Coconut, equally as valid is to use a pipeline-style approach, which is what we'll do, and write
```coconut
"hello, world!" |> print
```
which should let you see very clearly how Coconut's `|>` operator enables pipeline-style programming: it allows an object to be passed along from function to function, with a different operation performed at each step. In this case, we are piping the object `"hello, world!"` into the operation `print`. Now let's save our simple "hello, world!" program, and try to run it.

### Using the Compiler

Compiling Coconut files and projects with the Coconut command-line utility is incredibly simple. Just `cd` into the directory of your `hello_world.coco` file and type
```
coconut hello_world.coco
```
which should give the output
```
Coconut: Compiling       hello_world.coco ...
Coconut: Compiled to     hello_world.py .
```
and deposit a new `hello_world.py` file in the same directory as the `hello_world.coco` file. You should then be able to run that file with
```
python hello_world.py
```
which should produce `hello, world!` as the output.

_Note: You can compile and run your code all in one step if you use Coconut's `--run` option (`-r` for short)._

Compiling single files is not the only way to use the Coconut command-line utility, however. We can also compile all the Coconut files in a given directory simply by passing that directory as the first argument, which will get rid of the need to run the same Coconut header code in each file by storing it in a `__coconut__.py` file in the same directory.

The Coconut  compiler supports a large variety of different compilation options, the help for which can always be accessed by entering `coconut -h` into the command line. One of the most useful of these is `--line-numbers` (or `-l` for short). Using `--line-numbers` will add the line numbers of your source code as comments in the compiled code, allowing you to see what line in your source code corresponds to a line in the compiled code where an error occurred, for ease of debugging.

_Note: If you don't need the full control of the Coconut compiler, you can also [access your Coconut code just by importing it](./DOCS.md#automatic-compilation), either from the Coconut interpreter, or in any Python file where you import [`coconut.api`](./DOCS.md#coconut-api)._

### Using IPython/Jupyter

Although all different types of programming can benefit from using more functional techniques, scientific computing, perhaps more than any other field, lends itself very well to functional programming, an observation the case studies in this tutorial are very good examples of. That's why Coconut aims to provide extensive support for the established tools of scientific computing in Python.

To that end, Coconut provides [built-in IPython/Jupyter support](./DOCS.md#ipython-jupyter-support). To launch a Jupyter notebook with Coconut, just enter the command
```
coconut --jupyter notebook
```

_Alternatively, to launch the Jupyter interpreter with Coconut as the kernel, run `coconut --jupyter console` instead. Additionally, you can launch an interactive Coconut Jupyter console initialized from the current namespace by inserting `from coconut import embed; embed()` into your code, which can be a very useful debugging tool._

### Case Studies

Because Coconut is built to be useful, the best way to demo it is to show it in action. To that end, the majority of this tutorial will be showing how to apply Coconut to solve particular problems, which we'll call case studies.

These case studies are not intended to provide a complete picture of all of Coconut's features. For that, see Coconut's [documentation](./DOCS.md). Instead, they are intended to show how Coconut can actually be used to solve practical programming problems.

## Case Study 1: `factorial`

In the first case study we will be defining a `factorial` function, that is, a function that computes `n!` where `n` is an integer `>= 0`. This is somewhat of a toy example, since Python can fairly easily do this, but it will serve as a good showcase of some of the basic features of Coconut and how they can be used to great effect.

To start off with, we're going to have to decide what sort of an implementation of `factorial` we want. There are many different ways to tackle this problem, but for the sake of concision we'll split them into four major categories: imperative, recursive, iterative, and `addpattern`.

### Imperative Method

The imperative approach is the way you'd write `factorial` in a language like C. Imperative approaches involve lots of state change, where variables are regularly modified and loops are liberally used. In Coconut, the imperative approach to the `factorial` problem looks like this:
```coconut
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
-1 |> factorial |> print  # TypeError
0.5 |> factorial |> print  # TypeError
0 |> factorial |> print  # 1
3 |> factorial |> print  # 6
```

Before we delve into what exactly is happening here, let's give it a run and make sure the test cases check out. If we were really writing a Coconut program, we'd want to save and compile an actual file, but since we're just playing around, let's try copy-pasting into the interpreter. Here, you should get two `TypeErrors`, then `1`, then `6`.

Now that we've verified it works, let's take a look at what's going on. Since the imperative approach is a fundamentally non-functional method, Coconut can't help us improve this example very much. Even here, though, the use of Coconut's infix notation (where the function is put in-between its arguments, surrounded in backticks) in `` n `isinstance` int `` makes the code slightly cleaner and easier to read.

### Recursive Method

The recursive approach is the first of the fundamentally functional approaches, in that it doesn't involve the state change and loops of the imperative approach. Recursive approaches avoid the need to change variables by making that variable change implicit in the recursive function call. Here's the recursive approach to the `factorial` problem in Coconut:
```coconut
def factorial(n):
    """Compute n! where n is an integer >= 0."""
    match n:
        case 0:
            return 1
        case x `isinstance` int if x > 0:
            return x * factorial(x-1)
    else:
        raise TypeError("the argument to factorial must be an integer >= 0")

# Test cases:
-1 |> factorial |> print  # TypeError
0.5 |> factorial |> print  # TypeError
0 |> factorial |> print  # 1
3 |> factorial |> print  # 6
```

Go ahead and copy and paste the code and tests into the interpreter. You should get the same test results as you got for the imperative version—but you can probably tell there's quite a lot more going on here than there. That's intentional: Coconut is intended for functional programming, not imperative programming, and so its new features are built to be most useful when programming in a functional style.

Let's take a look at the specifics of the syntax in this example. The first thing we see is `match n`. This statement starts a `case` block, in which only `case` statements can occur. Each `case` statement will attempt to match its given pattern against the value in the `case` block. Only the first successful match inside of any given `case` block will be executed. When a match is successful, any variable bindings in that match will also be performed. Additionally, as is true in this case, `case` statements can also have `if` guards that will check the given condition before the match is considered final. Finally, after the `case` block, an `else` statement is allowed, which will only be executed if no `case` statement is.

Specifically, in this example, the first `case` statement checks whether `n` matches to `0`. If it does, it executes `return 1`. Then the second `case` statement checks whether `n` matches to `` x `isinstance` int ``, which checks that `n` is an `int` (using `isinstance`) and assigns `x = n` if so, then checks whether `x > 0`, and if so, executes `return x * factorial(x-1)`. If neither of those two statements are executed, the `else` statement triggers and executes `raise TypeError("the argument to factorial must be an integer >= 0")`.

Although this example is very basic, pattern-matching is both one of Coconut's most powerful and most complicated features. As a general intuitive guide, it is helpful to think _assignment_ whenever you see the keyword `match`. A good way to showcase this is that all `match` statements can be converted into equivalent destructuring assignment statements, which are also valid Coconut. In this case, the destructuring assignment equivalent to the `factorial` function above would be:
```coconut
def factorial(n):
    """Compute n! where n is an integer >= 0."""
    try:
        # The only value that can be assigned to 0 is 0, since 0 is an
        # immutable constant; thus, this assignment fails if n is not 0.
        0 = n
    except MatchError:
        pass
    else:
        return 1
    try:
        # This attempts to assign n to x, which has been declared to be
        # an int; since only an int can be assigned to an int, this
        # fails if n is not an int.
        x `isinstance` int = n
    except MatchError:
        pass
    else: if x > 0:  # in Coconut, statements can be nested on the same line
        return x * factorial(x-1)
    raise TypeError("the argument to factorial must be an integer >= 0")

# Test cases:
-1 |> factorial |> print  # TypeError
0.5 |> factorial |> print  # TypeError
0 |> factorial |> print  # 1
3 |> factorial |> print  # 6
```

First, copy and paste! While this destructuring assignment equivalent should work, it is much more cumbersome than `match` statements when you expect that they'll fail, which is why `match` statement syntax exists. But the destructuring assignment equivalent illuminates what exactly the pattern-matching is doing, by making it clear that `match` statements are really just fancy destructuring assignment statements. In fact, to be explicit about using destructuring assignment instead of normal assignment, the `match` keyword can be put before a destructuring assignment statement to signify it as such.

It will be helpful to, as we continue to use Coconut's pattern-matching and destructuring assignment statements in further examples, think _assignment_ whenever you see the keyword `match`.

Next, we can make a couple of simple improvements to our `factorial` function. First, we don't actually need to assign `x` as a new variable, since it has the same value as `n`, so if we use `_` instead of `x`, Coconut won't ever actually assign the variable. Thus, we can rewrite our `factorial` function as:
```coconut
def factorial(n):
    """Compute n! where n is an integer >= 0."""
    match n:
        case 0:
            return 1
        case _ `isinstance` int if n > 0:
            return n * factorial(n-1)
    else:
        raise TypeError("the argument to factorial must be an integer >= 0")

# Test cases:
-1 |> factorial |> print  # TypeError
0.5 |> factorial |> print  # TypeError
0 |> factorial |> print  # 1
3 |> factorial |> print  # 6
```

Copy, paste! This new `factorial` function should behave exactly the same as before.

Second, we can replace the `` _ `isinstance` int `` pattern with the class pattern `int()`, which, when used with no arguments like that, is equivalent. Thus, we can again rewrite our `factorial` function to:
```coconut
def factorial(n):
    """Compute n! where n is an integer >= 0."""
    match n:
        case 0:
            return 1
        case int() if n > 0:
            return n * factorial(n-1)
    else:
        raise TypeError("the argument to factorial must be an integer >= 0")

# Test cases:
-1 |> factorial |> print  # TypeError
0.5 |> factorial |> print  # TypeError
0 |> factorial |> print  # 1
3 |> factorial |> print  # 6
```

Up until now, for the recursive method, we have only dealt with pattern-matching, but there's actually another way that Coconut allows us to improve our `factorial` function. Coconut performs automatic tail call optimization, which means that whenever a function directly returns a call to another function, Coconut will optimize away the additional call. Thus, we can improve our `factorial` function by rewriting it to use a tail call:
```coconut
def factorial(n, acc=1):
    """Compute n! where n is an integer >= 0."""
    match n:
        case 0:
            return acc
        case int() if n > 0:
            return factorial(n-1, acc*n)
    else:
        raise TypeError("the argument to factorial must be an integer >= 0")

# Test cases:
-1 |> factorial |> print  # TypeError
0.5 |> factorial |> print  # TypeError
0 |> factorial |> print  # 1
3 |> factorial |> print  # 6
```

Copy, paste! This new `factorial` function is equivalent to the original version, with the exception that it will never raise a `RuntimeError` due to reaching Python's maximum recursion depth, since Coconut will optimize away the tail call.

### Iterative Method

The other main functional approach is the iterative one. Iterative approaches avoid the need for state change and loops by using higher-order functions, those that take other functions as their arguments, like `map` and `reduce`, to abstract out the basic operations being performed. In Coconut, the iterative approach to the `factorial` problem is:
```coconut
def factorial(n):
    """Compute n! where n is an integer >= 0."""
    match n:
        case 0:
            return 1
        case int() if n > 0:
            return range(1, n+1) |> reduce$(*)
    else:
        raise TypeError("the argument to factorial must be an integer >= 0")

# Test cases:
-1 |> factorial |> print  # TypeError
0.5 |> factorial |> print  # TypeError
0 |> factorial |> print  # 1
3 |> factorial |> print  # 6
```

Copy, paste! This definition differs from the recursive definition only by one line. That's intentional: because both the iterative and recursive approaches are functional approaches, Coconut can provide a great assist in making the code cleaner and more readable. The one line that differs is this one:
```coconut
return range(1, n+1) |> reduce$(*)
```

Let's break down what's happening on this line. First, the `range` function constructs an iterator of all the numbers that need to be multiplied together. Then, it is piped into the function `reduce$(*)`, which does that multiplication. But how? What is `reduce$(*)`?

We'll start with the base, the `reduce` function. `reduce` used to exist as a built-in in Python 2, and Coconut brings it back. `reduce` is a higher-order function that takes a function of two arguments as its first argument, and an iterator as its second argument, and applies that function to the given iterator by starting with the first element, and calling the function on the accumulated call so far and the next element, until the iterator is exhausted. Here's a visual representation:
```coconut
reduce(f, (a, b, c, d))

acc                 iter
                    (a, b, c, d)
a                   (b, c, d)
f(a, b)             (c, d)
f(f(a, b), c)       (d)
f(f(f(a, b), c), d)

return acc
```

Now let's take a look at what we do to `reduce` to make it multiply all the numbers we feed into it together. The Coconut code that we saw for that was `reduce$(*)`. There are two different Coconut constructs being used here: the operator function for multiplication in the form of `(*)`, and partial application in the form of `$`.

First, the operator function. In Coconut, a function form of any operator can be retrieved by surrounding that operator in parentheses. In this case, `(*)` is roughly equivalent to `lambda x, y: x*y`, but much cleaner and neater. In Coconut's lambda syntax, `(*)` is also equivalent to `(x, y) => x*y`, which we will use from now on for all lambdas, even though both are legal Coconut, because Python's `lambda` statement is too ugly and bulky to use regularly.

_Note: If Coconut's `--strict` mode is enabled, which will force your code to obey certain cleanliness standards, it will raise an error whenever Python `lambda` statements are used._

Second, the partial application. Think of partial application as _lazy function calling_, and `$` as the _lazy-ify_ operator, where lazy just means "don't evaluate this until you need to." In Coconut, if a function call is prefixed by a `$`, like in this example, instead of actually performing the function call, a new function is returned with the given arguments already provided to it, so that when it is then called, it will be called with both the partially-applied arguments and the new arguments, in that order. In this case, `reduce$(*)` is roughly equivalent to `(*args, **kwargs) => reduce((*), *args, **kwargs)`.

_You can partially apply arguments in any order using `?` in place of missing arguments, as in `to_binary = int$(?, 2)`._

Putting it all together, we can see how the single line of code
```coconut
range(1, n+1) |> reduce$(*)
```
is able to compute the proper factorial, without using any state or loops, only higher-order functions, in true functional style. By supplying the tools we use here like partial application (`$`), pipeline-style programming (`|>`), higher-order functions (`reduce`), and operator functions (`(*)`), Coconut enables this sort of functional programming to be done cleanly, neatly, and easily.

### `addpattern` Method

While the iterative approach is very clean, there are still some bulky pieces—looking at the iterative version below, you can see that it takes three entire indentation levels to get from the function definition to the actual objects being returned:
```coconut
def factorial(n):
    """Compute n! where n is an integer >= 0."""
    match n:
        case 0:
            return 1
        case int() if n > 0:
            return range(1, n+1) |> reduce$(*)
    else:
        raise TypeError("the argument to factorial must be an integer >= 0")
```

By making use of the [Coconut `addpattern` syntax](./DOCS.md#addpattern), we can take that from three indentation levels down to one. Take a look:
```
def factorial(0) = 1

addpattern def factorial(int() as n if n > 0) =
    """Compute n! where n is an integer >= 0."""
    range(1, n+1) |> reduce$(*)

# Test cases:
-1 |> factorial |> print  # MatchError
0.5 |> factorial |> print  # MatchError
0 |> factorial |> print  # 1
3 |> factorial |> print  # 6
```
Copy, paste! This should work exactly like before, except now it raises `MatchError` as a fall through instead of `TypeError`. There are three major new concepts to talk about here: `addpattern`, of course, assignment function notation, and pattern-matching function definition—how both of the functions above are defined.

First, assignment function notation. This one's pretty straightforward. If a function is defined with an `=` instead of a `:`, the last line is required to be an expression, and is automatically returned.

Second, pattern-matching function definition. Pattern-matching function definition does exactly that—pattern-matches against all the arguments that are passed to the function. Unlike normal function definition, however, if the pattern doesn't match (if for example the wrong number of arguments are passed), your function will raise a `MatchError`. Finally, like destructuring assignment, if you want to be more explicit about using pattern-matching function definition, you can add a `match` before the `def`. In this case, we're also using one new pattern-matching construct, the `as` match, which matches against the pattern on the left and assigns the result to the name on the right.

Third, `addpattern`. `addpattern` creates a new pattern-matching function by adding the new pattern as an additional case to the old pattern-matching function it is replacing. Thus, `addpattern` can be thought of as doing exactly what it says—it adds a new pattern to an existing pattern-matching function.

Finally, not only can we rewrite the iterative approach using `addpattern`, as we did above, we can also rewrite the recursive approach using `addpattern`, like so:
```coconut
def factorial(0) = 1

addpattern def factorial(int() as n if n > 0) =
    """Compute n! where n is an integer >= 0."""
    n * factorial(n - 1)

# Test cases:
-1 |> factorial |> print  # MatchError
0.5 |> factorial |> print  # MatchError
0 |> factorial |> print  # 1
3 |> factorial |> print  # 6
```
Copy, paste! It should work exactly like before, except, as above, with `TypeError` replaced by `MatchError`.

## Case Study 2: `quick_sort`

In the second case study, we will be implementing the [quick sort algorithm](https://en.wikipedia.org/wiki/Quicksort). We will implement two versions: first, a `quick_sort` function that takes in a list and outputs a list, and second, a `quick_sort` function that takes in an iterator and outputs an iterator.

### Sorting a Sequence

First up is `quick_sort` for lists. We're going to use a recursive `addpattern`-based approach to tackle this problem—a similar approach to the very last `factorial` function we wrote, using `addpattern` to reduce the amount of indentation we're going to need. Without further ado, here's our implementation of `quick_sort` for lists:
```coconut
def quick_sort([]) = []

addpattern def quick_sort([head] + tail) =
    """Sort the input sequence using the quick sort algorithm."""
    quick_sort(left) + [head] + quick_sort(right) where:
        left = [x for x in tail if x < head]
        right = [x for x in tail if x >= head]

# Test cases:
[] |> quick_sort |> print  # []
[3] |> quick_sort |> print  # [3]
[0,1,2,3,4] |> quick_sort |> print  # [0,1,2,3,4]
[4,3,2,1,0] |> quick_sort |> print  # [0,1,2,3,4]
[3,0,4,2,1] |> quick_sort |> print  # [0,1,2,3,4]
```
Copy, paste! Two new feature here: head-tail pattern-matching and `where` statements.

First, `where` statements are extremely straightforward. In fact, I bet you've already figured out what they do from the code above. A `where` statement is just a way to compute something in the context of some set of assignment statements.

Second, head-tail pattern-matching, which you can see here as `[head] + tail`, simply follows the form of a list or tuple added to a variable. When this appears in any pattern-matching context, the value being matched against will be treated as a sequence, the list or tuple matched against the beginning of that sequence, and the rest of it bound to the variable. In this case, we use the head-tail pattern to remove the head so we can use it as the pivot for splitting the rest of the list.

### Sorting an Iterator

Now it's time to try `quick_sort` for iterators. Our method for tackling this problem is going to be a combination of the recursive and iterative approaches we used for the `factorial` problem, in that we're going to be lazily building up an iterator, and we're going to be doing it recursively. Here's the code:
```coconut
def quick_sort(l):
    """Sort the input iterator using the quick sort algorithm."""
    match [head] :: tail in l:
        tail = reiterable(tail)
        yield from quick_sort(left) :: [head] :: quick_sort(right) where:
            left = (x for x in tail if x < head)
            right = (x for x in tail if x >= head)
    # By yielding nothing if the match falls through, we implicitly return an empty iterator.

# Test cases:
[] |> quick_sort |> list |> print  # []
[3] |> quick_sort |> list |> print  # [3]
[0,1,2,3,4] |> quick_sort |> list |> print  # [0,1,2,3,4]
[4,3,2,1,0] |> quick_sort |> list |> print  # [0,1,2,3,4]
[3,0,4,2,1] |> quick_sort |> list |> print  # [0,1,2,3,4]
```
Copy, paste! This `quick_sort` algorithm works uses a bunch of new constructs, so let's go over them.

First, the `::` operator, which appears here both in pattern-matching and by itself. In essence, the `::` operator is lazy `+` for iterators. On its own, it takes two iterators and concatenates, or chains, them together, and it does this lazily, not evaluating anything until its needed, so it can be used for making infinite iterators. In pattern-matching, it inverts that operation, destructuring the beginning of an iterator into a pattern, and binding the rest of that iterator to a variable.

Which brings us to the second new thing, `match ... in ...` notation. The notation
```coconut
match pattern in item:
    <body>
else:
    <else>
```
is shorthand for
```coconut
match item:
    case pattern:
        <body>
else:
    <else>
```
that avoids the need for an additional level of indentation when only one `match` is being performed.

The third new construct is the [Coconut built-in `reiterable`](./DOCS.md#reiterable). There is a problem in doing immutable functional programming with Python iterators: whenever an element of an iterator is accessed, it's lost. `reiterable` solves this problem by allowing the iterable it's called on to be iterated over multiple times while still yielding the same result each time

Finally, although it's not a new construct, since it exists in Python 3, the use of `yield from` here deserves a mention. In Python, `yield` is the statement used to construct iterators, functioning much like `return`, with the exception that multiple `yield`s can be encountered, and each one will produce another element. `yield from` is very similar, except instead of adding a single element to the produced iterator, it adds another whole iterator.

Putting it all together, here's our `quick_sort` function again:
```coconut
def quick_sort(l):
    """Sort the input iterator using the quick sort algorithm."""
    match [head] :: tail in l:
        tail = reiterable(tail)
        yield from quick_sort(left) :: [head] :: quick_sort(right) where:
            left = (x for x in tail if x < head)
            right = (x for x in tail if x >= head)
    # By yielding nothing if the match falls through, we implicitly return an empty iterator.
```

The function first attempts to split `l` into an initial element and a remaining iterator. If `l` is the empty iterator, that match will fail, and it will fall through, yielding the empty iterator (that's how the function handles the base case). Otherwise, we make a copy of the rest of the iterator, and yield the join of (the quick sort of all the remaining elements less than the initial element), (the initial element), and (the quick sort of all the remaining elements greater than the initial element).

The advantages of the basic approach used here, heavy use of iterators and recursion, as opposed to the classical imperative approach, are numerous. First, our approach is more clear and more readable, since it is describing _what_ `quick_sort` is instead of _how_ `quick_sort` could be implemented. Second, our approach is _lazy_ in that our `quick_sort` won't evaluate any data until it needs it. Finally, and although this isn't relevant for `quick_sort` it is relevant in many other cases, an example of which we'll see later in this tutorial, our approach allows for working with _infinite_ series just like they were finite.

And Coconut makes programming in such an advantageous functional approach significantly easier. In this example, Coconut's pattern-matching lets us easily split the given iterator, and Coconut's `::` iterator joining operator lets us easily put it back together again in sorted order.

## Case Study 3: `vector` Part I

In the next case study, we'll be doing something slightly different—instead of defining a function, we'll be creating an object. Specifically, we're going to try to implement an immutable n-vector that supports all the basic vector operations.

In functional programming, it is often very desirable to define _immutable_ objects, those that can't be changed once created—like Python's strings or tuples. Like strings and tuples, immutable objects are useful for a wide variety of reasons:
- they're easier to reason about, since you can be guaranteed they won't change,
- they're hashable and pickleable, so they can be used as keys and serialized,
- they're significantly more efficient since they require much less overhead,
- and when combined with pattern-matching, they can be used as what are called _algebraic data types_ to build up and then match against large, complicated data structures very easily.

### 2-Vector

Coconut's `data` statement brings the power and utility of _immutable, algebraic data types_ to Python, and it is this that we will be using to construct our `vector` type. The demonstrate the syntax of `data` statements, we'll start by defining a simple 2-vector. Our vector will have one special method `__abs__` which will compute the vector's magnitude, defined as the square root of the sum of the squares of the elements. Here's our 2-vector:
```coconut
data vector2(x, y):
    """Immutable 2-vector."""
    def __abs__(self) =
        """Return the magnitude of the 2-vector."""
        (self.x**2 + self.y**2)**0.5

# Test cases:
vector2(1, 2) |> print  # vector2(x=1, y=2)
vector2(3, 4) |> abs |> print  # 5
vector2(1, 2) |> fmap$(x => x*2) |> print  # vector2(x=2, y=4)
v = vector2(2, 3)
v.x = 7  # AttributeError
```

Copy, paste! This example shows the basic syntax of `data` statements:
```coconut
data <name>(<attributes>):
    <body>
```
where `<name>` and `<body>` are the same as the equivalent `class` definition, but `<attributes>` are the different attributes of the data type, in order that the constructor should take them as arguments. In this case, `vector2` is a data type of two attributes, `x` and `y`, with one defined method, `__abs__`, that computes the magnitude. As the test cases show, we can then create, print, but _not modify_ instances of `vector2`.

One other thing to call attention to here is the use of the [Coconut built-in `fmap`](./DOCS.md#fmap). `fmap` allows you to map functions over algebraic data types. Coconut's `data` types do support iteration, so the standard `map` works on them, but it doesn't return another object of the same data type. In this case, `fmap` is simply `map` plus a call to the object's constructor.

### n-Vector Constructor

Now that we've got the 2-vector under our belt, let's move to back to our original, more complicated problem: n-vectors, that is, vectors of arbitrary length. We're going to try to make our n-vector support all the basic vector operations, but we'll start out with just the `data` definition and the constructor:
```coconut
data vector(*pts):
    """Immutable n-vector."""
    def __new__(cls, *pts):
        """Create a new vector from the given pts."""
        match [v `isinstance` vector] in pts:
            return v  # vector(v) where v is a vector should return v
        else:
            return pts |*> makedata$(cls)  # accesses base constructor

# Test cases:
vector(1, 2, 3) |> print  # vector(*pts=(1, 2, 3))
vector(4, 5) |> vector |> print  # vector(*pts=(4, 5))
```

Copy, paste! The big new thing here is how to write `data` constructors. Since `data` types are immutable, `__init__` construction won't work. Instead, a different special method `__new__` is used, which must return the newly constructed instance, and unlike most methods, takes the class not the object as the first argument. Since `__new__` needs to return a fully constructed instance, in almost all cases it will be necessary to access the underlying `data` constructor. To achieve this, Coconut provides the [built-in `makedata` function](./DOCS.md#makedata), which takes a data type and calls its underlying `data` constructor with the rest of the arguments.

In this case, the constructor checks whether nothing but another `vector` was passed, in which case it returns that, otherwise it returns the result of passing the arguments to the underlying constructor, the form of which is `vector(*pts)`, since that is how we declared the data type. We use sequence pattern-matching to determine whether we were passed a single vector, which is just a list or tuple of patterns to match against the contents of the sequence.

One important pitfall that's worth pointing out here: in this case, you must use `` v `isinstance` vector `` rather than `vector() as v`, since, as we'll see later, patterns like `vector()` behave differently for `data` types than normal classes. In this case, `vector()` would only match a _zero-length_ vector, not just any vector.

The other new construct used here is the `|*>`, or star-pipe, operator, which functions exactly like the normal pipe, except that instead of calling the function with one argument, it calls it with as many arguments as there are elements in the sequence passed into it. The difference between `|>` and `|*>` is exactly analogous to the difference between `f(args)` and `f(*args)`.

### n-Vector Methods

Now that we have a constructor for our n-vector, it's time to write its methods. First up is `__abs__`, which should compute the vector's magnitude. This will be slightly more complicated than with the 2-vector, since we have to make it work over an arbitrary number of `pts`. Fortunately, we can use Coconut's pipeline-style programming and partial application to make it simple:
```coconut
    def __abs__(self) =
        """Return the magnitude of the vector."""
        self.pts |> map$(.**2) |> sum |> (.**0.5)
```
The basic algorithm here is map square over each element, sum them all, then square root the result. The one new construct here is the `(.**2)` and `(.**0.5)` syntax, which are effectively equivalent to `(x => x**2)` and `(x => x**0.5)`, respectively (though the `(.**2)` syntax produces a pickleable object). This syntax works for all [operator functions](./DOCS.md#operator-functions), so you can do things like `(1-.)` or `(cond() or .)`.

Next up is vector addition. The goal here is to add two vectors of equal length by adding their components. To do this, we're going to make use of Coconut's ability to perform pattern-matching, or in this case destructuring assignment, to data types, like so:
```coconut
    def __add__(self, vector(*other_pts)
                if len(other_pts) == len(self.pts)) =
        """Add two vectors together."""
        map((+), self.pts, other_pts) |*> vector
```

There are a couple of new constructs here, but the main notable one is the pattern-matching `vector(*other_pts)` which showcases the syntax for pattern-matching against data types: it mimics exactly the original `data` declaration of that data type. In this case, `vector(*other_pts)` will only match a vector, raising a `MatchError` otherwise, and if it does match a vector, will assign the vector's `pts` attribute to the variable `other_pts`.

Next is vector subtraction, which is just like vector addition, but with `(-)` instead of `(+)`:
```coconut
    def __sub__(self, vector(*other_pts)
                if len(other_pts) == len(self.pts)) =
        """Subtract one vector from another."""
        map((-), self.pts, other_pts) |*> vector
```

One thing to note here is that unlike the other operator functions, `(-)` can either mean negation or subtraction, the meaning of which will be inferred based on how many arguments are passed, 1 for negation, 2 for subtraction. To show this, we'll use the same `(-)` function to implement vector negation, which should simply negate each element:
```coconut
    def __neg__(self) =
        """Retrieve the negative of the vector."""
        self.pts |> map$(-) |*> vector
```

The last method we'll implement is multiplication. This one is a little bit tricky, since mathematically, there are a whole bunch of different ways to multiply vectors. For our purposes, we're just going to look at two: between two vectors of equal length, we want to compute the dot product, defined as the sum of the corresponding elements multiplied together, and between a vector and a scalar, we want to compute the scalar multiple, which is just each element multiplied by that scalar. Here's our implementation:
```coconut
    def __mul__(self, other):
        """Scalar multiplication and dot product."""
        match vector(*other_pts) in other:
            assert len(other_pts) == len(self.pts)
            return map((*), self.pts, other_pts) |> sum  # dot product
        else:
            return self.pts |> map$(.*other) |*> vector  # scalar multiple
    def __rmul__(self, other) =
        """Necessary to make scalar multiplication commutative."""
        self * other
```

The first thing to note here is that unlike with addition and subtraction, where we wanted to raise an error if the vector match failed, here, we want to do scalar multiplication if the match fails, so instead of using destructuring assignment, we use a `match` statement. The second thing to note here is the combination of pipeline-style programming, partial application, operator functions, and higher-order functions we're using to compute the dot product and scalar multiple. For the dot product, we map multiplication over the two vectors, then sum the result. For the scalar multiple, we take the original points, map multiplication by the scalar over them, then use them to make a new vector.

Finally, putting everything together:
```coconut
data vector(*pts):
    """Immutable n-vector."""
    def __new__(cls, *pts):
        """Create a new vector from the given pts."""
        match [v `isinstance` vector] in pts:
            return v  # vector(v) where v is a vector should return v
        else:
            return pts |*> makedata$(cls)  # accesses base constructor
    def __abs__(self) =
        """Return the magnitude of the vector."""
        self.pts |> map$(.**2) |> sum |> (.**0.5)
    def __add__(self, vector(*other_pts)
                if len(other_pts) == len(self.pts)) =
        """Add two vectors together."""
        map((+), self.pts, other_pts) |*> vector
    def __sub__(self, vector(*other_pts)
                if len(other_pts) == len(self.pts)) =
        """Subtract one vector from another."""
        map((-), self.pts, other_pts) |*> vector
    def __neg__(self) =
        """Retrieve the negative of the vector."""
        self.pts |> map$(-) |*> vector
    def __mul__(self, other):
        """Scalar multiplication and dot product."""
        match vector(*other_pts) in other:
            assert len(other_pts) == len(self.pts)
            return map((*), self.pts, other_pts) |> sum  # dot product
        else:
            return self.pts |> map$(.*other) |*> vector  # scalar multiplication
    def __rmul__(self, other) =
        """Necessary to make scalar multiplication commutative."""
        self * other

# Test cases:
vector(1, 2, 3) |> print  # vector(*pts=(1, 2, 3))
vector(4, 5) |> vector |> print  # vector(*pts=(4, 5))
vector(3, 4) |> abs |> print  # 5
vector(1, 2) + vector(2, 3) |> print  # vector(*pts=(3, 5))
vector(2, 2) - vector(0, 1) |> print  # vector(*pts=(2, 1))
-vector(1, 3) |> print  # vector(*pts=(-1, -3))
(vector(1, 2) == "string") |> print  # False
(vector(1, 2) == vector(3, 4)) |> print  # False
(vector(2, 4) == vector(2, 4)) |> print  # True
2*vector(1, 2) |> print  # vector(*pts=(2, 4))
vector(1, 2) * vector(1, 3) |> print  # 7
```

Copy, paste! Now that was a lot of code. But looking it over, it looks clean, readable, and concise, and it does precisely what we intended it to do: create an algebraic data type for an immutable n-vector that supports the basic vector operations. And we did the whole thing without needing any imperative constructs like state or loops—pure functional programming.

## Case Study 4: `vector_field`

For the final case study, instead of me writing the code, and you looking at it, you'll be writing the code—of course, I won't be looking at it, but I will show you how I would have done it after you give it a shot by yourself.

_The bonus challenge for this section is to write each of the functions we'll be defining in just one line. Try using assignment functions to help with that!_

First, let's introduce the general goal of this case study. We want to write a program that will allow us to produce infinite vector fields that we can iterate over and apply operations to. And in our case, we'll say we only care about vectors with positive components.

Our first step, therefore, is going to be creating a field of all the points with positive `x` and `y` values—that is, the first quadrant of the `x-y` plane, which looks something like this:
```
...

(0,2)   ...

(0,1)   (1,1)   ...

(0,0)   (1,0)   (2,0)   ...
```

But since we want to be able to iterate over that plane, we're going to need to linearize it somehow, and the easiest way to do that is to split it up into diagonals, and traverse the first diagonal, then the second diagonal, and so on, like this:
```
(0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2), ...
```

### `diagonal_line`

Thus, our first function `diagonal_line(n)` should construct an iterator of all the points, represented as coordinate tuples, in the `n`th diagonal, starting with `(0, 0)` as the `0`th diagonal. Like we said at the start of this case study, this is where we I let go and you take over. Using all the tools of functional programming that Coconut provides, give `diagonal_line` a shot. When you're ready to move on, scroll down.

Here are some tests that you can use:
```coconut
diagonal_line(0) `isinstance` (list, tuple) |> print  # False (should be an iterator)
diagonal_line(0) |> list |> print  # [(0, 0)]
diagonal_line(1) |> list |> print  # [(0, 1), (1, 0)]
```

_Hint: the `n`th diagonal should contain `n+1` elements, so try starting with `range(n+1)` and then transforming it in some way._

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

That wasn't so bad, now was it? Now, let's take a look at my solution:
```coconut
def diagonal_line(n) = range(n+1) |> map$(i => (i, n-i))
```
Pretty simple, huh? We take `range(n+1)`, and use `map` to transform it into the right sequence of tuples.

### `linearized_plane`

Now that we've created our diagonal lines, we need to join them together to make the full linearized plane, and to do that we're going to write the function `linearized_plane()`. `linearized_plane` should produce an iterator that goes through all the points in the plane, in order of all the points in the first `diagonal(0)`, then the second `diagonal(1)`, and so on. `linearized_plane` is going to be, by necessity, an infinite iterator, since it needs to loop through all the points in the plane, which have no end. To help you accomplish this, remember that the `::` operator is lazy, and won't evaluate its operands until they're needed, which means it can be used to construct infinite iterators. When you're ready to move on, scroll down.

Tests:
```coconut
# Note: these tests use $[] notation, which we haven't introduced yet
#  but will introduce later in this case study; for now, just run the
#  tests, and make sure you get the same result as is in the comment
linearized_plane()$[0] |> print  # (0, 0)
linearized_plane()$[:3] |> list |> print  # [(0, 0), (0, 1), (1, 0)]
```

_Hint: instead of defining the function as `linearized_plane()`, try defining it as `linearized_plane(n=0)`, where `n` is the diagonal to start at, and use recursion to build up from there._

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

That was a little bit rougher than the first one, but hopefully still not too bad. Let's compare to my solution:
```coconut
def linearized_plane(n=0) = diagonal_line(n) :: linearized_plane(n+1)
```
As you can see, it's a very fundamentally simple solution: just use `::` and recursion to join all the diagonals together in order.

### `vector_field`

Now that we have a function that builds up all the points we need, it's time to turn them into vectors, and to do that we'll define the new function `vector_field()`, which should turn all the tuples in `linearized_plane` into vectors, using the n-vector class we defined earlier.

Tests:
```coconut
# You'll need to bring in the vector class from earlier to make these work
vector_field()$[0] |> print  # vector(*pts=(0, 0))
vector_field()$[2:3] |> list |> print  # [vector(*pts=(1, 0))]
```

_Hint: Remember, the way we defined vector it takes the components as separate arguments, not a single tuple. You may find the [Coconut built-in `starmap`](./DOCS.md#starmap) useful in dealing with that._

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

We're making good progress! Before we move on, check your solution against mine:
```coconut
def vector_field() = linearized_plane() |> starmap$(vector)
```
All we're doing is taking our `linearized_plane` and mapping `vector` over it, but using `starmap` instead of `map` so that `vector` gets called with each element of the tuple as a separate argument.

### Applications

Now that we've built all the functions we need for our vector field, it's time to put it all together and test it. Feel free to substitute in your versions of the functions below:
```coconut
data vector(*pts):
    """Immutable n-vector."""
    def __new__(cls, *pts):
        """Create a new vector from the given pts."""
        match [v `isinstance` vector] in pts:
            return v  # vector(v) where v is a vector should return v
        else:
            return pts |*> makedata$(cls)  # accesses base constructor
    def __abs__(self) =
        """Return the magnitude of the vector."""
        self.pts |> map$(.**2) |> sum |> (.**0.5)
    def __add__(self, vector(*other_pts)
                if len(other_pts) == len(self.pts)) =
        """Add two vectors together."""
        map((+), self.pts, other_pts) |*> vector
    def __sub__(self, vector(*other_pts)
                if len(other_pts) == len(self.pts)) =
        """Subtract one vector from another."""
        map((-), self.pts, other_pts) |*> vector
    def __neg__(self) =
        """Retrieve the negative of the vector."""
        self.pts |> map$(-) |*> vector
    def __mul__(self, other):
        """Scalar multiplication and dot product."""
        match vector(*other_pts) in other:
            assert len(other_pts) == len(self.pts)
            return map((*), self.pts, other_pts) |> sum  # dot product
        else:
            return self.pts |> map$(.*other) |*> vector  # scalar multiplication
    def __rmul__(self, other) =
        """Necessary to make scalar multiplication commutative."""
        self * other

def diagonal_line(n) = range(n+1) |> map$(i => (i, n-i))
def linearized_plane(n=0) = diagonal_line(n) :: linearized_plane(n+1)
def vector_field() = linearized_plane() |> starmap$(vector)

# Test cases:
diagonal_line(0) `isinstance` (list, tuple) |> print  # False (should be an iterator)
diagonal_line(0) |> list |> print  # [(0, 0)]
diagonal_line(1) |> list |> print  # [(0, 1), (1, 0)]
linearized_plane()$[0] |> print  # (0, 0)
linearized_plane()$[:3] |> list |> print  # [(0, 0), (0, 1), (1, 0)]
vector_field()$[0] |> print  # vector(*pts=(0, 0))
vector_field()$[2:3] |> list |> print  # [vector(*pts=(1, 0))]
```

Copy, paste! Once you've made sure everything is working correctly if you substituted in your own functions, take a look at the last 4 tests. You'll notice that they use a new notation, similar to the notation for partial application we saw earlier, but with brackets instead of parentheses. This is the notation for iterator slicing. Similar to how partial application was lazy function calling, iterator slicing is _lazy sequence slicing_. Like with partial application, it is helpful to think of `$` as the _lazy-ify_ operator, in this case turning normal Python slicing, which is evaluated immediately, into lazy iterator slicing, which is evaluated only when the elements in the slice are needed.

With that in mind, now that we've built our vector field, it's time to use iterator slicing to play around with it. Try doing something cool to our vector fields like
- create a `magnitude_field` where each point is that vector's magnitude
- combine entire vector fields together with `map` and the vector addition and multiplication methods we wrote earlier

then use iterator slicing to take out portions and examine them.

## Case Study 5: `vector` Part II

For the some of the applications you might want to use your `vector_field` for, it might be desirable to add some useful methods to our `vector`. In this case study, we're going to be focusing on one in particular: `.angle`.

`.angle` will take one argument, another vector, and compute the angle between the two vectors. Mathematically, the formula for the angle between two vectors is the dot product of the vectors' respective unit vectors. Thus, before we can implement `.angle`, we're going to need `.unit`. Mathematically, the formula for the unit vector of a given vector is that vector divided by its magnitude. Thus, before we can implement `.unit`, and by extension `.angle`, we'll need to start by implementing division.

### `__truediv__`

Vector division is just scalar division, so we're going to write a `__truediv__` method that takes `self` as the first argument and `other` as the second argument, and returns a new vector the same size as `self` with every element divided by `other`. For an extra challenge, try writing this one in one line using assignment function notation.

Tests:
```coconut
vector(3, 4) / 1 |> print  # vector(*pts=(3.0, 4.0))
vector(2, 4) / 2 |> print  # vector(*pts=(1.0, 2.0))
```

_Hint: Look back at how we implemented scalar multiplication._

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

Here's my solution for you to check against:
```coconut
    def __truediv__(self, other) = self.pts |> map$(x => x/other) |*> vector
```

### `.unit`

Next up, `.unit`. We're going to write a `unit` method that takes just `self` as its argument and returns a new vector the same size as `self` with each element divided by the magnitude of `self`, which we can retrieve with `abs`. This should be a very simple one-line function.

Tests:
```coconut
vector(0, 1).unit() |> print  # vector(*pts=(0.0, 1.0))
vector(5, 0).unit() |> print  # vector(*pts=(1.0, 0.0))
```

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

Here's my solution:
```coconut
    def unit(self) = self / abs(self)
```

### `.angle`

This one is going to be a little bit more complicated. For starters, the mathematical formula for the angle between two vectors is the `math.acos` of the dot product of those vectors' respective unit vectors, and recall that we already implemented the dot product of two vectors when we wrote `__mul__`. So, `.angle` should take `self` as the first argument and `other` as the second argument, and if `other` is a vector, use that formula to compute the angle between `self` and `other`, or if `other` is not a vector, `.angle` should raise a `MatchError`. To accomplish this, we're going to want to use destructuring assignment to check that `other` is indeed a `vector`.

Tests:
```coconut
import math
vector(2, 0).angle(vector(3, 0)) |> print  # 0.0
print(vector(1, 0).angle(vector(0, 2)), math.pi/2)  # should be the same
vector(1, 2).angle(5)  # MatchError
```

_Hint: Look back at how we checked whether the argument to `factorial` was an integer using pattern-matching._

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

Here's my solution—take a look:
```coconut
    def angle(self, other `isinstance` vector) = math.acos(self.unit() * other.unit())
```

And now it's time to put it all together. Feel free to substitute in your own versions of the methods we just defined.

```coconut
import math  # necessary for math.acos in .angle

data vector(*pts):
    """Immutable n-vector."""
    def __new__(cls, *pts):
        """Create a new vector from the given pts."""
        match [v `isinstance` vector] in pts:
            return v  # vector(v) where v is a vector should return v
        else:
            return pts |*> makedata$(cls)  # accesses base constructor
    def __abs__(self) =
        """Return the magnitude of the vector."""
        self.pts |> map$(.**2) |> sum |> (.**0.5)
    def __add__(self, vector(*other_pts)
                if len(other_pts) == len(self.pts)) =
        """Add two vectors together."""
        map((+), self.pts, other_pts) |*> vector
    def __sub__(self, vector(*other_pts)
                if len(other_pts) == len(self.pts)) =
        """Subtract one vector from another."""
        map((-), self.pts, other_pts) |*> vector
    def __neg__(self) =
        """Retrieve the negative of the vector."""
        self.pts |> map$(-) |*> vector
    def __mul__(self, other):
        """Scalar multiplication and dot product."""
        match vector(*other_pts) in other:
            assert len(other_pts) == len(self.pts)
            return map((*), self.pts, other_pts) |> sum  # dot product
        else:
            return self.pts |> map$(.*other) |*> vector  # scalar multiplication
    def __rmul__(self, other) =
        """Necessary to make scalar multiplication commutative."""
        self * other
    # New one-line functions necessary for finding the angle between vectors:
    def __truediv__(self, other) = self.pts |> map$(x => x/other) |*> vector
    def unit(self) = self / abs(self)
    def angle(self, other `isinstance` vector) = math.acos(self.unit() * other.unit())

# Test cases:
vector(3, 4) / 1 |> print  # vector(*pts=(3.0, 4.0))
vector(2, 4) / 2 |> print  # vector(*pts=(1.0, 2.0))
vector(0, 1).unit() |> print  # vector(*pts=(0.0, 1.0))
vector(5, 0).unit() |> print  # vector(*pts=(1.0, 0.0))
vector(2, 0).angle(vector(3, 0)) |> print  # 0.0
print(vector(1, 0).angle(vector(0, 2)), math.pi/2)  # should be the same
vector(1, 2).angle(5)  # MatchError
```
_One note of warning here: be careful not to leave a blank line when substituting in your methods, or the interpreter will cut off the code for the `vector` there. This isn't a problem in normal Coconut code, only here because we're copy-and-pasting into the command line._

Copy, paste! If everything is working, you can try going back to playing around with `vector_field` [applications](#applications) using our new methods.

## Filling in the Gaps

And with that, this tutorial is out of case studies—but that doesn't mean Coconut is out of features! In this last section, we'll touch on some of the other useful features of Coconut that we managed to miss in the case studies.

### Lazy Lists

First up is lazy lists. Lazy lists are lazily-evaluated lists, similar in their laziness to Coconut's `::` operator, in that any expressions put inside a lazy list won't be evaluated until that element of the lazy list is needed. The syntax for lazy lists is exactly the same as the syntax for normal lists, but with "banana brackets" (`(|` and `|)`) instead of normal brackets, like so:
```coconut
abc = (| a, b, c |)
```

Unlike Python iterators, lazy lists can be iterated over multiple times and still return the same result.

Unlike Python lists, however, using a lazy list, it is possible to define the values used in the following expressions as needed without raising a `NameError`:

```coconut
abcd = (| d(a), d(b), d(c) |)  # a, b, c, and d are not defined yet
def d(n) = n + 1

a = 1
abcd$[0]
b = 2
abcd$[1]
c = 3
abcd$[2]
```

### Function Composition

Next is function composition. In Coconut, this is primarily accomplished through the `f1 ..> f2` operator, which takes two functions and composes them, creating a new function equivalent to `(*args, **kwargs) => f2(f1(*args, **kwargs))`. This can be useful in combination with partial application for piecing together multiple higher-order functions, like so:
```coconut
zipsum = zip ..> map$(sum)
```

_While `..>` is generally preferred, if you'd rather use the more traditional mathematical function composition ordering, you can get that with the `<..` operator._

If the composed functions are wrapped in parentheses, arguments can be passed into them:
```coconut
def plus1(x) = x + 1
def square(x) = x * x

(square ..> plus1)(3) == 10  # True
```

Functions of different arities can be composed together, as long as they are in the correct order. If they are in the incorrect order, a `TypeError` will be raised. In this example we will compose a unary function with a binary function:
```coconut
def add(n, m) = n + m  # binary function
def square(n) = n * n  # unary function

(square ..> add)(3, 1)    # Raises TypeError: square() takes exactly 1 argument (2 given)
(add ..> square)(3, 1)    # 16
```

Another useful trick with function composition involves composing a function with a higher-order function:
```coconut
def inc_or_dec(t):
    # Our higher-order function, which returns another function
    if t:
        return x => x+1
    else:
        return x => x-1

def square(n) = n * n

square_inc = inc_or_dec(True) ..> square
square_dec = inc_or_dec(False) ..> square
square_inc(4)  # 25
square_dec(4)  # 9

```

_Note: Coconut also supports the function composition operators `..`, `..*>`, `<*..`, `..**>`, and `<**..`._

### Implicit Partials

Another useful Coconut feature is implicit partials. Coconut supports a number of different "incomplete" expressions that will evaluate to a function that takes in the part necessary to complete them, that is, an implicit partial application function. The different allowable expressions are:
```coconut
.attr
.method(args)
func$
seq[]
iter$[]
.[slice]
.$[slice]
```

For a full explanation of what each implicit partial does, see Coconut's documentation on [implicit partials](./DOCS.md#implicit-partial-application).

### Type Annotations

For many people, one of the big downsides of Python is the fact that it is dynamically-typed. In Python, this problem is addressed by [MyPy](http://mypy-lang.org/), a static type analyzer for Python, which can check Python-3-style type annotations such as
```coconut_python
def plus1(x: int) -> int:
    return x + 1
a: int = plus1(10)
```

Unfortunately, in Python, such type annotation syntax only exists in Python 3. Not to worry in Coconut, however, which compiles Python-3-style type annotations to universally compatible type comments. Not only that, but Coconut has built-in [MyPy integration](./DOCS.md#mypy-integration) for automatically type-checking your code, and its own [enhanced type annotation syntax](./DOCS.md#enhanced-type-annotation) for more easily expressing complex types, like so:
```coconut
def int_map(
    f: int -> int,
    xs: int[],
) -> int[] =
    xs |> map$(f) |> list
```

### Further Reading

And that's it for this tutorial! But that's hardly it for Coconut. All of the features examined in this tutorial, as well as a bunch of others, are detailed in Coconut's [documentation](./DOCS.md).

Also, if you have any other questions not covered in this tutorial, feel free to ask around at Coconut's [Gitter](https://gitter.im/evhub/coconut), a GitHub-integrated chat room for Coconut developers.

Finally, Coconut is a new, growing language, and if you'd like to get involved in the development of Coconut, all the code is available completely open-source on Coconut's [GitHub](https://github.com/evhub/coconut). Contributing is a simple as forking the code, making your changes, and proposing a pull request! See Coconuts [contributing guidelines](./CONTRIBUTING.md) for more information.
