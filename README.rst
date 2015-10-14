Coconut
=======

*Coconut is a variant of Python built for simple, elegant functional programming.*

Coconut can be found on GitHub_ and PyPI_.

A full **introduction and tutorial** of the Coconut programming language can be found in the HELP_ file. If you don't know what you're doing, you should start there.

The full Coconut **documentation** can be found in the DOCS_ file. If you're looking for info about a specific feature, you should go there.

.. _GitHub: https://github.com/evhub/coconut
.. _PyPI: https://pypi.python.org/pypi/coconut
.. _HELP: https://github.com/evhub/coconut/blob/master/HELP.md
.. _DOCS: https://github.com/evhub/coconut/blob/master/DOCS.md

Why Coconut?
------------

\1. **It's just Python!**

Love Python? So do I! All valid Python 3 is also valid Coconut. That means that not only does learning Coconut not require learning new libraries, it doesn't even require learning a new core syntax! Integrating Coconut into your existing projects is as simple as replacing ``.py`` with ``.coc``.

\2. *But...* **Coconut has powerful destructuring assignment.**

Enjoy writing simple, readable code like ``a, b = get_two_items()``, but wish you could do something like ``{"text": text, "tags": {"href": link}} = get_html()``? Coconut provides destructuring assignment that can accoplish all that and much, much more!

\3. *But...* **Coconut has nicer syntax.**

Hate typing out ``lambda`` or ``return`` every time you want to create a one-line function? Love rhetorical questions and parallel grammatical structure? So do I! Coconut supports function definition syntax that's as simple as ``(x) -> x`` or ``def f(x) = x``.

\4. *But...* **Coconut has algebraic data types.**

If you know Python, then you already know how useful immutable lists can be. Don't believe me? They're called tuples, of course! Python lets tuples hog all that immutability goodness, but wouldn't it be nice if you could create arbitrary immutable data types? Coconut's ``data`` statement allows you to create any sort of immutable data type that you wish!

\5. *But...* **Coconut has pattern matching.**

If you've ever used a functional programming language before, you probably know how awesome pattern matching is. Coconut's ``match`` statement brings all that to Python. Here's just a taste of how powerful Coconut's pattern-matching is:

    >>> data point(x, y): pass
    >>> my_point = point(3, 0)
    >>> match point(x, 0) in my_point:
           print(x)
    3

\6. *But...* **Coconut allows for truly Pythonic functional programming.**

Not only can Coconut do all those awesome things, it also has syntactic support for lazy lists, iterator chaining, iterator slicing, partial application, function composition, pipeline-style programming, infix calling, frozen set literals, unicode operators, tail call optimization, and a whole host of other constructs for you to explore.

Ready to give Coconut a try? Head over to the HELP_ file for a full tutorial to help (ha, get it?) you get started.
