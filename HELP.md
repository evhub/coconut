# Coconut Tutorial

This tutorial will teach you how to write clean, functional, Pythonic code using the [Coconut](https://github.com/evhub/coconut) programming language. It is assumed that the reader knows some basic Python, but no other prior knowledge or experience is required.

## I. Getting Started

### 1. Install Coconut

The first thing you're going to need to do is install Coconut. Since Coconut is hosted on the [Python Package Index](https://pypi.python.org/pypi/coconut), it can be installed easily using `pip`. Simply install [Python](https://www.python.org/downloads/), open up a command line prompt, and enter the following:
```
pip install coconut
```

To test that `coconut` is working, make sure the Coconut help appears when you enter into the command line:
```
coconut -h
```

_Note: If the `pip` or `coconut` commands aren't working for you, try prefixing them with `python -m`, like so:_
```
python -m pip install coconut
python -m coconut -h
```

### 2. Set Up a Workspace

Now that you've installed Coconut, it's time to create your first Coconut program. Open up your favorite text editor and save a new file named `tutorial.coc`. It is recommended that you tell your text editor to treat all `.coc` files as Python source files for the purpose of syntax highlighting. All Coconut files should use the extension `.coc` so they can be recognized as such when compiling folders of many different files.

### 3. Start Coding!

If you're familiar with Python, then you're already familiar with most of Coconut. Coconut is nearly a strict superset of Python 3 syntax, with the sole exception of `lambda` statements, which will be later in this tutorial. For now, let's start with a simple `hello, world!` program:
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

You should now notice that a new file, `tutorial.py` was created in the `tutorial.coc` directory when you ran the compiler. That file contains the compiled Python code, which was why you had to enter `python tutorial.py` instead of `python tutorial.coc`.

Open `tutorial.py` and look inside. You should see two sections, `Coconut Header` and `Compiled Coconut`. The `Coconut Header` section contains code inserted into all compiled coconut files, whereas the `Compiled Coconut` section contains the specific code the compiler produced from your source file.

### 5. Understanding Compiled Folders

You might have noticed that the `Coconut Header` section in `tutorial.py` is rather large. This is because that section contains all the code necessary to set up the Coconut environment. Because Coconut needs to set up that environment in every file, it puts a header at the top.

It would be terribly innefficient, however, if Coconut put that entire header in every file of a module (or other folder of files that are intended to stay together). Instead, Coconut puts all of that code in a `__coconut__.py` file in each folder directory.

### 6. Compile a Folder!

To compile a module (or folder) this way, simply call the `coconut` command with the module (or folder) directory as the first argument. Go ahead and try it on the `tutorial.coc` directory:
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

## II. Functions

### 1. Lambdas

Now that you've gotten your feet wet with a simple `hello, world!` program, but before we delve into the special things Coconut can do that Python can't, we should cover the one exception to the rule of Coconut being a strict superset of Python: lambdas.

In Python, lambdas are ugly and bulky, requiring the entire word `lambda` to be written out every time one is constructed. This is fine if in-line functions are very rarely needed, but in functional programming in-line functions are an essential tool, and so Coconut substitues in a much simpler lambda syntax: the `->` operator.

Just to demonstrate the lambda syntax, try modifying your `hello, world!` program by adding a function defined with a lambda that prints `"hello, "+arg+"!"`, and call it with `"lambdas"` as the `arg`:
```
hello = (arg="hello") -> print("hello, "+arg+"!")
hello("lambdas")
```

Then run it and test that it works:
```
$ coconut tutorial.coc
...
$ python tutorial.py
hello, lambdas!
```

### 2. Partial Application

### 3. Function Composition

### 4. Pipe Forward

### 5. Infix Calling

### 6. Function Definition

### 7. Operator Functions

### 8. `reduce`

### 9. `recursive`

## III. Iterators

### 1. Slicing

### 2. Chaining

### 3. `takewhile`

## IV. Values

### 1. `data`

## V. Further Reading

This tutorial was too short to be able to fully cover all the features provided by the Coconut programming language. For the full documentation, see the [DOCS](https://github.com/evhub/coconut/blob/master/DOCS.md) file.
