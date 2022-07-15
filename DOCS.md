```{eval-rst}
:tocdepth: 3
```

# Coconut Documentation

```{contents}
---
local:
depth: 2
---
```

## Overview

This documentation covers all the features of the [Coconut Programming Language](http://evhub.github.io/coconut/), and is intended as a reference/specification, not a tutorialized introduction. For a full introduction and tutorial of Coconut, see [the tutorial](HELP.html).

Coconut is a variant of [Python](https://www.python.org/) built for **simple, elegant, Pythonic functional programming**. Coconut syntax is a strict superset of Python 3 syntax. Thus, users familiar with Python will already be familiar with most of Coconut.

The Coconut compiler turns Coconut code into Python code. The primary method of accessing the Coconut compiler is through the Coconut command-line utility, which also features an interpreter for real-time compilation. In addition to the command-line utility, Coconut also supports the use of IPython/Jupyter notebooks.

Thought Coconut syntax is primarily based on that of Python, Coconut also takes inspiration from [Haskell](https://www.haskell.org/), [CoffeeScript](http://coffeescript.org/), [F#](http://fsharp.org/), and [patterns.py](https://github.com/Suor/patterns).

## Try It Out

If you want to try Coconut in your browser, check out the [online interpreter](https://cs121-team-panda.github.io/coconut-interpreter).

## Installation

### Using Pip

Since Coconut is hosted on the [Python Package Index](https://pypi.python.org/pypi/coconut), it can be installed easily using `pip`. Simply [install Python](https://www.python.org/downloads/), open up a command-line prompt, and enter
```
pip install coconut
```
which will install Coconut and its required dependencies.

_Note: If you have an old version of Coconut installed and you want to upgrade, run `pip install --upgrade coconut` instead._

If you are encountering errors running `pip install coconut`, try adding `--user` or running
```
pip install --no-deps --upgrade coconut pyparsing
```
which will force Coconut to use the pure-Python [`pyparsing`](https://github.com/pyparsing/pyparsing) module instead of the faster [`cPyparsing`](https://github.com/evhub/cpyparsing) module. If you are still getting errors, you may want to try [using conda](#using-conda) instead.

If `pip install coconut` works, but you cannot access the `coconut` command, be sure that Coconut's installation location is in your `PATH` environment variable. On UNIX, that is `/usr/local/bin` (without `--user`) or `${HOME}/.local/bin/` (with `--user`).

### Using Conda

If you prefer to use [`conda`](https://conda.io/docs/) instead of `pip` to manage your Python packages, you can also install Coconut using `conda`. Just [install `conda`](https://conda.io/miniconda.html), open up a command-line prompt, and enter
```
conda config --add channels conda-forge
conda install coconut
```
which will properly create and build a `conda` recipe out of [Coconut's `conda-forge` feedstock](https://github.com/conda-forge/coconut-feedstock).

_Note: Coconut's `conda` recipe uses `pyparsing` rather than `cPyparsing`, which may lead to degraded performance relative to installing Coconut via `pip`._

### Using Homebrew

If you prefer to use [Homebrew](https://brew.sh/), you can also install Coconut using `brew`:
```
brew install coconut
```

_Note: Coconut's Homebrew formula may not always be up-to-date with the latest version of Coconut._

### Optional Dependencies

Coconut also has optional dependencies, which can be installed by entering
```
pip install coconut[name_of_optional_dependency]
```
or, to install multiple optional dependencies,
```
pip install coconut[opt_dep_1,opt_dep_2]
```

The full list of optional dependencies is:

- `all`: alias for `jupyter,watch,jobs,mypy,backports` (this is the recommended way to install a feature-complete version of Coconut),
- `jupyter/ipython`: enables use of the `--jupyter` / `--ipython` flag,
- `watch`: enables use of the `--watch` flag,
- `jobs`: improves use of the `--jobs` flag,
- `mypy`: enables use of the `--mypy` flag,
- `backports`: enables use of the [`asyncio`](https://docs.python.org/3/library/asyncio.html) library on older Python versions by making use of [`trollius`](https://pypi.python.org/pypi/trollius), the [`enum`](https://docs.python.org/3/library/enum.html) library by making use of [`aenum`](https://pypi.org/project/aenum), and other similar backports.
- `tests`: everything necessary to test the Coconut language itself,
- `docs`: everything necessary to build Coconut's documentation, and
- `dev`: everything necessary to develop on Coconut, including all of the dependencies above.

### Develop Version

Alternatively, if you want to test out Coconut's latest and greatest, enter
```
pip install coconut-develop
```
which will install the most recent working version from Coconut's [`develop` branch](https://github.com/evhub/coconut/tree/develop). Optional dependency installation is supported in the same manner as above. For more information on the current development build, check out the [development version of this documentation](http://coconut.readthedocs.io/en/develop/DOCS.html). Be warned: `coconut-develop` is likely to be unstable—if you find a bug, please report it by [creating a new issue](https://github.com/evhub/coconut/issues/new).

## Compilation

### Usage

```
coconut [-h] [--and source dest] [-v] [-t version] [-i] [-p] [-a] [-l] [-k] [-w] [-r] [-n] [-d] [-q] [-s]
       [--no-tco] [--no-wrap] [-c code] [-j processes] [-f] [--minify] [--jupyter ...] [--mypy ...]
       [--argv ...] [--tutorial] [--docs] [--style name] [--history-file path] [--vi-mode]
       [--recursion-limit limit] [--site-install] [--site-uninstall] [--verbose] [--trace] [--profile]
       [source] [dest]
```

#### Positional Arguments

```
source              path to the Coconut file/folder to compile
dest                destination directory for compiled files (defaults to
                    the source directory)
```

#### Optional Arguments

```
optional arguments:
  -h, --help            show this help message and exit
  --and source dest     additional source/dest pairs to compile
  -v, -V, --version     print Coconut and Python version information
  -t version, --target version
                        specify target Python version (defaults to universal)
  -i, --interact        force the interpreter to start (otherwise starts if no other command is
                        given) (implies --run)
  -p, --package         compile source as part of a package (defaults to only if source is a
                        directory)
  -a, --standalone, --stand-alone
                        compile source as standalone files (defaults to only if source is a single
                        file)
                        add line number comments for ease of debugging
  -k, --keep-lines, --keeplines
                        include source code in comments for ease of debugging
  -w, --watch           watch a directory and recompile on changes
  -r, --run             execute compiled Python
  -n, --no-write, --nowrite
                        disable writing compiled Python
  -d, --display         print compiled Python
  -q, --quiet           suppress all informational output (combine with --display to write runnable
                        code to stdout)
  -s, --strict          enforce code cleanliness standards
  --no-tco, --notco     disable tail call optimization
  --no-wrap, --nowrap   disable wrapping type annotations in strings and turn off 'from __future__
                        import annotations' behavior
  -c code, --code code  run Coconut passed in as a string (can also be piped into stdin)
  -j processes, --jobs processes
                        number of additional processes to use (defaults to 0) (pass 'sys' to use
                        machine default)
  -f, --force           force re-compilation even when source code and compilation parameters
                        haven't changed
  --minify              reduce size of compiled Python
  --jupyter ..., --ipython ...
                        run Jupyter/IPython with Coconut as the kernel (remaining args passed to
                        Jupyter)
  --mypy ...            run MyPy on compiled Python (remaining args passed to MyPy) (implies
                        --package)
  --argv ..., --args ...
                        set sys.argv to source plus remaining args for use in the Coconut script
                        being run
  --tutorial            open Coconut's tutorial in the default web browser
  --docs, --documentation
                        open Coconut's documentation in the default web browser
  --style name          set Pygments syntax highlighting style (or 'list' to list styles) (defaults
                        to COCONUT_STYLE environment variable if it exists, otherwise 'default')
  --history-file path   set history file (or '' for no file) (defaults to
                        '~/.coconut_history') (can be modified by setting
                        COCONUT_HOME environment variable)
  --vi-mode, --vimode   enable vi mode in the interpreter (defaults to False) (can be modified
                        by setting COCONUT_VI_MODE environment variable)
  --recursion-limit limit, --recursionlimit limit
                        set maximum recursion depth in compiler (defaults to 2000)
  --site-install, --siteinstall
                        set up coconut.convenience to be imported on Python start
  --site-uninstall, --siteuninstall
                        revert the effects of --site-install
  --verbose             print verbose debug output
  --trace               print verbose parsing data (only available in coconut-develop)
  --profile             collect and print timing info (only available in coconut-develop)
```

### Coconut Scripts

To run a Coconut file as a script, Coconut provides the command
```
coconut-run <source> <args>
```
as an alias for
```
coconut --run --quiet --target sys <source> --argv <args>
```
which will quietly compile and run `<source>`, passing any additional arguments to the script, mimicking how the `python` command works.

`coconut-run` can be used in a Unix shebang line to create a Coconut script by adding the following line to the start of your script:
```bash
#!/usr/bin/env coconut-run
```

### Naming Source Files

Coconut source files should, so the compiler can recognize them, use the extension `.coco` (preferred), `.coc`, or `.coconut`. When Coconut compiles a `.coco` (or `.coc`/`.coconut`) file, it will compile to another file with the same name, except with `.py` instead of `.coco`, which will hold the compiled code. If an extension other than `.py` is desired for the compiled files, such as `.pyde` for [Python Processing](http://py.processing.org/), then that extension can be put before `.coco` in the source file name, and it will be used instead of `.py` for the compiled files. For example, `name.coco` will compile to `name.py`, whereas `name.pyde.coco` will compile to `name.pyde`.

### Compilation Modes

Files compiled by the `coconut` command-line utility will vary based on compilation parameters. If an entire directory of files is compiled (which the compiler will search recursively for any folders containing `.coco`, `.coc`, or `.coconut` files), a `__coconut__.py` file will be created to house necessary functions (package mode), whereas if only a single file is compiled, that information will be stored within a header inside the file (standalone mode). Standalone mode is better for single files because it gets rid of the overhead involved in importing `__coconut__.py`, but package mode is better for large packages because it gets rid of the need to run the same Coconut header code again in every file, since it can just be imported from `__coconut__.py`.

By default, if the `source` argument to the command-line utility is a file, it will perform standalone compilation on it, whereas if it is a directory, it will recursively search for all `.coco` (or `.coc` / `.coconut`) files and perform package compilation on them. Thus, in most cases, the mode chosen by Coconut automatically will be the right one. But if it is very important that no additional files like `__coconut__.py` be created, for example, then the command-line utility can also be forced to use a specific mode with the `--package` (`-p`) and `--standalone` (`-a`) flags.

### Compatible Python Versions

While Coconut syntax is based off of Python 3, Coconut code compiled in universal mode (the default `--target`), and the Coconut compiler, should run on any Python version `>= 2.6` on the `2.x` branch or `>= 3.2` on the `3.x` branch on either [CPython](https://www.python.org/) or [PyPy](http://pypy.org/).

To make Coconut built-ins universal across Python versions, Coconut makes available on any Python version built-ins that only exist in later versions, including **automatically overwriting Python 2 built-ins with their Python 3 counterparts.** Additionally, Coconut also overwrites some Python 3 built-ins for optimization and enhancement purposes. If access to the original Python versions of any overwritten built-ins is desired, the old built-ins can be retrieved by prefixing them with `py_`. Specifically, the overwritten built-ins are:

- `py_chr`,
- `py_hex`,
- `py_input`,
- `py_int`,
- `py_map`,
- `py_object`,
- `py_oct`,
- `py_open`,
- `py_print`,
- `py_range`,
- `py_str`,
- `py_zip`,
- `py_filter`,
- `py_reversed`,
- `py_enumerate`,
- `py_raw_input`,
- `py_xrange`,
- `py_repr`, and
- `py_breakpoint`.

_Note: Coconut's `repr` can be somewhat tricky, as it will attempt to remove the `u` before reprs of unicode strings, but will not always be able to do so if the unicode string is nested._

For standard library compatibility, **Coconut automatically maps imports under Python 3 names to imports under Python 2 names**. Thus, Coconut will automatically take care of any standard library modules that were renamed from Python 2 to Python 3 if just the Python 3 name is used. For modules or objects that only exist in Python 3, however, Coconut has no way of maintaining compatibility.

Additionally, Coconut allows the [`__set_name__`](https://docs.python.org/3/reference/datamodel.html#object.__set_name__) magic method for descriptors to work on any Python version.

Finally, while Coconut will try to compile Python-3-specific syntax to its universal equivalent, the following constructs have no equivalent in Python 2, and require the specification of a target of at least `3` to be used:

- the `nonlocal` keyword,
- `exec` used in a context where it must be a function,
- keyword-only function parameters (use pattern-matching function definition instead),
- `@` as matrix multiplication (requires `--target 3.5`),
- `async` and `await` statements (requires `--target 3.5`),
- `:=` assignment expressions (requires `--target 3.8`),
- positional-only function parameters (use pattern-matching function definition instead) (requires `--target 3.8`), and
- `except*` multi-except statement (requires `--target 3.11`).

### Allowable Targets

If the version of Python that the compiled code will be running on is known ahead of time, a target should be specified with `--target`. The given target will only affect the compiled code and whether or not the Python-3-specific syntax detailed above is allowed. Where Python 3 and Python 2 syntax standards differ, Coconut syntax will always follow Python 3 across all targets. The supported targets are:

- `universal` (default) (will work on _any_ of the below),
- `2`, `2.6` (will work on any Python `>= 2.6` but `< 3`),
- `2.7` (will work on any Python `>= 2.7` but `< 3`),
- `3`, `3.2` (will work on any Python `>= 3.2`),
- `3.3` (will work on any Python `>= 3.3`),
- `3.4` (will work on any Python `>= 3.4`),
- `3.5` (will work on any Python `>= 3.5`),
- `3.6` (will work on any Python `>= 3.6`),
- `3.7` (will work on any Python `>= 3.7`),
- `3.8` (will work on any Python `>= 3.8`),
- `3.9` (will work on any Python `>= 3.9`),
- `3.10` (will work on any Python `>= 3.10`),
- `3.11` (will work on any Python `>= 3.11`), and
- `sys` (chooses the target corresponding to the current Python version).

_Note: Periods are ignored in target specifications, such that the target `27` is equivalent to the target `2.7`._

### `strict` Mode

If the `--strict` (`-s` for short) flag is enabled, Coconut will perform additional checks on the code being compiled. It is recommended that you use the `--strict` flag if you are starting a new Coconut project, as it will help you write cleaner code. Specifically, the extra checks done by `--strict` are

- disabling deprecated features (making them entirely unavailable to code compiled with `--strict`),
- warning about unused imports,
- warning on missing `__init__.coco` files when compiling in `--package` mode,
- throwing errors on various style problems (see list below).

The style issues which will cause `--strict` to throw an error are:

- mixing of tabs and spaces (without `--strict` will show a warning),
- use of `from __future__` imports (Coconut does these automatically) (without `--strict` will show a warning)
- missing new line at end of file,
- trailing whitespace at end of lines,
- semicolons at end of lines,
- use of the Python-style `lambda` statement (use [Coconut's lambda syntax](#lambdas) instead),
- [Python 3.10/PEP-634-style `match ...: case ...:` syntax](#pep-634-support) (use [Coconut's `case ...: match ...:` syntax](#case) instead),
- Python-3.10/PEP-634-style dotted names in pattern-matching (Coconut style is to preface these with an `=`),
- inheriting from `object` in classes (Coconut does this automatically),
- use of `u` to denote Unicode strings (all Coconut strings are Unicode strings), and
- use of backslash continuation (use [parenthetical continuation](#enhanced-parenthetical-continuation) instead).

## Integrations

### Syntax Highlighting

Text editors with support for Coconut syntax highlighting are:

- **VSCode**: Install [Coconut (Official)](https://marketplace.visualstudio.com/items?itemName=evhub.coconut) (for **VSCodium**, install from Open VSX [here](https://open-vsx.org/extension/evhub/coconut) instead).
- **SublimeText**: See SublimeText section below.
- **Spyder** (or any other editor that supports **Pygments**): See Pygments section below.
- **Vim**: See [`coconut.vim`](https://github.com/manicmaniac/coconut.vim).
- **Emacs**: See [`coconut-mode`](https://github.com/NickSeagull/coconut-mode).
- **Atom**: See [`language-coconut`](https://github.com/enilsen16/language-coconut).
- **IntelliJ IDEA**: See [registering file types](https://www.jetbrains.com/help/idea/creating-and-registering-file-types.html).

Alternatively, if none of the above work for you, you can just treat Coconut as Python. Simply set up your editor so it interprets all `.coco` files as Python and that should highlight most of your code well enough.

#### SublimeText

Coconut syntax highlighting for SublimeText requires that [Package Control](https://packagecontrol.io/installation), the standard package manager for SublimeText, be installed. Once that is done, simply:

1. open the SublimeText command palette by pressing `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac),
2. type and enter `Package Control: Install Package`, and
3. finally type and enter `Coconut`.

To make sure everything is working properly, open a `.coco` file, and make sure `Coconut` appears in the bottom right-hand corner. If something else appears, like `Plain Text`, click on it, select `Open all with current extension as...` at the top of the resulting menu, and then select `Coconut`.

_Note: Coconut syntax highlighting for SublimeText is provided by the [sublime-coconut](https://github.com/evhub/sublime-coconut) package._

#### Pygments

The same `pip install coconut` command that installs the Coconut command-line utility will also install the `coconut` Pygments lexer. How to use this lexer depends on the Pygments-enabled application being used, but in general simply use the `.coco` file extension (should be all you need to do for Spyder) and/or enter `coconut` as the language being highlighted and Pygments should be able to figure it out.

For example, this documentation is generated with [Sphinx](http://www.sphinx-doc.org/en/stable/), with the syntax highlighting you see created by adding the line
```coconut_python
highlight_language = "coconut"
```
to Coconut's `conf.py`.

### IPython/Jupyter Support

If you prefer [IPython](http://ipython.org/) (the python kernel for the [Jupyter](http://jupyter.org/) framework) to the normal Python shell, Coconut can be used as a Jupyter kernel or IPython extension.

#### Kernel

If Coconut is used as a kernel, all code in the console or notebook will be sent directly to Coconut instead of Python to be evaluated. Otherwise, the Coconut kernel behaves exactly like the IPython kernel, including support for `%magic` commands.

Simply installing Coconut should add a `Coconut` kernel to your Jupyter/IPython notebooks. If you are having issues accessing the Coconut kernel, however, the command `coconut --jupyter` will re-install the `Coconut` kernel to ensure it is using the current Python as well as add the additional kernels `Coconut (Default Python)`, `Coconut (Default Python 2)`, and `Coconut (Default Python 3)` which will use, respectively, the Python accessible as `python`, `python2`, and `python3` (these kernels are accessible in the console as `coconut_py`, `coconut_py2`, and `coconut_py3`). Furthermore, the Coconut kernel fully supports [`nb_conda_kernels`](https://github.com/Anaconda-Platform/nb_conda_kernels) to enable accessing the Coconut kernel in one Conda environment from another Conda environment.

Coconut also provides the following convenience commands:

- `coconut --jupyter notebook` will ensure that the Coconut kernel is available and launch a Jupyter/IPython notebook.
- `coconut --jupyter console` will launch a Jupyter/IPython console using the Coconut kernel.
- `coconut --jupyter lab` will ensure that the Coconut kernel is available and launch [JupyterLab](https://github.com/jupyterlab/jupyterlab).

Additionally, [Jupytext](https://github.com/mwouts/jupytext) contains special support for the Coconut kernel.

#### Extension

If Coconut is used as an extension, a special magic command will send snippets of code to be evaluated using Coconut instead of IPython, but IPython will still be used as the default.

The line magic `%load_ext coconut` will load Coconut as an extension, providing the `%coconut` and `%%coconut` magics and adding Coconut built-ins. The `%coconut` line magic will run a line of Coconut with default parameters, and the `%%coconut` block magic will take command-line arguments on the first line, and run any Coconut code provided in the rest of the cell with those parameters.

### MyPy Integration

Coconut has the ability to integrate with [MyPy](http://mypy-lang.org/) to provide optional static type-checking, including for all Coconut built-ins. Simply pass `--mypy` to `coconut` to enable MyPy integration, though be careful to pass it only as the last argument, since all arguments after `--mypy` are passed to `mypy`, not Coconut.

You can also call `mypy` directly on the compiled Coconut if you run `coconut --mypy` at least once and then add `~/.coconut_stubs` to your [`MYPYPATH`](https://mypy.readthedocs.io/en/latest/running_mypy.html#how-imports-are-found). To install the stubs without launching the interpreter, you can also run `coconut --mypy install` instead of `coconut --mypy`.

To explicitly annotate your code with types for MyPy to check, Coconut supports [Python 3 function type annotations](https://www.python.org/dev/peps/pep-0484/), [Python 3.6 variable type annotations](https://www.python.org/dev/peps/pep-0526/), and even Coconut's own [enhanced type annotation syntax](#enhanced-type-annotation). By default, all type annotations are compiled to Python-2-compatible type comments, which means it all works on any Python version.

Coconut even supports `--mypy` in the interpreter, which will intelligently scan each new line of code, in the context of previous lines, for newly-introduced MyPy errors. For example:
```coconut
>>> a: str = count()[0]
<string>:14: error: Incompatible types in assignment (expression has type "int", variable has type "str")
>>> reveal_type(a)
0
<string>:19: note: Revealed type is 'builtins.unicode'
```
_For more information on `reveal_type`, see [`reveal_type` and `reveal_locals`](#reveal-type-and-reveal-locals)._

Sometimes, MyPy will not know how to handle certain Coconut constructs, such as `addpattern`. For the `addpattern` case, it is recommended to pass `--allow-redefinition` to MyPy (i.e. run `coconut <args> --mypy --allow-redefinition`), though in some cases `--allow-redefinition` may not be sufficient. In that case, either hide the offending code using [`TYPE_CHECKING`](#type-checking) or put a `# type: ignore` comment on the Coconut line which is generating the line MyPy is complaining about (you can figure out what line this is using `--line-numbers`) and the comment will be added to every generated line.

## Operators

In order of precedence, highest first, the operators supported in Coconut are:
```
===================== ==========================
Symbol(s)             Associativity
===================== ==========================
..                    n/a
f x                   n/a
await x               n/a
**                    right
+, -, ~               unary
*, /, //, %, @        left
+, -                  left
<<, >>                left
&                     left
^                     left
|                     left
::                    n/a (lazy)
a `b` c               left (captures lambda)
??                    left (short-circuits)
..>, <.., ..*>, <*.., n/a (captures lambda)
  ..**>, <**..
|>, <|, |*>, <*|,     left (captures lambda)
  |**>, <**|
==, !=, <, >,
  <=, >=,
  in, not in,
  is, is not          n/a
not                   unary
and                   left (short-circuits)
or                    left (short-circuits)
x if c else y,        ternary left (short-circuits)
  if c then x else y
->                    right
===================== ==========================
```

Note that because addition has a greater precedence than piping, expressions of the form `x |> y + z` are equivalent to `x |> (y + z)`.

### Lambdas

Coconut provides the simple, clean `->` operator as an alternative to Python's `lambda` statements. The syntax for the `->` operator is `(parameters) -> expression` (or `parameter -> expression` for one-argument lambdas). The operator has the same precedence as the old statement, which means it will often be necessary to surround the lambda in parentheses, and is right-associative.

Additionally, Coconut also supports an implicit usage of the `->` operator of the form `(-> expression)`, which is equivalent to `((_=None) -> expression)`, which allows an implicit lambda to be used both when no arguments are required, and when one argument (assigned to `_`) is required.

_Note: If normal lambda syntax is insufficient, Coconut also supports an extended lambda syntax in the form of [statement lambdas](#statement-lambdas). Statement lambdas support full statements rather than just expressions and allow type annotations for their parameters._

##### Rationale

In Python, lambdas are ugly and bulky, requiring the entire word `lambda` to be written out every time one is constructed. This is fine if in-line functions are very rarely needed, but in functional programming in-line functions are an essential tool.

##### Python Docs

Lambda forms (lambda expressions) have the same syntactic position as expressions. They are a shorthand to create anonymous functions; the expression `(arguments) -> expression` yields a function object. The unnamed object behaves like a function object defined with:
```coconut
def <lambda>(arguments):
    return expression
```
Note that functions created with lambda forms cannot contain statements or annotations.

##### Example

**Coconut:**
```coconut
dubsums = map((x, y) -> 2*(x+y), range(0, 10), range(10, 20))
dubsums |> list |> print
```

**Python:**
```coconut_python
dubsums = map(lambda x, y: 2*(x+y), range(0, 10), range(10, 20))
print(list(dubsums))
```

#### Implicit Lambdas

Coconut also supports implicit lambdas, which allow a lambda to take either no arguments or a single argument. Implicit lambdas are formed with the usual Coconut lambda operator `->`, in the form `(-> expression)`. This is equivalent to `((_=None) -> expression)`. When an argument is passed to an implicit lambda, it will be assigned to `_`, replacing the default value `None`.

Below are two examples of implicit lambdas. The first uses the implicit argument `_`, while the second does not.

**Single Argument Example:**
```coconut
square = (-> _**2)
```

**No-Argument Example:**
```coconut
import random

get_random_number = (-> random.random())
```

_Note: Nesting implicit lambdas can lead to problems with the scope of the `_` parameter to each lambda. It is recommended that nesting implicit lambdas be avoided._

### Partial Application

Coconut uses a `$` sign right after a function's name but before the open parenthesis used to call the function to denote partial application.

Coconut's partial application also supports the use of a `?` to skip partially applying an argument, deferring filling in that argument until the partially-applied function is called. This is useful if you want to partially apply arguments that aren't first in the argument order.

##### Rationale

Partial application, or currying, is a mainstay of functional programming, and for good reason: it allows the dynamic customization of functions to fit the needs of where they are being used. Partial application allows a new function to be created out of an old function with some of its arguments pre-specified.

##### Python Docs

Return a new `partial` object which when called will behave like _func_ called with the positional arguments _args_ and keyword arguments _keywords_. If more arguments are supplied to the call, they are appended to _args_. If additional keyword arguments are supplied, they extend and override _keywords_. Roughly equivalent to:
```coconut_python
def partial(func, *args, **keywords):
    def newfunc(*fargs, **fkeywords):
        newkeywords = keywords.copy()
        newkeywords.update(fkeywords)
        return func(*(args + fargs), **newkeywords)
    newfunc.func = func
    newfunc.args = args
    newfunc.keywords = keywords
    return newfunc
```
The `partial` object is used for partial function application which “freezes” some portion of a function's arguments and/or keywords resulting in a new object with a simplified signature.

##### Example

**Coconut:**
```coconut
expnums = range(5) |> map$(pow$(?, 2))
expnums |> list |> print
```

**Python:**
```coconut_python
# unlike this simple lambda, $ produces a pickleable object
expnums = map(lambda x: pow(x, 2), range(5))
print(list(expnums))
```

### Pipeline

Coconut uses pipe operators for pipeline-style function application. All the operators have a precedence in-between function composition pipes and comparisons, and are left-associative. All operators also support in-place versions. The different operators are:
```coconut
(|>)    => pipe forward
(|*>)   => multiple-argument pipe forward
(|**>)  => keyword argument pipe forward
(<|)    => pipe backward
(<*|)   => multiple-argument pipe backward
(<**|)  => keyword argument pipe backward
(|?>)   => None-aware pipe forward
(|?*>)  => None-aware multi-arg pipe forward
(|?**>) => None-aware keyword arg pipe forward
```

Additionally, all pipe operators support a lambda as the last argument, despite lambdas having a lower precedence. Thus, `a |> x -> b |> c` is equivalent to `a |> (x -> b |> c)`, not `a |> (x -> b) |> c`. Note also that the None-aware pipe operators here are equivalent to a [monadic bind](https://en.wikipedia.org/wiki/Monad_(functional_programming)) treating the object as a `Maybe` monad composed of either `None` or the given object.

_Note: To visually spread operations across several lines, just use [parenthetical continuation](#enhanced-parenthetical-continuation)._

##### Optimizations

It is common in Coconut to write code that uses pipes to pass an object through a series of [partials](#partial-application) and/or [implicit partials](#implicit-partial-application), as in
```coconut
obj |> .attribute |> .method(args) |> func$(args) |> .[index]
```
which is often much more readable, as it allows the operations to be written in the order in which they are performed, instead of as in
```coconut_python
func(args, obj.attribute.method(args))[index]
```
where `func` has to go at the beginning.

If Coconut compiled each of the partials in the pipe syntax as an actual partial application object, it would make the Coconut-style syntax significantly slower than the Python-style syntax. Thus, Coconut does not do that. If any of the above styles of partials or implicit partials are used in pipes, they will whenever possible be compiled to the Python-style syntax, producing no intermediate partial application objects.

This applies even to in-place pipes such as `|>=`.

##### Example

**Coconut:**
```coconut
def sq(x) = x**2
(1, 2) |*> (+) |> sq |> print
```

**Python:**
```coconut_python
import operator
def sq(x): return x**2
print(sq(operator.add(1, 2)))
```

### Compose

Coconut has three basic function composition operators: `..`, `..>`, and `<..`. Both `..` and `<..` use math-style "backwards" function composition, where the first function is called last, while `..>` uses "forwards" function composition, where the first function is called first. Forwards and backwards function composition pipes cannot be used together in the same expression (unlike normal pipes) and have precedence in-between `None`-coalescing and normal pipes. The `..>` and `<..` function composition pipe operators also have `..*>` and `<*..` forms which are, respectively, the equivalents of `|*>` and `<*|` as well as `..**>` and `<**..` forms which correspond to `|**>` and `<**|`.

The `..` operator has lower precedence than attribute access, slices, function calls, etc., but higher precedence than all other operations while the `..>` pipe operators have a precedence directly higher than normal pipes.

The in-place function composition operators are `..=`, `..>=`, `<..=`, `..*>=`, `<*..=`, `..**>`, and `..**>`.

##### Example

**Coconut:**
```coconut
fog = f..g
f_into_g = f ..> g
```

**Python:**
```coconut_python
# unlike these simple lambdas, Coconut produces pickleable objects
fog = lambda *args, **kwargs: f(g(*args, **kwargs))
f_into_g = lambda *args, **kwargs: g(f(*args, **kwargs))
```

### Chain

Coconut uses the `::` operator for iterator chaining. Coconut's iterator chaining is done lazily, in that the arguments are not evaluated until they are needed. It has a precedence in-between bitwise or and infix calls. The in-place operator is `::=`.

##### Rationale

A useful tool to make working with iterators as easy as working with sequences is the ability to lazily combine multiple iterators together. This operation is called chain, and is equivalent to addition with sequences, except that nothing gets evaluated until it is needed.

##### Python Docs

Make an iterator that returns elements from the first iterable until it is exhausted, then proceeds to the next iterable, until all of the iterables are exhausted. Used for treating consecutive sequences as a single sequence. Chained inputs are evaluated lazily. Roughly equivalent to:
```coconut_python
def chain(*iterables):
    # chain('ABC', 'DEF') --> A B C D E F
    for it in iterables:
        for element in it:
            yield element
```

##### Example

**Coconut:**
```coconut
def N(n=0) = (n,) :: N(n+1)  # no infinite loop because :: is lazy

(range(-10, 0) :: N())$[5:15] |> list |> print
```

**Python:**
_Can't be done without a complicated iterator comprehension in place of the lazy chaining. See the compiled code for the Python syntax._

### Iterator Slicing

Coconut uses a `$` sign right after an iterator before a slice to perform iterator slicing. Coconut's iterator slicing works much the same as Python's sequence slicing, and looks much the same as Coconut's partial application, but with brackets instead of parentheses.

Iterator slicing works just like sequence slicing, including support for negative indices and slices, and support for `slice` objects in the same way as can be done with normal slicing. Iterator slicing makes no guarantee, however, that the original iterator passed to it be preserved (to preserve the iterator, use Coconut's [`tee`](#tee) or [`reiterable`](#reiterable) built-ins).

Coconut's iterator slicing is very similar to Python's `itertools.islice`, but unlike `itertools.islice`, Coconut's iterator slicing supports negative indices, and will preferentially call an object's `__iter_getitem__` (Coconut-specific magic method, preferred) or `__getitem__` (general Python magic method), if they exist. Coconut's iterator slicing is also optimized to work well with all of Coconut's built-in objects, only computing the elements of each that are actually necessary to extract the desired slice.

##### Example

**Coconut:**
```coconut
map(x -> x*2, range(10**100))$[-1] |> print
```

**Python:**
_Can't be done without a complicated iterator slicing function and inspection of custom objects. The necessary definitions in Python can be found in the Coconut header._

### None Coalescing

Coconut provides `??` as a `None`-coalescing operator, similar to the `??` null-coalescing operator in C# and Swift. Additionally, Coconut implements all of the `None`-aware operators proposed in [PEP 505](https://www.python.org/dev/peps/pep-0505/).

Coconut's `??` operator evaluates to its left operand if that operand is not `None`, otherwise its right operand. The expression `foo ?? bar` evaluates to `foo` as long as it isn't `None`, and to `bar` if it is. The `None`-coalescing operator is short-circuiting, such that if the left operand is not `None`, the right operand won't be evaluated. This allows the right operand to be a potentially expensive operation without incurring any unnecessary cost.

The `None`-coalescing operator has a precedence in-between infix function calls and composition pipes, and is left-associative.

##### Example

**Coconut:**
```coconut
could_be_none() ?? calculate_default_value()
```

**Python:**
```coconut_python
(lambda result: result if result is not None else calculate_default_value())(could_be_none())
```

#### Coalescing Assignment Operator

The in-place assignment operator is `??=`, which allows conditionally setting a variable if it is currently `None`.

```coconut
foo = 1
bar = None
foo ??= 10  # foo is still 1
bar ??= 10  # bar is now 10
```

As described with the standard `??` operator, the `None`-coalescing assignment operator will not evaluate the right hand side unless the left hand side is `None`.

```coconut
baz = 0
baz ??= expensive_task()  # right hand side isn't evaluated
```

#### Other None-Aware Operators

Coconut also allows a single `?` before attribute access, function calling, partial application, and (iterator) indexing to short-circuit the rest of the evaluation if everything so far evaluates to `None`. This is sometimes known as a "safe navigation" operator.

When using a `None`-aware operator for member access, either for a method or an attribute, the syntax is `obj?.method()` or `obj?.attr` respectively. `obj?.attr` is equivalent to `obj.attr if obj is not None else obj`. This does not prevent an `AttributeError` if `attr` is not an attribute or method of `obj`.

The `None`-aware indexing operator is used identically to normal indexing, using `?[]` instead of `[]`. `seq?[index]` is equivalent to the expression `seq[index] is seq is not None else seq`. Using this operator will not prevent an `IndexError` if `index` is outside the bounds of `seq`.

Coconut also supports None-aware [pipe operators](#pipeline).

##### Example

**Coconut:**
```coconut
could_be_none?.attr     # attribute access
could_be_none?(arg)     # function calling
could_be_none?.method() # method calling
could_be_none?$(arg)    # partial application
could_be_none()?[0]     # indexing
could_be_none()?.attr[index].method()
```

**Python:**
```coconut_python
import functools
(lambda result: None if result is None else result.attr)(could_be_none())
(lambda result: None if result is None else result(arg))(could_be_none())
(lambda result: None if result is None else result.method())(could_be_none())
(lambda result: None if result is None else functools.partial(result, arg))(could_be_none())
(lambda result: None if result is None else result[0])(could_be_none())
(lambda result: None if result is None else result.attr[index].method())(could_be_none())
```

### Expanded Indexing for Iterables

Beyond indexing standard Python sequences, Coconut supports indexing into a number of iterables, including `range` and `map`, which do not support random access in all Python versions but do in Coconut. In Coconut, indexing into an iterable of this type uses the same syntax as indexing into a sequence in vanilla Python.

##### Example

**Coconut:**
```coconut
range(0, 12, 2)[4]  # 8

map((i->i*2), range(10))[2]  # 4
```

**Python:**
Can’t be done quickly without Coconut’s iterable indexing, which requires many complicated pieces. The necessary definitions in Python can be found in the Coconut header.

##### Indexing into `filter`

Coconut cannot index into `filter` directly, as there is no efficient way to do so.

```coconut
range(10) |> filter$(i->i>3) |> .[0]  # doesn't work
```

In order to make this work, you can explicitly use iterator slicing, which is less efficient in the general case:

```coconut
range(10) |> filter$(i->i>3) |> .$[0]  # works
```

For more information on Coconut's iterator slicing, see [here](#iterator-slicing).

### Unicode Alternatives

Coconut supports Unicode alternatives to many different operator symbols. The Unicode alternatives are relatively straightforward, and chosen to reflect the look and/or meaning of the original symbol.

##### Full List

```
→ (\u2192)                  => "->"
↦ (\u21a6)                  => "|>"
↤ (\u21a4)                  => "<|"
*↦ (*\u21a6)                => "|*>"
↤* (\u21a4*)                => "<*|"
**↦ (**\u21a6)              => "|**>"
↤** (\u21a4**)              => "<**|"
× (\xd7)                    => "*"
↑ (\u2191)                  => "**"
÷ (\xf7)                    => "/"
÷/ (\xf7/)                  => "//"
∘ (\u2218)                  => ".."
∘> (\u2218>)                => "..>"
<∘ (<\u2218)                => "<.."
∘*> (\u2218*>)              => "..*>"
<*∘ (<*\u2218)              => "<*.."
∘**> (\u2218**>)            => "..**>"
<**∘ (<**\u2218)            => "<**.."
− (\u2212)                  => "-" (only subtraction)
⁻ (\u207b)                  => "-" (only negation)
¬ (\xac)                    => "~"
≠ (\u2260) or ¬= (\xac=)    => "!="
≤ (\u2264)                  => "<="
≥ (\u2265)                  => ">="
∧ (\u2227) or ∩ (\u2229)    => "&"
∨ (\u2228) or ∪ (\u222a)    => "|"
⊻ (\u22bb) or ⊕ (\u2295)    => "^"
« (\xab)                    => "<<"
» (\xbb)                    => ">>"
… (\u2026)                  => "..."
⋅ (\u22c5)                  => "@" (only matrix multiplication)
λ (\u03bb)                  => "lambda"
```

## Keywords

### `data`

Coconut's `data` keyword is used to create immutable, algebraic data types with built-in support for destructuring [pattern-matching](#match), [`fmap`](#fmap), and typed equality.

The syntax for `data` blocks is a cross between the syntax for functions and the syntax for classes. The first line looks like a function definition, but the rest of the body looks like a class, usually containing method definitions. This is because while `data` blocks actually end up as classes in Python, Coconut automatically creates a special, immutable constructor based on the given arguments.

Coconut data statement syntax looks like:
```coconut
data <name>(<args>) [from <inherits>]:
    <body>
```
`<name>` is the name of the new data type, `<args>` are the arguments to its constructor as well as the names of its attributes, `<body>` contains the data type's methods, and `<inherits>` optionally contains any desired base classes.

Coconut allows data fields in `<args>` to have defaults and/or [type annotations](#enhanced-type-annotation) attached to them, and supports a starred parameter at the end to collect extra arguments.

Writing constructors for `data` types must be done using the `__new__` method instead of the `__init__` method. For helping to easily write `__new__` methods, Coconut provides the [makedata](#makedata) built-in.

Subclassing `data` types can be done easily by inheriting from them either in another `data` statement or a normal Python `class`. If a normal `class` statement is used, making the new subclass immutable will require adding the line
```coconut
__slots__ = ()
```
which will need to be put in the subclass body before any method or attribute definitions. If you need to inherit magic methods from a base class in your `data` type, such subclassing is the recommended method, as the `data ... from ...` syntax will overwrite any magic methods in the base class with magic methods built for the new `data` type.

##### Rationale

A mainstay of functional programming that Coconut improves in Python is the use of values, or immutable data types. Immutable data can be very useful because it guarantees that once you have some data it won't change, but in Python creating custom immutable data types is difficult. Coconut makes it very easy by providing `data` blocks.

##### Examples

**Coconut:**
```coconut
data vector2(x:int=0, y:int=0):
    def __abs__(self):
        return (self.x**2 + self.y**2)**.5

v = vector2(3, 4)
v |> print  # all data types come with a built-in __repr__
v |> abs |> print
v.x = 2  # this will fail because data objects are immutable
vector2() |> print
```
_Showcases the syntax, features, and immutable nature of `data` types, as well as the use of default arguments and type annotations._
```coconut
data Empty()
data Leaf(n)
data Node(l, r)

def size(Empty()) = 0

@addpattern(size)
def size(Leaf(n)) = 1

@addpattern(size)
def size(Node(l, r)) = size(l) + size(r)

size(Node(Empty(), Leaf(10))) == 1
```
_Showcases the algebraic nature of `data` types when combined with pattern-matching._
```coconut
data vector(*pts):
    """Immutable arbitrary-length vector."""

    def __abs__(self) =
        self.pts |> map$(pow$(?, 2)) |> sum |> pow$(?, 0.5)

    def __add__(self, other) =
        vector(*other_pts) = other
        assert len(other_pts) == len(self.pts)
        map((+), self.pts, other_pts) |*> vector

    def __neg__(self) =
        self.pts |> map$((-)) |*> vector

    def __sub__(self, other) =
        self + -other
```
_Showcases starred `data` declaration._

**Python:**
_Can't be done without a series of method definitions for each data type. See the compiled code for the Python syntax._

### `match`

Coconut provides fully-featured, functional pattern-matching through its `match` statements.

##### Overview

Match statements follow the basic syntax `match <pattern> in <value>`. The match statement will attempt to match the value against the pattern, and if successful, bind any variables in the pattern to whatever is in the same position in the value, and execute the code below the match statement. Match statements also support, in their basic syntax, an `if <cond>` that will check the condition after executing the match before executing the code below, and an `else` statement afterwards that will only be executed if the `match` statement is not. What is allowed in the match statement's pattern has no equivalent in Python, and thus the specifications below are provided to explain it.

##### Syntax Specification

Coconut match statement syntax is
```coconut
match <pattern> [not] in <value> [if <cond>]:
    <body>
[else:
    <body>]
```
where `<value>` is the item to match against, `<cond>` is an optional additional check, and `<body>` is simply code that is executed if the header above it succeeds. `<pattern>` follows its own, special syntax, defined roughly like so:

```coconut
pattern ::= and_pattern ("or" and_pattern)*  # match any

and_pattern ::= as_pattern ("and" as_pattern)*  # match all

as_pattern ::= infix_pattern ("as" name)*  # explicit binding

infix_pattern ::= bar_or_pattern ("`" EXPR "`" EXPR)*  # infix check

bar_or_pattern ::= pattern ("|" pattern)*  # match any

base_pattern ::= (
    "(" pattern ")"                 # parentheses
    | "None" | "True" | "False"     # constants
    | ["as"] NAME                   # variable binding
    | "=" EXPR                      # check
    | DOTTED_NAME                   # implicit check (disabled in destructuring assignment)
    | NUMBER                        # numbers
    | STRING                        # strings
    | NAME "(" patterns ")"         # data types (or classes if using PEP 634 syntax)
    | "data" NAME "(" patterns ")"  # data types
    | "class" NAME "(" patterns ")" # classes
    | pattern "is" exprs            # isinstance check
    | "{" pattern_pairs             # dictionaries
        ["," "**" (NAME | "{}")] "}"
    | ["s"] "{" pattern_consts "}"  # sets
    | (EXPR) -> pattern             # view patterns
    | "(" patterns ")"              # sequences can be in tuple form
    | "[" patterns "]"              #  or in list form
    | "(|" patterns "|)"            # lazy lists
    | ("(" | "[")                   # star splits
        patterns
        "*" middle
        patterns
      (")" | "]")
    | (                             # head-tail splits
        "(" patterns ")"
        | "[" patterns "]"
      ) "+" pattern
    | pattern "+" (                 # init-last splits
        "(" patterns ")"
        | "[" patterns "]"
      )
    | (                             # head-last splits
        "(" patterns ")"
        | "[" patterns "]"
      ) "+" pattern "+" (
        "(" patterns ")"                # this match must be the same
        | "[" patterns "]"              #  construct as the first match
      )
    | (                             # iterator splits
        "(" patterns ")"
        | "[" patterns "]"
        | "(|" patterns "|)"
      ) "::" pattern
    | ([STRING "+"] NAME            # complex string matching
        ["+" STRING])
)
```

##### Semantics Specification

`match` statements will take their pattern and attempt to "match" against it, performing the checks and deconstructions on the arguments as specified by the pattern. The different constructs that can be specified in a pattern, and their function, are:
- Constants, Numbers, and Strings: will only match to the same constant, number, or string in the same position in the arguments.
- Variable Bindings: will match to anything, and will be bound to whatever they match to, with some exceptions:
  * If the same variable is used multiple times, a check will be performed that each use matches to the same value.
  * If the variable name `_` is used, nothing will be bound and everything will always match to it (`_` is Coconut's "wildcard").
- Explicit Bindings (`<pattern> as <var>`): will bind `<var>` to `<pattern>`.
- Checks (`=<expr>`): will check that whatever is in that position is `==` to the expression `<expr>`.
- `isinstance` Checks (`<var> is <types>`): will check that whatever is in that position `isinstance` of `<types>` before binding the `<var>`.
- Infix Checks (`` <pattern> `<op>` <expr> ``): will check that the operator `<op>$(<expr>)` returns a truthy value when called on whatever is in that position, then matches `<pattern>`.
- Data Types (`<name>(<args>)`): will check that whatever is in that position is of data type `<name>` and will match the attributes to `<args>`. Includes support for positional arguments, named arguments, and starred arguments.
- Classes (`class <name>(<args>)`): does [PEP-634-style class matching](https://www.python.org/dev/peps/pep-0634/#class-patterns).
- Lists (`[<patterns>]`), Tuples (`(<patterns>)`): will only match a sequence (`collections.abc.Sequence`) of the same length, and will check the contents against `<patterns>`.
- Lazy lists (`(|<patterns>|)`): same as list or tuple matching, but checks for an Iterable (`collections.abc.Iterable`) instead of a Sequence.
- Fixed-Length Dicts (`{<pairs>}`): will only match a mapping (`collections.abc.Mapping`) of the same length, and will check the contents against `<pairs>`.
- Dicts With Rest (`{<pairs>, **<rest>}`): will match a mapping (`collections.abc.Mapping`) containing all the `<pairs>`, and will put a `dict` of everything else into `<rest>`.
- Sets (`{<constants>}`): will only match a set (`collections.abc.Set`) of the same length and contents.
- View Patterns (`(<expression>) -> <pattern>`): calls `<expression>` on the item being matched and matches the result to `<pattern>`. The match fails if a [`MatchError`](#matcherror) is raised. `<expression>` may be unparenthesized only when it is a single atom.
- Head-Tail Splits (`<list/tuple> + <var>`): will match the beginning of the sequence against the `<list/tuple>`, then bind the rest to `<var>`, and make it the type of the construct used.
- Init-Last Splits (`<var> + <list/tuple>`): exactly the same as head-tail splits, but on the end instead of the beginning of the sequence.
- Head-Last Splits (`<list/tuple> + <var> + <list/tuple>`): the combination of a head-tail and an init-last split.
- Iterator Splits (`<list/tuple/lazy list> :: <var>`): will match the beginning of an iterable (`collections.abc.Iterable`) against the `<list/tuple/lazy list>`, then bind the rest to `<var>` or check that the iterable is done.
- Complex String Matching (`<string> + <var> + <string>`): matches strings that start and end with the given substrings, binding the middle to `<var>`.

_Note: Like [iterator slicing](#iterator-slicing), iterator and lazy list matching make no guarantee that the original iterator matched against be preserved (to preserve the iterator, use Coconut's [`tee`](#tee) or [`reiterable`](#reiterable) built-ins)._

When checking whether or not an object can be matched against in a particular fashion, Coconut makes use of Python's abstract base classes. Therefore, to ensure proper matching for a custom object, it's recommended to register it with the proper abstract base classes.

##### Examples

**Coconut:**
```coconut
def factorial(value):
    match 0 in value:
        return 1
    else: match n is int in value if n > 0:  # Coconut allows nesting of statements on the same line
        return n * factorial(n-1)
    else:
        raise TypeError("invalid argument to factorial of: "+repr(value))

3 |> factorial |> print
```
_Showcases `else` statements, which work much like `else` statements in Python: the code under an `else` statement is only executed if the corresponding match fails._
```coconut
data point(x, y):
    def transform(self, other):
        match point(x, y) in other:
            return point(self.x + x, self.y + y)
        else:
            raise TypeError("arg to transform must be a point")

point(1,2) |> point(3,4).transform |> print
point(1,2) |> (==)$(point(1,2)) |> print
```
_Showcases matching to data types and the default equality operator. Values defined by the user with the `data` statement can be matched against and their contents accessed by specifically referencing arguments to the data type's constructor._
```coconut
class Tree
data Empty() from Tree
data Leaf(n) from Tree
data Node(l, r) from Tree

def depth(Tree()) = 0

@addpattern(depth)
def depth(Tree(n)) = 1

@addpattern(depth)
def depth(Tree(l, r)) = 1 + max([depth(l), depth(r)])

Empty() |> depth |> print
Leaf(5) |> depth |> print
Node(Leaf(2), Node(Empty(), Leaf(3))) |> depth |> print
```
_Showcases how the combination of data types and match statements can be used to powerful effect to replicate the usage of algebraic data types in other functional programming languages._
```coconut
def duplicate_first([x] + xs as l) =
    [x] + l

[1,2,3] |> duplicate_first |> print
```
_Showcases head-tail splitting, one of the most common uses of pattern-matching, where a `+ <var>` (or `:: <var>` for any iterable) at the end of a list or tuple literal can be used to match the rest of the sequence._
```
def sieve([head] :: tail) =
    [head] :: sieve(n for n in tail if n % head)

@addpattern(sieve)
def sieve((||)) = []
```
_Showcases how to match against iterators, namely that the empty iterator case (`(||)`) must come last, otherwise that case will exhaust the whole iterator before any other pattern has a chance to match against it._

**Python:**
_Can't be done without a long series of checks for each `match` statement. See the compiled code for the Python syntax._

### `case`

Coconut's `case` statement is an extension of Coconut's `match` statement for performing multiple `match` statements against the same value, where only one of them should succeed. Unlike lone `match` statements, only one match statement inside of a `case` block will ever succeed, and thus more general matches should be put below more specific ones.

Each pattern in a case block is checked until a match is found, and then the corresponding body is executed, and the case block terminated. The syntax for case blocks is
```coconut
case <value>:
    match <pattern> [if <cond>]:
        <body>
    match <pattern> [if <cond>]:
        <body>
    ...
[else:
    <body>]
```
where `<pattern>` is any `match` pattern, `<value>` is the item to match against, `<cond>` is an optional additional check, and `<body>` is simply code that is executed if the header above it succeeds. Note the absence of an `in` in the `match` statements: that's because the `<value>` in `case <value>` is taking its place. If no `else` is present and no match succeeds, then the `case` statement is simply skipped over as with [`match` statements](#match) (though unlike [destructuring assignments](#destructuring-assignment)).

Additionally, to help disambiguate Coconut's `case` syntax from Python 3.10's PEP 634 syntax (which Coconut also supports—see below), `cases` can be used as the top-level keyword instead of `case`, as in:
```coconut
cases <value>:
    match <pattern>:
        <body>
```

##### PEP 634 Support

Additionally, since Coconut is a strict superset of Python, Coconut has full Python 3.10+ [PEP 634](https://www.python.org/dev/peps/pep-0634) support. Note that, when using PEP 634 match-case syntax, Coconut will use PEP 634 pattern-matching rules rather than Coconut pattern-matching rules, though a warning will always be issued when those rules conflict. To use PEP 634 pattern-matching, the syntax is:
```coconut
match <value>:
    case <pattern> [if <cond>]:
        <body>
    case <pattern> [if <cond>]:
        <body>
    ...
[else:
    <body>]
```

As Coconut's pattern-matching rules and the PEP 634 rules sometimes conflict (specifically for classes and dictionaries), it is recommended to just always use Coconut-style pattern-matching (e.g. `case ...: match ...:` instead of `match ...: case ...:`) and use the following provided special constructs for getting PEP-634-style behavior:
- for matching dictionaries PEP-634-style, use `{..., **_}` to denote that the dictionary can contain extra unmatched items (to explicitly request the Coconut behavior, instead use `{..., **{}}`) and
- for matching classes PEP-634-style, use `class cls_name(args)` to denote that a `class` match rather than a `data` match is desired (to explicitly request a Coconut-style `data` match, instead use `data data_name(args)`).

_Note that `--strict` disables PEP-634-style pattern-matching syntax entirely._

##### Examples

**Coconut:**
```coconut
def classify_sequence(value):
    out = ""        # unlike with normal matches, only one of the patterns
    case value:     #  will match, and out will only get appended to once
        match ():
            out += "empty"
        match (_,):
            out += "singleton"
        match (x,x):
            out += "duplicate pair of "+str(x)
        match (_,_):
            out += "pair"
        match _ is (tuple, list):
            out += "sequence"
    else:
        raise TypeError()
    return out

[] |> classify_sequence |> print
() |> classify_sequence |> print
[1] |> classify_sequence |> print
(1,1) |> classify_sequence |> print
(1,2) |> classify_sequence |> print
(1,1,1) |> classify_sequence |> print
```
_Example of using Coconut's `case` syntax._
```coconut
match {"a": 1, "b": 2}:
    case {"a": a}:
        pass
    case _:
        assert False
assert a == 1
```
_Example of Coconut's PEP 634 support._

**Python:**
_Can't be done without a long series of checks for each `match` statement. See the compiled code for the Python syntax._

### `match data`

In addition to normal `data` statements, Coconut also supports pattern-matching data statements that enable the use of Coconut's pattern-matching syntax to define the data type's constructor. Pattern-matching data types look like
```
[match] data <name>(<patterns>) [from <base class>]:
    <body>
```
where `<patterns>` are exactly as in [pattern-matching functions](#pattern-matching-functions).

It is important to keep in mind that pattern-matching data types vary from normal data types in a variety of ways. First, like pattern-matching functions, they raise [`MatchError`](#matcherror) instead of `TypeError` when passed the wrong arguments. Second, pattern-matching data types will not do any special handling of starred arguments. Thus,
```
data vec(*xs)
```
when iterated over will iterate over all the elements of `xs`, but
```
match data vec(*xs)
```
when iterated over will only give the single element `xs`.

##### Example

**Coconut:**
```
data namedpt(name is str, x is int, y is int):
    def mag(self) = (self.x**2 + self.y**2)**0.5
```

**Python:**
_Can't be done without a series of method definitions for each data type. See the compiled code for the Python syntax._

### `where`

Coconut's `where` statement is extremely straightforward. The syntax for a `where` statement is just
```
<stmt> where:
    <body>
```
which just executes `<body>` followed by `<stmt>`.

##### Example

**Coconut:**
```coconut
c = a + b where:
    a = 1
    b = 2
```

**Python:**
```coconut_python
a = 1
b = 2
c = a + b
```

### Handling Keyword/Variable Name Overlap

In Coconut, the following keywords are also valid variable names:
- `async` (keyword in Python 3.5)
- `await` (keyword in Python 3.5)
- `data`
- `match`
- `case`
- `cases`
- `where`
- `addpattern`
- `then`
- `λ` (a [Unicode alternative](#unicode-alternatives) for `lambda`)

While Coconut can usually disambiguate these two use cases, special syntax is available for disambiguating these two use cases. To specify that you want a _variable_, prefix the name with a backslash as in `\data`, and to specify that you want a _keyword_, prefix the name with a colon as in `:match`. Note that, if what you're writing can be interpreted as valid Python 3, Coconut will always prefer that interpretation by default.

In addition to helping with cases where the two uses conflict, such disambiguation syntax can also be helpful for letting syntax highlighters know what you're doing.

##### Examples

**Coconut:**
```coconut
\data = 5
print(\data)
```

```coconut
# without the colon, Coconut will interpret this as the valid Python match[x, y] = input_list
:match [x, y] = input_list
```

**Python:**
```coconut_python
data = 5
print(data)
```

```coconut_python
x, y = input_list
```

## Expressions

### Statement Lambdas

The statement lambda syntax is an extension of the [normal lambda syntax](#lambdas) to support statements, not just expressions.

The syntax for a statement lambda is
```
def (arguments) -> statement; statement; ...
```
where `arguments` can be standard function arguments or [pattern-matching function definition](#pattern-matching-functions) arguments and `statement` can be an assignment statement or a keyword statement. If the last `statement` (not followed by a semicolon) is an `expression`, it will automatically be returned.

Statement lambdas also support implicit lambda syntax such that `def -> _` is equivalent to `def (_=None) -> _` as well as explicit pattern-matching syntax such that `match def (x) -> x` will be a pattern-matching function.

##### Example

**Coconut:**
```coconut
L |> map$(def (x) ->
    y = 1/x;
    y*(1 - y))
```

**Python:**
```coconut_python
def _lambda(x):
    y = 1/x
    return y*(1 - y)
map(_lambda, L)
```

#### Type annotations

Another case where statement lambdas would be used over standard lambdas is when the parameters to the lambda are typed with type annotations. Statement lambdas use the standard Python syntax for adding type annotations to their parameters:

```coconut
f = def (c: str) -> print(c)

g = def (a: int, b: int) -> a ** b
```

### Lazy Lists

Coconut supports the creation of lazy lists, where the contents in the list will be treated as an iterator and not evaluated until they are needed. Unlike normal iterators, however, lazy lists can be iterated over multiple times and still return the same result. Lazy lists can be created in Coconut simply by surrounding a comma-separated list of items with `(|` and `|)` (so-called "banana brackets") instead of `[` and `]` for a list or `(` and `)` for a tuple.

Lazy lists use [reiterable](#reiterable) under the hood to enable them to be iterated over multiple times.

##### Rationale

Lazy lists, where sequences are only evaluated when their contents are requested, are a mainstay of functional programming, allowing for dynamic evaluation of the list's contents.

##### Example

**Coconut:**
```coconut
(| print("hello,"), print("world!") |) |> consume
```

**Python:**
_Can't be done without a complicated iterator comprehension in place of the lazy list. See the compiled code for the Python syntax._

### Implicit Partial Application

Coconut supports a number of different syntactical aliases for common partial application use cases. These are:
```coconut
.attr           =>      operator.attrgetter("attr")
.method(args)   =>      operator.methodcaller("method", args)
obj.            =>      getattr$(obj)
func$           =>      ($)$(func)
seq[]           =>      operator.getitem$(seq)
iter$[]         =>      # the equivalent of seq[] for iterators
.[a:b:c]        =>      operator.itemgetter(slice(a, b, c))
.$[a:b:c]       =>      # the equivalent of .[a:b:c] for iterators
```

##### Example

**Coconut:**
```coconut
1 |> "123"[]
mod$ <| 5 <| 3
```

**Python:**
```coconut_python
"123"[1]
mod(5, 3)
```

### Operator Functions

Coconut uses a simple operator function short-hand: surround an operator with parentheses to retrieve its function. Similarly to iterator comprehensions, if the operator function is the only argument to a function, the parentheses of the function call can also serve as the parentheses for the operator function.

##### Rationale

A very common thing to do in functional programming is to make use of function versions of built-in operators: currying them, composing them, and piping them. To make this easy, Coconut provides a short-hand syntax to access operator functions.

##### Full List

```coconut
(|>)        => # pipe forward
(|*>)       => # multi-arg pipe forward
(|**>)      => # keyword arg pipe forward
(<|)        => # pipe backward
(<*|)       => # multi-arg pipe backward
(<**|)      => # keyword arg pipe backward
(|?>)       => # None-aware pipe forward
(|?*>)      => # None-aware multi-arg pipe forward
(|?**>)     => # None-aware keyword arg pipe forward
(..), (<..) => # backward function composition
(..>)       => # forward function composition
(<*..)      => # multi-arg backward function composition
(..*>)      => # multi-arg forward function composition
(<**..)     => # keyword arg backward function composition
(..**>)     => # keyword arg forward function composition
(.)         => (getattr)
(::)        => (itertools.chain)  # will not evaluate its arguments lazily
($)         => (functools.partial)
($[])       => # iterator slicing operator
(+)         => (operator.add)
(-)         => # 1 arg: operator.neg, 2 args: operator.sub
(*)         => (operator.mul)
(**)        => (operator.pow)
(/)         => (operator.truediv)
(//)        => (operator.floordiv)
(%)         => (operator.mod)
(&)         => (operator.and_)
(^)         => (operator.xor)
(|)         => (operator.or_)
(<<)        => (operator.lshift)
(>>)        => (operator.rshift)
(<)         => (operator.lt)
(>)         => (operator.gt)
(==)        => (operator.eq)
(<=)        => (operator.le)
(>=)        => (operator.ge)
(!=)        => (operator.ne)
(~)         => (operator.inv)
(@)         => (operator.matmul)
(not)       => (operator.not_)
(and)       => # boolean and
(or)        => # boolean or
(is)        => (operator.is_)
(in)        => (operator.contains)
(assert)    => # assert function
```

##### Example

**Coconut:**
```coconut
(range(0, 5), range(5, 10)) |*> map$(+) |> list |> print
```

**Python:**
```coconut_python
import operator
print(list(map(operator.add, range(0, 5), range(5, 10))))
```

### Implicit Function Application

Coconut supports implicit function application of the form `f x y`, which is compiled to `f(x, y)` (note: **not** `f(x)(y)` as is common in many languages with automatic currying). Implicit function application has a lower precedence than `..` function composition and a higher precedence than `**`.

Supported arguments to implicit function application are highly restricted, and must be either variables/attributes or **non-string** constants (e.g. `f x 1` will work but `f x [1]`, `f x (1+2)`, and `f "abc"` will not). Strings are disallowed due to conflicting with [Python's implicit string concatenation](https://stackoverflow.com/questions/18842779/string-concatenation-without-operator). Implicit function application is only intended for simple use cases—for more complex cases, use either standard function application or [pipes](#pipeline).

##### Examples

**Coconut:**
```coconut
def f(x, y) = (x, y)
print (f 5 10)
```

```coconut
def p1(x) = x + 1
print..p1 5
```

**Python:**
```coconut_python
def f(x, y): return (x, y)
print(f(100, 5+6))
```

```coconut_python
def p1(x): return x + 1
print(p1(5))
```

### Enhanced Type Annotation

Since Coconut syntax is a superset of Python 3 syntax, it supports [Python 3 function type annotation syntax](https://www.python.org/dev/peps/pep-0484/) and [Python 3.6 variable type annotation syntax](https://www.python.org/dev/peps/pep-0526/). By default, Coconut compiles all type annotations into Python-2-compatible type comments. If you want to keep the type annotations instead, simply pass a `--target` that supports them.

Since not all supported Python versions support the [`typing`](https://docs.python.org/3/library/typing.html) module, Coconut provides the [`TYPE_CHECKING`](#type-checking) built-in for hiding your `typing` imports and `TypeVar` definitions from being executed at runtime. Furthermore, when compiling type annotations to Python 3 versions without [PEP 563](https://www.python.org/dev/peps/pep-0563/) support, Coconut wraps annotation in strings to prevent them from being evaluated at runtime (note that `--no-wrap` disables all wrapping, including via PEP 563 support).

Additionally, Coconut adds special syntax for making type annotations easier and simpler to write. When inside of a type annotation, Coconut treats certain syntax constructs differently, compiling them to type annotations instead of what they would normally represent. Specifically, Coconut applies the following transformations:
```coconut
<type>?
    => typing.Optional[<type>]
<type>[]
    => typing.Sequence[<type>]
<type>$[]
    => typing.Iterable[<type>]
() -> <ret>
    => typing.Callable[[], <ret>]
<arg> -> <ret>
    => typing.Callable[[<arg>], <ret>]
(<args>) -> <ret>
    => typing.Callable[[<args>], <ret>]
-> <ret>
    => typing.Callable[..., <ret>]
<type> | <type>
    => typing.Union[<type>, <type>]
```
where `typing` is the Python 3.5 built-in [`typing` module](https://docs.python.org/3/library/typing.html).

_Note: The transformation to `Union` is not done on Python 3.10 as Python 3.10 has native [PEP 604](https://www.python.org/dev/peps/pep-0604) support._

Importantly, note that `<type>[]` does not map onto `typing.List[<int>]` but onto `typing.Sequence[<int>]`. This is because, when writing in an idiomatic functional style, assignment should be rare and tuples should be common. Using `Sequence` covers both cases, accommodating tuples and lists and preventing indexed assignment. When an indexed assignment is attempted into a variable typed with `Sequence`, MyPy will generate an error:

```
foo: int[] = [0, 1, 2, 3, 4, 5]
foo[0] = 1   # MyPy error: "Unsupported target for indexed assignment"
```

If you want to use `List` instead (if you want to support indexed assignment), use the standard Python 3.5 variable type annotation syntax: `foo: List[<type>]`.

_Note: To easily view your defined types, see [`reveal_type` and `reveal_locals`](#reveal-type-and-reveal-locals)._

##### Example

**Coconut:**
```coconut
def int_map(
    f: int -> int,
    xs: int[],
) -> int[] =
    xs |> map$(f) |> list
```

**Python:**
```coconut_python
import typing  # unlike this typing import, Coconut produces universal code
def int_map(
    f,  # type: typing.Callable[[int], int]
    xs,  # type: typing.Sequence[int]
):
    # type: (...) -> typing.Sequence[int]
    return list(map(f, xs))
```

### Set Literals

Coconut allows an optional `s` to be prepended in front of Python set literals. While in most cases this does nothing, in the case of the empty set it lets Coconut know that it is an empty set and not an empty dictionary. Additionally, an `f` is also supported, in which case a Python `frozenset` will be generated instead of a normal set.

##### Example

**Coconut:**
```coconut
empty_frozen_set = f{}
```

**Python:**
```coconut_python
empty_frozen_set = frozenset()
```

### Imaginary Literals

In addition to Python's `<num>j` or `<num>J` notation for imaginary literals, Coconut also supports `<num>i` or `<num>I`, to make imaginary literals more readable if used in a mathematical context.

##### Python Docs

Imaginary literals are described by the following lexical definitions:
```coconut
imagnumber ::= (floatnumber | intpart) ("j" | "J" | "i" | "I")
```
An imaginary literal yields a complex number with a real part of 0.0. Complex numbers are represented as a pair of floating point numbers and have the same restrictions on their range. To create a complex number with a nonzero real part, add a floating point number to it, e.g., `(3+4i)`. Some examples of imaginary literals:
```coconut
3.14i   10.i    10i     .001i   1e100i  3.14e-10i
```

##### Example

**Coconut:**
```coconut
3 + 4i |> abs |> print
```

**Python:**
```coconut_python
print(abs(3 + 4j))
```

### Alternative Ternary Operator

Python supports the ternary operator syntax
```coconut_python
result = if_true if condition else if_false
```
which, since Coconut is a superset of Python, Coconut also supports.

However, Coconut also provides an alternative syntax that uses the more conventional argument ordering as
```
result = if condition then if_true else if_false
```
making use of the Coconut-specific `then` keyword ([though Coconut still allows `then` as a variable name](#handling-keyword-variable-name-overlap)).

##### Example

**Coconut:**
```coconut
value = (
    if should_use_a() then a
    else if should_use_b() then b
    else if should_use_c() then c
    else fallback
)
```

**Python:**
```coconut_python
value = (
    a if should_use_a() else
    b if should_use_b() else
    c if should_use_c() else
    fallback
)
```

## Function Definition

### Tail Call Optimization

Coconut will perform automatic [tail call](https://en.wikipedia.org/wiki/Tail_call) optimization and tail recursion elimination on any function that meets the following criteria:

1. it must directly return (using either `return` or [assignment function notation](#assignment-functions)) a call to itself (tail recursion elimination, the most powerful optimization) or another function (tail call optimization),
2. it must not be a generator (uses `yield`) or an asynchronous function (uses `async`).

_Note: Tail call optimization (though not tail recursion elimination) will work even for 1) mutual recursion and 2) pattern-matching functions split across multiple definitions using [`addpattern`](#addpattern)._

If you are encountering a `RuntimeError` due to maximum recursion depth, it is highly recommended that you rewrite your function to meet either the criteria above for tail call optimization, or the corresponding criteria for [`recursive_iterator`](#recursive-iterator), either of which should prevent such errors.

##### Example

**Coconut:**
```coconut
# unlike in Python, this function will never hit a maximum recursion depth error
def factorial(n, acc=1):
    case n:
        match 0:
            return acc
        match _ is int if n > 0:
            return factorial(n-1, acc*n)
```
_Showcases tail recursion elimination._
```coconut
# unlike in Python, neither of these functions will ever hit a maximum recursion depth error
def is_even(0) = True
@addpattern(is_even)
def is_even(n is int if n > 0) = is_odd(n-1)

def is_odd(0) = False
@addpattern(is_odd)
def is_odd(n is int if n > 0) = is_even(n-1)
```
_Showcases tail call optimization._

**Python:**
_Can't be done without rewriting the function(s)._

#### `--no-tco` flag

_Note: Tail call optimization will be turned off if you pass the `--no-tco` command-line option, which is useful if you are having trouble reading your tracebacks and/or need maximum performance._

`--no-tco` does not disable tail recursion elimination.
This is because tail recursion elimination is usually faster than doing nothing, while other types of tail call optimization are usually slower than doing nothing.
Tail recursion elimination results in a big performance win because Python has a fairly large function call overhead. By unwinding a recursive function, far fewer function calls need to be made.
When the `--no-tco` flag is disabled, Coconut will attempt to do all types of tail call optimizations, handling non-recursive tail calls, split pattern-matching functions, mutual recursion, and tail recursion. When the `--no-tco` flag is enabled, Coconut will no longer perform any tail call optimizations other than tail recursion elimination.

#### Tail Recursion Elimination and Python lambdas

Coconut does not perform tail recursion elimination in functions that utilize lambdas in their tail call. This is because of the way that Python handles lambdas.
Each lambda stores a pointer to the namespace enclosing it, rather than a copy of the namespace. Thus, if the Coconut compiler tries to recycle anything in the namespace that produced the lambda, which needs to be done for TRE, the lambda can be changed retroactively.
A simple example demonstrating this behavior in Python:

```python
x = 1
foo = lambda: x
print(foo())  # 1
x = 2         # Directly alter the values in the namespace enclosing foo
print(foo())  # 2 (!)
```

Because this could have unintended and potentially damaging consequences, Coconut opts to not perform TRE on any function with a lambda in its tail call.

### Assignment Functions

Coconut allows for assignment function definition that automatically returns the last line of the function body. An assignment function is constructed by substituting `=` for `:` after the function definition line. Thus, the syntax for assignment function definition is either
```coconut
def <name>(<args>) = <expr>
```
for one-liners or
```coconut
def <name>(<args>) =
    <stmts>
    <expr>
```
for full functions, where `<name>` is the name of the function, `<args>` are the functions arguments, `<stmts>` are any statements that the function should execute, and `<expr>` is the value that the function should return.

_Note: Assignment function definition can be combined with infix and/or pattern-matching function definition._

##### Rationale

Coconut's Assignment function definition is as easy to write as assignment to a lambda, but will appear named in tracebacks, as it compiles to normal Python function definition.

##### Example

**Coconut:**
```coconut
def binexp(x) = 2**x
5 |> binexp |> print
```

**Python:**
```coconut_python
def binexp(x): return 2**x
print(binexp(5))
```

### Pattern-Matching Functions

Coconut pattern-matching functions are just normal functions where the arguments are patterns to be matched against instead of variables to be assigned to. The syntax for pattern-matching function definition is
```coconut
[match] def <name>(<arg>, <arg>, ... [if <cond>]) [-> <return_type>]:
    <body>
```
where `<arg>` is defined as
```coconut
[*|**] <pattern> [= <default>]
```
where `<name>` is the name of the function, `<cond>` is an optional additional check, `<body>` is the body of the function, `<pattern>` is defined by Coconut's [`match` statement](#match), `<default>` is the optional default if no argument is passed, and `<return_type>` is the optional return type annotation (note that argument type annotations are not supported for pattern-matching functions). The `match` keyword at the beginning is optional, but is sometimes necessary to disambiguate pattern-matching function definition from normal function definition, which will always take precedence.

If `<pattern>` has a variable name (either directly or with `as`), the resulting pattern-matching function will support keyword arguments using that variable name. If pattern-matching function definition fails, it will raise a [`MatchError`](#matcherror) object just like [destructuring assignment](#destructuring-assignment).

_Note: Pattern-matching function definition can be combined with assignment and/or infix function definition._

##### Example

**Coconut:**
```coconut
def last_two(_ + [a, b]):
    return a, b
def xydict_to_xytuple({"x":x is int, "y":y is int}):
    return x, y

range(5) |> last_two |> print
{"x":1, "y":2} |> xydict_to_xytuple |> print
```

**Python:**
_Can't be done without a long series of checks at the top of the function. See the compiled code for the Python syntax._

### `addpattern` Functions

Coconut provides the `addpattern def` syntax as a shortcut for the full
```coconut
@addpattern(func)
match def func(...):
  ...
```
syntax using the [`addpattern`](#addpattern) decorator.

If you want to put a decorator on an `addpattern def` function, make sure to put it on the _last_ pattern function.

##### Example

**Coconut:**
```coconut
def factorial(0) = 1
addpattern def factorial(n) = n * factorial(n - 1)
```

**Python:**
_Can't be done without a complicated decorator definition and a long series of checks for each pattern-matching. See the compiled code for the Python syntax._

### Infix Functions

Coconut allows for infix function calling, where an expression that evaluates to a function is surrounded by backticks and then can have arguments placed in front of or behind it. Infix calling has a precedence in-between chaining and `None`-coalescing, and is left-associative. Additionally, infix notation supports a lambda as the last argument, despite lambdas having a lower precedence. Thus, ``a `func` b -> c`` is equivalent to `func(a, b -> c)`.

Coconut also supports infix function definition to make defining functions that are intended for infix usage simpler. The syntax for infix function definition is
```coconut
def <arg> `<name>` <arg>:
    <body>
```
where `<name>` is the name of the function, the `<arg>`s are the function arguments, and `<body>` is the body of the function. If an `<arg>` includes a default, the `<arg>` must be surrounded in parentheses.

_Note: Infix function definition can be combined with assignment and/or pattern-matching function definition._

##### Rationale

A common idiom in functional programming is to write functions that are intended to behave somewhat like operators, and to call and define them by placing them between their arguments. Coconut's infix syntax makes this possible.

##### Example

**Coconut:**
```coconut
def a `mod` b = a % b
(x `mod` 2) `print`
```

**Python:**
```coconut_python
def mod(a, b): return a % b
print(mod(x, 2))
```

### Explicit Generators

Coconut supports the syntax
```
yield def <name>(<args>):
    <body>
```
to denote that you are explicitly defining a generator function. This is useful to ensure that, even if all the `yield`s in your function are removed, it'll always be a generator function. Explicit generator functions also support [pattern-matching syntax](#pattern-matching-functions), but not [assignment function syntax](#assignment-functions), as an assignment function would create a generator return, which is usually undesirable.

##### Example

**Coconut:**
```coconut
yield def empty_it(): pass
```

**Python:**
```coconut_python
def empty_it():
    if False:
        yield
```

### Dotted Function Definition

Coconut allows for function definition using a dotted name to assign a function as a method of an object as specified in [PEP 542](https://www.python.org/dev/peps/pep-0542/).

##### Example

**Coconut:**
```coconut
def MyClass.my_method(self):
    ...
```

**Python:**
```coconut_python
def my_method(self):
    ...
MyClass.my_method = my_method
```

## Statements

### Destructuring Assignment

Coconut supports significantly enhanced destructuring assignment, similar to Python's tuple/list destructuring, but much more powerful. The syntax for Coconut's destructuring assignment is
```coconut
[match] <pattern> = <value>
```
where `<value>` is any expression and `<pattern>` is defined by Coconut's [`match` statement](#match). The `match` keyword at the beginning is optional, but is sometimes necessary to disambiguate destructuring assignment from normal assignment, which will always take precedence. Coconut's destructuring assignment is equivalent to a match statement that follows the syntax:
```coconut
match <pattern> in <value>:
    pass
else:
    err = MatchError(<error message>)
    err.pattern = "<pattern>"
    err.value = <value>
    raise err
```
If a destructuring assignment statement fails, then instead of continuing on as if a `match` block had failed, a [`MatchError`](#matcherror) object will be raised describing the failure.

##### Example

**Coconut:**
```coconut
_ + [a, b] = [0, 1, 2, 3]
print(a, b)
```

**Python:**
_Can't be done without a long series of checks in place of the destructuring assignment statement. See the compiled code for the Python syntax._

### Decorators

Unlike Python, which only supports a single variable or function call in a decorator, Coconut supports any expression as in [PEP 614](https://www.python.org/dev/peps/pep-0614/).

##### Example

**Coconut:**
```coconut
@ wrapper1 .. wrapper2$(arg)
def func(x) = x**2
```

**Python:**
```coconut_python
def wrapper(func):
    return wrapper1(wrapper2(arg, func))
@wrapper
def func(x):
    return x**2
```

### Statement Nesting

Coconut supports the nesting of compound statements on the same line. This allows the mixing of `match` and `if` statements together, as well as compound `try` statements.

##### Example

**Coconut:**
```coconut
if invalid(input_list):
    raise Exception()
else: match [head] + tail in input_list:
    print(head, tail)
else:
    print(input_list)
```

**Python:**
```coconut_python
from collections.abc import Sequence
if invalid(input_list):
    raise Exception()
elif isinstance(input_list, Sequence):
    head, tail = inputlist[0], inputlist[1:]
    print(head, tail)
else:
    print(input_list)
```

### `except` Statements

Python 3 requires that if multiple exceptions are to be caught, they must be placed inside of parentheses, so as to disallow Python 2's use of a comma instead of `as`. Coconut allows commas in except statements to translate to catching multiple exceptions without the need for parentheses, since, as in Python 3, `as` is always required to bind the exception to a name.

##### Example

**Coconut:**
```coconut
try:
    unsafe_func(arg)
except SyntaxError, ValueError as err:
    handle(err)
```

**Python:**
```coconut_python
try:
    unsafe_func(arg)
except (SyntaxError, ValueError) as err:
    handle(err)
```

### Implicit `pass`

Coconut supports the simple `class name(base)` and `data name(args)` as aliases for `class name(base): pass` and `data name(args): pass`.

##### Example

**Coconut:**
```coconut
class Tree
data Empty from Tree
data Leaf(item) from Tree
data Node(left, right) from Tree
```

**Python:**
_Can't be done without a series of method definitions for each data type. See the compiled code for the Python syntax._

### In-line `global` And `nonlocal` Assignment

Coconut allows for `global` or `nonlocal` to precede assignment to a list of variables or (augmented) assignment to a variable to make that assignment `global` or `nonlocal`, respectively.

##### Example

**Coconut:**
```coconut
global state_a, state_b = 10, 100
global state_c += 1
```

**Python:**
```coconut_python
global state_a, state_b; state_a, state_b = 10, 100
global state_c; state_c += 1
```

### Code Passthrough

Coconut supports the ability to pass arbitrary code through the compiler without being touched, for compatibility with other variants of Python, such as [Cython](http://cython.org/) or [Mython](http://mython.org/). Anything placed between `\(` and the corresponding close parenthesis will be passed through, as well as any line starting with `\\`, which will have the additional effect of allowing indentation under it.

##### Example

**Coconut:**
```coconut
\\cdef f(x):
    return x |> g
```

**Python:**
```coconut_python
cdef f(x):
    return g(x)
```

### Enhanced Parenthetical Continuation

Since Coconut syntax is a superset of Python 3 syntax, Coconut supports the same line continuation syntax as Python. That means both backslash line continuation and implied line continuation inside of parentheses, brackets, or braces will all work.

In Python, however, there are some cases (such as multiple `with` statements) where only backslash continuation, and not parenthetical continuation, is supported. Coconut adds support for parenthetical continuation in all these cases.

Supporting parenthetical continuation everywhere allows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) convention, which avoids backslash continuation in favor of implied parenthetical continuation, to always be possible to follow. From PEP 8:

> The preferred way of wrapping long lines is by using Python's implied line continuation inside parentheses, brackets and braces. Long lines can be broken over multiple lines by wrapping expressions in parentheses. These should be used in preference to using a backslash for line continuation.

_Note: Passing `--strict` will enforce the PEP 8 convention by disallowing backslash continuations._

##### Example

**Coconut:**
```coconut
with (open('/path/to/some/file/you/want/to/read') as file_1,
      open('/path/to/some/file/being/written', 'w') as file_2):
    file_2.write(file_1.read())
```

**Python:**
```coconut_python
# split into two with statements for Python 2.6 compatibility
with open('/path/to/some/file/you/want/to/read') as file_1:
    with open('/path/to/some/file/being/written', 'w') as file_2:
        file_2.write(file_1.read())
```

## Built-Ins

### Enhanced Built-Ins

Coconut's `map`, `zip`, `filter`, `reversed`, and `enumerate` objects are enhanced versions of their Python equivalents that support:

- `reversed`,
- `repr`,
- optimized normal (and iterator) slicing (all but `filter`),
- `len` (all but `filter`),
- the ability to be iterated over multiple times if the underlying iterators are iterables,
- [PEP 618](https://www.python.org/dev/peps/pep-0618) `zip(..., strict=True)` support on all Python versions, and
- have added attributes which subclasses can make use of to get at the original arguments to the object:
  * `map`: `func`, `iters`
  * `zip`: `iters`
  * `filter`: `func`, `iter`
  * `reversed`: `iter`
  * `enumerate`: `iter`, `start`

##### Example

**Coconut:**
```coconut
map((+), range(5), range(6)) |> len |> print
range(10) |> filter$((x) -> x < 5) |> reversed |> tuple |> print
```

**Python:**
_Can't be done without defining a custom `map` type. The full definition of `map` can be found in the Coconut header._

### `addpattern`

Takes one argument that is a [pattern-matching function](#pattern-matching-functions), and returns a decorator that adds the patterns in the existing function to the new function being decorated, where the existing patterns are checked first, then the new. Roughly equivalent to:
```
def addpattern(base_func, *, allow_any_func=True):
    """Decorator to add a new case to a pattern-matching function, where the new case is checked last."""
    def pattern_adder(func):
        def add_pattern_func(*args, **kwargs):
            try:
                return base_func(*args, **kwargs)
            except MatchError:
                return func(*args, **kwargs)
        return add_pattern_func
    return pattern_adder
```

If you want to give an `addpattern` function a docstring, make sure to put it on the _last_ function.

Note that the function taken by `addpattern` must be a pattern-matching function. If `addpattern` receives a non pattern-matching function, the function with not raise `MatchError`, and `addpattern` won't be able to detect the failed match. Thus, if a later function was meant to be called, `addpattern` will not know that the first match failed and the correct path will never be reached.

For example, the following code raises a `TypeError`:
```coconut
def print_type():
    print("Received no arguments.")

@addpattern(print_type)
def print_type(x is int):
    print("Received an int.")

print_type()  # appears to work
print_type(1) # TypeError: print_type() takes 0 positional arguments but 1 was given
```

This can be fixed by using either the `match` or `addpattern` keyword. For example:
```coconut
match def print_type():
    print("Received no arguments.")

addpattern def print_type(x is int):
    print("Received an int.")

print_type(1)  # Works as expected
print_type("This is a string.") # Raises MatchError
```

The last case in an `addpattern` function, however, doesn't have to be a pattern-matching function if it is intended to catch all remaining cases.

To catch this mistake, `addpattern` will emit a warning if passed what it believes to be a non-pattern-matching function. However, this warning can sometimes be erroneous if the original pattern-matching function has been wrapped in some way, in which case you can pass `allow_any_func=True` to dismiss the warning.

##### Example

**Coconut:**
```coconut
def factorial(0) = 1

@addpattern(factorial)
def factorial(n) = n * factorial(n - 1)
```

**Python:**
_Can't be done without a complicated decorator definition and a long series of checks for each pattern-matching. See the compiled code for the Python syntax._

##### `prepattern`

**DEPRECATED:** Coconut also has a `prepattern` built-in, which adds patterns in the opposite order of `addpattern`; `prepattern` is defined as:

```coconut_python
def prepattern(base_func):
    """Decorator to add a new case to a pattern-matching function,
    where the new case is checked first."""
    def pattern_prepender(func):
        return addpattern(func)(base_func)
    return pattern_prepender
```
_Note: Passing `--strict` disables deprecated features._

### `reduce`

Coconut re-introduces Python 2's `reduce` built-in, using the `functools.reduce` version.

##### Python Docs

**reduce**(_function, iterable_**[**_, initializer_**]**)

Apply _function_ of two arguments cumulatively to the items of _sequence_, from left to right, so as to reduce the sequence to a single value. For example, `reduce((x, y) -> x+y, [1, 2, 3, 4, 5])` calculates `((((1+2)+3)+4)+5)`. The left argument, _x_, is the accumulated value and the right argument, _y_, is the update value from the _sequence_. If the optional _initializer_ is present, it is placed before the items of the sequence in the calculation, and serves as a default when the sequence is empty. If _initializer_ is not given and _sequence_ contains only one item, the first item is returned.

##### Example

**Coconut:**
```coconut
product = reduce$(*)
range(1, 10) |> product |> print
```

**Python:**
```coconut_python
import operator
import functools
product = functools.partial(functools.reduce, operator.mul)
print(product(range(1, 10)))
```

### `zip_longest`

Coconut provides an enhanced version of `itertools.zip_longest` as a built-in under the name `zip_longest`. `zip_longest` supports all the same features as Coconut's [enhanced zip](#enhanced-built-ins) as well as the additional attribute `fillvalue`.

##### Python Docs

**zip_longest**(_\*iterables, fillvalue=None_)

Make an iterator that aggregates elements from each of the iterables. If the iterables are of uneven length, missing values are filled-in with _fillvalue_. Iteration continues until the longest iterable is exhausted. Roughly equivalent to:

```coconut_python
def zip_longest(*args, fillvalue=None):
    # zip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
    iterators = [iter(it) for it in args]
    num_active = len(iterators)
    if not num_active:
        return
    while True:
        values = []
        for i, it in enumerate(iterators):
            try:
                value = next(it)
            except StopIteration:
                num_active -= 1
                if not num_active:
                    return
                iterators[i] = repeat(fillvalue)
                value = fillvalue
            values.append(value)
        yield tuple(values)
```

If one of the iterables is potentially infinite, then the `zip_longest()` function should be wrapped with something that limits the number of calls (for example iterator slicing or `takewhile`). If not specified, _fillvalue_ defaults to `None`.

##### Example

**Coconut:**
```coconut
result = zip_longest(range(5), range(10))
```

**Python:**
```coconut_python
import itertools
result = itertools.zip_longest(range(5), range(10))
```

### `takewhile`

Coconut provides `itertools.takewhile` as a built-in under the name `takewhile`.

##### Python Docs

**takewhile**(_predicate, iterable_)

Make an iterator that returns elements from the _iterable_ as long as the _predicate_ is true. Equivalent to:
```coconut_python
def takewhile(predicate, iterable):
    # takewhile(lambda x: x<5, [1,4,6,4,1]) --> 1 4
    for x in iterable:
        if predicate(x):
            yield x
        else:
            break
```

##### Example

**Coconut:**
```coconut
negatives = takewhile(numiter, x -> x < 0)
```

**Python:**
```coconut_python
import itertools
negatives = itertools.takewhile(numiter, lambda x: x < 0)
```

### `dropwhile`

Coconut provides `itertools.dropwhile` as a built-in under the name `dropwhile`.

##### Python Docs

**dropwhile**(_predicate, iterable_)

Make an iterator that drops elements from the _iterable_ as long as the _predicate_ is true; afterwards, returns every element. Note: the iterator does not produce any output until the predicate first becomes false, so it may have a lengthy start-up time. Equivalent to:
```coconut_python
def dropwhile(predicate, iterable):
    # dropwhile(lambda x: x<5, [1,4,6,4,1]) --> 6 4 1
    iterable = iter(iterable)
    for x in iterable:
        if not predicate(x):
            yield x
            break
    for x in iterable:
        yield x
```

##### Example

**Coconut:**
```coconut
positives = dropwhile(numiter, x -> x < 0)
```

**Python:**
```coconut_python
import itertools
positives = itertools.dropwhile(numiter, lambda x: x < 0)
```

### `memoize`

Coconut provides `functools.lru_cache` as a built-in under the name `memoize` with the modification that the _maxsize_ parameter is set to `None` by default. `memoize` makes the use case of optimizing recursive functions easier, as a _maxsize_ of `None` is usually what is desired in that case.

Use of `memoize` requires `functools.lru_cache`, which exists in the Python 3 standard library, but under Python 2 will require `pip install backports.functools_lru_cache` to function. Additionally, if on Python 2 and `backports.functools_lru_cache` is present, Coconut will patch `functools` such that `functools.lru_cache = backports.functools_lru_cache.lru_cache`.

##### Python Docs

**memoize**(_maxsize=None, typed=False_)

Decorator to wrap a function with a memoizing callable that saves up to the _maxsize_ most recent calls. It can save time when an expensive or I/O bound function is periodically called with the same arguments.

Since a dictionary is used to cache results, the positional and keyword arguments to the function must be hashable.

If _maxsize_ is set to `None`, the LRU feature is disabled and the cache can grow without bound. The LRU feature performs best when _maxsize_ is a power-of-two.

If _typed_ is set to true, function arguments of different types will be cached separately. For example, `f(3)` and `f(3.0)` will be treated as distinct calls with distinct results.

To help measure the effectiveness of the cache and tune the _maxsize_ parameter, the wrapped function is instrumented with a `cache_info()` function that returns a named tuple showing _hits_, _misses_, _maxsize_ and _currsize_. In a multi-threaded environment, the hits and misses are approximate.

The decorator also provides a `cache_clear()` function for clearing or invalidating the cache.

The original underlying function is accessible through the `__wrapped__` attribute. This is useful for introspection, for bypassing the cache, or for rewrapping the function with a different cache.

An LRU (least recently used) cache works best when the most recent calls are the best predictors of upcoming calls (for example, the most popular articles on a news server tend to change each day). The cache’s size limit assures that the cache does not grow without bound on long-running processes such as web servers.

Example of an LRU cache for static web content:
```coconut_python
@memoize(maxsize=32)
def get_pep(num):
    'Retrieve text of a Python Enhancement Proposal'
    resource = 'http://www.python.org/dev/peps/pep-%04d/' % num
    try:
        with urllib.request.urlopen(resource) as s:
            return s.read()
    except urllib.error.HTTPError:
        return 'Not Found'

>>> for n in 8, 290, 308, 320, 8, 218, 320, 279, 289, 320, 9991:
...     pep = get_pep(n)
...     print(n, len(pep))

>>> get_pep.cache_info()
CacheInfo(hits=3, misses=8, maxsize=32, currsize=8)
```

##### Example

**Coconut:**
```coconut
def fib(n if n < 2) = n

@memoize()
@addpattern(fib)
def fib(n) = fib(n-1) + fib(n-2)
```

**Python:**
```coconut_python
try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache
@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)
```

### `override`

Coconut provides the `@override` decorator to allow declaring a method definition in a subclass as an override of some parent class method. When `@override` is used on a method, if a method of the same name does not exist on some parent class, the class definition will raise a `RuntimeError`.

##### Example

**Coconut:**
```coconut
class A:
    x = 1
    def f(self, y) = self.x + y

class B:
    @override
    def f(self, y) = self.x + y + 1
```

**Python:**
_Can't be done without a long decorator definition. The full definition of the decorator in Python can be found in the Coconut header._

### `groupsof`

Coconut provides the `groupsof` built-in to split an iterable into groups of a specific length. Specifically, `groupsof(n, iterable)` will split `iterable` into tuples of length `n`, with only the last tuple potentially of size `< n` if the length of `iterable` is not divisible by `n`.

##### Example

**Coconut:**
```coconut
pairs = range(1, 11) |> groupsof$(2)
```

**Python:**
```coconut_python
pairs = []
group = []
for item in range(1, 11):
    group.append(item)
    if len(group) == 2:
        pairs.append(tuple(group))
        group = []
if group:
    pairs.append(tuple(group))
```

### `tee`

Coconut provides an optimized version of `itertools.tee` as a built-in under the name `tee`.

##### Python Docs

**tee**(_iterable, n=2_)

Return _n_ independent iterators from a single iterable. Equivalent to:
```coconut_python
def tee(iterable, n=2):
    it = iter(iterable)
    deques = [collections.deque() for i in range(n)]
    def gen(mydeque):
        while True:
            if not mydeque:             # when the local deque is empty
                newval = next(it)       # fetch a new value and
                for d in deques:        # load it to all the deques
                    d.append(newval)
            yield mydeque.popleft()
    return tuple(gen(d) for d in deques)
```
Once `tee()` has made a split, the original _iterable_ should not be used anywhere else; otherwise, the _iterable_ could get advanced without the tee objects being informed.

This itertool may require significant auxiliary storage (depending on how much temporary data needs to be stored). In general, if one iterator uses most or all of the data before another iterator starts, it is faster to use `list()` instead of `tee()`.

##### Example

**Coconut:**
```coconut
original, temp = tee(original)
sliced = temp$[5:]
```

**Python:**
```coconut_python
import itertools
original, temp = itertools.tee(original)
sliced = itertools.islice(temp, 5, None)
```

### `reiterable`

Sometimes, when an iterator may need to be iterated over an arbitrary number of times, [`tee`](#tee) can be cumbersome to use. For such cases, Coconut provides `reiterable`, which wraps the given iterator such that whenever an attempt to iterate over it is made, it iterates over a `tee` instead of the original.

##### Example

**Coconut:**
```coconut
def list_type(xs):
    case reiterable(xs):
        match [fst, snd] :: tail:
            return "at least 2"
        match [fst] :: tail:
            return "at least 1"
        match (| |):
            return "empty"
```

**Python:**
_Can't be done without a long series of checks for each `match` statement. See the compiled code for the Python syntax._

### `consume`

Coconut provides the `consume` function to efficiently exhaust an iterator and thus perform any lazy evaluation contained within it. `consume` takes one optional argument, `keep_last`, that defaults to 0 and specifies how many, if any, items from the end to return as an iterable (`None` will keep all elements).

Equivalent to:
```coconut
def consume(iterable, keep_last=0):
    """Fully exhaust iterable and return the last keep_last elements."""
    return collections.deque(iterable, maxlen=keep_last)  # fastest way to exhaust an iterator
```

##### Rationale

In the process of lazily applying operations to iterators, eventually a point is reached where evaluation of the iterator is necessary. To do this efficiently, Coconut provides the `consume` function, which will fully exhaust the iterator given to it.

##### Example

**Coconut:**
```coconut
range(10) |> map$((x) -> x**2) |> map$(print) |> consume
```

**Python:**
```coconut_python
collections.deque(map(print, map(lambda x: x**2, range(10))), maxlen=0)
```

### `count`

Coconut provides a modified version of `itertools.count` that supports `in`, normal slicing, optimized iterator slicing, the standard `count` and `index` sequence methods, `repr`, and `start`/`step` attributes as a built-in under the name `count`.

Additionally, if the _step_ parameter is set to `None`, `count` will behave like `itertools.repeat` instead.

##### Python Docs

**count**(_start=0, step=1_)

Make an iterator that returns evenly spaced values starting with number _start_. Often used as an argument to `map()` to generate consecutive data points. Also, used with `zip()` to add sequence numbers. Roughly equivalent to:
```coconut_python
def count(start=0, step=1):
    # count(10) --> 10 11 12 13 14 ...
    # count(2.5, 0.5) -> 2.5 3.0 3.5 ...
    n = start
    while True:
        yield n
        if step:
          n += step
```

##### Example

**Coconut:**
```coconut
count()$[10**100] |> print
```

**Python:**
_Can't be done quickly without Coconut's iterator slicing, which requires many complicated pieces. The necessary definitions in Python can be found in the Coconut header._

### `makedata`

Coconut provides the `makedata` function to construct a container given the desired type and contents. This is particularly useful when writing alternative constructors for data types by overwriting `__new__`, since it allows direct access to the base constructor of the data type created with the Coconut `data` statement. `makedata` takes the data type to construct as the first argument, and the objects to put in that container as the rest of the arguments.

**DEPRECATED:** Coconut also has a `datamaker` built-in, which partially applies `makedata`; `datamaker` is defined as:
```coconut
def datamaker(data_type):
    """Get the original constructor of the given data type or class."""
    return makedata$(data_type)
```
_Note: Passing `--strict` disables deprecated features._

##### Example

**Coconut:**
```coconut
data Tuple(elems):
    def __new__(cls, *elems):
        return elems |> makedata$(cls)
```

**Python:**
_Can't be done without a series of method definitions for each data type. See the compiled code for the Python syntax._

### `fmap`

In functional programming, `fmap(func, obj)` takes a data type `obj` and returns a new data type with `func` mapped over the contents. Coconut's `fmap` function does the exact same thing in Coconut.

`fmap` can also be used on built-ins such as `str`, `list`, `set`, and `dict` as a variant of `map` that returns back an object of the same type. The behavior of `fmap` for a given object can be overridden by defining an `__fmap__(self, func)` magic method that will be called whenever `fmap` is invoked on that object.

For `dict`, or any other `collections.abc.Mapping`, `fmap` will `starmap` over the mapping's `.items()` instead of the default iteration through its `.keys()`.

As an additional special case, for [`numpy`](http://www.numpy.org/) and [`pandas`](https://pandas.pydata.org/) objects, `fmap` will use [`np.vectorize`](https://docs.scipy.org/doc/numpy/reference/generated/numpy.vectorize.html) to produce the result.

##### Example

**Coconut:**
```coconut
[1, 2, 3] |> fmap$(x -> x+1) == [2, 3, 4]

class Maybe
data Nothing() from Maybe
data Just(n) from Maybe

Just(3) |> fmap$(x -> x*2) == Just(6)
Nothing() |> fmap$(x -> x*2) == Nothing()
```

**Python:**
_Can't be done without a series of method definitions for each data type. See the compiled code for the Python syntax._

### `starmap`

Coconut provides a modified version of `itertools.starmap` that supports `reversed`, `repr`, optimized normal (and iterator) slicing, `len`, and `func`/`iter` attributes.

##### Python Docs

**starmap**(_function, iterable_)

Make an iterator that computes the function using arguments obtained from the iterable. Used instead of `map()` when argument parameters are already grouped in tuples from a single iterable (the data has been "pre-zipped"). The difference between `map()` and `starmap()` parallels the distinction between `function(a,b)` and `function(*c)`. Roughly equivalent to:

```coconut_python
def starmap(function, iterable):
    # starmap(pow, [(2,5), (3,2), (10,3)]) --> 32 9 1000
    for args in iterable:
        yield function(*args)
```

##### Example

**Coconut:**
```coconut
range(1, 5) |> map$(range) |> starmap$(print) |> consume
```

**Python:**
```coconut_python
import itertools, collections
collections.deque(itertools.starmap(print, map(range, range(1, 5))), maxlen=0)
```

### `scan`

Coconut provides a modified version of `itertools.accumulate` with opposite argument order as `scan` that also supports `repr`, `len`, and `func`/`iter`/`initializer` attributes. `scan` works exactly like [`reduce`](#reduce), except that instead of only returning the last accumulated value, it returns an iterator of all the intermediate values.

##### Python Docs

**scan**(_function, iterable_**[**_, initializer_**]**)

Make an iterator that returns accumulated results of some function of two arguments. Elements of the input iterable may be any type that can be accepted as arguments to _function_. (For example, with the operation of addition, elements may be any addable type including Decimal or Fraction.) If the input iterable is empty, the output iterable will also be empty.

If no _initializer_ is given, roughly equivalent to:
```coconut_python
def scan(function, iterable):
    'Return running totals'
    # scan(operator.add, [1,2,3,4,5]) --> 1 3 6 10 15
    # scan(operator.mul, [1,2,3,4,5]) --> 1 2 6 24 120
    it = iter(iterable)
    try:
        total = next(it)
    except StopIteration:
        return
    yield total
    for element in it:
        total = function(total, element)
        yield total
```

##### Example

**Coconut:**
```coconut
input_data = [3, 4, 6, 2, 1, 9, 0, 7, 5, 8]
running_max = input_data |> scan$(max) |> list
```

**Python:**
```coconut_python
input_data = [3, 4, 6, 2, 1, 9, 0, 7, 5, 8]
running_max = []
max_so_far = input_data[0]
for x in input_data:
    if x > max_so_far:
        max_so_far = x
    running_max.append(x)
```

### `flatten`

Coconut provides an enhanced version of `itertools.chain.from_iterable` as a built-in under the name `flatten` with added support for `reversed`, `repr`, `in`, `.count()`, `.index()`, and `fmap`.

##### Python Docs

chain.**from_iterable**(_iterable_)

Alternate constructor for `chain()`. Gets chained inputs from a single iterable argument that is evaluated lazily. Roughly equivalent to:

```coconut_python
def flatten(iterables):
    # flatten(['ABC', 'DEF']) --> A B C D E F
    for it in iterables:
        for element in it:
            yield element
```

##### Example

**Coconut:**
```coconut
iter_of_iters = [[1, 2], [3, 4]]
flat_it = iter_of_iters |> flatten |> list
```

**Python:**
```coconut_python
from itertools import chain
iter_of_iters = [[1, 2], [3, 4]]
flat_it = iter_of_iters |> chain.from_iterable |> list
```

### `recursive_iterator`

Coconut provides a `recursive_iterator` decorator that provides significant optimizations for any stateless, recursive function that returns an iterator. To use `recursive_iterator` on a function, it must meet the following criteria:

1. your function either always `return`s an iterator or generates an iterator using `yield`,
2. when called multiple times with arguments that are equal, your function produces the same iterator (your function is stateless), and
3. your function gets called (usually calls itself) multiple times with the same arguments.

If you are encountering a `RuntimeError` due to maximum recursion depth, it is highly recommended that you rewrite your function to meet either the criteria above for `recursive_iterator`, or the corresponding criteria for Coconut's [tail call optimization](#tail-call-optimization), either of which should prevent such errors.

Furthermore, `recursive_iterator` also allows the resolution of a [nasty segmentation fault in Python's iterator logic that has never been fixed](http://bugs.python.org/issue14010). Specifically, instead of writing
```coconut
seq = get_elem() :: seq
```
which will crash due to the aforementioned Python issue, write
```coconut
@recursive_iterator
def seq() = get_elem() :: seq()
```
which will work just fine.

One pitfall to keep in mind working with `recursive_iterator` is that it shouldn't be used in contexts where the function can potentially be called multiple times with the same iterator object as an input, but with that object not actually corresponding to the same items (e.g. because the first time the object hasn't been iterated over yet and the second time it has been).

##### Example

**Coconut:**
```coconut
@recursive_iterator
def fib() = (1, 1) :: map((+), fib(), fib()$[1:])
```

**Python:**
_Can't be done without a long decorator definition. The full definition of the decorator in Python can be found in the Coconut header._

### `parallel_map`

Coconut provides a parallel version of `map` under the name `parallel_map`. `parallel_map` makes use of multiple processes, and is therefore much faster than `map` for CPU-bound tasks. `parallel_map` never loads the entire input iterator into memory, though it does consume the entire input iterator as soon as a single output is requested. If any exceptions are raised inside of `parallel_map`, a traceback will be printed as soon as they are encountered.

Because `parallel_map` uses multiple processes for its execution, it is necessary that all of its arguments be pickleable. Only objects defined at the module level, and not lambdas, objects defined inside of a function, or objects defined inside of the interpreter, are pickleable. Furthermore, on Windows, it is necessary that all calls to `parallel_map` occur inside of an `if __name__ == "__main__"` guard.

If multiple sequential calls to `parallel_map` need to be made, it is highly recommended that they be done inside of a `with parallel_map.multiple_sequential_calls():` block, which will cause the different calls to use the same process pool and result in `parallel_map` immediately returning a list rather than a `parallel_map` object. If multiple sequential calls are necessary and the laziness of parallel_map is required, then the `parallel_map` objects should be constructed before the `multiple_sequential_calls` block and then only iterated over once inside the block.

`parallel_map.multiple_sequential_calls` also supports a `max_workers` argument to set the number of processes.

##### Python Docs

**parallel_map**(_func, \*iterables_, _chunksize_=`1`)

Equivalent to `map(func, *iterables)` except _func_ is executed asynchronously and several calls to _func_ may be made concurrently. If a call raises an exception, then that exception will be raised when its value is retrieved from the iterator.

`parallel_map` chops the iterable into a number of chunks which it submits to the process pool as separate tasks. The (approximate) size of these chunks can be specified by setting _chunksize_ to a positive integer. For very long iterables using a large value for _chunksize_ can make the job complete **much** faster than using the default value of `1`.

##### Example

**Coconut:**
```coconut
parallel_map(pow$(2), range(100)) |> list |> print
```

**Python:**
```coconut_python
import functools
from multiprocessing import Pool
with Pool() as pool:
    print(list(pool.imap(functools.partial(pow, 2), range(100))))
```

### `concurrent_map`

Coconut provides a concurrent version of [`parallel_map`](#parallel-map) under the name `concurrent_map`. `concurrent_map` behaves identically to `parallel_map` except that it uses multithreading instead of multiprocessing, and is therefore primarily useful for IO-bound tasks.

##### Python Docs

**concurrent_map**(_func, \*iterables_, _chunksize_=`1`)

Equivalent to `map(func, *iterables)` except _func_ is executed asynchronously and several calls to _func_ may be made concurrently. If a call raises an exception, then that exception will be raised when its value is retrieved from the iterator.

`concurrent_map` chops the iterable into a number of chunks which it submits to the process pool as separate tasks. The (approximate) size of these chunks can be specified by setting _chunksize_ to a positive integer. For very long iterables using a large value for _chunksize_ can make the job complete **much** faster than using the default value of `1`.

##### Example

**Coconut:**
```coconut
concurrent_map(get_data_for_user, get_all_users()) |> list |> print
```

**Python:**
```coconut_python
import functools
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor() as executor:
    print(list(executor.map(get_data_for_user, get_all_users())))
```

### `MatchError`

A `MatchError` is raised when a [destructuring assignment](#destructuring-assignment) statement fails, and thus `MatchError` is provided as a built-in for catching those errors. `MatchError` objects support three attributes: `pattern`, which is a string describing the failed pattern; `value`, which is the object that failed to match that pattern; and `message` which is the full error message. To avoid unnecessary `repr` calls, `MatchError` only computes the `message` once it is actually requested.

Additionally, if you are using [view patterns](#match), you might need to raise your own `MatchError` (though you can also just use a destructuring assignment or pattern-matching function definition to do so). To raise your own `MatchError`, just `raise MatchError(pattern, value)` (both arguments are optional).

### `TYPE_CHECKING`

The `TYPE_CHECKING` variable is set to `False` at runtime and `True` during type-checking, allowing you to prevent your `typing` imports and `TypeVar` definitions from being executed at runtime. By wrapping your `typing` imports in an `if TYPE_CHECKING:` block, you can even use the [`typing`](https://docs.python.org/3/library/typing.html) module on Python versions that don't natively support it. Furthermore, `TYPE_CHECKING` can also be used to hide code that is mistyped by default.

##### Python Docs

A special constant that is assumed to be `True` by 3rd party static type checkers. It is `False` at runtime. Usage:
```coconut_python
if TYPE_CHECKING:
    import expensive_mod

def fun(arg: expensive_mod.SomeType) -> None:
    local_var: expensive_mod.AnotherType = other_fun()
```

##### Examples

**Coconut:**
```coconut
if TYPE_CHECKING:
    from typing import List
x: List[str] = ["a", "b"]
```

```coconut
if TYPE_CHECKING:
    def factorial(n: int) -> int: ...
else:
    def factorial(0) = 1
    addpattern def factorial(n) = n * factorial(n-1)
```

**Python:**
```coconut_python
try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import List
x: List[str] = ["a", "b"]
```

```coconut_python
try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    def factorial(n: int) -> int: ...
else:
    def factorial(n):
        if n == 0:
            return 1
        else:
            return n * factorial(n-1)
```

### `reveal_type` and `reveal_locals`

When using MyPy, `reveal_type(<expr>)` will cause MyPy to print the type of `<expr>` and `reveal_locals()` will cause MyPy to print the types of the current `locals()`. At runtime, `reveal_type(x)` is always the identity function and `reveal_locals()` always returns `None`. See [the MyPy documentation](https://mypy.readthedocs.io/en/stable/common_issues.html#reveal-type) for more information.

##### Example

**Coconut:**
```coconut_pycon
> coconut --mypy
Coconut Interpreter vX.X.X:
(enter 'exit()' or press Ctrl-D to end)
>>> reveal_type(fmap)
<function fmap at 0x00000239B06E2040>
<string>:17: note: Revealed type is 'def [_T, _U] (func: def (_T`-1) -> _U`-2, obj: typing.Iterable[_T`-1]) -> typing.Iterable[_U`-2]'
>>>
```

**Python**
```coconut_python
try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if not TYPE_CHECKING:
    def reveal_type(x):
        return x

from coconut.__coconut__ import fmap
reveal_type(fmap)
```

## Coconut API

### `coconut.embed`

**coconut.embed**(_kernel_=`None`, _depth_=`0`, \*\*_kwargs_)

If _kernel_=`False` (default), embeds a Coconut Jupyter console initialized from the current local namespace. If _kernel_=`True`, launches a Coconut Jupyter kernel initialized from the local namespace that can then be attached to. The _depth_ indicates how many additional call frames to ignore. _kwargs_ are as in [IPython.embed](https://ipython.readthedocs.io/en/stable/api/generated/IPython.terminal.embed.html#IPython.terminal.embed.embed) or [IPython.embed_kernel](https://ipython.readthedocs.io/en/stable/api/generated/IPython.html#IPython.embed_kernel) based on _kernel_.

Recommended usage is as a debugging tool, where the code `from coconut import embed; embed()` can be inserted to launch an interactive Coconut shell initialized from that point.

### Automatic Compilation

If you don't care about the exact compilation parameters you want to use, automatic compilation lets Coconut take care of everything for you. Automatic compilation can be enabled either by importing [`coconut.convenience`](#coconut-convenience) before you import anything else, or by running `coconut --site-install`. Once automatic compilation is enabled, Coconut will check each of your imports to see if you are attempting to import a `.coco` file and, if so, automatically compile it for you. Note that, for Coconut to know what file you are trying to import, it will need to be accessible via `sys.path`, just like a normal import.

Automatic compilation always compiles modules and packages in-place, and always uses `--target sys`. Automatic compilation is always available in the Coconut interpreter, and, if using the Coconut interpreter, a `reload` built-in is provided to easily reload imported modules. Additionally, the interpreter always allows importing from the current working directory, letting you easily compile and play around with a `.coco` file simply by running the Coconut interpreter and importing it.

### Coconut Encoding

While automatic compilation is the preferred method for dynamically compiling Coconut files, as it caches the compiled code as a `.py` file to prevent recompilation, Coconut also supports a special
```coconut
# coding: coconut
```
declaration which can be added to `.py` files to have them treated as Coconut files instead. To use such a coding declaration, you'll need to either run `coconut --site-install` or `import coconut.convenience` at some point before you first attempt to import a file with a `# coding: coconut` declaration. Like automatic compilation, compilation is always done with `--target sys` and is always available from the Coconut interpreter.

### `coconut.convenience`

In addition to enabling automatic compilation, `coconut.convenience` can also be used to call the Coconut compiler from code instead of from the command line. See below for specifications of the different convenience functions.

#### `parse`

**coconut.convenience.parse**(**[**_code,_ **[**_mode_**]]**)

Likely the most useful of the convenience functions, `parse` takes Coconut code as input and outputs the equivalent compiled Python code. The second argument, _mode_, is used to indicate the context for the parsing.

If _code_ is not passed, `parse` will output just the given _mode_'s header, which can be executed to set up an execution environment in which future code can be parsed and executed without a header.

Each _mode_ has two components: what parser it uses, and what header it prepends. The parser determines what Coconut code is allowed as input, and the header determines how the compiled Python can be used. Possible values of _mode_ are:

- `"sys"`: (the default)
    + parser: file
        * The file parser can parse any Coconut code.
    + header: sys
        * This header imports [`coconut.__coconut__`](#coconut-coconut) to access the necessary Coconut objects.
- `"exec"`:
    + parser: file
    + header: exec
        * When passed to `exec` at the global level, this header will create all the necessary Coconut objects itself instead of importing them.
- `"file"`:
    + parser: file
    + header: file
        * This header is meant to be written to a `--standalone` file and should not be passed to `exec`.
- `"package"`:
    + parser: file
    + header: package
        * This header is meant to be written to a `--package` file and should not be passed to `exec`.
- `"block"`:
    + parser: file
    + header: none
        * No header is included, thus this can only be passed to `exec` if code with a header has already been executed at the global level.
- `"single"`:
    + parser: single
        * Can only parse one line of Coconut code.
    + header: none
- `"eval"`:
    + parser: eval
        * Can only parse a Coconut expression, not a statement.
    + header: none
- `"any"`:
    + parser: any
        * Can parse any Coconut code, allows leading whitespace, and has no trailing newline.
    + header: none

##### Example

```coconut_python
from coconut.convenience import parse
exec(parse())
while True:
    exec(parse(input(), mode="block"))
```

#### `setup`

**coconut.convenience.setup**(_target, strict, minify, line\_numbers, keep\_lines, no\_tco_)

`setup` can be used to pass command line flags for use in `parse`. The possible values for each flag argument are:

- _target_: `None` (default), or any [allowable target](#allowable-targets)
- _strict_: `False` (default) or `True`
- _minify_: `False` (default) or `True`
- _line\_numbers_: `False` (default) or `True`
- _keep\_lines_: `False` (default) or `True`
- _no\_tco_: `False` (default) or `True`

#### `cmd`

**coconut.convenience.cmd**(_args_, **[**_interact_**]**)

Executes the given _args_ as if they were fed to `coconut` on the command-line, with the exception that unless _interact_ is true or `-i` is passed, the interpreter will not be started. Additionally, since `parse` and `cmd` share the same convenience parsing object, any changes made to the parsing with `cmd` will work just as if they were made with `setup`.

#### `coconut_eval`

**coconut.convenience.coconut_eval**(_expression_, _globals_=`None`, _locals_=`None`)

Version of [`eval`](https://docs.python.org/3/library/functions.html#eval) which can evaluate Coconut code. Uses the same convenience parsing object as the other functions and thus can be controlled by `setup`.

#### `version`

**coconut.convenience.version**(**[**_which_**]**)

Retrieves a string containing information about the Coconut version. The optional argument _which_ is the type of version information desired. Possible values of _which_ are:

- `"num"`: the numerical version (the default)
- `"name"`: the version codename
- `"spec"`: the numerical version with the codename attached
- `"tag"`: the version tag used in GitHub and documentation URLs
- `"-v"`: the full string printed by `coconut -v`

#### `auto_compilation`

**coconut.convenience.auto_compilation**(_on_=`True`)

Turns [automatic compilation](#automatic-compilation) on or off. This function is called automatically when `coconut.convenience` is imported.

#### `use_coconut_breakpoint`

**coconut.convenience.use_coconut_breakpoint**(_on_=`True`)

Switches the [`breakpoint` built-in](https://www.python.org/dev/peps/pep-0553/) which Coconut makes universally available to use [`coconut.embed`](#coconut-embed) instead of [`pdb.set_trace`](https://docs.python.org/3/library/pdb.html#pdb.set_trace) (or undoes that switch if `on=False`). This function is called automatically when `coconut.convenience` is imported.

#### `CoconutException`

If an error is encountered in a convenience function, a `CoconutException` instance may be raised. `coconut.convenience.CoconutException` is provided to allow catching such errors.

### `coconut.__coconut__`

It is sometimes useful to be able to access Coconut built-ins from pure Python. To accomplish this, Coconut provides `coconut.__coconut__`, which behaves exactly like the `__coconut__.py` header file included when Coconut is compiled in package mode.

All Coconut built-ins are accessible from `coconut.__coconut__`. The recommended way to import them is to use `from coconut.__coconut__ import` and import whatever built-ins you'll be using.

##### Example

```coconut_python
from coconut.__coconut__ import parallel_map
```
