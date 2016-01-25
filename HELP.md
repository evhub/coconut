# Coconut Tutorial

Why Coconut?
------------

1\. **It's just Python!**

Love Python? So do I! All valid Python 3 is also valid Coconut. That means that not only does learning Coconut not require learning new libraries, it doesn't even require learning a new core syntax! Integrating Coconut into your existing projects is as simple as replacing `.py` with `.coc`.

2\. *But...* **Coconut has powerful destructuring assignment.**

Enjoy writing simple, readable code like `a, b = get_two_items()`, but wish you could do something like `{"text": text, "tags": [first] + rest} = get_dict()`? Coconut provides destructuring assignment that can accoplish all that and much, much more!

3\. *But...* **Coconut has nicer syntax.**

Hate typing out `lambda` or `return` every time you want to create a one-line function? Love rhetorical questions and parallel grammatical structure? So do I! Coconut supports function definition syntax that's as simple as `(x) -> x` or `def f(x) = x`.

4\. *But...* **Coconut has algebraic data types.**

If you know Python, then you already know how useful immutable lists can be. Don't believe me? They're called tuples, of course! Python lets tuples hog all that immutability goodness, but wouldn't it be nice if you could create arbitrary immutable data types? Coconut's `data` statement allows you to create any sort of immutable data type that you wish!

5\. *But...* **Coconut has pattern-matching.**

If you've ever used a functional programming language before, you probably know how awesome pattern-matching is. Coconut's `match` statement brings all that to Python. Here's just a taste of how powerful Coconut's pattern-matching is:

```
>>> data point(x, y): pass
>>> my_point = point(3, 0)
>>> match point(a, 0) in my_point:
       print("x = " + str(a))
x = 3
```

6\. *But...* **Coconut has lazy evaluation.**

Common to functional programming, but missing from Python, is lazy evaluation, where expressions aren't evaluated until they're needed. Coconut's powerful constructs for lazy evaluation allows for such cool things as:

```
>>> def natural_numbers(n=0) = (n,) :: natural_numbers(n+1)
>>> natural_numbers()$[0:5] |> list |> print
[0, 1, 2, 3, 4]
```

7\. *But...* **Coconut allows for truly Pythonic functional programming.**

Not only can Coconut do all those awesome things, it also has syntactic support for partial application, function composition, infix calling, lazy lists, frozen set literals, unicode operators, tail call optimization, and a whole host of other constructs for you to explore, including built-in integration with IPython/Jupyter.

```python
product = reduce$((*))
```

```python
def factorial(n):
    """Compute n! where n is an integer > 0."""
    case n:
        match 0:
            return 1
        match n is int if n > 0:
            return n * factorial(n-1)
    else:
        raise TypeError("the argument to factorial must be an integer > 0")
```

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
        return self + -other
```

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
