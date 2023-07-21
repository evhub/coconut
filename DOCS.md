```{eval-rst}
:tocdepth: 2
```

# Coconut Documentation

```{contents}
---
local:
depth: 2
---
```

## Overview

This documentation covers all the features of the [Coconut Programming Language](http://evhub.github.io/coconut/), and is intended as a reference/specification, not a tutorialized introduction. For a full introduction and tutorial of Coconut, see [the tutorial](./HELP.md).

Coconut is a variant of [Python](https://www.python.org/) built for **simple, elegant, Pythonic functional programming**. Coconut syntax is a strict superset of the latest Python 3 syntax. Thus, users familiar with Python will already be familiar with most of Coconut.

The Coconut compiler turns Coconut code into Python code. The primary method of accessing the Coconut compiler is through the Coconut command-line utility, which also features an interpreter for real-time compilation. In addition to the command-line utility, Coconut also supports the use of IPython/Jupyter notebooks.

Thought Coconut syntax is primarily based on that of Python, other languages that inspired Coconut include [Haskell](https://www.haskell.org/), [CoffeeScript](http://coffeescript.org/), [F#](http://fsharp.org/), and [Julia](https://julialang.org/).

#### Try It Out

If you want to try Coconut in your browser, check out the [online interpreter](https://cs121-team-panda.github.io/coconut-interpreter). Note, however, that it may be running an outdated version of Coconut.

## Installation

```{contents}
---
local:
depth: 2
---
```

#### Using Pip

Since Coconut is hosted on the [Python Package Index](https://pypi.python.org/pypi/coconut), it can be installed easily using `pip`. Simply [install Python](https://www.python.org/downloads/), open up a command-line prompt, and enter
```
pip install coconut
```
which will install Coconut and its required dependencies.

_Note: If you have an old version of Coconut installed and you want to upgrade, run `pip install --upgrade coconut` instead._

If you are encountering errors running `pip install coconut`, try adding `--user` or running
```
pip install --no-deps --upgrade coconut "pyparsing<3"
```
which will force Coconut to use the pure-Python [`pyparsing`](https://github.com/pyparsing/pyparsing) module instead of the faster [`cPyparsing`](https://github.com/evhub/cpyparsing) module. If you are still getting errors, you may want to try [using conda](#using-conda) instead.

If `pip install coconut` works, but you cannot access the `coconut` command, be sure that Coconut's installation location is in your `PATH` environment variable. On UNIX, that is `/usr/local/bin` (without `--user`) or `${HOME}/.local/bin/` (with `--user`).

#### Using Conda

If you prefer to use [`conda`](https://conda.io/docs/) instead of `pip` to manage your Python packages, you can also install Coconut using `conda`. Just [install `conda`](https://conda.io/miniconda.html), open up a command-line prompt, and enter
```
conda config --add channels conda-forge
conda install coconut
```
which will properly create and build a `conda` recipe out of [Coconut's `conda-forge` feedstock](https://github.com/conda-forge/coconut-feedstock).

_Note: Coconut's `conda` recipe uses `pyparsing` rather than `cPyparsing`, which may lead to degraded performance relative to installing Coconut via `pip`._

#### Using Homebrew

If you prefer to use [Homebrew](https://brew.sh/), you can also install Coconut using `brew`:
```
brew install coconut
```

_Note: Coconut's Homebrew formula may not always be up-to-date with the latest version of Coconut._

#### Optional Dependencies

Coconut also has optional dependencies, which can be installed by entering
```
pip install coconut[name_of_optional_dependency]
```
or, to install multiple optional dependencies,
```
pip install coconut[opt_dep_1,opt_dep_2]
```

The full list of optional dependencies is:

- `all`: alias for `jupyter,watch,mypy,backports,xonsh` (this is the recommended way to install a feature-complete version of Coconut).
- `jupyter`/`ipython`: enables use of the `--jupyter` / `--ipython` flag.
- `watch`: enables use of the `--watch` flag.
- `mypy`: enables use of the `--mypy` flag.
- `backports`: installs libraries that backport newer Python features to older versions, which Coconut will automatically use instead of the standard library if the standard library is not available. Specifically:
  - Installs [`dataclasses`](https://pypi.org/project/dataclasses/) to backport [`dataclasses`](https://docs.python.org/3/library/dataclasses.html).
  - Installs [`typing`](https://pypi.org/project/typing/) to backport [`typing`](https://docs.python.org/3/library/typing.html) ([`typing_extensions`](https://pypi.org/project/typing-extensions/) is always installed for backporting individual `typing` objects).
  - Installs [`aenum`](https://pypi.org/project/aenum) to backport [`enum`](https://docs.python.org/3/library/enum.html).
  - Installs [`async_generator`](https://github.com/python-trio/async_generator) to backport [`async` generators](https://peps.python.org/pep-0525/) and [`asynccontextmanager`](https://docs.python.org/3/library/contextlib.html#contextlib.asynccontextmanager).
  - Installs [`trollius`](https://pypi.python.org/pypi/trollius) to backport [`async`/`await`](https://docs.python.org/3/library/asyncio-task.html) and [`asyncio`](https://docs.python.org/3/library/asyncio.html).
- `xonsh`: enables use of Coconut's [`xonsh` support](#xonsh-support).
- `kernel`: lightweight subset of `jupyter` that only includes the dependencies that are strictly necessary for Coconut's [Jupyter kernel](#kernel).
- `tests`: everything necessary to test the Coconut language itself.
- `docs`: everything necessary to build Coconut's documentation.
- `dev`: everything necessary to develop on the Coconut language itself, including all of the dependencies above.

#### Develop Version

Alternatively, if you want to test out Coconut's latest and greatest, enter
```
pip install coconut-develop
```
which will install the most recent working version from Coconut's [`develop` branch](https://github.com/evhub/coconut/tree/develop). Optional dependency installation is supported in the same manner as above. For more information on the current development build, check out the [development version of this documentation](http://coconut.readthedocs.io/en/develop/DOCS.html). Be warned: `coconut-develop` is likely to be unstable—if you find a bug, please report it by [creating a new issue](https://github.com/evhub/coconut/issues/new).

_Note: if you have an existing release version of `coconut` installed, you'll need to `pip uninstall coconut` before installing `coconut-develop`._

## Compilation

```{contents}
---
local:
depth: 1
---
```

#### Usage

```
coconut [-h] [--and source [dest ...]] [-v] [-t version] [-i] [-p] [-a] [-l] [-k] [-w]
        [-r] [-n] [-d] [-q] [-s] [--no-tco] [--no-wrap-types] [-c code] [-j processes]
        [-f] [--minify] [--jupyter ...] [--mypy ...] [--argv ...] [--tutorial]
        [--docs] [--style name] [--history-file path] [--vi-mode]
        [--recursion-limit limit] [--stack-size kbs] [--site-install]
        [--site-uninstall] [--verbose] [--trace] [--profile]
        [source] [dest]
```

##### Positional Arguments

```
source              path to the Coconut file/folder to compile
dest                destination directory for compiled files (defaults to
                    the source directory)
```

##### Optional Arguments

```
-h, --help            show this help message and exit
--and source [dest ...]
                      add an additional source/dest pair to compile (dest is optional)
-v, -V, --version     print Coconut and Python version information
-t version, --target version
                      specify target Python version (defaults to universal)
-i, --interact        force the interpreter to start (otherwise starts if no other command
                      is given) (implies --run)
-p, --package         compile source as part of a package (defaults to only if source is a
                      directory)
-a, --standalone, --stand-alone
                      compile source as standalone files (defaults to only if source is a
                      single file)
-l, --line-numbers, --linenumbers
                      force enable line number comments (--line-numbers are enabled by
                      default unless --minify is passed)
--no-line-numbers, --nolinenumbers
                      disable line number comments (opposite of --line-numbers)
-k, --keep-lines, --keeplines
                      include source code in comments for ease of debugging
-w, --watch           watch a directory and recompile on changes
-r, --run             execute compiled Python
-n, --no-write, --nowrite
                      disable writing compiled Python
-d, --display         print compiled Python
-q, --quiet           suppress all informational output (combine with --display to write
                      runnable code to stdout)
-s, --strict          enforce code cleanliness standards
--no-tco, --notco     disable tail call optimization
--no-wrap-types, --nowraptypes
                      disable wrapping type annotations in strings and turn off 'from
                      __future__ import annotations' behavior
-c code, --code code  run Coconut passed in as a string (can also be piped into stdin)
-j processes, --jobs processes
                      number of additional processes to use (defaults to 'sys') (0 is no
                      additional processes; 'sys' uses machine default)
-f, --force           force re-compilation even when source code and compilation parameters
                      haven't changed
--minify              reduce size of compiled Python
--jupyter ..., --ipython ...
                      run Jupyter/IPython with Coconut as the kernel (remaining args passed
                      to Jupyter)
--mypy ...            run MyPy on compiled Python (remaining args passed to MyPy) (implies
                      --package --line-numbers)
--argv ..., --args ...
                      set sys.argv to source plus remaining args for use in the Coconut
                      script being run
--tutorial            open Coconut's tutorial in the default web browser
--docs, --documentation
                      open Coconut's documentation in the default web browser
--style name          set Pygments syntax highlighting style (or 'list' to list styles)
                      (defaults to COCONUT_STYLE environment variable if it exists,
                      otherwise 'default')
--history-file path   set history file (or '' for no file) (can be modified by setting
                      COCONUT_HOME environment variable)
--vi-mode, --vimode   enable vi mode in the interpreter (currently set to False) (can be
                      modified by setting COCONUT_VI_MODE environment variable)
--recursion-limit limit, --recursionlimit limit
                      set maximum recursion depth in compiler (defaults to 1920) (when
                      increasing --recursion-limit, you may also need to increase --stack-
                      size; setting them to approximately equal values is recommended)
--stack-size kbs, --stacksize kbs
                      run the compiler in a separate thread with the given stack size in
                      kilobytes
--site-install, --siteinstall
                      set up coconut.api to be imported on Python start
--site-uninstall, --siteuninstall
                      revert the effects of --site-install
--verbose             print verbose debug output
--trace               print verbose parsing data (only available in coconut-develop)
--profile             collect and print timing info (only available in coconut-develop)
```

#### Coconut Scripts

To run a Coconut file as a script, Coconut provides the command
```
coconut-run <source> <args>
```
as an alias for
```
coconut --quiet --target sys --keep-lines --run <source> --argv <args>
```
which will quietly compile and run `<source>`, passing any additional arguments to the script, mimicking how the `python` command works.

`coconut-run` can be used in a Unix shebang line to create a Coconut script by adding the following line to the start of your script:
```bash
#!/usr/bin/env coconut-run
```

To pass additional compilation arguments to `coconut-run` (e.g. `--no-tco`), put them before the `<source>` file.

`coconut-run` will always enable [automatic compilation](#automatic-compilation), such that Coconut source files can be directly imported from any Coconut files run via `coconut-run`. Additionally, compilation parameters (e.g. `--no-tco`) used in `coconut-run` will be passed along and used for any auto compilation.

On Python 3.4+, `coconut-run` will use a `__coconut_cache__` directory to cache the compiled Python. Note that `__coconut_cache__` will always be removed from `__file__`.

#### Naming Source Files

Coconut source files should, so the compiler can recognize them, use the extension `.coco` (preferred), `.coc`, or `.coconut`.

When Coconut compiles a `.coco` file, it will compile to another file with the same name, except with `.py` instead of `.coco`, which will hold the compiled code.

If an extension other than `.py` is desired for the compiled files, then that extension can be put before `.coco` in the source file name, and it will be used instead of `.py` for the compiled files. For example, `name.coco` will compile to `name.py`, whereas `name.abc.coco` will compile to `name.abc`.

#### Compilation Modes

Files compiled by the `coconut` command-line utility will vary based on compilation parameters. If an entire directory of files is compiled (which the compiler will search recursively for any folders containing `.coco`, `.coc`, or `.coconut` files), a `__coconut__.py` file will be created to house necessary functions (package mode), whereas if only a single file is compiled, that information will be stored within a header inside the file (standalone mode). Standalone mode is better for single files because it gets rid of the overhead involved in importing `__coconut__.py`, but package mode is better for large packages because it gets rid of the need to run the same Coconut header code again in every file, since it can just be imported from `__coconut__.py`.

By default, if the `source` argument to the command-line utility is a file, it will perform standalone compilation on it, whereas if it is a directory, it will recursively search for all `.coco` files and perform package compilation on them. Thus, in most cases, the mode chosen by Coconut automatically will be the right one. But if it is very important that no additional files like `__coconut__.py` be created, for example, then the command-line utility can also be forced to use a specific mode with the `--package` (`-p`) and `--standalone` (`-a`) flags.

#### Compatible Python Versions

While Coconut syntax is based off of the latest Python 3, Coconut code compiled in universal mode (the default `--target`)—and the Coconut compiler itself—should run on any Python version `>= 2.6` on the `2.x` branch or `>= 3.2` on the `3.x` branch (and on either [CPython](https://www.python.org/) or [PyPy](http://pypy.org/)).

To make Coconut built-ins universal across Python versions, Coconut makes available on any Python version built-ins that only exist in later versions, including **automatically overwriting Python 2 built-ins with their Python 3 counterparts.** Additionally, Coconut also [overwrites some Python 3 built-ins for optimization and enhancement purposes](#enhanced-built-ins). If access to the original Python versions of any overwritten built-ins is desired, the old built-ins can be retrieved by prefixing them with `py_`. Specifically, the overwritten built-ins are:

- `py_chr`
- `py_dict`
- `py_hex`
- `py_input`
- `py_int`
- `py_map`
- `py_object`
- `py_oct`
- `py_open`
- `py_print`
- `py_range`
- `py_str`
- `py_super`
- `py_zip`
- `py_filter`
- `py_reversed`
- `py_enumerate`
- `py_raw_input`
- `py_xrange`
- `py_repr`
- `py_breakpoint`

_Note: Coconut's `repr` can be somewhat tricky, as it will attempt to remove the `u` before reprs of unicode strings on Python 2, but will not always be able to do so if the unicode string is nested._

For standard library compatibility, **Coconut automatically maps imports under Python 3 names to imports under Python 2 names**. Thus, Coconut will automatically take care of any standard library modules that were renamed from Python 2 to Python 3 if just the Python 3 name is used. For modules or packages that only exist in Python 3, however, Coconut has no way of maintaining compatibility.

Finally, while Coconut will try to compile Python-3-specific syntax to its universal equivalent, the following constructs have no equivalent in Python 2, and require the specification of a target of at least `3` to be used:

- the `nonlocal` keyword,
- keyword-only function parameters (use [pattern-matching function definition](#pattern-matching-functions) for universal code),
- `async` and `await` statements (requires a specific target; Coconut will attempt different backports based on the targeted version),
- `:=` assignment expressions (requires `--target 3.8`),
- positional-only function parameters (use [pattern-matching function definition](#pattern-matching-functions) for universal code) (requires `--target 3.8`),
- `a[x, *y]` variadic generic syntax (use [type parameter syntax](#type-parameter-syntax) for universal code) (requires `--target 3.11`), and
- `except*` multi-except statements (requires `--target 3.11`).

_Note: Coconut also universalizes many magic methods, including making `__bool__` and [`__set_name__`](https://docs.python.org/3/reference/datamodel.html#object.__set_name__) work on any Python version._

#### Allowable Targets

If the version of Python that the compiled code will be running on is known ahead of time, a target should be specified with `--target`. The given target will only affect the compiled code and whether or not the Python-3-specific syntax detailed above is allowed. Where Python syntax differs across versions, Coconut syntax will always follow the latest Python 3 across all targets. The supported targets are:

- `universal`, `univ` (the default): will work on _any_ of the below
- `2`, `2.6`: will work on any Python `>= 2.6` but `< 3`
- `2.7`: will work on any Python `>= 2.7` but `< 3`
- `3`, `3.2`: will work on any Python `>= 3.2`
- `3.3`: will work on any Python `>= 3.3`
- `3.4`: will work on any Python `>= 3.4`
- `3.5`: will work on any Python `>= 3.5`
- `3.6`: will work on any Python `>= 3.6`
- `3.7`: will work on any Python `>= 3.7`
- `3.8`: will work on any Python `>= 3.8`
- `3.9`: will work on any Python `>= 3.9`
- `3.10`: will work on any Python `>= 3.10`
- `3.11`: will work on any Python `>= 3.11`
- `3.12`: will work on any Python `>= 3.12`
- `3.13`: will work on any Python `>= 3.13`
- `sys`: chooses the target corresponding to the current Python version
- `psf`: will work on any Python not considered [end-of-life](https://devguide.python.org/versions/) by the PSF (Python Software Foundation)

_Note: Periods are optional in target specifications, such that the target `27` is equivalent to the target `2.7`._

#### `strict` Mode

If the `--strict` (`-s` for short) flag is enabled, Coconut will perform additional checks on the code being compiled. It is recommended that you use the `--strict` flag if you are starting a new Coconut project, as it will help you write cleaner code. Specifically, the extra checks done by `--strict` are:

- disabling deprecated features (making them entirely unavailable to code compiled with `--strict`),
- errors instead of warnings on unused imports (unless they have a `# NOQA` or `# noqa` comment),
- errors instead of warnings when overwriting built-ins (unless a backslash is used to escape the built-in name),
- warning on missing `__init__.coco` files when compiling in `--package` mode,
- throwing errors on various style problems (see list below).

The style issues which will cause `--strict` to throw an error are:

- mixing of tabs and spaces
- use of `from __future__` imports (Coconut does these automatically)
- inheriting from `object` in classes (Coconut does this automatically)
- semicolons at end of lines
- use of `u` to denote Unicode strings (all Coconut strings are Unicode strings)
- `f`-strings with no format expressions in them
- commas after [statement lambdas](#statement-lambdas) (not recommended as it can be unclear whether the comma is inside or outside the lambda)
- missing new line at end of file
- trailing whitespace at end of lines
- use of the Python-style `lambda` statement (use [Coconut's lambda syntax](#lambdas) instead)
- use of backslash continuation (use [parenthetical continuation](#enhanced-parenthetical-continuation) instead)
- Python-3.10/PEP-634-style dotted names in pattern-matching (Coconut style is to preface these with `==`)
- use of `:` instead of `<:` to specify upper bounds in [Coconut's type parameter syntax](#type-parameter-syntax)

Note that many of the above style issues will still show a warning if `--strict` is not present.

## Integrations

```{contents}
---
local:
depth: 2
---
```

#### Syntax Highlighting

Text editors with support for Coconut syntax highlighting are:

- **VSCode**: Install [Coconut (Official)](https://marketplace.visualstudio.com/items?itemName=evhub.coconut) (for **VSCodium**, install from Open VSX [here](https://open-vsx.org/extension/evhub/coconut) instead).
- **SublimeText**: See SublimeText section below.
- **Spyder** (or any other editor that supports **Pygments**): See Pygments section below.
- **Vim**: See [`coconut.vim`](https://github.com/manicmaniac/coconut.vim).
- **Emacs**: See [`emacs-coconut`](https://codeberg.org/kobarity/emacs-coconut)/[`emacs-ob-coconut`](https://codeberg.org/kobarity/emacs-ob-coconut).
- **Atom**: See [`language-coconut`](https://github.com/enilsen16/language-coconut).

Alternatively, if none of the above work for you, you can just treat Coconut as Python. Simply set up your editor so it interprets all `.coco` files as Python and that should highlight most of your code well enough (e.g. for IntelliJ IDEA see [registering file types](https://www.jetbrains.com/help/idea/creating-and-registering-file-types.html)).

##### SublimeText

Coconut syntax highlighting for SublimeText requires that [Package Control](https://packagecontrol.io/installation), the standard package manager for SublimeText, be installed. Once that is done, simply:

1. open the SublimeText command palette by pressing `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac),
2. type and enter `Package Control: Install Package`, and
3. finally type and enter `Coconut`.

To make sure everything is working properly, open a `.coco` file, and make sure `Coconut` appears in the bottom right-hand corner. If something else appears, like `Plain Text`, click on it, select `Open all with current extension as...` at the top of the resulting menu, and then select `Coconut`.

_Note: Coconut syntax highlighting for SublimeText is provided by the [sublime-coconut](https://github.com/evhub/sublime-coconut) package._

##### Pygments

The same `pip install coconut` command that installs the Coconut command-line utility will also install the `coconut` Pygments lexer. How to use this lexer depends on the Pygments-enabled application being used, but in general simply use the `.coco` file extension (should be all you need to do for Spyder) and/or enter `coconut` as the language being highlighted and Pygments should be able to figure it out.

For example, this documentation is generated with [Sphinx](http://www.sphinx-doc.org/en/stable/), with the syntax highlighting you see created by adding the line
```coconut_python
highlight_language = "coconut"
```
to Coconut's `conf.py`.

#### IPython/Jupyter Support

If you use [IPython](http://ipython.org/) (the Python kernel for the [Jupyter](http://jupyter.org/) framework) notebooks or console, Coconut can be used as a Jupyter kernel or IPython extension.

##### Kernel

If Coconut is used as a kernel, all code in the console or notebook will be sent directly to Coconut instead of Python to be evaluated. Otherwise, the Coconut kernel behaves exactly like the IPython kernel, including support for `%magic` commands.

Simply installing Coconut should add a `Coconut` kernel to your Jupyter/IPython notebooks. If you are having issues accessing the Coconut kernel, however, the special command `coconut --jupyter install` will re-install the `Coconut` kernel to ensure it is using the current Python as well as add the additional kernels `Coconut (Default Python)`, `Coconut (Default Python 2)`, and `Coconut (Default Python 3)` which will use, respectively, the Python accessible as `python`, `python2`, and `python3` (these kernels are accessible in the console as `coconut_py`, `coconut_py2`, and `coconut_py3`). Coconut also supports `coconut --jupyter install --user` for user installation. Furthermore, the Coconut kernel fully supports [`nb_conda_kernels`](https://github.com/Anaconda-Platform/nb_conda_kernels) to enable accessing the Coconut kernel in one Conda environment from another Conda environment.

The Coconut kernel will always compile using the parameters: `--target sys --line-numbers --keep-lines --no-wrap-types`.

Coconut also provides the following api commands:

- `coconut --jupyter notebook` will ensure that the Coconut kernel is available and launch a Jupyter/IPython notebook.
- `coconut --jupyter console` will launch a Jupyter/IPython console using the Coconut kernel.
- `coconut --jupyter lab` will ensure that the Coconut kernel is available and launch [JupyterLab](https://github.com/jupyterlab/jupyterlab).

Additionally, [Jupytext](https://github.com/mwouts/jupytext) contains special support for the Coconut kernel and Coconut contains special support for [Papermill](https://papermill.readthedocs.io/en/latest/).

##### Extension

If Coconut is used as an extension, a special magic command will send snippets of code to be evaluated using Coconut instead of IPython, but IPython will still be used as the default.

The line magic `%load_ext coconut` will load Coconut as an extension, providing the `%coconut` and `%%coconut` magics and adding Coconut built-ins. The `%coconut` line magic will run a line of Coconut with default parameters, and the `%%coconut` block magic will take command-line arguments on the first line, and run any Coconut code provided in the rest of the cell with those parameters.

_Note: Unlike the normal Coconut command-line, `%%coconut` defaults to the `sys` target rather than the `universal` target._

#### Type Checking

##### MyPy Integration

Coconut has the ability to integrate with [MyPy](http://mypy-lang.org/) to provide optional static type_checking, including for all Coconut built-ins. Simply pass `--mypy` to `coconut` to enable MyPy integration, though be careful to pass it only as the last argument, since all arguments after `--mypy` are passed to `mypy`, not Coconut.

You can also run `mypy`—or any other static type checker—directly on the compiled Coconut. If the static type checker is unable to find the necessary stub files, however, then you may need to:

1. run `coconut --mypy install` and
2. tell your static type checker of choice to look in `~/.coconut_stubs` for stub files (for `mypy`, this is done by adding it to your [`MYPYPATH`](https://mypy.readthedocs.io/en/latest/running_mypy.html#how-imports-are-found)).

To distribute your code with checkable type annotations, you'll need to include `coconut` as a dependency (though a `--no-deps` install should be fine), as installing it is necessary to make the requisite stub files available. You'll also probably want to include a [`py.typed`](https://peps.python.org/pep-0561/) file.

##### Syntax

To explicitly annotate your code with types to be checked, Coconut supports (on all Python versions):
* [Python 3 function type annotations](https://www.python.org/dev/peps/pep-0484/),
* [Python 3.6 variable type annotations](https://www.python.org/dev/peps/pep-0526/),
* [Python 3.12 type parameter syntax](#type-parameter-syntax) for easily adding type parameters to classes, functions, [`data` types](#data), and type aliases,
* Coconut's own [enhanced type annotation syntax](#enhanced-type-annotation), and
* Coconut's [protocol intersection operator](#protocol-intersection).

By default, all type annotations are compiled to Python-2-compatible type comments, which means they should all work on any Python version.

Sometimes, MyPy will not know how to handle certain Coconut constructs, such as `addpattern`. For the `addpattern` case, it is recommended to pass `--allow-redefinition` to MyPy (i.e. run `coconut <args> --mypy --allow-redefinition`), though in some cases `--allow-redefinition` may not be sufficient. In that case, either hide the offending code using [`TYPE_CHECKING`](#type_checking) or put a `# type: ignore` comment on the Coconut line which is generating the line MyPy is complaining about and the comment will be added to every generated line.

##### Interpreter

Coconut even supports `--mypy` in the interpreter, which will intelligently scan each new line of code, in the context of previous lines, for newly-introduced MyPy errors. For example:
```coconut_pycon
>>> a: str = count()[0]
<string>:14: error: Incompatible types in assignment (expression has type "int", variable has type "str")
>>> reveal_type(a)
0
<string>:19: note: Revealed type is 'builtins.unicode'
```
_For more information on `reveal_type`, see [`reveal_type` and `reveal_locals`](#reveal-type-and-reveal-locals)._

#### `numpy` Integration

To allow for better use of [`numpy`](https://numpy.org/) objects in Coconut, all compiled Coconut code will do a number of special things to better integrate with `numpy` (if `numpy` is available to import when the code is run). Specifically:

- Coconut's [multidimensional array literal and array concatenation syntax](#multidimensional-array-literalconcatenation-syntax) supports `numpy` objects, including using fast `numpy` concatenation methods if given `numpy` arrays rather than Coconut's default much slower implementation built for Python lists of lists.
- Many of Coconut's built-ins include special `numpy` support, specifically:
  * [`fmap`](#fmap) will use [`numpy.vectorize`](https://numpy.org/doc/stable/reference/generated/numpy.vectorize.html) to map over `numpy` arrays.
  * [`multi_enumerate`](#multi_enumerate) allows for easily looping over all the multi-dimensional indices in a `numpy` array.
  * [`cartesian_product`](#cartesian_product) can compute the Cartesian product of given `numpy` arrays as a `numpy` array.
  * [`all_equal`](#all_equal) allows for easily checking if all the elements in a `numpy` array are the same.
- [`numpy.ndarray`](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html) is registered as a [`collections.abc.Sequence`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence), enabling it to be used in [sequence patterns](#semantics-specification).
- `numpy` objects are allowed seamlessly in Coconut's [implicit coefficient syntax](#implicit-function-application-and-coefficients), allowing the use of e.g. `A B**2` shorthand for `A * B**2` when `A` and `B` are `numpy` arrays (note: **not** `A @ B**2`).
- Coconut supports `@` for matrix multiplication of `numpy` arrays on all Python versions, as well as supplying the `(@)` [operator function](#operator-functions).

Additionally, Coconut provides the exact same support for [`pandas`](https://pandas.pydata.org/), [`pytorch`](https://pytorch.org/), and [`jax.numpy`](https://jax.readthedocs.io/en/latest/jax.numpy.html), including using `pandas`/`jax`-specific methods over `numpy` methods when given `pandas`/`jax` objects.

#### `xonsh` Support

Coconut integrates with [`xonsh`](https://xon.sh/) to allow the use of Coconut code directly from your command line. To use Coconut in `xonsh`, simply `pip install coconut` should be all you need to enable the use of Coconut syntax in the `xonsh` shell. In some circumstances, in particular depending on the installed `xonsh` version, adding `xontrib load coconut` to your [`xonshrc`](https://xon.sh/xonshrc.html) file might be necessary.

For an example of using Coconut from `xonsh`:
```
user@computer ~ $ xontrib load coconut
user@computer ~ $ cd ./files
user@computer ~ $ $(ls -la) |> .splitlines() |> len
30
```

Compilation always uses the same parameters as in the [Coconut Jupyter kernel](#kernel).

Note that the way that Coconut integrates with `xonsh`, `@(<code>)` syntax and the `execx` command will only work with Python code, not Coconut code. Additionally, Coconut will only compile individual commands—Coconut will not touch the `.xonshrc` or any other `.xsh` files.

## Operators

```{contents}
---
local:
depth: 1
---
```

### Precedence

In order of precedence, highest first, the operators supported in Coconut are:
```
====================== ==========================
Symbol(s)              Associativity
====================== ==========================
await x                n/a
**                     right (allows unary)
f x                    n/a
+, -, ~                unary
*, /, //, %, @         left
+, -                   left
<<, >>                 left
&                      left
&:                     left
^                      left
|                      left
::                     n/a (lazy)
..                     n/a
a `b` c,               left (captures lambda)
  all custom operators
??                     left (short-circuits)
..>, <.., ..*>, <*..,  n/a (captures lambda)
  ..**>, <**..
|>, <|, |*>, <*|,      left (captures lambda)
  |**>, <**|
==, !=, <, >,
  <=, >=,
  in, not in,
  is, is not           n/a
not                    unary
and                    left (short-circuits)
or                     left (short-circuits)
x if c else y,         ternary left (short-circuits)
  if c then x else y
=>                     right
====================== ==========================
```

For example, since addition has a higher precedence than piping, expressions of the form `x |> y + z` are equivalent to `x |> (y + z)`.

### Lambdas

Coconut provides the simple, clean `=>` operator as an alternative to Python's `lambda` statements. The syntax for the `=>` operator is `(parameters) => expression` (or `parameter => expression` for one-argument lambdas). The operator has the same precedence as the old statement, which means it will often be necessary to surround the lambda in parentheses, and is right-associative.

Additionally, Coconut also supports an implicit usage of the `=>` operator of the form `(=> expression)`, which is equivalent to `((_=None) => expression)`, which allows an implicit lambda to be used both when no arguments are required, and when one argument (assigned to `_`) is required.

_Note: If normal lambda syntax is insufficient, Coconut also supports an extended lambda syntax in the form of [statement lambdas](#statement-lambdas). Statement lambdas support full statements rather than just expressions and allow for the use of [pattern-matching function definition](#pattern-matching-functions)._

_Deprecated: `->` can be used as an alternative to `=>`, though `->`-based lambdas are disabled inside type annotations to avoid conflicting with Coconut's [enhanced type annotation syntax](#enhanced-type-annotation)._

##### Rationale

In Python, lambdas are ugly and bulky, requiring the entire word `lambda` to be written out every time one is constructed. This is fine if in-line functions are very rarely needed, but in functional programming in-line functions are an essential tool.

##### Python Docs

Lambda forms (lambda expressions) have the same syntactic position as expressions. They are a shorthand to create anonymous functions; the expression `(arguments) => expression` yields a function object. The unnamed object behaves like a function object defined with:
```coconut
def <lambda>(arguments):
    return expression
```
Note that functions created with lambda forms cannot contain statements or annotations.

##### Example

**Coconut:**
```coconut
dubsums = map((x, y) => 2*(x+y), range(0, 10), range(10, 20))
dubsums |> list |> print
```

**Python:**
```coconut_python
dubsums = map(lambda x, y: 2*(x+y), range(0, 10), range(10, 20))
print(list(dubsums))
```

#### Implicit Lambdas

Coconut also supports implicit lambdas, which allow a lambda to take either no arguments or a single argument. Implicit lambdas are formed with the usual Coconut lambda operator `=>`, in the form `(=> expression)`. This is equivalent to `((_=None) => expression)`. When an argument is passed to an implicit lambda, it will be assigned to `_`, replacing the default value `None`.

Below are two examples of implicit lambdas. The first uses the implicit argument `_`, while the second does not.

**Single Argument Example:**
```coconut
square = (=> _**2)
```

**No-Argument Example:**
```coconut
import random

get_random_number = (=> random.random())
```

_Note: Nesting implicit lambdas can lead to problems with the scope of the `_` parameter to each lambda. It is recommended that nesting implicit lambdas be avoided._

### Partial Application

Coconut uses a `$` sign right after a function's name but before the open parenthesis used to call the function to denote partial application.

Coconut's partial application also supports the use of a `?` to skip partially applying an argument, deferring filling in that argument until the partially-applied function is called. This is useful if you want to partially apply arguments that aren't first in the argument order.

Additionally, `?` can even be used as the value of keyword arguments to convert them into positional arguments. For example, `f$(x=?)` is effectively equivalent to
```coconut_python
def new_f(x, *args, **kwargs):
    kwargs["x"] = x
    return f(*args, **kwargs)
```

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

### Pipes

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
(<?|)   => None-aware pipe backward
(<*?|)  => None-aware multi-arg pipe backward
(<**?|) => None-aware keyword arg pipe backward
```

The None-aware pipe operators here are equivalent to a [monadic bind](https://en.wikipedia.org/wiki/Monad_(functional_programming)) treating the object as a `Maybe` monad composed of either `None` or the given object. Thus, `x |?> f` is equivalent to `None if x is None else f(x)`. Note that only the object being piped, not the function being piped into, may be `None` for `None`-aware pipes.

For working with `async` functions in pipes, all non-starred pipes support piping into `await` to await the awaitable piped into them, such that `x |> await` is equivalent to `await x`.

Additionally, all pipe operators support a lambda as the last argument, despite lambdas having a lower precedence. Thus, `a |> x => b |> c` is equivalent to `a |> (x => b |> c)`, not `a |> (x => b) |> c`.

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

##### Examples

**Coconut:**
```coconut
def sq(x) = x**2
(1, 2) |*> (+) |> sq |> print
```

```coconut
async def do_stuff(some_data) = (
    some_data
    |> async_func
    |> await
    |> post_proc
)
```

**Python:**
```coconut_python
import operator
def sq(x): return x**2
print(sq(operator.add(1, 2)))
```

```coconut_python
async def do_stuff(some_data):
    return post_proc(await async_func(some_data))
```

### Function Composition

Coconut has three basic function composition operators: `..`, `..>`, and `<..`. Both `..` and `<..` use math-style "backwards" function composition, where the first function is called last, while `..>` uses "forwards" function composition, where the first function is called first. Forwards and backwards function composition pipes cannot be used together in the same expression (unlike normal pipes) and have precedence in-between `None`-coalescing and normal pipes.

The `..>` and `<..` function composition pipe operators also have multi-arg, keyword, and None variants as with [normal pipes](#pipes). The full list of function composition pipe operators is:
```
..>    => forwards function composition pipe
<..    => backwards function composition pipe
..*>   => forwards multi-arg function composition pipe
<*..   => backwards multi-arg function composition pipe
..**>  => forwards keyword arg function composition pipe
<**..  => backwards keyword arg function composition pipe
..?>   => forwards None-aware function composition pipe
<?..   => backwards None-aware function composition pipe
..?*>  => forwards None-aware multi-arg function composition pipe
<*?..  => backwards None-aware multi-arg function composition pipe
..?**> => forwards None-aware keyword arg function composition pipe
<**?.. => backwards None-aware keyword arg function composition pipe
```

Note that `None`-aware function composition pipes don't allow either function to be `None`—rather, they allow the return of the first evaluated function to be `None`, in which case `None` is returned immediately rather than calling the next function.

The `..` operator has lower precedence than `::` but higher precedence than infix functions while the `..>` pipe operators have a precedence directly higher than normal pipes.

All function composition operators also have in-place versions (e.g. `..=`).

Since all forms of function composition always call the first function in the composition (`f` in `f ..> g` and `g` in `f <.. g`) with exactly the arguments passed into the composition, all forms of function composition will preserve all metadata attached to the first function in the composition, including the function's [signature](https://docs.python.org/3/library/inspect.html#inspect.signature) and any of that function's attributes.

_Note: for composing `async` functions, see [`and_then` and `and_then_await`](#and_then-and-and_then_await)._

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

### Iterator Slicing

Coconut uses a `$` sign right after an iterator before a slice to perform iterator slicing, as in `it$[:5]`. Coconut's iterator slicing works much the same as Python's sequence slicing, and looks much the same as Coconut's partial application, but with brackets instead of parentheses.

Iterator slicing works just like sequence slicing, including support for negative indices and slices, and support for `slice` objects in the same way as can be done with normal slicing. Iterator slicing makes no guarantee, however, that the original iterator passed to it be preserved (to preserve the iterator, use Coconut's [`reiterable`](#reiterable) built-in).

Coconut's iterator slicing is very similar to Python's `itertools.islice`, but unlike `itertools.islice`, Coconut's iterator slicing supports negative indices, and will preferentially call an object's `__iter_getitem__` (always used if available) or `__getitem__` (only used if the object is a `collections.abc.Sequence`). Coconut's iterator slicing is also optimized to work well with all of Coconut's built-in objects, only computing the elements of each that are actually necessary to extract the desired slice.

##### Example

**Coconut:**
```coconut
map(x => x*2, range(10**100))$[-1] |> print
```

**Python:**
_Can't be done without a complicated iterator slicing function and inspection of custom objects. The necessary definitions in Python can be found in the Coconut header._

### Iterator Chaining

Coconut uses the `::` operator for iterator chaining. Coconut's iterator chaining is done lazily, in that the arguments are not evaluated until they are needed. It has a precedence in-between bitwise or and infix calls. Chains are reiterable (can be iterated over multiple times and get the same result) only when the iterators passed in are reiterable. The in-place operator is `::=`.

_Note that [lazy lists](#lazy-lists) and [flatten](#flatten) are used under the hood to implement chaining such that `a :: b` is equivalent to `flatten((|a, b|))`._

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

### Infix Functions

Coconut allows for infix function calling, where an expression that evaluates to a function is surrounded by backticks and then can have arguments placed in front of or behind it. Infix calling has a precedence in-between chaining and `None`-coalescing, and is left-associative.

The allowable notations for infix calls are:
```coconut
x `f` y  =>  f(x, y)
`f` x    =>  f(x)
x `f`    =>  f(x)
`f`      =>  f()
```
Additionally, infix notation supports a lambda as the last argument, despite lambdas having a lower precedence. Thus, ``a `func` b => c`` is equivalent to `func(a, b => c)`.

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

### Custom Operators

Coconut allows you to declare your own custom operators with the syntax
```
operator <op>
```
where `<op>` is whatever sequence of Unicode characters you want to use as a custom operator. The `operator` statement must appear at the top level and only affects code that comes after it.

Once declared, you can use your custom operator anywhere where you would be able to use an [infix function](#infix-functions) as well as refer to the actual operator itself with the same `(<op>)` syntax as in other [operator functions](#operator-functions). Since custom operators work like infix functions, they always have the same precedence as infix functions and are always left-associative. Custom operators can be used as binary, unary, or none-ary operators, and both prefix and postfix notation for unary operators is supported.

Some example syntaxes for defining custom operators once declared:
```
def x <op> y: ...
def <op> x = ...
match def (x) <op> (y): ...
(<op>) = ...
from module import name as (<op>)
```

And some example syntaxes for using custom operators:
```
x <op> y
x <op> y <op> z
<op> x
x <op>
x = (<op>)
f(<op>)
(x <op> .)
(. <op> y)
match x <op> in ...: ...
match x <op> y in ...: ...
```

Additionally, to import custom operators from other modules, Coconut supports the special syntax:
```
from <module> import operator <op>
```

Custom operators will often need to be surrounded by whitespace (or parentheses when used as an operator function) to be parsed correctly.

If a custom operator that is also a valid name is desired, you can use a backslash before the name to get back the name instead using Coconut's [keyword/variable disambiguation syntax](#handling-keywordvariable-name-overlap).

_Note: redefining existing Coconut operators using custom operator definition syntax is forbidden, including Coconut's built-in [Unicode operator alternatives](#unicode-alternatives)._

##### Examples

**Coconut:**
```coconut
operator %%
(%%) = math.remainder
10 %% 3 |> print

operator !!
(!!) = bool
!! 0 |> print

operator log10
from math import \log10 as (log10)
100 log10 |> print
```

**Python:**
```coconut_python
print(math.remainder(10, 3))

print(bool(0))

print(math.log10(100))
```

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

Coconut also supports None-aware [pipe operators](#pipes) and [function composition pipes](#function-composition).

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

### Protocol Intersection

Coconut uses the `&:` operator to indicate protocol intersection. That is, for two [`typing.Protocol`s](https://docs.python.org/3/library/typing.html#typing.Protocol) `Protocol1` and `Protocol1`, `Protocol1 &: Protocol2` is equivalent to a `Protocol` that combines the requirements of both `Protocol1` and `Protocol2`.

The recommended way to use Coconut's protocol intersection operator is in combination with Coconut's [operator `Protocol`s](#supported-protocols). Note, however, that while `&:` will work anywhere, operator `Protocol`s will only work inside type annotations (which means, for example, you'll need to do `type HasAdd = (+)` instead of just `HasAdd = (+)`).

See Coconut's [enhanced type annotation](#enhanced-type-annotation) for more information on how Coconut handles type annotations more generally.

##### Example

**Coconut:**
```coconut
from typing import Protocol

class X(Protocol):
    x: str

class Y(Protocol):
    y: str

def foo(xy: X &: Y) -> None:
    print(xy.x, xy.y)

type CanAddAndSub = (+) &: (-)
```

**Python:**
```coconut_python
from typing import Protocol, TypeVar, Generic

class X(Protocol):
    x: str

class Y(Protocol):
    y: str

class XY(X, Y, Protocol):
    pass

def foo(xy: XY) -> None:
    print(xy.x, xy.y)

T = TypeVar("T", infer_variance=True)
U = TypeVar("U", infer_variance=True)
V = TypeVar("V", infer_variance=True)

class CanAddAndSub(Protocol, Generic[T, U, V]):
    def __add__(self: T, other: U) -> V:
        raise NotImplementedError
    def __sub__(self: T, other: U) -> V:
        raise NotImplementedError
    def __neg__(self: T) -> V:
        raise NotImplementedError
```

### Unicode Alternatives

Coconut supports Unicode alternatives to many different operator symbols. The Unicode alternatives are relatively straightforward, and chosen to reflect the look and/or meaning of the original symbol.

_Note: these are only the default, built-in unicode operators. Coconut supports [custom operator definition](#custom-operators) to define your own._

##### Full List

```
⇒ (\u21d2)                 => "=>"
→ (\u2192)                  => "->"
× (\xd7)                    => "*" (only multiplication)
↑ (\u2191)                  => "**" (only exponentiation)
÷ (\xf7)                    => "/" (only division)
÷/ (\xf7/)                  => "//"
⁻ (\u207b)                  => "-" (only negation)
≠ (\u2260) or ¬= (\xac=)    => "!="
≤ (\u2264) or ⊆ (\u2286)    => "<="
≥ (\u2265) or ⊇ (\u2287)    => ">="
⊊ (\u228a)                  => "<"
⊋ (\u228b)                  => ">"
∩ (\u2229)                  => "&"
∪ (\u222a)                  => "|"
« (\xab)                    => "<<"
» (\xbb)                    => ">>"
… (\u2026)                  => "..."
λ (\u03bb)                  => "lambda"
↦ (\u21a6)                 => "|>"
↤ (\u21a4)                 => "<|"
*↦ (*\u21a6)               => "|*>"
↤* (\u21a4*)               => "<*|"
**↦ (**\u21a6)             => "|**>"
↤** (\u21a4**)             => "<**|"
?↦ (?\u21a6)               => "|?>"
↤? (?\u21a4)               => "<?|"
?*↦ (?*\u21a6)             => "|?*>"
↤*? (\u21a4*?)             => "<*?|"
?**↦ (?**\u21a6)           => "|?**>"
↤**? (\u21a4**?)           => "<**?|"
∘ (\u2218)                  => ".."
∘> (\u2218>)                => "..>"
<∘ (<\u2218)                => "<.."
∘*> (\u2218*>)              => "..*>"
<*∘ (<*\u2218)              => "<*.."
∘**> (\u2218**>)            => "..**>"
<**∘ (<**\u2218)            => "<**.."
∘?> (\u2218?>)              => "..?>"
<?∘ (<?\u2218)              => "<?.."
∘?*> (\u2218?*>)            => "..?*>"
<*?∘ (<*?\u2218)            => "<*?.."
∘?**> (\u2218?**>)          => "..?**>"
<**?∘ (<**?\u2218)          => "<**?.."
⏨ (\u23e8)                  => "e" (in scientific notation)
```

## Keywords

```{contents}
---
local:
depth: 1
---
```

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
where `<value>` is the item to match against, `<cond>` is an optional additional check, and `<body>` is simply code that is executed if the header above it succeeds. `<pattern>` follows its own, special syntax, defined roughly as below. In the syntax specification below, brackets denote optional syntax and parentheses followed by a `*` denote that the syntax may appear zero or more times.

```coconut
pattern ::= and_pattern ("or" and_pattern)*  # match any

and_pattern ::= as_pattern ("and" as_pattern)*  # match all

as_pattern ::= infix_pattern ("as" name)*  # explicit binding

infix_pattern ::= bar_or_pattern ("`" EXPR "`" [EXPR])*  # infix check

bar_or_pattern ::= pattern ("|" pattern)*  # match any

base_pattern ::= (
    "(" pattern ")"                  # parentheses
    | "None" | "True" | "False"      # constants
    | NUMBER                         # numbers
    | STRING                         # strings
    | ["as"] NAME                    # variable binding
    | "==" EXPR                      # equality check
    | "is" EXPR                      # identity check
    | DOTTED_NAME                    # implicit equality check (disabled in destructuring assignment)
    | NAME "(" patterns ")"          # classes or data types
    | "data" NAME "(" patterns ")"   # data types
    | "class" NAME "(" patterns ")"  # classes
    | "{" pattern_pairs              # dictionaries
        ["," "**" (NAME | "{}")] "}" #  (keys must be constants or equality checks)
    | ["s" | "f" | "m"] "{"
        pattern_consts
        ["," ("*_" | "*()")]
      "}"                            # sets
    | (EXPR) -> pattern              # view patterns
    | "(" patterns ")"               # sequences can be in tuple form
    | "[" patterns "]"               #  or in list form
    | "(|" patterns "|)"             # lazy lists
    | ("(" | "[")                    # star splits
        [patterns ","]
        "*" pattern
        ["," patterns]
        ["*" pattern
        ["," patterns]]
      (")" | "]")
    | [(                             # sequence splits
        "(" patterns ")"
        | "[" patterns "]"
      ) "+"] NAME ["+" (
        "(" patterns ")"                 # this match must be the same
        | "[" patterns "]"               #  construct as the first match
      )] ["+" NAME ["+" (
        "(" patterns ")"                 # and same here
        | "[" patterns "]"
      )]]
    | [(                             # iterable splits
        "(" patterns ")"
        | "[" patterns "]"
        | "(|" patterns "|)"
      ) "::"] NAME ["::" (
        "(" patterns ")"
        | "[" patterns "]"
        | "(|" patterns "|)"
      )] [ "::" NAME [
        "(" patterns ")"
        | "[" patterns "]"
        | "(|" patterns "|)"
      ]]
    | [STRING "+"] NAME              # complex string matching
        ["+" STRING]
        ["+" NAME ["+" STRING]]
)
```

##### Semantics Specification

`match` statements will take their pattern and attempt to "match" against it, performing the checks and deconstructions on the arguments as specified by the pattern. The different constructs that can be specified in a pattern, and their function, are:
- Variable Bindings:
  - Implicit Bindings (`<var>`): will match to anything, and will be bound to whatever they match to, with some exceptions:
    * If the same variable is used multiple times, a check will be performed that each use matches to the same value.
    * If the variable name `_` is used, nothing will be bound and everything will always match to it (`_` is Coconut's "wildcard").
  - Explicit Bindings (`<pattern> as <var>`): will bind `<var>` to `<pattern>`.
- Basic Checks:
  - Constants, Numbers, and Strings: will only match to the same constant, number, or string in the same position in the arguments.
  - Equality Checks (`==<expr>`): will check that whatever is in that position is `==` to the expression `<expr>`.
  - Identity Checks (`is <expr>`): will check that whatever is in that position `is` the expression `<expr>`.
- Arbitrary Function Patterns:
  - Infix Checks (`` <pattern> `<op>` <expr> ``): will check that the operator `<op>$(?, <expr>)` returns a truthy value when called on whatever is in that position, then matches `<pattern>`. For example, `` x `isinstance` int `` will check that whatever is in that position `isinstance$(?, int)` and bind it to `x`. If `<expr>` is not given, will simply check `<op>` directly rather than `<op>$(<expr>)`. Additionally, `` `<op>` `` can instead be a [custom operator](#custom-operators) (in that case, no backticks should be used).
  - View Patterns (`(<expression>) -> <pattern>`): calls `<expression>` on the item being matched and matches the result to `<pattern>`. The match fails if a [`MatchError`](#matcherror) is raised. `<expression>` may be unparenthesized only when it is a single atom.
- Class and Data Type Matching:
  - Classes or Data Types (`<name>(<args>)`): will match as a data type if given [a Coconut `data` type](#data) (or a tuple of Coconut data types) and a class otherwise.
  - Data Types (`data <name>(<args>)`): will check that whatever is in that position is of data type `<name>` and will match the attributes to `<args>`. Generally, `data <name>(<args>)` will match any data type that could have been constructed with `makedata(<name>, <args>)`. Includes support for positional arguments, named arguments, default arguments, and starred arguments. Also supports strict attributes by prepending a dot to the attribute name that raises `AttributError` if the attribute is not present rather than failing the match (e.g. `data MyData(.my_attr=<some_pattern>)`).
  - Classes (`class <name>(<args>)`): does [PEP-634-style class matching](https://www.python.org/dev/peps/pep-0634/#class-patterns). Also supports strict attribute matching as above.
- Mapping Destructuring:
  - Dicts (`{<key>: <value>, ...}`): will match any mapping (`collections.abc.Mapping`) with the given keys and values that match the value patterns. Keys must be constants or equality checks.
  - Dicts With Rest (`{<pairs>, **<rest>}`): will match a mapping (`collections.abc.Mapping`) containing all the `<pairs>`, and will put a `dict` of everything else into `<rest>`. If `<rest>` is `{}`, will enforce that the mapping is exactly the same length as `<pairs>`.
- Set Destructuring:
  - Sets (`s{<constants>, *_}`): will match a set (`collections.abc.Set`) that contains the given `<constants>`, though it may also contain other items. The `s` prefix and the `*_` are optional.
  - Fixed-length Sets (`s{<constants>, *()}`): will match a `set` (`collections.abc.Set`) that contains the given `<constants>`, and nothing else.
  - Frozensets (`f{<constants>}`): will match a `frozenset` (`frozenset`) that contains the given `<constants>`. May use either normal or fixed-length syntax.
  - Multisets (`m{<constants>}`): will match a [`multiset`](#multiset) (`collections.Counter`) that contains at least the given `<constants>`. May use either normal or fixed-length syntax.
- Sequence Destructuring:
  - Lists (`[<patterns>]`), Tuples (`(<patterns>)`): will only match a sequence (`collections.abc.Sequence`) of the same length, and will check the contents against `<patterns>` (Coconut automatically registers `numpy` arrays and `collections.deque` objects as sequences).
  - Lazy lists (`(|<patterns>|)`): same as list or tuple matching, but checks for an Iterable (`collections.abc.Iterable`) instead of a Sequence.
  - Head-Tail Splits (`<list/tuple> + <var>` or `(<patterns>, *<var>)`): will match the beginning of the sequence against the `<list/tuple>`/`<patterns>`, then bind the rest to `<var>`, and make it the type of the construct used.
  - Init-Last Splits (`<var> + <list/tuple>` or `(*<var>, <patterns>)`): exactly the same as head-tail splits, but on the end instead of the beginning of the sequence.
  - Head-Last Splits (`<list/tuple> + <var> + <list/tuple>` or `(<patterns>, *<var>, <patterns>)`): the combination of a head-tail and an init-last split.
  - Search Splits (`<var1> + <list/tuple> + <var2>` or `(*<var1>, <patterns>, *<var2>)`): searches for the first occurrence of the `<list/tuple>`/`<patterns>` in the sequence, then puts everything before into `<var1>` and everything after into `<var2>`.
  - Head-Last Search Splits (`<list/tuple> + <var> + <list/tuple> + <var> + <list/tuple>` or `(<patterns>, *<var>, <patterns>, *<var>, <patterns>)`): the combination of a head-tail split and a search split.
  - Iterable Splits (`<list/tuple/lazy list> :: <var> :: <list/tuple/lazy list> :: <var> :: <list/tuple/lazy list>`): same as other sequence destructuring, but works on any iterable (`collections.abc.Iterable`), including infinite iterators (note that if an iterator is matched against it will be modified unless it is [`reiterable`](#reiterable)).
  - Complex String Matching (`<string> + <var> + <string> + <var> + <string>`): string matching supports the same destructuring options as above.

_Note: Like [iterator slicing](#iterator-slicing), iterator and lazy list matching make no guarantee that the original iterator matched against be preserved (to preserve the iterator, use Coconut's [`reiterable`](#reiterable) built-in)._

When checking whether or not an object can be matched against in a particular fashion, Coconut makes use of Python's abstract base classes. Therefore, to ensure proper matching for a custom object, it's recommended to register it with the proper abstract base classes.

##### Examples

**Coconut:**
```coconut
def factorial(value):
    match 0 in value:
        return 1
    else: match n `isinstance` int in value if n > 0:  # Coconut allows nesting of statements on the same line
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

addpattern def depth(Tree(n)) = 1

addpattern def depth(Tree(l, r)) = 1 + max([depth(l), depth(r)])

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

addpattern def sieve((||)) = []
```
_Showcases how to match against iterators, namely that the empty iterator case (`(||)`) must come last, otherwise that case will exhaust the whole iterator before any other pattern has a chance to match against it._

```
def odd_primes(p=3) =
    (p,) :: filter(=> _ % p != 0, odd_primes(p + 2))

def primes() =
    (2,) :: odd_primes()

def twin_primes(_ :: [p, (.-2) -> p] :: ps) =
    [(p, p+2)] :: twin_primes([p + 2] :: ps)

addpattern def twin_primes() =  # type: ignore
    twin_primes(primes())

twin_primes()$[:5] |> list |> print
```
_Showcases the use of an iterable search pattern and a view pattern to construct an iterator of all twin primes._

**Python:**
_Can't be done without a long series of checks for each `match` statement. See the compiled code for the Python syntax._

### `case`

Coconut's `case` blocks serve as an extension of Coconut's `match` statement for performing multiple `match` statements against the same value, where only one of them should succeed. Unlike lone `match` statements, only one match statement inside of a `case` block will ever succeed, and thus more general matches should be put below more specific ones.

Coconut's `case` blocks are an extension of Python 3.10's [`case` blocks](https://www.python.org/dev/peps/pep-0634) to support additional pattern-matching constructs added by Coconut (and Coconut will ensure that they work on all Python versions, not just 3.10+).

Each pattern in a case block is checked until a match is found, and then the corresponding body is executed, and the case block terminated. The syntax for case blocks is
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
where `<pattern>` is any `match` pattern, `<value>` is the item to match against, `<cond>` is an optional additional check, and `<body>` is simply code that is executed if the header above it succeeds. Note the absence of an `in` in the `match` statements: that's because the `<value>` in `case <value>` is taking its place. If no `else` is present and no match succeeds, then the `case` statement is simply skipped over as with [`match` statements](#match) (though unlike [destructuring assignments](#destructuring-assignment)).

Additionally, `cases` can be used as the top-level keyword instead of `match`, and in such a `case` block `match` is allowed for each case rather than `case`. _Deprecated: Coconut also supports `case` instead of `cases` as the top-level keyword for backwards-compatibility purposes._

##### Examples

**Coconut:**
```coconut
def classify_sequence(value):
    out = ""        # unlike with normal matches, only one of the patterns
    match value:     #  will match, and out will only get appended to once
        case ():
            out += "empty"
        case (_,):
            out += "singleton"
        case (x,x):
            out += "duplicate pair of "+str(x)
        case (_,_):
            out += "pair"
        case _ is (tuple, list):
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
cases {"a": 1, "b": 2}:
    match {"a": a}:
        pass
    match _:
        assert False
assert a == 1
```
_Example of the `cases` keyword instead._

**Python:**
_Can't be done without a long series of checks for each `match` statement. See the compiled code for the Python syntax._

### `match for`

Coconut supports pattern-matching in for loops, where the pattern is matched against each item in the iterable. The syntax is
```coconut
[match] for <pattern> in <iterable>:
    <body>
```
which is equivalent to the [destructuring assignment](#destructuring-assignment)
```coconut
for elem in <iterable>:
    match <pattern> = elem
    <body>
```

Pattern-matching can also be used in `async for` loops, with both `async match for` and `match async for` allowed as explicit syntaxes.

##### Example

**Coconut:**
```
for {"user": uid, **_} in get_data():
    print(uid)
```

**Python:**
```
for user_data in get_data():
    uid = user_data["user"]
    print(uid)
```

### `data`

Coconut's `data` keyword is used to create immutable, algebraic data types, including built-in support for destructuring [pattern-matching](#match) and [`fmap`](#fmap).

The syntax for `data` blocks is a cross between the syntax for functions and the syntax for classes. The first line looks like a function definition, but the rest of the body looks like a class, usually containing method definitions. This is because while `data` blocks actually end up as classes in Python, Coconut automatically creates a special, immutable constructor based on the given arguments.

Coconut data statement syntax looks like:
```coconut
data <name>(<args>) [from <inherits>]:
    <body>
```
`<name>` is the name of the new data type, `<args>` are the arguments to its constructor as well as the names of its attributes, `<body>` contains the data type's methods, and `<inherits>` optionally contains any desired base classes.

Coconut allows data fields in `<args>` to have defaults and/or [type annotations](#enhanced-type-annotation) attached to them, and supports a starred parameter at the end to collect extra arguments. Additionally, Coconut allows type parameters to be specified in brackets after `<name>` using Coconut's [type parameter syntax](#type-parameter-syntax).

Writing constructors for `data` types must be done using the `__new__` method instead of the `__init__` method. For helping to easily write `__new__` methods, Coconut provides the [makedata](#makedata) built-in.

Subclassing `data` types can be done easily by inheriting from them either in another `data` statement or a normal Python `class`. If a normal `class` statement is used, making the new subclass immutable will require adding the line
```coconut
__slots__ = ()
```
which will need to be put in the subclass body before any method or attribute definitions. If you need to inherit magic methods from a base class in your `data` type, such subclassing is the recommended method, as the `data ... from ...` syntax will overwrite any magic methods in the base class with magic methods built for the new `data` type.

Compared to [`namedtuple`s](#anonymous-namedtuples), from which `data` types are derived, `data` types:

- use typed equality,
- don't support tuple addition or multiplication (unless explicitly defined via special methods in the `data` body),
- support starred, typed, and [pattern-matching](#match-data) arguments, and
- have special [pattern-matching](#match) behavior.

Like [`namedtuple`s](https://docs.python.org/3/library/collections.html#namedtuple-factory-function-for-tuples-with-named-fields), `data` types also support a variety of extra methods, such as [`._asdict()`](https://docs.python.org/3/library/collections.html#collections.somenamedtuple._asdict) and [`._replace(**kwargs)`](https://docs.python.org/3/library/collections.html#collections.somenamedtuple._replace).

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

addpattern def size(Leaf(n)) = 1

addpattern def size(Node(l, r)) = size(l) + size(r)

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

#### `match data`

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
data namedpt(name `isinstance` str, x `isinstance` int, y `isinstance` int):
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

### `async with for`

In modern Python `async` code, such as when using [`contextlib.aclosing`](https://docs.python.org/3/library/contextlib.html#contextlib.aclosing), it is often recommended to use a pattern like
```coconut_python
async with aclosing(my_generator()) as values:
    async for value in values:
        ...
```
since it is substantially safer than the more syntactically straightforward
```coconut_python
async for value in my_generator():
    ...
```

This is especially true when using [`trio`](https://github.com/python-trio/trio), which [completely disallows iterating over `async` generators with `async for`](https://discuss.python.org/t/preventing-yield-inside-certain-context-managers/1091), instead requiring the above `async with ... async for` pattern using utilities such as [`trio_util.trio_async_generator`](https://trio-util.readthedocs.io/en/latest/#trio_util.trio_async_generator).

Since this pattern can often be quite syntactically cumbersome, Coconut provides the shortcut syntax
```
async with for aclosing(my_generator()) as values:
    ...
```
which compiles to exactly the pattern above.

`async with for` also [supports pattern-matching, just like normal Coconut `for` loops](#match-for).

##### Example

**Coconut:**
```coconut
from trio_util import trio_async_generator

@trio_async_generator
async def my_generator():
    # yield values, possibly from a nursery or cancel scope
    # ...

async with for value in my_generator():
    print(value)
```

**Python:**
```coconut_python
from trio_util import trio_async_generator

@trio_async_generator
async def my_generator():
    # yield values, possibly from a nursery or cancel scope
    # ...

async with my_generator() as agen:
    async for value in agen:
        print(value)
```

### Handling Keyword/Variable Name Overlap

In Coconut, the following keywords are also valid variable names:
- `data`
- `match`
- `case`
- `cases`
- `addpattern`
- `where`
- `operator`
- `then`
- `λ` (a [Unicode alternative](#unicode-alternatives) for `lambda`)

While Coconut can usually disambiguate these two use cases, special syntax is available for disambiguating them if necessary. Note that, if what you're writing can be interpreted as valid Python 3, Coconut will always prefer that interpretation by default.

To specify that you want a _variable_, prefix the name with a backslash as in `\data`, and to specify that you want a _keyword_, prefix the name with a colon as in `:match`.

Additionally, backslash syntax for escaping variable names can also be used to distinguish between variable names and [custom operators](#custom-operators) as well as explicitly signify that an assignment to a built-in is desirable to dismiss [`--strict` warnings](#strict-mode).

Finally, such disambiguation syntax can also be helpful for letting syntax highlighters know what you're doing.

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

```{contents}
---
local:
depth: 1
---
```

### Statement Lambdas

The statement lambda syntax is an extension of the [normal lambda syntax](#lambdas) to support statements, not just expressions.

The syntax for a statement lambda is
```
[async|match|copyclosure] def (arguments) => statement; statement; ...
```
where `arguments` can be standard function arguments or [pattern-matching function definition](#pattern-matching-functions) arguments and `statement` can be an assignment statement or a keyword statement. Note that the `async`, `match`, and [`copyclosure`](#copyclosure-functions) keywords can be combined and can be in any order.

If the last `statement` (not followed by a semicolon) in a statement lambda is an `expression`, it will automatically be returned.

Statement lambdas also support implicit lambda syntax such that `def => _` is equivalent to `def (_=None) => _` as well as explicitly marking them as pattern-matching such that `match def (x) => x` will be a pattern-matching function.

Note that statement lambdas have a lower precedence than normal lambdas and thus capture things like trailing commas. To avoid confusion, statement lambdas should always be wrapped in their own set of parentheses.

_Deprecated: Statement lambdas also support `->` instead of `=>`. Note that when using `->`, any lambdas in the body of the statement lambda must also use `->` rather than `=>`._

##### Example

**Coconut:**
```coconut
L |> map$(def (x) =>
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
f = def (c: str) -> None => print(c)

g = def (a: int, b: int) -> int => a ** b
```

_Deprecated: if the deprecated `->` is used in place of `=>`, then return type annotations will not be available._

### Operator Functions

Coconut uses a simple operator function short-hand: surround an operator with parentheses to retrieve its function. Similarly to iterator comprehensions, if the operator function is the only argument to a function, the parentheses of the function call can also serve as the parentheses for the operator function.

##### Rationale

A very common thing to do in functional programming is to make use of function versions of built-in operators: currying them, composing them, and piping them. To make this easy, Coconut provides a short-hand syntax to access operator functions.

##### Full List

```coconut
(::)        => (itertools.chain)  # will not evaluate its arguments lazily
($)         => (functools.partial)
(.)         => (getattr)
(,)         => (*args) => args  # (but pickleable)
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
(|>)        => # pipe forward
(|*>)       => # multi-arg pipe forward
(|**>)      => # keyword arg pipe forward
(<|)        => # pipe backward
(<*|)       => # multi-arg pipe backward
(<**|)      => # keyword arg pipe backward
(|?>)       => # None-aware pipe forward
(|?*>)      => # None-aware multi-arg pipe forward
(|?**>)     => # None-aware keyword arg pipe forward
(<?|)       => # None-aware pipe backward
(<*?|)      => # None-aware multi-arg pipe backward
(<**?|)     => # None-aware keyword arg pipe backward
(..), (<..) => # backward function composition
(..>)       => # forward function composition
(<*..)      => # multi-arg backward function composition
(..*>)      => # multi-arg forward function composition
(<**..)     => # keyword arg backward function composition
(..**>)     => # keyword arg forward function composition
(not)       => (operator.not_)
(and)       => # boolean and
(or)        => # boolean or
(is)        => (operator.is_)
(is not)    => (operator.is_not)
(in)        => (operator.contains)
(not in)    => # negative containment
(assert)    => def (cond, msg=None) => assert cond, msg  # (but a better msg if msg is None)
(raise)     => def (exc=None, from_exc=None) => raise exc from from_exc  # or just raise if exc is None
# there are two operator functions that don't require parentheses:
.[]         => (operator.getitem)
.$[]        => # iterator slicing operator
```

For an operator function for function application, see [`call`](#call).

Though no operator function is available for `await`, an equivalent syntax is available for [pipes](#pipes) in the form of `awaitable |> await`.

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

### Implicit Partial Application

Coconut supports a number of different syntactical aliases for common partial application use cases. These are:
```coconut
.attr           =>      operator.attrgetter("attr")
.method(args)   =>      operator.methodcaller("method", args)
func$           =>      ($)$(func)
seq[]           =>      operator.getitem$(seq)
iter$[]         =>      # the equivalent of seq[] for iterators
.[a:b:c]        =>      operator.itemgetter(slice(a, b, c))
.$[a:b:c]       =>      # the equivalent of .[a:b:c] for iterators
```

Additionally, `.attr.method(args)`, `.[x][y]`, and `.$[x]$[y]` are also supported.

In addition, for every Coconut [operator function](#operator-functions), Coconut supports syntax for implicitly partially applying that operator function as
```
(. <op> <arg>)
(<arg> <op> .)
```
where `<op>` is the operator function and `<arg>` is any expression. Note that, as with operator functions themselves, the parentheses are necessary for this type of implicit partial application.

Additionally, Coconut also supports implicit operator function partials for arbitrary functions as
```
(. `<name>` <arg>)
(<arg> `<name>` .)
```
based on Coconut's [infix notation](#infix-functions) where `<name>` is the name of the function. Additionally, `` `<name>` `` can instead be a [custom operator](#custom-operators) (in that case, no backticks should be used).

_Deprecated: Coconut also supports `obj.` as an implicit partial for `getattr$(obj)`, but its usage is deprecated and will show a warning to switch to `getattr$(obj)` instead._

##### Example

**Coconut:**
```coconut
1 |> "123"[]
mod$ <| 5 <| 3
3 |> (.*2) |> (.+1)
```

**Python:**
```coconut_python
"123"[1]
mod(5, 3)
(3 * 2) + 1
```

### Enhanced Type Annotation

Since Coconut syntax is a superset of the latest Python 3 syntax, it supports [Python 3 function type annotation syntax](https://www.python.org/dev/peps/pep-0484/) and [Python 3.6 variable type annotation syntax](https://www.python.org/dev/peps/pep-0526/). By default, Coconut compiles all type annotations into Python-2-compatible type comments. If you want to keep the type annotations instead, simply pass a `--target` that supports them.

Since not all supported Python versions support the [`typing`](https://docs.python.org/3/library/typing.html) module, Coconut provides the [`TYPE_CHECKING`](#type_checking) built-in for hiding your `typing` imports and `TypeVar` definitions from being executed at runtime. Coconut will also automatically use [`typing_extensions`](https://pypi.org/project/typing-extensions/) over `typing` objects at runtime when importing them from `typing`, even when they aren't natively supported on the current Python version (this works even if you just do `import typing` and then `typing.<Object>`).

Furthermore, when compiling type annotations to Python 3 versions without [PEP 563](https://www.python.org/dev/peps/pep-0563/) support, Coconut wraps annotation in strings to prevent them from being evaluated at runtime (to avoid this, e.g. if you want to use annotations at runtime, `--no-wrap-types` will disable all wrapping, including via PEP 563 support). Only on `--target 3.13` does `--no-wrap-types` do nothing, since there [PEP 649](https://peps.python.org/pep-0649/) support is used instead.

Additionally, Coconut adds special syntax for making type annotations easier and simpler to write. When inside of a type annotation, Coconut treats certain syntax constructs differently, compiling them to type annotations instead of what they would normally represent. Specifically, Coconut applies the following transformations:
```coconut
A | B
    => typing.Union[A, B]
(A; B)
    => typing.Tuple[A, B]
A?
    => typing.Optional[A]
A[]
    => typing.Sequence[A]
A$[]
    => typing.Iterable[A]
() -> <ret>
    => typing.Callable[[], <ret>]
<arg> -> <ret>
    => typing.Callable[[<arg>], <ret>]
(<args>) -> <ret>
    => typing.Callable[[<args>], <ret>]
-> <ret>
    => typing.Callable[..., <ret>]
(<args>, **<ParamSpec>) -> <ret>
    => typing.Callable[typing.Concatenate[<args>, <ParamSpec>], <ret>]
async (<args>) -> <ret>
    => typing.Callable[[<args>], typing.Awaitable[<ret>]]
```
where `typing` is the Python 3.5 built-in [`typing` module](https://docs.python.org/3/library/typing.html). For more information on the Callable syntax, see [PEP 677](https://peps.python.org/pep-0677), which Coconut fully supports.

Additionally, many of Coconut's [operator functions](#operator-functions) will compile into equivalent [`Protocol`s](https://docs.python.org/3/library/typing.html#typing.Protocol) instead when inside a type annotation. See below for the full list and specification.

_Note: The transformation to `Union` is not done on Python 3.10 as Python 3.10 has native [PEP 604](https://www.python.org/dev/peps/pep-0604) support._

To use these transformations in a [type alias](https://peps.python.org/pep-0484/#type-aliases), use the syntax
```
type <name> = <type>
```
which will allow `<type>` to include Coconut's special type annotation syntax and type `<name>` as a [`typing.TypeAlias`](https://docs.python.org/3/library/typing.html#typing.TypeAlias). If you try to instead just do a naked `<name> = <type>` type alias, Coconut won't be able to tell you're attempting a type alias and thus won't apply any of the above transformations.

Such type alias statements—as well as all `class`, `data`, and function definitions in Coconut—also support Coconut's [type parameter syntax](#type-parameter-syntax), allowing you to do things like `type OrStr[T] = T | str`.

##### Supported Protocols

Using Coconut's [operator function](#operator-functions) syntax inside of a type annotation will instead produce a [`Protocol`](https://docs.python.org/3/library/typing.html#typing.Protocol) corresponding to that operator (or raise a syntax error if no such `Protocol` is available). All available `Protocol`s are listed below.

For the operator functions
```
(+)
(*)
(**)
(/)
(//)
(%)
(&)
(^)
(|)
(<<)
(>>)
(@)
```
the resulting `Protocol` is
```coconut
class SupportsOp[T, U, V](Protocol):
    def __op__(self: T, other: U) -> V:
        raise NotImplementedError(...)
```
where `__op__` is the magic method corresponding to that operator.

For the operator function `(-)`, the resulting `Protocol` is:
```coconut
class SupportsMinus[T, U, V](Protocol):
    def __sub__(self: T, other: U) -> V:
        raise NotImplementedError
    def __neg__(self: T) -> V:
        raise NotImplementedError
```

For the operator function `(~)`, the resulting `Protocol` is:
```coconut
class SupportsInv[T, V](Protocol):
    def __invert__(self: T) -> V:
        raise NotImplementedError(...)
```

##### `List` vs. `Sequence`

Importantly, note that `T[]` does not map onto `typing.List[T]` but onto `typing.Sequence[T]`. This allows the resulting type to be covariant, such that if `U` is a subtype of `T`, then `U[]` is a subtype of `T[]`. Additionally, `Sequence[T]` allows for tuples, and when writing in an idiomatic functional style, assignment should be rare and tuples should be common. Using `Sequence` covers both cases, accommodating tuples and lists and preventing indexed assignment. When an indexed assignment is attempted into a variable typed with `Sequence`, MyPy will generate an error:

```coconut
foo: int[] = [0, 1, 2, 3, 4, 5]
foo[0] = 1   # MyPy error: "Unsupported target for indexed assignment"
```

If you want to use `List` instead (e.g. if you want to support indexed assignment), use the standard Python 3.5 variable type annotation syntax: `foo: List[<type>]`.

_Note: To easily view your defined types, see [`reveal_type` and `reveal_locals`](#reveal-type-and-reveal-locals)._

##### Example

**Coconut:**
```coconut
def int_map(
    f: int -> int,
    xs: int[],
) -> int[] =
    xs |> map$(f) |> list

type CanAddAndSub = (+) &: (-)
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

T = typing.TypeVar("T", infer_variance=True)
U = typing.TypeVar("U", infer_variance=True)
V = typing.TypeVar("V", infer_variance=True)
class CanAddAndSub(typing.Protocol, typing.Generic[T, U, V]):
    def __add__(self: T, other: U) -> V:
        raise NotImplementedError
    def __sub__(self: T, other: U) -> V:
        raise NotImplementedError
    def __neg__(self: T) -> V:
        raise NotImplementedError
```

### Multidimensional Array Literal/Concatenation Syntax

Coconut supports multidimensional array literal and array [concatenation](https://numpy.org/doc/stable/reference/generated/numpy.concatenate.html)/[stack](https://numpy.org/doc/stable/reference/generated/numpy.stack.html) syntax.

By default, all multidimensional array syntax will simply operate on Python lists of lists (or any non-`str` `Sequence`). However, if [`numpy`](#numpy-integration) objects are used, the appropriate `numpy` calls will be made instead. To give custom objects multidimensional array concatenation support, define `type(obj).__matconcat__` (should behave as `np.concat`), `obj.ndim` (should behave as `np.ndarray.ndim`), and `obj.reshape` (should behave as `np.ndarray.reshape`).

As a simple example, 2D matrices can be constructed by separating the rows with `;;` inside of a list literal:
```coconut_pycon
>>> [1, 2 ;;
     3, 4]

[[1, 2], [3, 4]]
>>> import numpy as np
>>> np.array([1, 2 ;; 3, 4])
array([[1, 2],
       [3, 4]])
```
As can be seen, `np.array` (or equivalent) can be used to turn the resulting list of lists into an actual array. This syntax works because `;;` inside of a list literal functions as a concatenation/stack along the `-2` axis (with the inner arrays being broadcast to `(1, 2)` arrays before concatenation). Note that this concatenation is done entirely in Python lists of lists here, since the `np.array` call comes only at the end.

In general, the number of semicolons indicates the dimension from the end on which to concatenate. Thus, `;` indicates conatenation along the `-1` axis, `;;` along the `-2` axis, and so on. Before concatenation, arrays are always broadcast to a shape which is large enough to allow the concatenation.

Thus, if `a` is a `numpy` array, `[a; a]` is equivalent to `np.concatenate((a, a), axis=-1)`, while `[a ;; a]` would be equivalent to a version of `np.concatenate((a, a), axis=-2)` that also ensures that `a` is at least two dimensional. For normal lists of lists, the behavior is the same, but is implemented without any `numpy` calls.

If multiple different concatenation operators are used, the operators with the least number of semicolons will bind most tightly. Thus, you can write a 3D array literal as:
```coconut_pycon
>>> [1, 2 ;;
     3, 4
     ;;;
     5, 6 ;;
     7, 8]

[[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
```

##### Comparison to Julia

Coconut's multidimensional array syntax is based on that of [Julia](https://docs.julialang.org/en/v1/manual/arrays/#man-array-literals). The primary difference between Coconut's syntax and Julia's syntax is that multidimensional arrays are row-first in Coconut (following `numpy`), but column-first in Julia. Thus, `;` is vertical concatenation in Julia but **horizontal concatenation** in Coconut and `;;` is horizontal concatenation in Julia but **vertical concatenation** in Coconut.

##### Examples

**Coconut:**
```coconut_pycon
>>> [[1;;2] ; [3;;4]]
[[1, 3], [2, 4]]
```
_Array literals can be written in column-first order if the columns are first created via vertical concatenation (`;;`) and then joined via horizontal concatenation (`;`)._

```coconut_pycon
>>> [range(3) |> list ;; x+1 for x in range(3)]
[[0, 1, 2], [1, 2, 3]]
```
_Arbitrary expressions, including comprehensions, are allowed in multidimensional array literals._

```coconut_pycon
>>> import numpy as np
>>> a = np.array([1, 2 ;; 3, 4])
>>> [a ; a]
array([[1, 2, 1, 2],
       [3, 4, 3, 4]])
>>> [a ;; a]
array([[1, 2],
       [3, 4],
       [1, 2],
       [3, 4]])
>>> [a ;;; a]
array([[[1, 2],
        [3, 4]],

       [[1, 2],
        [3, 4]]])
```
_General showcase of how the different concatenation operators work using `numpy` arrays._

**Python:** _The equivalent Python array literals can be seen in the printed representations in each example._

### Lazy Lists

Coconut supports the creation of lazy lists, where the contents in the list will be treated as an iterator and not evaluated until they are needed. Unlike normal iterators, however, lazy lists can be iterated over multiple times and still return the same result. Lazy lists can be created in Coconut simply by surrounding a comma-separated list of items with `(|` and `|)` (so-called "banana brackets") instead of `[` and `]` for a list or `(` and `)` for a tuple.

Lazy lists use [reiterable](#reiterable) under the hood to enable them to be iterated over multiple times. Lazy lists will even continue to be reiterable when combined with [lazy chaining](#iterator-chaining).

##### Rationale

Lazy lists, where sequences are only evaluated when their contents are requested, are a mainstay of functional programming, allowing for dynamic evaluation of the list's contents.

##### Example

**Coconut:**
```coconut
(| print("hello,"), print("world!") |) |> consume
```

**Python:**
_Can't be done without a complicated iterator comprehension in place of the lazy list. See the compiled code for the Python syntax._

### Implicit Function Application and Coefficients

Coconut supports implicit function application of the form `f x y`, which is compiled to `f(x, y)` (note: **not** `f(x)(y)` as is common in many languages with automatic currying).

Additionally, if the first argument is not callable, and is instead an `int`, `float`, `complex`, or [`numpy`](#numpy-integration) object, then the result is multiplication rather than function application, such that `2 x` is equivalent to `2*x`.

Though the first item may be any atom, following arguments are highly restricted, and must be:
- variables/attributes (e.g. `a.b`),
- literal constants (e.g. `True`),
- number literals (e.g. `1.5`), or
- one of the above followed by an exponent (e.g. `a**-5`).

For example, `(f .. g) x 1` will work, but `f x [1]`, `f x (1+2)`, and `f "abc"` will not.

Implicit function application and coefficient syntax is only intended for simple use cases. For more complex cases, use the standard multiplication operator `*`, standard function application, or [pipes](#pipes).

Implicit function application and coefficient syntax has a lower precedence than `**` but a higher precedence than unary operators. As a result, `2 x**2 + 3 x` is equivalent to `2 * x**2 + 3 * x`.

Due to potential confusion, some syntactic constructs are explicitly disallowed in implicit function application and coefficient syntax. Specifically:
- Strings are always disallowed everywhere in implicit function application / coefficient syntax due to conflicting with [Python's implicit string concatenation](https://stackoverflow.com/questions/18842779/string-concatenation-without-operator).
- Multiplying two or more numeric literals with implicit coefficient syntax is prohibited, so `10 20` is not allowed.
- `await` is not allowed in front of implicit function application and coefficient syntax. To use `await`, simply parenthesize the expression, as in `await (f x)`.

_Note: implicit function application and coefficient syntax is disabled when [using Coconut in `xonsh`](#xonsh-support) due to conflicting with console commands._

##### Examples

**Coconut:**
```coconut
def f(x, y) = (x, y)
print(f 5 10)
```

```coconut
def p1(x) = x + 1
print <| p1 5
```

```coconut
quad = 5 x**2 + 3 x + 1
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

```coconut_python
quad = 5 * x**2 + 3 * x + 1
```

### Keyword Argument Name Elision

When passing in long variable names as keyword arguments of the same name, Coconut supports the syntax
```
f(...=long_variable_name)
```
as a shorthand for
```
f(long_variable_name=long_variable_name)
```

Such syntax is also supported in [partial application](#partial-application) and [anonymous `namedtuple`s](#anonymous-namedtuples).

##### Example

**Coconut:**
```coconut
really_long_variable_name_1 = get_1()
really_long_variable_name_2 = get_2()
main_func(
    ...=really_long_variable_name_1,
    ...=really_long_variable_name_2,
)
```

**Python:**
```coconut_python
really_long_variable_name_1 = get_1()
really_long_variable_name_2 = get_2()
main_func(
    really_long_variable_name_1=really_long_variable_name_1,
    really_long_variable_name_2=really_long_variable_name_2,
)
```

### Anonymous Namedtuples

Coconut supports anonymous [`namedtuple`](https://docs.python.org/3/library/collections.html#collections.namedtuple) literals, such that `(a=1, b=2)` can be used just as `(1, 2)`, but with added names. Anonymous `namedtuple`s are always pickleable.

The syntax for anonymous namedtuple literals is:
```coconut
(<name> [: <type>] = <value>, ...)
```
where, if `<type>` is given for any field, [`typing.NamedTuple`](https://docs.python.org/3/library/typing.html#typing.NamedTuple) is used instead of `collections.namedtuple`.

Anonymous `namedtuple`s also support [keyword argument name elision](#keyword-argument-name-elision).

##### `_namedtuple_of`

On Python versions `>=3.6`, `_namedtuple_of` is provided as a built-in that can mimic the behavior of anonymous namedtuple literals such that `_namedtuple_of(a=1, b=2)` is equivalent to `(a=1, b=2)`. Since `_namedtuple_of` is only available on Python 3.6 and above, however, it is generally recommended to use anonymous namedtuple literals instead, as they work on any Python version.

_`_namedtuple_of` is just provided to give namedtuple literals a representation that corresponds to an expression that can be used to recreate them._

##### Example

**Coconut:**
```coconut
users = [
    (id=1, name="Alice"),
    (id=2, name="Bob"),
]
```

**Python:**
```coconut_python
from collections import namedtuple

users = [
    namedtuple("_", "id, name")(1, "Alice"),
    namedtuple("_", "id, name")(2, "Bob"),
]
```

### Set Literals

Coconut allows an optional `s` to be prepended in front of Python set literals. While in most cases this does nothing, in the case of the empty set it lets Coconut know that it is an empty set and not an empty dictionary. Set literals also support unpacking syntax (e.g. `s{*xs}`).

Additionally, Coconut also supports replacing the `s` with an `f` to generate a `frozenset` or an `m` to generate a Coconut [`multiset`](#multiset).

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

```{contents}
---
local:
depth: 1
---
```

### Tail Call Optimization

Coconut will perform automatic [tail call](https://en.wikipedia.org/wiki/Tail_call) optimization and tail recursion elimination on any function that meets the following criteria:

1. it must directly return (using either `return` or [assignment function notation](#assignment-functions)) a call to itself (tail recursion elimination, the most powerful optimization) or another function (tail call optimization),
2. it must not be a generator (uses `yield`) or an asynchronous function (uses `async`).

Tail call optimization (though not tail recursion elimination) will work even for 1) mutual recursion and 2) pattern-matching functions split across multiple definitions using [`addpattern`](#addpattern).

If you are encountering a `RuntimeError` due to maximum recursion depth, it is highly recommended that you rewrite your function to meet either the criteria above for tail call optimization, or the corresponding criteria for [`recursive_iterator`](#recursive-iterator), either of which should prevent such errors.

##### Example

**Coconut:**
```coconut
# unlike in Python, this function will never hit a maximum recursion depth error
def factorial(n, acc=1):
    match n:
        case 0:
            return acc
        case int() if n > 0:
            return factorial(n-1, acc*n)
```
_Showcases tail recursion elimination._

```coconut
# unlike in Python, neither of these functions will ever hit a maximum recursion depth error
def is_even(0) = True
addpattern def is_even(n `isinstance` int if n > 0) = is_odd(n-1)

def is_odd(0) = False
addpattern def is_odd(n `isinstance` int if n > 0) = is_even(n-1)
```
_Showcases tail call optimization._

**Python:**
_Can't be done without rewriting the function(s)._

#### `--no-tco` flag

Tail call optimization will be turned off if you pass the `--no-tco` command-line option, which is useful if you are having trouble reading your tracebacks and/or need maximum performance.

`--no-tco` does not disable tail recursion elimination.
This is because tail recursion elimination is usually faster than doing nothing, while other types of tail call optimization are usually slower than doing nothing.
Tail recursion elimination results in a big performance win because Python has a fairly large function call overhead. By unwinding a recursive function, far fewer function calls need to be made.
When the `--no-tco` flag is disabled, Coconut will attempt to do all types of tail call optimizations, handling non-recursive tail calls, split pattern-matching functions, mutual recursion, and tail recursion. When the `--no-tco` flag is enabled, Coconut will no longer perform any tail call optimizations other than tail recursion elimination.

#### Tail Recursion Elimination and Python lambdas

Coconut does not perform tail recursion elimination in functions that utilize lambdas or inner functions. This is because of the way that Python handles lambdas.

Each lambda stores a pointer to the namespace enclosing it, rather than a copy of the namespace. Thus, if the Coconut compiler tries to recycle anything in the namespace that produced the lambda, which needs to be done for TRE, the lambda can be changed retroactively.

A simple example demonstrating this behavior in Python:

```python
x = 1
foo = lambda: x
print(foo())  # 1
x = 2         # Directly alter the values in the namespace enclosing foo
print(foo())  # 2 (!)
```

Because this could have unintended and potentially damaging consequences, Coconut opts to not perform TRE on any function with a lambda or inner function.

### Assignment Functions

Coconut allows for assignment function definition that automatically returns the last line of the function body. An assignment function is constructed by substituting `=` for `:` after the function definition line. Thus, the syntax for assignment function definition is either
```coconut
[async] def <name>(<args>) = <expr>
```
for one-liners or
```coconut
[async] def <name>(<args>) =
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

Coconut pattern-matching functions are just normal functions, except where the arguments are patterns to be matched against instead of variables to be assigned to. The syntax for pattern-matching function definition is
```coconut
[match] def <name>(<arg>, <arg>, ... [if <cond>]) [-> <return_type>]:
    <body>
```
where `<arg>` is defined as
```coconut
[*|**] <pattern> [= <default>]
```
where `<name>` is the name of the function, `<cond>` is an optional additional check, `<body>` is the body of the function, `<pattern>` is defined by Coconut's [`match` statement](#match), `<default>` is the optional default if no argument is passed, and `<return_type>` is the optional return type annotation (note that argument type annotations are not supported for pattern-matching functions). The `match` keyword at the beginning is optional, but is sometimes necessary to disambiguate pattern-matching function definition from normal function definition, since Python function definition will always take precedence. Note that the `async` and `match` keywords can be in any order.

If `<pattern>` has a variable name (either directly or with `as`), the resulting pattern-matching function will support keyword arguments using that variable name.

In addition to supporting pattern-matching in their arguments, pattern-matching function definitions also have a couple of notable differences compared to Python functions. Specifically:
- If pattern-matching function definition fails, it will raise a [`MatchError`](#matcherror) (just like [destructuring assignment](#destructuring-assignment)) instead of a `TypeError`.
- All defaults in pattern-matching function definition are late-bound rather than early-bound. Thus, `match def f(xs=[]) = xs` will instantiate a new list for each call where `xs` is not given, unlike `def f(xs=[]) = xs`, which will use the same list for all calls where `xs` is unspecified.

Pattern-matching function definition can also be combined with `async` functions, [`copyclosure` functions](#copyclosure-functions), [`yield` functions](#explicit-generators), [infix function definition](#infix-functions), and [assignment function syntax](#assignment-functions). The various keywords in front of the `def` can be put in any order.

##### Example

**Coconut:**
```coconut
def last_two(_ + [a, b]):
    return a, b
def xydict_to_xytuple({"x": x `isinstance` int, "y": y `isinstance` int}):
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

Additionally, `addpattern def` will act just like a normal [`match def`](#pattern-matching-functions) if the function has not previously been defined, allowing for `addpattern def` to be used for each case rather than requiring `match def` for the first case and `addpattern def` for future cases.

If you want to put a decorator on an `addpattern def` function, make sure to put it on the _last_ pattern function.

##### Example

**Coconut:**
```coconut
addpattern def factorial(0) = 1
addpattern def factorial(n) = n * factorial(n - 1)
```

**Python:**
_Can't be done without a complicated decorator definition and a long series of checks for each pattern-matching. See the compiled code for the Python syntax._

### `copyclosure` Functions

Coconut supports the syntax
```
copyclosure def <name>(<args>):
    <body>
```
to define a function that uses as its closure a shallow copy of its enclosing scopes at the time that the function is defined, rather than a reference to those scopes (as with normal Python functions).

For example,`in
```coconut
def outer_func():
    funcs = []
    for x in range(10):
        copyclosure def inner_func():
            return x
        funcs.append(inner_func)
    return funcs
```
the resulting `inner_func`s will each return a _different_ `x` value rather than all the same `x` value, since they look at what `x` was bound to at function definition time rather than during function execution.

`copyclosure` functions can also be combined with `async` functions, [`yield` functions](#explicit-generators), [pattern-matching functions](#pattern-matching-functions), [infix function definition](#infix-functions), and [assignment function syntax](#assignment-functions). The various keywords in front of the `def` can be put in any order.

If `global` or `nonlocal` are used in a `copyclosure` function, they will not be able to modify variables in enclosing scopes. However, they will allow state to be preserved accross multiple calls to the `copyclosure` function.

##### Example

**Coconut:**
```coconut
def outer_func():
    funcs = []
    for x in range(10):
        copyclosure def inner_func():
            return x
        funcs.append(inner_func)
    return funcs
```

**Python:**
```coconut_python
from functools import partial

def outer_func():
    funcs = []
    for x in range(10):
        def inner_func(_x):
            return _x
        funcs.append(partial(inner_func, x))
    return funcs
```

### Explicit Generators

Coconut supports the syntax
```
yield def <name>(<args>):
    <body>
```
to denote that you are explicitly defining a generator function. This is useful to ensure that, even if all the `yield`s in your function are removed, it'll always be a generator function.

Explicit generator functions can also be combined with `async` functions, [`copyclosure` functions](#copyclosure-functions), [pattern-matching functions](#pattern-matching-functions), [infix function definition](#infix-functions), and [assignment function syntax](#assignment-functions) (though note that assignment function syntax here creates a generator return). The various keywords in front of the `def` can be put in any order.

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

Coconut allows for function definition using a dotted name to assign a function as a method of an object as specified in [PEP 542](https://www.python.org/dev/peps/pep-0542/). Dotted function definition can be combined with all other types of function definition above.

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

```{contents}
---
local:
depth: 1
---
```

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

### Type Parameter Syntax

Coconut fully supports [Python 3.12 PEP 695](https://peps.python.org/pep-0695/) type parameter syntax on all Python versions.

That includes type parameters for classes, [`data` types](#data), and [all types of function definition](#function-definition). For different types of function definition, the type parameters always come in brackets right after the function name. Coconut's [enhanced type annotation syntax](#enhanced-type-annotation) is supported for all type parameter bounds.

_Warning: until `mypy` adds support for `infer_variance=True` in `TypeVar`, `TypeVar`s created this way will always be invariant._

Additionally, Coconut supports the alternative bounds syntax of `type NewType[T <: bound] = ...` rather than `type NewType[T: bound] = ...`, to make it more clear that it is an upper bound rather than a type. In `--strict` mode, `<:` is required over `:` for all type parameter bounds. _Deprecated: `<=` can also be used as an alternative to `<:`._

Note that the `<:` syntax should only be used for [type bounds](https://peps.python.org/pep-0695/#upper-bound-specification), not [type constraints](https://peps.python.org/pep-0695/#constrained-type-specification)—for type constraints, Coconut style prefers the vanilla Python `:` syntax, which helps to disambiguate between the two cases, as they are functionally different but otherwise hard to tell apart at a glance. This is enforced in `--strict` mode.

_Note that, by default, all type declarations are wrapped in strings to enable forward references and improve runtime performance. If you don't want that—e.g. because you want to use type annotations at runtime—simply pass the `--no-wrap-types` flag._

##### PEP 695 Docs

Defining a generic class prior to this PEP looks something like this.

```coconut_python
from typing import Generic, TypeVar

_T_co = TypeVar("_T_co", covariant=True, bound=str)

class ClassA(Generic[_T_co]):
    def method1(self) -> _T_co:
        ...
```

With the new syntax, it looks like this.

```coconut
class ClassA[T: str]:
    def method1(self) -> T:
        ...
```

Here is an example of a generic function today.

```coconut_python
from typing import TypeVar

_T = TypeVar("_T")

def func(a: _T, b: _T) -> _T:
    ...
```

And the new syntax.

```coconut
def func[T](a: T, b: T) -> T:
    ...
```

Here is an example of a generic type alias today.

```coconut_python
from typing import TypeAlias

_T = TypeVar("_T")

ListOrSet: TypeAlias = list[_T] | set[_T]
```

And with the new syntax.

```coconut
type ListOrSet[T] = list[T] | set[T]
```


##### Example

**Coconut:**
```coconut
data D[T](x: T, y: T)

def my_ident[T](x: T) -> T = x
```

**Python:**
_Can't be done without a complex definition for the data type. See the compiled code for the Python syntax._

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
elif isinstance(input_list, Sequence) and len(input_list) >= 1:
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

Coconut supports the ability to pass arbitrary code through the compiler without being touched, for compatibility with other variants of Python, such as [Cython](http://cython.org/) or [Mython](http://mython.org/). When using Coconut to compile to another variant of Python, make sure you [name your source file properly](#naming-source-files) to ensure the resulting compiled code has the right file extension for the intended usage.

Anything placed between `\(` and the corresponding close parenthesis will be passed through, as well as any line starting with `\\`, which will have the additional effect of allowing indentation under it.

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

Since Coconut syntax is a superset of the latest Python 3 syntax, Coconut supports the same line continuation syntax as Python. That means both backslash line continuation and implied line continuation inside of parentheses, brackets, or braces will all work.

In Python, however, there are some cases (such as multiple `with` statements) where only backslash continuation, and not parenthetical continuation, is supported. Coconut adds support for parenthetical continuation in all these cases. This also includes support as per [PEP 679](https://peps.python.org/pep-0679) for parenthesized `assert` statements.

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

### Assignment Expression Chaining

Unlike Python, Coconut allows assignment expressions to be chained, as in `a := b := c`. Note, however, that assignment expressions in general are currently only supported on `--target 3.8` or higher.

##### Example

**Coconut:**
```coconut
(a := b := 1)
```

**Python:**
```coconut_python
(a := (b := 1))
```

## Built-Ins

```{contents}
---
local:
depth: 2
---
```

### Built-In Function Decorators

```{contents}
---
local:
depth: 1
---
```

#### `addpattern`

**addpattern**(_base\_func_, *_add\_funcs_, _allow\_any\_func_=`False`)

Takes one argument that is a [pattern-matching function](#pattern-matching-functions), and returns a decorator that adds the patterns in the existing function to the new function being decorated, where the existing patterns are checked first, then the new. `addpattern` also supports a shortcut syntax where the new patterns can be passed in directly.

Roughly equivalent to:
```
def _pattern_adder(base_func, add_func):
    def add_pattern_func(*args, **kwargs):
        try:
            return base_func(*args, **kwargs)
        except MatchError:
            return add_func(*args, **kwargs)
    return add_pattern_func
def addpattern(base_func, *add_funcs, allow_any_func=False):
    """Decorator to add a new case to a pattern-matching function (where the new case is checked last).

    Pass allow_any_func=True to allow any object as the base_func rather than just pattern-matching functions.
    If add_func is passed, addpattern(base_func, add_func) is equivalent to addpattern(base_func)(add_func).
    """
    if not add_funcs:
        return addpattern$(base_func)
    for add_func in add_funcs:
        base_func = pattern_adder(base_func, add_func)
    return base_func
```

If you want to give an `addpattern` function a docstring, make sure to put it on the _last_ function.

Note that the function taken by `addpattern` must be a pattern-matching function. If `addpattern` receives a non pattern-matching function, the function with not raise `MatchError`, and `addpattern` won't be able to detect the failed match. Thus, if a later function was meant to be called, `addpattern` will not know that the first match failed and the correct path will never be reached.

For example, the following code raises a `TypeError`:
```coconut
def print_type():
    print("Received no arguments.")

@addpattern(print_type)
def print_type(int()):
    print("Received an int.")

print_type()  # appears to work
print_type(1) # TypeError: print_type() takes 0 positional arguments but 1 was given
```

This can be fixed by using either the `match` or `addpattern` keyword. For example:
```coconut
match def print_type():
    print("Received no arguments.")

addpattern def print_type(int()):
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
_Simple example of adding a new pattern to a pattern-matching function._

```coconut
"[A], [B]" |> windowsof$(3) |> map$(addpattern(
    (def (("[","A","]")) => "A"),
    (def (("[","B","]")) => "B"),
    (def ((_,_,_)) => None),
)) |> filter$((.is None) ..> (not)) |> list |> print
```
_An example of a case where using the `addpattern` function is necessary over the [`addpattern` keyword](#addpattern-functions) due to the use of in-line pattern-matching [statement lambdas](#statement-lambdas)._

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

#### `memoize`

**memoize**(_maxsize_=`None`, _typed_=`False`)

**memoize**(_user\_function_)

Coconut provides `functools.lru_cache` as a built-in under the name `memoize` with the modification that the _maxsize_ parameter is set to `None` by default. `memoize` makes the use case of optimizing recursive functions easier, as a _maxsize_ of `None` is usually what is desired in that case.

Use of `memoize` requires `functools.lru_cache`, which exists in the Python 3 standard library, but under Python 2 will require `pip install backports.functools_lru_cache` to function. Additionally, if on Python 2 and `backports.functools_lru_cache` is present, Coconut will patch `functools` such that `functools.lru_cache = backports.functools_lru_cache.lru_cache`.

##### Python Docs

@**memoize**(_user\_function_)

@**memoize**(_maxsize=None, typed=False_)

Decorator to wrap a function with a memoizing callable that saves up to the _maxsize_ most recent calls. It can save time when an expensive or I/O bound function is periodically called with the same arguments.

Since a dictionary is used to cache results, the positional and keyword arguments to the function must be hashable.

Distinct argument patterns may be considered to be distinct calls with separate cache entries. For example, `f(a=1, b=2)` and `f(b=2, a=1)` differ in their keyword argument order and may have two separate cache entries.

If _user\_function_ is specified, it must be a callable. This allows the _memoize_ decorator to be applied directly to a user function, leaving the maxsize at its default value of `None`:
```coconut_python
@memoize
def count_vowels(sentence):
    return sum(sentence.count(vowel) for vowel in 'AEIOUaeiou')
```

If _maxsize_ is set to `None`, the LRU feature is disabled and the cache can grow without bound.

If _typed_ is set to true, function arguments of different types will be cached separately. If typed is false, the implementation will usually regard them as equivalent calls and only cache a single result. (Some types such as str and int may be cached separately even when typed is false.)

Note, type specificity applies only to the function’s immediate arguments rather than their contents. The scalar arguments, `Decimal(42)` and `Fraction(42)` are be treated as distinct calls with distinct results. In contrast, the tuple arguments `('answer', Decimal(42))` and `('answer', Fraction(42))` are treated as equivalent.

The decorator also provides a `cache_clear()` function for clearing or invalidating the cache.

The original underlying function is accessible through the `__wrapped__` attribute. This is useful for introspection, for bypassing the cache, or for rewrapping the function with a different cache.

The cache keeps references to the arguments and return values until they age out of the cache or until the cache is cleared.

If a method is cached, the `self` instance argument is included in the cache. See [How do I cache method calls?](https://docs.python.org/3/faq/programming.html#faq-cache-method-calls)

An [LRU (least recently used) cache](https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU)) works best when the most recent calls are the best predictors of upcoming calls (for example, the most popular articles on a news server tend to change each day). The cache’s size limit assures that the cache does not grow without bound on long-running processes such as web servers.

In general, the LRU cache should only be used when you want to reuse previously computed values. Accordingly, it doesn’t make sense to cache functions with side-effects, functions that need to create distinct mutable objects on each call, or impure functions such as time() or random().

Example of efficiently computing Fibonacci numbers using a cache to implement a dynamic programming technique:
```coconut_pycon
@memoize
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

>>> [fib(n) for n in range(16)]
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]

>>> fib.cache_info()
CacheInfo(hits=28, misses=16, maxsize=None, currsize=16)
```

##### Example

**Coconut:**
```coconut
def fib(n if n < 2) = n

@memoize
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

#### `override`

**override**(_func_)

Coconut provides the `@override` decorator to allow declaring a method definition in a subclass as an override of some parent class method. When `@override` is used on a method, if a method of the same name does not exist on some parent class, the class definition will raise a `RuntimeError`.

Additionally, `override` will present to type checkers as [`typing_extensions.override`](https://pypi.org/project/typing-extensions/).

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

#### `recursive_iterator`

**recursive\_iterator**(_func_)

Coconut provides a `recursive_iterator` decorator that memoizes any stateless, recursive function that returns an iterator. To use `recursive_iterator` on a function, it must meet the following criteria:

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

### Built-In Types

```{contents}
---
local:
depth: 1
---
```

#### `multiset`

**multiset**(_iterable_=`None`, /, **kwds)

Coconut provides `multiset` as a built-in subclass of [`collections.Counter`](https://docs.python.org/3/library/collections.html#collections.Counter) that additionally implements the full [Set and MutableSet interfaces](https://docs.python.org/3/library/collections.abc.html).

For easily constructing multisets, Coconut also provides [multiset literals](#set-literals).

The new methods provided by `multiset` on top of `collections.Counter` are:
- multiset.**add**(_item_): Add an element to a multiset.
- multiset.**discard**(_item_): Remove an element from a multiset if it is a member.
- multiset.**remove**(_item_): Remove an element from a multiset; it must be a member.
- multiset.**isdisjoint**(_other_): Return True if two multisets have a null intersection.
- multiset.**\_\_xor\_\_**(_other_): Return the symmetric difference of two multisets as a new multiset. Specifically: `a ^ b = (a - b) | (b - a)`
- multiset.**count**(_item_): Return the number of times an element occurs in a multiset. Equivalent to `multiset[item]`, but additionally verifies the count is non-negative.
- multiset.**\_\_fmap\_\_**(_func_): Apply a function to the contents of the multiset, preserving counts; magic method for [`fmap`](#fmap).

Coconut also ensures that `multiset` supports [rich comparisons and `Counter.total()`](https://docs.python.org/3/library/collections.html#collections.Counter) on all Python versions.

##### Example

**Coconut:**
```coconut
my_multiset = m{1, 1, 2}
my_multiset.add(3)
my_multiset.remove(2)
print(my_multiset)
```

**Python:**
```coconut_python
from collections import Counter
my_counter = Counter((1, 1, 2))
my_counter[3] += 1
my_counter[2] -= 1
if my_counter[2] <= 0:
    del my_counter[2]
print(my_counter)
```

#### `Expected`

**Expected**(_result_=`None`, _error_=`None`)

Coconut's `Expected` built-in is a Coconut [`data` type](#data) that represents a value that may or may not be an error, similar to Haskell's [`Either`](https://hackage.haskell.org/package/base-4.17.0.0/docs/Data-Either.html).

`Expected` is effectively equivalent to the following:
```coconut
data Expected[T](result: T? = None, error: BaseException? = None):
    def __bool__(self) -> bool:
        return self.error is None
    def __fmap__[U](self, func: T -> U) -> Expected[U]:
        return self.__class__(func(self.result)) if self else self
    def and_then[U](self, func: T -> Expected[U]) -> Expected[U]:
        """Maps a T -> Expected[U] over an Expected[T] to produce an Expected[U].
        Implements a monadic bind. Equivalent to fmap ..> .join()."""
        return self |> fmap$(func) |> .join()
    def join(self: Expected[Expected[T]]) -> Expected[T]:
        """Monadic join. Converts Expected[Expected[T]] to Expected[T]."""
        if not self:
            return self
        if not self.result `isinstance` Expected:
            raise TypeError("Expected.join() requires an Expected[Expected[_]]")
        return self.result
    def map_error(self, func: BaseException -> BaseException) -> Expected[T]:
        """Maps func over the error if it exists."""
        return self if self else self.__class__(error=func(self.error))
    def or_else[U](self, func: BaseException -> Expected[U]) -> Expected[T | U]:
        """Return self if no error, otherwise return the result of evaluating func on the error."""
        return self if self else func(self.error)
    def result_or[U](self, default: U) -> T | U:
        """Return the result if it exists, otherwise return the default."""
        return self.result if self else default
    def result_or_else[U](self, func: BaseException -> U) -> T | U:
        """Return the result if it exists, otherwise return the result of evaluating func on the error."""
        return self.result if self else func(self.error)
    def unwrap(self) -> T:
        """Unwrap the result or raise the error."""
        if not self:
            raise self.error
        return self.result
```

`Expected` is primarily used as the return type for [`safe_call`](#safe_call). Generally, the best way to use `Expected` is with [`fmap`](#fmap), which will apply a function to the result if it exists, or otherwise retain the error. If you want to sequence multiple `Expected`-returning operations, `.and_then` should be used instead of `fmap`.

To match against an `Expected`, just:
```
Expected(res) = Expected("result")
Expected(error=err) = Expected(error=TypeError())
```

##### Example

**Coconut:**
```coconut
def try_divide(x: float, y: float) -> Expected[float]:
    try:
        return Expected(x / y)
    except Exception as err:
        return Expected(error=err)

try_divide(1, 2) |> fmap$(.+1) |> print
try_divide(1, 0) |> fmap$(.+1) |> print
```

**Python:**
_Can't be done without a complex `Expected` definition. See the compiled code for the Python syntax._

#### `MatchError`

A `MatchError` is raised when a [destructuring assignment](#destructuring-assignment) or [pattern-matching function](#pattern-matching-functions) fails, and thus `MatchError` is provided as a built-in for catching those errors. `MatchError` objects support three attributes: `pattern`, which is a string describing the failed pattern; `value`, which is the object that failed to match that pattern; and `message` which is the full error message. To avoid unnecessary `repr` calls, `MatchError` only computes the `message` once it is actually requested.

Additionally, if you are using [view patterns](#match), you might need to raise your own `MatchError` (though you can also just use a destructuring assignment or pattern-matching function definition to do so). To raise your own `MatchError`, just `raise MatchError(pattern, value)` (both arguments are optional).

In some cases where there are multiple Coconut packages installed at the same time, there may be multiple `MatchError`s defined in different packages. Coconut can perform some magic under the hood to make sure that all these `MatchError`s will seamlessly interoperate, but only if all such packages are compiled in [`--package` mode rather than `--standalone` mode](#compilation-modes).

### Generic Built-In Functions

```{contents}
---
local:
depth: 1
---
```

#### `makedata`

**makedata**(_data\_type_, *_args_)

Coconut provides the `makedata` function to construct a container given the desired type and contents. This is particularly useful when writing alternative constructors for [`data`](#data) types by overwriting `__new__`, since it allows direct access to the base constructor of the data type created with the Coconut `data` statement.

`makedata` takes the data type to construct as the first argument, and the objects to put in that container as the rest of the arguments.

`makedata` can also be used to extract the underlying constructor for [`match data`](#match-data) types that bypasses the normal pattern-matching constructor.

Additionally, `makedata` can also be called with non-`data` type as the first argument, in which case it will do its best to construct the given type of object with the given arguments. This functionality is used internally by `fmap`.

##### `datamaker`

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

#### `fmap`

**fmap**(_func_, _obj_)

In Haskell, `fmap(func, obj)` takes a data type `obj` and returns a new data type with `func` mapped over the contents. Coconut's `fmap` function does the exact same thing for Coconut's [data types](#data).

`fmap` can also be used on the built-in objects `str`, `dict`, `list`, `tuple`, `set`, `frozenset`, and `dict` as a variant of `map` that returns back an object of the same type.

The behavior of `fmap` for a given object can be overridden by defining an `__fmap__(self, func)` magic method that will be called whenever `fmap` is invoked on that object. Note that `__fmap__` implementations should always satisfy the [Functor Laws](https://wiki.haskell.org/Functor).

For `dict`, or any other `collections.abc.Mapping`, `fmap` will map over the mapping's `.items()` instead of the default iteration through its `.keys()`, with the new mapping reconstructed from the mapped over items. _Deprecated: `fmap$(starmap_over_mappings=True)` will `starmap` over the `.items()` instead of `map` over them._

For [`numpy`](#numpy-integration) objects, `fmap` will use [`np.vectorize`](https://docs.scipy.org/doc/numpy/reference/generated/numpy.vectorize.html) to produce the result.

For [`pandas`](https://pandas.pydata.org/) objects, `fmap` will use [`.apply`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.apply.html) along the last axis (so row-wise for `DataFrame`'s, element-wise for `Series`'s).

For asynchronous iterables, `fmap` will map asynchronously, making `fmap` equivalent in that case to
```coconut_python
async def fmap_over_async_iters(func, async_iter):
    async for item in async_iter:
        yield func(item)
```
such that `fmap` can effectively be used as an async map.

_Deprecated: `fmap(func, obj, fallback_to_init=True)` will fall back to `obj.__class__(map(func, obj))` if no `fmap` implementation is available rather than raise `TypeError`._

##### Example

**Coconut:**
```coconut
[1, 2, 3] |> fmap$(x => x+1) == [2, 3, 4]

class Maybe
data Nothing() from Maybe
data Just(n) from Maybe

Just(3) |> fmap$(x => x*2) == Just(6)
Nothing() |> fmap$(x => x*2) == Nothing()
```

**Python:**
_Can't be done without a series of method definitions for each data type. See the compiled code for the Python syntax._


#### `call`

**call**(_func_, /, *_args_, \*\*_kwargs_)

Coconut's `call` simply implements function application. Thus, `call` is effectively equivalent to
```coconut
def call(f, /, *args, **kwargs) = f(*args, **kwargs)
```

`call` is primarily useful as an [operator function](#operator-functions) for function application when writing in a point-free style.

_Deprecated: `of` is available as a deprecated alias for `call`. Note that deprecated features are disabled in `--strict` mode._

#### `safe_call`

**safe_call**(_func_, /, *_args_, \*\*_kwargs_)

Coconut's `safe_call` is a version of [`call`](#call) that catches any `Exception`s and returns an [`Expected`](#expected) containing either the result or the error.

`safe_call` is effectively equivalent to:
```coconut
def safe_call(f, /, *args, **kwargs):
    try:
        return Expected(f(*args, **kwargs))
    except Exception as err:
        return Expected(error=err)
```

##### Example

**Coconut:**
```coconut
res, err = safe_call(=> 1 / 0) |> fmap$(.+1)
```

**Python:**
_Can't be done without a complex `Expected` definition. See the compiled code for the Python syntax._

#### `ident`

**ident**(_x_, *, _side\_effect_=`None`)

Coconut's `ident` is the identity function, generally equivalent to `x => x`.

`ident` also accepts one keyword-only argument, `side_effect`, which specifies a function to call on the argument before it is returned. Thus, `ident` is effectively equivalent to:
```coconut
def ident(x, *, side_effect=None):
    if side_effect is not None:
        side_effect(x)
    return x
```

`ident` is primarily useful when writing in a point-free style (e.g. in combination with [`lift`](#lift)) or for debugging [pipes](#pipes) where `ident$(side_effect=print)` can let you see what is being piped.

#### `const`

**const**(_value_)

Coconut's `const` simply constructs a function that, whatever its arguments, just returns the given value. Thus, `const` is equivalent to a pickleable version of
```coconut
def const(value) = (*args, **kwargs) => value
```

`const` is primarily useful when writing in a point-free style (e.g. in combination with [`lift`](#lift)).

#### `flip`

**flip**(_func_, _nargs_=`None`)

Coconut's `flip(f, nargs=None)` is a higher-order function that, given a function `f`, returns a new function with reversed argument order. If `nargs` is passed, only the first `nargs` arguments are reversed.

For the binary case, `flip` works as
```coconut
flip(f, 2)(x, y) == f(y, x)
```
such that `flip$(?, 2)` implements the `C` combinator (`flip` in Haskell).

In the general case, `flip` is equivalent to a pickleable version of
```coconut
def flip(f, nargs=None) =
    (*args, **kwargs) => (
        f(*args[::-1], **kwargs) if nargs is None
        else f(*(args[nargs-1::-1] + args[nargs:]), **kwargs)
    )
```

#### `lift`

**lift**(_func_)

**lift**(_func_, *_func\_args_, **_func\_kwargs_)

Coconut's `lift` built-in is a higher-order function that takes in a function and “lifts” it up so that all of its arguments are functions.

As a simple example, for a binary function `f(x, y)` and two unary functions `g(z)` and `h(z)`, `lift` works as
```coconut
lift(f)(g, h)(z) == f(g(z), h(z))
```
such that in this case `lift` implements the `S'` combinator (`liftA2` or `liftM2` in Haskell).

In the general case, `lift` is equivalent to a pickleable version of
```coconut
def lift(f) = (
    (*func_args, **func_kwargs) =>
        (*args, **kwargs) =>
            f(
                *(g(*args, **kwargs) for g in func_args),
                **{k: h(*args, **kwargs) for k, h in func_kwargs.items()}
            )
)
```

`lift` also supports a shortcut form such that `lift(f, *func_args, **func_kwargs)` is equivalent to `lift(f)(*func_args, **func_kwargs)`.

##### Example

**Coconut:**
```coconut
xs_and_xsp1 = ident `lift(zip)` map$(=>_+1)
min_and_max = lift(,)(min, max)
plus_and_times = (+) `lift(,)` (*)
```

**Python:**
```coconut_python
def xs_and_xsp1(xs):
    return zip(xs, map(lambda x: x + 1, xs))
def min_and_max(xs):
    return min(xs), max(xs)
def plus_and_times(x, y):
    return x + y, x * y
```

#### `and_then` and `and_then_await`

Coconut provides the `and_then` and `and_then_await` built-ins for composing `async` functions. Specifically:
* To forwards compose an async function `async_f` with a normal function `g` (such that `g` is called on the result of `await`ing `async_f`), write ``async_f `and_then` g``.
* To forwards compose an async function `async_f` with another async function `async_g` (such that `async_g` is called on the result of `await`ing `async_f`, and then `async_g` is itself awaited), write ``async_f `and_then_await` async_g``.
* To forwards compose a normal function `f` with an async function `async_g` (such that `async_g` is called on the result of `f`), just write `f ..> async_g`.

Note that all of the above will always result in the resulting composition being an `async` function.

The built-ins are effectively equivalent to:
```coconut
def and_then[**T, U, V](
    first_async_func: async (**T) -> U,
    second_func: U -> V,
) -> async (**T) -> V =
    async def (*args, **kwargs) => (
        first_async_func(*args, **kwargs)
        |> await
        |> second_func
    )

def and_then_await[**T, U, V](
    first_async_func: async (**T) -> U,
    second_async_func: async U -> V,
) -> async (**T) -> V =
    async def (*args, **kwargs) => (
        first_async_func(*args, **kwargs)
        |> await
        |> second_async_func
        |> await
    )
```

Like normal [function composition](#function-composition), `and_then` and `and_then_await` will preserve all metadata attached to the first function in the composition.

##### Example

**Coconut:**
```coconut
load_and_send_data = (
    load_data_async()
    `and_then` proc_data
    `and_then_await` send_data
)
```

**Python:**
```coconut_python
async def load_and_send_data():
    return await send_data(proc_data(await load_data_async()))
```

### Built-Ins for Working with Iterators

```{contents}
---
local:
depth: 1
---
```

#### Enhanced Built-Ins

Coconut's `map`, `zip`, `filter`, `reversed`, and `enumerate` objects are enhanced versions of their Python equivalents that support:

- `reversed`
- `repr`
- Optimized normal (and iterator) indexing/slicing (`map`, `zip`, `reversed`, and `enumerate` but not `filter`).
- `len` (all but `filter`) (though `bool` will still always yield `True`).
- The ability to be iterated over multiple times if the underlying iterators can be iterated over multiple times.
- [PEP 618](https://www.python.org/dev/peps/pep-0618) `zip(..., strict=True)` support on all Python versions.
- Added `strict=True` support to `map` as well (enforces that iterables are the same length in the multi-iterable case; uses `zip` under the hood such that errors will show up as `zip(..., strict=True)` errors).
- Added attributes which subclasses can make use of to get at the original arguments to the object:
  * `map`: `func`, `iters`
  * `zip`: `iters`
  * `filter`: `func`, `iter`
  * `reversed`: `iter`
  * `enumerate`: `iter`, `start`

##### Indexing into other built-ins

Though Coconut provides random access indexing/slicing to `range`, `map`, `zip`, `reversed`, and `enumerate`, Coconut cannot index into built-ins like `filter`, `takewhile`, or `dropwhile` directly, as there is no efficient way to do so.

```coconut
range(10) |> filter$(i => i>3) |> .[0]  # doesn't work
```

In order to make this work, you can explicitly use iterator slicing, which is less efficient in the general case:

```coconut
range(10) |> filter$(i => i>3) |> .$[0]  # works
```

For more information on Coconut's iterator slicing, see [here](#iterator-slicing).

##### Examples

**Coconut:**
```coconut
map((+), range(5), range(6)) |> len |> print
range(10) |> filter$((x) => x < 5) |> reversed |> tuple |> print
```

**Python:**
_Can't be done without defining a custom `map` type. The full definition of `map` can be found in the Coconut header._

**Coconut:**
```coconut
range(0, 12, 2)[4]  # 8

map((i => i*2), range(10))[2]  # 4
```

**Python:**
_Can’t be done quickly without Coconut’s iterable indexing, which requires many complicated pieces. The necessary definitions in Python can be found in the Coconut header._

#### `reduce`

**reduce**(_function_, _iterable_[, _initial_], /)

Coconut re-introduces Python 2's `reduce` built-in, using the `functools.reduce` version.

##### Python Docs

**reduce**(_function, iterable_**[**_, initial_**]**)

Apply _function_ of two arguments cumulatively to the items of _sequence_, from left to right, so as to reduce the sequence to a single value. For example, `reduce((x, y) => x+y, [1, 2, 3, 4, 5])` calculates `((((1+2)+3)+4)+5)`. The left argument, _x_, is the accumulated value and the right argument, _y_, is the update value from the _sequence_. If the optional _initial_ is present, it is placed before the items of the sequence in the calculation, and serves as a default when the sequence is empty. If _initial_ is not given and _sequence_ contains only one item, the first item is returned.

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

#### `reiterable`

**reiterable**(_iterable_)

`reiterable` wraps the given iterable to ensure that every time the `reiterable` is iterated over, it produces the same results. Note that the result need not be a `reiterable` object if the given iterable is already reiterable. `reiterable` uses [`tee`](#tee) under the hood and `tee` can be used in its place, though `reiterable` is generally recommended over `tee`.

##### Example

**Coconut:**
```coconut
def list_type(xs):
    match reiterable(xs):
        case [fst, snd] :: tail:
            return "at least 2"
        case [fst] :: tail:
            return "at least 1"
        case (| |):
            return "empty"
```

**Python:**
_Can't be done without a long series of checks for each `match` statement. See the compiled code for the Python syntax._

#### `starmap`

**starmap**(_function_, _iterable_)

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

#### `zip_longest`

**zip\_longest**(*_iterables_, _fillvalue_=`None`)

Coconut provides an enhanced version of `itertools.zip_longest` as a built-in under the name `zip_longest`. `zip_longest` supports all the same features as Coconut's [enhanced zip](#enhanced-built-ins) as well as the additional attribute `fillvalue`.

##### Python Docs

**zip\_longest**(_\*iterables, fillvalue=None_)

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

#### `takewhile`

**takewhile**(_predicate_, _iterable_, /)

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
negatives = numiter |> takewhile$(x => x < 0)
```

**Python:**
```coconut_python
import itertools
negatives = itertools.takewhile(lambda x: x < 0, numiter)
```

#### `dropwhile`

**dropwhile**(_predicate_, _iterable_, /)

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
positives = numiter |> dropwhile$(x => x < 0)
```

**Python:**
```coconut_python
import itertools
positives = itertools.dropwhile(lambda x: x < 0, numiter)
```

#### `flatten`

**flatten**(_iterable_, _levels_=`1`)

Coconut provides an enhanced version of `itertools.chain.from_iterable` as a built-in under the name `flatten` with added support for `reversed`, `repr`, `in`, `.count()`, `.index()`, and `fmap`.

By default, `flatten` only flattens the top level of the given iterable/array. If _levels_ is passed, however, it can be used to control the number of levels flattened, with `0` meaning no flattening and `None` flattening as many iterables as are found. Note that if _levels_ is set to any non-`None` value, the first _levels_ levels must be iterables, or else an error will be raised.

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

#### `scan`

**scan**(_function_, _iterable_[, _initial_])

Coconut provides a modified version of `itertools.accumulate` with opposite argument order as `scan` that also supports `repr`, `len`, and `func`/`iter`/`initial` attributes. `scan` works exactly like [`reduce`](#reduce), except that instead of only returning the last accumulated value, it returns an iterator of all the intermediate values.

##### Python Docs

**scan**(_function, iterable_**[**_, initial_**]**)

Make an iterator that returns accumulated results of some function of two arguments. Elements of the input iterable may be any type that can be accepted as arguments to _function_. (For example, with the operation of addition, elements may be any addable type including Decimal or Fraction.) If the input iterable is empty, the output iterable will also be empty.

If no _initial_ is given, roughly equivalent to:
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

#### `count`

**count**(_start_=`0`, _step_=`1`)

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

#### `cycle`

**cycle**(_iterable_, _times_=`None`)

Coconut's `cycle` is a modified version of `itertools.cycle` with a `times` parameter that controls the number of times to cycle through _iterable_ before stopping. `cycle` also supports `in`, slicing, `len`, `reversed`, `.count()`, `.index()`, and `repr`.

##### Python Docs

**cycle**(_iterable_)

Make an iterator returning elements from the iterable and saving a copy of each. When the iterable is exhausted, return elements from the saved copy. Repeats indefinitely. Roughly equivalent to:

```coconut_python
def cycle(iterable):
    # cycle('ABCD') --> A B C D A B C D A B C D ...
    saved = []
    for element in iterable:
        yield element
        saved.append(element)
    while saved:
        for element in saved:
              yield element
```

Note, this member of the toolkit may require significant auxiliary storage (depending on the length of the iterable).

##### Example

**Coconut:**
```coconut
cycle(range(2), 2) |> list |> print
```

**Python:**
```coconut_python
from itertools import cycle, islice
print(list(islice(cycle(range(2)), 4)))
```

#### `cartesian_product`

**cartesian\_product**(*_iterables_, _repeat_=`1`)

Coconut provides an enhanced version of `itertools.product` as a built-in under the name `cartesian_product` with added support for `len`, `repr`, `in`, `.count()`, and `fmap`.

Additionally, `cartesian_product` includes special support for [`numpy`](#numpy-integration) objects, in which case a multidimensional array is returned instead of an iterator.

##### Python Docs

**cartesian\_product**(_\*iterables, repeat=1_)

Cartesian product of input iterables.

Roughly equivalent to nested for-loops in a generator expression. For example, `cartesian_product(A, B)` returns the same as `((x,y) for x in A for y in B)`.

The nested loops cycle like an odometer with the rightmost element advancing on every iteration. This pattern creates a lexicographic ordering so that if the input’s iterables are sorted, the product tuples are emitted in sorted order.

To compute the product of an iterable with itself, specify the number of repetitions with the optional repeat keyword argument. For example, `product(A, repeat=4)` means the same as `cartesian_product(A, A, A, A)`.

This function is roughly equivalent to the following code, except that the actual implementation does not build up intermediate results in memory:

```coconut_python
def cartesian_product(*args, repeat=1):
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    pools = [tuple(pool) for pool in args] * repeat
    result = [[]]
    for pool in pools:
        result = [x+[y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)
```

Before `cartesian_product()` runs, it completely consumes the input iterables, keeping pools of values in memory to generate the products. Accordingly, it is only useful with finite inputs.

##### Example

**Coconut:**
```coconut
v = [1, 2]
assert cartesian_product(v, v) |> list == [(1, 1), (1, 2), (2, 1), (2, 2)]
```

**Python:**
```coconut_python
from itertools import product
v = [1, 2]
assert list(product(v, v)) == [(1, 1), (1, 2), (2, 1), (2, 2)]
```

#### `multi_enumerate`

**multi\_enumerate**(_iterable_)

Coconut's `multi_enumerate` enumerates through an iterable of iterables. `multi_enumerate` works like enumerate, but indexes through inner iterables and produces a tuple index representing the index in each inner iterable. Supports indexing.

For [`numpy`](#numpy-integration) objects, uses [`np.nditer`](https://numpy.org/doc/stable/reference/generated/numpy.nditer.html) under the hood. Also supports `len` for [`numpy`](#numpy-integration) arrays.

##### Example

**Coconut:**
```coconut_pycon
>>> [1, 2;; 3, 4] |> multi_enumerate |> list
[((0, 0), 1), ((0, 1), 2), ((1, 0), 3), ((1, 1), 4)]
```

**Python:**
```coconut_python
array = [[1, 2], [3, 4]]
enumerated_array = []
for i in range(len(array)):
    for j in range(len(array[i])):
        enumerated_array.append(((i, j), array[i][j]))
```

#### `groupsof`

**groupsof**(_n_, _iterable_, _fillvalue_=`...`)

Coconut provides the `groupsof` built-in to split an iterable into groups of a specific length. Specifically, `groupsof(n, iterable)` will split `iterable` into tuples of length `n`, with only the last tuple potentially of size `< n` if the length of `iterable` is not divisible by `n`. If that is not the desired behavior, _fillvalue_ can be passed and will be used to pad the end of the last tuple to length `n`.

Additionally, `groupsof` supports `len` when `iterable` supports `len`.

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

#### `windowsof`

**windowsof**(_size_, _iterable_, _fillvalue_=`...`, _step_=`1`)

`windowsof` produces an iterable that effectively mimics a sliding window over _iterable_ of size _size_. _step_ determines the spacing between windows.

If _size_ is larger than _iterable_, `windowsof` will produce an empty iterable. If that is not the desired behavior, _fillvalue_ can be passed and will be used in place of missing values. Also, if _fillvalue_ is passed and the length of the _iterable_ is not divisible by _step_, _fillvalue_ will be used in that case to pad the last window as well. Note that _fillvalue_ will only ever appear in the last window.

Additionally, `windowsof` supports `len` when `iterable` supports `len`.

##### Example

**Coconut:**
```coconut
assert "12345" |> windowsof$(3) |> list == [("1", "2", "3"), ("2", "3", "4"), ("3", "4", "5")]
```

**Python:**
_Can't be done without the definition of `windowsof`; see the compiled header for the full definition._

#### `collectby`

**collectby**(_key\_func_, _iterable_, _value\_func_=`None`, _reduce\_func_=`None`)

`collectby(key_func, iterable)` collects the items in `iterable` into a dictionary of lists keyed by `key_func(item)`.

If `value_func` is passed, `collectby(key_func, iterable, value_func=value_func)` instead collects value_func(item) into each list instead of item.

If `reduce_func` is passed, `collectby(key_func, iterable, reduce_func=reduce_func)`, instead of collecting the items into lists, reduces over the items of each key with reduce_func, effectively implementing a MapReduce operation.

`collectby` is effectively equivalent to:
```coconut_python
from collections import defaultdict

def collectby(key_func, iterable, value_func=ident, reduce_func=None):
    collection = defaultdict(list) if reduce_func is None else {}
    for item in iterable:
        key = key_func(item)
        value = value_func(item)
        if reduce_func is None:
            collection[key].append(value)
        else:
            old_value = collection.get(key, sentinel)
            if old_value is not sentinel:
                value = reduce_func(old_value, value)
            collection[key] = value
    return collection
```

`collectby` is similar to [`itertools.groupby`](https://docs.python.org/3/library/itertools.html#itertools.groupby) except that `collectby` aggregates common elements regardless of their order in the input iterable, whereas `groupby` only aggregates common elements that are adjacent in the input iterable.

##### Example

**Coconut:**
```coconut
user_balances = (
    balance_data
    |> collectby$(.user, value_func=.balance, reduce_func=(+))
)
```

**Python:**
```coconut_python
from collections import defaultdict

user_balances = defaultdict(int)
for item in balance_data:
    user_balances[item.user] += item.balance
```

#### `all_equal`

**all\_equal**(_iterable_)

Coconut's `all_equal` built-in takes in an iterable and determines whether all of its elements are equal to each other. `all_equal` assumes transitivity of equality and that `!=` is the negation of `==`. Special support is provided for [`numpy`](#numpy-integration) objects.

##### Example

**Coconut:**
```coconut
all_equal([1, 1, 1])
all_equal([1, 1, 2])
```

**Python:**
```coconut_python
sentinel = object()
def all_equal(iterable):
    first_item = sentinel
    for item in iterable:
        if first_item is sentinel:
            first_item = item
        elif first_item != item:
            return False
    return True
all_equal([1, 1, 1])
all_equal([1, 1, 2])
```

#### `parallel_map`

**parallel\_map**(_function_, *_iterables_, *, _chunksize_=`1`, _strict_=`False`)

Coconut provides a parallel version of `map` under the name `parallel_map`. `parallel_map` makes use of multiple processes, and is therefore much faster than `map` for CPU-bound tasks. `parallel_map` never loads the entire input iterator into memory, though it does consume the entire input iterator as soon as a single output is requested. If any exceptions are raised inside of `parallel_map`, a traceback will be printed as soon as they are encountered.

Because `parallel_map` uses multiple processes for its execution, it is necessary that all of its arguments be pickleable. Only objects defined at the module level, and not lambdas, objects defined inside of a function, or objects defined inside of the interpreter, are pickleable. Furthermore, on Windows, it is necessary that all calls to `parallel_map` occur inside of an `if __name__ == "__main__"` guard.

`parallel_map` supports a `chunksize` argument, which determines how many items are passed to each process at a time. Larger values of _chunksize_ are recommended when dealing with very long iterables. Additionally, in the multi-iterable case, _strict_ can be set to `True` to ensure that all iterables are the same length.

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

#### `concurrent_map`

**concurrent\_map**(_function_, *_iterables_, *, _chunksize_=`1`, _strict_=`False`)

Coconut provides a concurrent version of [`parallel_map`](#parallel_map) under the name `concurrent_map`. `concurrent_map` behaves identically to `parallel_map` (including support for `concurrent_map.multiple_sequential_calls`) except that it uses multithreading instead of multiprocessing, and is therefore primarily useful only for IO-bound tasks due to CPython's Global Interpreter Lock.

##### Python Docs

**concurrent_map**(_func, \*iterables_, _chunksize_=`1`)

Equivalent to `map(func, *iterables)` except _func_ is executed asynchronously and several calls to _func_ may be made concurrently. If a call raises an exception, then that exception will be raised when its value is retrieved from the iterator.

`concurrent_map` chops the iterable into a number of chunks which it submits to the thread pool as separate tasks. The (approximate) size of these chunks can be specified by setting _chunksize_ to a positive integer. For very long iterables using a large value for _chunksize_ can make the job complete **much** faster than using the default value of `1`.

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

#### `tee`

**tee**(_iterable_, _n_=`2`)

Coconut provides an optimized version of `itertools.tee` as a built-in under the name `tee`.

Though `tee` is not deprecated, [`reiterable`](#reiterable) is generally recommended over `tee`.

Custom `tee`/`reiterable` implementations for custom [Containers/Collections](https://docs.python.org/3/library/collections.abc.html) should be put in the `__copy__` method. Note that all [Sequences/Mappings/Sets](https://docs.python.org/3/library/collections.abc.html) are always assumed to be reiterable even without calling `__copy__`.

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

#### `consume`

**consume**(_iterable_, _keep\_last_=`0`)

Coconut provides the `consume` function to efficiently exhaust an iterator and thus perform any lazy evaluation contained within it. `consume` takes one optional argument, `keep_last`, that defaults to 0 and specifies how many, if any, items from the end to return as a sequence (`None` will keep all elements).

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
range(10) |> map$((x) => x**2) |> map$(print) |> consume
```

**Python:**
```coconut_python
collections.deque(map(print, map(lambda x: x**2, range(10))), maxlen=0)
```

### Typing-Specific Built-Ins

```{contents}
---
local:
depth: 1
---
```

#### `TYPE_CHECKING`

The `TYPE_CHECKING` variable is set to `False` at runtime and `True` during type_checking, allowing you to prevent your `typing` imports and `TypeVar` definitions from being executed at runtime. By wrapping your `typing` imports in an `if TYPE_CHECKING:` block, you can even use the [`typing`](https://docs.python.org/3/library/typing.html) module on Python versions that don't natively support it. Furthermore, `TYPE_CHECKING` can also be used to hide code that is mistyped by default.

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

#### `reveal_type` and `reveal_locals`

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

```{contents}
---
local:
depth: 2
---
```

### `coconut.embed`

**coconut.embed**(_kernel_=`None`, _depth_=`0`, \*\*_kwargs_)

If _kernel_=`False` (default), embeds a Coconut Jupyter console initialized from the current local namespace. If _kernel_=`True`, launches a Coconut Jupyter kernel initialized from the local namespace that can then be attached to. The _depth_ indicates how many additional call frames to ignore. _kwargs_ are as in [IPython.embed](https://ipython.readthedocs.io/en/stable/api/generated/IPython.terminal.embed.html#IPython.terminal.embed.embed) or [IPython.embed_kernel](https://ipython.readthedocs.io/en/stable/api/generated/IPython.html#IPython.embed_kernel) based on _kernel_.

Recommended usage is as a debugging tool, where the code `from coconut import embed; embed()` can be inserted to launch an interactive Coconut shell initialized from that point.

### Automatic Compilation

Automatic compilation lets you simply import Coconut files directly without having to go through a compilation step first. Automatic compilation can be enabled either by importing [`coconut.api`](#coconut-api) before you import anything else, or by running `coconut --site-install`.

Once automatic compilation is enabled, Coconut will check each of your imports to see if you are attempting to import a `.coco` file and, if so, automatically compile it for you. Note that, for Coconut to know what file you are trying to import, it will need to be accessible via `sys.path`, just like a normal import.

Automatic compilation always compiles with `--target sys --line-numbers --keep-lines` by default. On Python 3.4+, automatic compilation will use a `__coconut_cache__` directory to cache the compiled Python. Note that `__coconut_cache__` will always be removed from `__file__`.

Automatic compilation is always available in the Coconut interpreter or when using [`coconut-run`](#coconut-scripts). When using auto compilation through the Coconut interpreter, any compilation options passed in will also be used for auto compilation. Additionally, the interpreter always allows importing from the current working directory, letting you easily compile and play around with a `.coco` file simply by running the Coconut interpreter and importing it.

If using the Coconut interpreter, a `reload` built-in is always provided to easily reload (and thus recompile) imported modules.

### Coconut Encoding

While automatic compilation is the preferred method for dynamically compiling Coconut files, as it caches the compiled code as a `.py` file to prevent recompilation, Coconut also supports a special
```coconut
# coding: coconut
```
declaration which can be added to `.py` files to have them treated as Coconut files instead. To use such a coding declaration, you'll need to either run `coconut --site-install` or `import coconut.api` at some point before you first attempt to import a file with a `# coding: coconut` declaration. Like automatic compilation, the Coconut encoding is always available from the Coconut interpreter. Compilation always uses the same parameters as in the [Coconut Jupyter kernel](#kernel).

### `coconut.api`

In addition to enabling automatic compilation, `coconut.api` can also be used to call the Coconut compiler from code instead of from the command line. See below for specifications of the different api functions.

_Deprecated: `coconut.convenience` is a deprecated alias for `coconut.api`._

#### `get_state`

**coconut.api.get\_state**(_state_=`None`)

Gets a state object which stores the current compilation parameters. State objects can be configured with [**setup**](#setup) or [**cmd**](#cmd) and then used in [**parse**](#parse) or other endpoints.

If _state_ is `None`, gets a new state object, whereas if _state_ is `False`, the global state object is returned.

#### `parse`

**coconut.api.parse**(_code_=`""`, _mode_=`"sys"`, _state_=`False`, _keep\_internal\_state_=`None`)

Likely the most useful of the api functions, `parse` takes Coconut code as input and outputs the equivalent compiled Python code. _mode_ is used to indicate the context for the parsing and _state_ is the state object storing the compilation parameters to use as obtained from [**get_state**](#get_state) (if `False`, uses the global state object). _keep\_internal\_state_ determines whether the state object will keep internal state (such as what [custom operators](#custom-operators) have been declared)—if `None`, internal state will be kept iff you are not using the global _state_.

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
- `"lenient"`:
    + parser: lenient
        * Can parse any Coconut code, allows leading whitespace, and has no trailing newline.
    + header: none
- `"xonsh"`:
    + parser: xonsh
        * Parses Coconut [`xonsh`](https://xon.sh) code for use in [Coconut's `xonsh` support](#xonsh-support).
    + header: none

##### Example

```coconut_python
from coconut.api import parse
exec(parse())
while True:
    exec(parse(input(), mode="block"))
```

#### `setup`

**coconut.api.setup**(_target_=`None`, _strict_=`False`, _minify_=`False`, _line\_numbers_=`True`, _keep\_lines_=`False`, _no\_tco_=`False`, _no\_wrap_=`False`, *, _state_=`False`)

`setup` can be used to set up the given state object with the given compilation parameters, each corresponding to the command-line flag of the same name. _target_ should be either `None` for the default target or a string of any [allowable target](#allowable-targets).

If _state_ is `False`, the global state object is used.

#### `warm_up`

**coconut.api.warm_up**(_force_=`True`, _enable\_incremental\_mode_=`False`, *, _state_=`False`)

Can optionally be called to warm up the compiler and get it ready for parsing. Passing _force_ will cause the warm up to take longer but will substantially reduce parsing times (by default, this level of warm up is only done when the compiler encounters a large file). Passing _enable\_incremental\_mode_ will enable the compiler's incremental mdoe, where parsing some string, then later parsing a continuation of that string, will yield substantial performance improvements.

#### `cmd`

**coconut.api.cmd**(_args_=`None`, *, _argv_=`None`, _interact_=`False`, _default\_target_=`None`, _state_=`False`)

Executes the given _args_ as if they were fed to `coconut` on the command-line, with the exception that unless _interact_ is true or `-i` is passed, the interpreter will not be started. Additionally, _argv_ can be used to pass in arguments as in `--argv` and _default\_target_ can be used to set the default `--target`.

Has the same effect of setting the command-line flags on the given _state_ object as `setup` (with the global `state` object used when _state_ is `False`).

#### `coconut_exec`

**coconut.api.coconut_exec**(_expression_, _globals_=`None`, _locals_=`None`, _state_=`False`, _keep\_internal\_state_=`None`)

Version of [`exec`](https://docs.python.org/3/library/functions.html#exec) which can execute Coconut code.

#### `coconut_eval`

**coconut.api.coconut_eval**(_expression_, _globals_=`None`, _locals_=`None`, _state_=`False`, _keep\_internal\_state_=`None`)

Version of [`eval`](https://docs.python.org/3/library/functions.html#eval) which can evaluate Coconut code.

#### `version`

**coconut.api.version**(**[**_which_**]**)

Retrieves a string containing information about the Coconut version. The optional argument _which_ is the type of version information desired. Possible values of _which_ are:

- `"num"`: the numerical version (the default)
- `"name"`: the version codename
- `"spec"`: the numerical version with the codename attached
- `"tag"`: the version tag used in GitHub and documentation URLs
- `"-v"`: the full string printed by `coconut -v`

#### `auto_compilation`

**coconut.api.auto_compilation**(_on_=`True`, _args_=`None`, _use\_cache\_dir_=`None`)

Turns [automatic compilation](#automatic-compilation) on or off. This function is called automatically when `coconut.api` is imported.

If _args_ is passed, it will set the Coconut command-line arguments to use for automatic compilation. Arguments will be processed the same way as with [`coconut-run`](#coconut-scripts) such that `--quiet --target sys --keep-lines` will all be set by default.

If _use\_cache\_dir_ is passed, it will turn on or off the usage of a `__coconut_cache__` directory to put compile files in rather than compiling them in-place. Note that `__coconut_cache__` will always be removed from `__file__`.

#### `use_coconut_breakpoint`

**coconut.api.use_coconut_breakpoint**(_on_=`True`)

Switches the [`breakpoint` built-in](https://www.python.org/dev/peps/pep-0553/) which Coconut makes universally available to use [`coconut.embed`](#coconut-embed) instead of [`pdb.set_trace`](https://docs.python.org/3/library/pdb.html#pdb.set_trace) (or undoes that switch if `on=False`). This function is called automatically when `coconut.api` is imported.

#### `CoconutException`

If an error is encountered in a api function, a `CoconutException` instance may be raised. `coconut.api.CoconutException` is provided to allow catching such errors.

### `coconut.__coconut__`

It is sometimes useful to be able to access Coconut built-ins from pure Python. To accomplish this, Coconut provides `coconut.__coconut__`, which behaves exactly like the `__coconut__.py` header file included when Coconut is compiled in package mode.

All Coconut built-ins are accessible from `coconut.__coconut__`. The recommended way to import them is to use `from coconut.__coconut__ import` and import whatever built-ins you'll be using.

##### Example

```coconut_python
from coconut.__coconut__ import parallel_map
```
