# Coconut

Coconut is a **functional programming language** that **compiles to [Python](https://www.python.org/)**. Since **all valid Python is valid Coconut**, using Coconut will only extend and enhance what you're already capable of in Python.

Why use Coconut? Coconut is built to be fundamentally **useful**. Coconut enhances the repertoire of Python programmers to include the tools of modern functional programming, in such a way that those tools are **easy** to use and immensely **powerful**; that is, **Coconut does to functional programming what Python did to imperative programming**. And Coconut code runs the same on **any Python version**, making the Python 2/3 split a thing of the past.

Installing Coconut is as easy as

1. installing [Python](https://www.python.org/downloads/),
2. opening a command-line prompt,
3. and entering:

<div class="code-block">pip install coconut</div>

which will give you access to all the features of Coconut, which adds to Python **built-in, syntactical support** for:
- pipeline-style programming
```coconut
"hello, world!" |> print
```
- prettier lambdas
```coconut
(x) -> x ** 2
```
- partial application
```coconut
range(10) |> map$(pow$(?, 2)) |> list
```
- pattern-matching
```coconut
match [head] + tail in [0, 1, 2, 3]:
    print(head, tail)
```
- destructuring assignment
```coconut
{"list": [0] + rest} = {"list": [0, 1, 2, 3]}
```
- infix notation
```coconut
5 `mod` 3 == 2
```
- operator functions
```coconut
range(15) |> map$((*)$(2)) |> list
```
- function composition
```coconut
(f .. g .. h)(x, y, z)
```
- lazy lists
```coconut
(| first_elem() |) :: rest_elems()
```
- parallel programming
```coconut
range(100) |> parallel_map$(pow$(2)) |> list
```
- tail recursion optimization
```coconut
def factorial(n, acc=1):
    case n:
        match 0:
            return acc
        match _ is int if n > 0:
            return factorial(n-1, acc*n)
```
- algebraic data types
```coconut
data Empty()
data Leaf(n)
data Node(l, r)

def size(Empty()) = 0

@addpattern(size)
def size(Leaf(n)) = 1

@addpattern(size)
def size(Node(l, r)) = size(l) + size(r)
```

and much more!

Like what you see? Don't forget to star Coconut on GitHub!

<a class="github-button" href="https://github.com/evhub/coconut" data-icon="octicon-star" data-size="large" data-show-count="true" aria-label="Star evhub/coconut on GitHub">Star</a>

Ready to get started? Here are some links to help you out:
- [Coconut's **tutorial**](http://coconut.readthedocs.io/en/latest/HELP.html) will guide you through the process of starting to enhance your Python with Coconut in a straightforward, easy-to-follow way.
- [Coconut's **documentation**](http://coconut.readthedocs.io/en/latest/DOCS.html) is an extensive catalog of information on all of Coconut's features for whenever you see something that you want more information about.
- [The Coconut FAQ](http://coconut.readthedocs.io/en/latest/FAQ.html) should hopefully answer any questions you might have about who Coconut is built for and whether or not you should use it.
- [Creating a new issue](https://github.com/evhub/coconut/issues/new) is the best way for you to get help if you're having a problem with Coconut—just detail the problem in the issue and it will be addressed as soon as possible.
- [Coconut's chat room](https://gitter.im/evhub/coconut) is a great place if you want to pose any general questions, concerns, or comments you have about Coconut to other Coconut developers.
