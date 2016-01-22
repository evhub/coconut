_In the process of being rewritten from the ground up for next version._

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
        return iter(())
```

```python
data vector(pts):
    """Immutable n-vector."""
    def __new__(cls, *pts):
        """Create a new vector from the given pts."""
        if len(pts) == 1 and pts[0] `isinstance` vector:
            return pts[0]
        else:
            return pts |> tuple |> datamaker(cls)
    def __abs__(self):
        return self.pts |> map$((x) -> x**2) |> sum |> ((s) -> s**0.5)
    def __eq__(self, other):
        match vector(=self.pts) in other:
            return True
        else:
            return False
    def __add__(self, other):
        match vector(pts) in other if len(pts) == len(self.pts):
            return map((+), self.pts, pts) |*> vector
        else:
            raise TypeError("vectors can only be added to other vectors of the same length")
    def __mul__(self, other):
        match vector(pts) in other if len(pts) == len(self.pts):
            return map((*), self.pts, pts) |> sum
        else:
            return self.pts |> map$((*)$(other)) |*> vector
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
