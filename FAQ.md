# Coconut Frequently Asked Questions

<!-- MarkdownTOC -->

1. [Can I use Python modules from Coconut and Coconut modules from Python?](#can-i-use-python-modules-from-coconut-and-coconut-modules-from-python)
1. [What versions of Python does Coconut support?](#what-versions-of-python-does-coconut-support)
1. [Help! I tried to write a recursive iterator and my Python segfaulted!](#help-i-tried-to-write-a-recursive-iterator-and-my-python-segfaulted)
1. [If I'm already perfectly happy with Python, why should I learn Coconut?](#if-im-already-perfectly-happy-with-python-why-should-i-learn-coconut)
1. [How will I be able to debug my Python if I'm not the one writing it?](#how-will-i-be-able-to-debug-my-python-if-im-not-the-one-writing-it)
1. [I don't like functional programming, should I still learn Coconut?](#i-dont-like-functional-programming-should-i-still-learn-coconut)
1. [I don't know functional programming, should I still learn Coconut?](#i-dont-know-functional-programming-should-i-still-learn-coconut)
1. [I don't know Python very well, should I still learn Coconut?](#i-dont-know-python-very-well-should-i-still-learn-coconut)
1. [Why isn't Coconut purely functional?](#why-isnt-coconut-purely-functional)
1. [Won't a transpiled language like Coconut be bad for the Python community?](#wont-a-transpiled-language-like-coconut-be-bad-for-the-python-community)
1. [I want to contribute to Coconut, how do I get started?](#i-want-to-contribute-to-coconut-how-do-i-get-started)
1. [Why the name Coconut?](#why-the-name-coconut)
1. [Who developed Coconut?](#who-developed-coconut)

<!-- /MarkdownTOC -->

### Can I use Python modules from Coconut and Coconut modules from Python?

Yes and yes! Coconut compiles to Python, so Coconut modules are accessible from Python and Python modules are accessible from Coconut, including the entire Python standard library.

### What versions of Python does Coconut support?

Coconut supports any Python version `>= 2.6` on the `2.x` branch or `>= 3.2` on the `3.x` branch. See [compatible Python versions](http://coconut.readthedocs.io/en/master/DOCS.html#compatible-python-versions) for more information.

### Help! I tried to write a recursive iterator and my Python segfaulted!

No problem—just use Coconut's [`recursive_iterator`](http://coconut.readthedocs.io/en/master/DOCS.html#recursive_iterator) decorator and you should be fine. This is a [known Python issue](http://bugs.python.org/issue14010) but `recursive_iterator` will fix it for you.

### If I'm already perfectly happy with Python, why should I learn Coconut?

You're exactly the person Coconut was built for! Coconut lets you keep doing the thing you do well—write Python—without having to worry about annoyances like version compatibility, while also allowing you to do new cool things you might never have thought were possible before like pattern-matching and lazy evaluation. If you've ever used a functional programming language before, you'll know that functional code is often much simpler, cleaner, and more readable (but not always, which is why Coconut isn't purely functional). Python is a wonderful imperative language, but when it comes to modern functional programming—which, in Python's defense, it wasn't designed for—Python falls short, and Coconut corrects that shortfall.

### How will I be able to debug my Python if I'm not the one writing it?

Ease of debugging has long been a problem for all compiled languages, including languages like `C` and `C++` that these days we think of as very low-level languages. The solution to this problem has always been the same: line number maps. If you know what line in the compiled code corresponds to what line in the source code, you can easily debug just from the source code, without ever needing to deal with the compiled code at all. In Coconut, this can easily be accomplished by passing the `--line-numbers` or `-l` flag, which will add a comment to every line in the compiled code with the number of the corresponding line in the source code. Alternatively, `--keep-lines` or `-k` will put in the verbatim source line instead of or in addition to the source line number. Then, if Python raises an error, you'll be able to see from the snippet of the compiled code that it shows you a comment telling you what line in your source code you need to look at to debug the error.

### I don't like functional programming, should I still learn Coconut?

Definitely! While Coconut is great for functional programming, it also has a bunch of other awesome features as well, including the ability to compile Python 3 code into universal Python code that will run the same on _any version_. And that's not even mentioning all of the features like pattern-matching and destructuring assignment with utility extending far beyond just functional programming. That being said, I'd highly recommend you give functional programming a shot, and since Coconut isn't purely functional, it's a great introduction to the functional style.

### I don't know functional programming, should I still learn Coconut?

Yes, absolutely! Coconut's [tutorial](http://coconut.readthedocs.io/en/master/HELP.html) assumes absolutely no prior knowledge of functional programming, only Python. Because Coconut is not a purely functional programming language, and all valid Python is valid Coconut, Coconut is a great introduction to functional programming. If you learn Coconut, you'll be able to try out a new functional style of programming without having to abandon all the Python you already know and love.

### I don't know Python very well, should I still learn Coconut?

Maybe. If you know the very basics of Python, and are also very familiar with functional programming, then definitely—Coconut will let you continue to use all your favorite tools of functional programming while you make your way through learning Python. If you're not very familiar either with Python, or with functional programming, then you may be better making your way through a Python tutorial before you try learning Coconut. That being said, using Coconut to compile your pure Python code might still be very helpful for you, since it will alleviate having to worry about version incompatibility.

### Why isn't Coconut purely functional?

The short answer is that Python isn't purely functional, and all valid Python is valid Coconut. The long answer is that Coconut isn't purely functional for the same reason Python was never purely imperative—different problems demand different approaches. Coconut is built to be _useful_, and that means not imposing constraints about what style the programmer is allowed to use. That being said, Coconut is built specifically to work nicely when programming in a functional style, which means if you want to write all your code purely functionally, Coconut will make it a smooth experience, and allow you to have good-looking code to show for it.

### Won't a transpiled language like Coconut be bad for the Python community?

I certainly hope not! Unlike most transpiled languages, all valid Python is valid Coconut. Coconut's goal isn't to replace Python, but to _extend_ it. If a newbie learns Coconut, it won't mean they have a harder time learning Python, it'll mean they _already know_ Python. And not just any Python, the newest and greatest—Python 3. And of course, Coconut is perfectly interoperable with Python, and uses all the same libraries—thus, Coconut can't split the Python community, because the Coconut community _is_ the Python community.

### I want to contribute to Coconut, how do I get started?

That's great! Coconut is completely open-source, and new contributors are always welcome. Contributing to Coconut is as simple as forking Coconut on [GitHub](https://github.com/evhub/coconut), making changes to the [`develop` branch](https://github.com/evhub/coconut/tree/develop), and proposing a pull request. If you have any questions at all about contributing, including understanding the source code, figuring out how to implement a specific change, or just trying to figure out what needs to be done, try asking around at Coconut's [Gitter](https://gitter.im/evhub/coconut), a GitHub-integrated chat room for Coconut developers.

### Why the name Coconut?

![Monty Python and the Holy Grail](http://i.imgur.com/PoFot.jpg)

If you don't get the reference, the image above is from [Monty Python and the Holy Grail](https://en.wikipedia.org/wiki/Monty_Python_and_the_Holy_Grail), in which the Knights of the Round Table bang Coconuts together to mimic the sound of riding a horse. The name was chosen to reference the fact that [Python is named after Monty Python](https://www.python.org/doc/essays/foreword/) as well.

### Who developed Coconut?

[Evan Hubinger](https://github.com/evhub) is an undergraduate student studying mathematics and computer science at [Harvey Mudd College](https://www.hmc.edu/). You can find him on LinkedIn at <https://www.linkedin.com/in/ehubinger>.
