# Coconut Contributing Guidelines

**Anyone is welcome to submit a pull request regardless of whether or not they have read this document.** The purpose of this document is simply to explain the contribution process and the internals of how Coconut works to make contributing easier.

## Asking Questions

If you are thinking about contributing to Coconut, please don't hesitate to ask questions at Coconut's [Gitter](https://gitter.im/evhub/coconut)! That includes any questions at all about contributing, including understanding the source code, figuring out how to implement a specific change, or just trying to figure out what needs to be done.

## Contribution Process

Contributing to Coconut is as simple as

1. forking Coconut on [GitHub](https://github.com/evhub/coconut),
2. making changes to the [`develop` branch](https://github.com/evhub/coconut/tree/develop), and
3. proposing a pull request.

## File Layout

- `DOCS.md`
    + Markdown file containing detailed documentation on every Coconut feature. If you are adding a new feature, you should also add documentation on it to this file.
- `FAQ.md`
    + Markdown file containing frequently asked questions and their answers. If you had a question you wished was answered earlier when learning Coconut, you should add it to this file.
- `HELP.md`
    + Markdown file containing Coconut's tutorial. The tutorial should be a streamlined introduction to Coconut and all of its most important features.
- `Makefile`
    + Contains targets for installing Coconut, building the documentation, checking for dependency updates, etc. The target `make dev` will automatically install the full Coconut developer environment.
- `setup.py`
    + Using information from `requirements.py` and `constants.py` to install Coconut. Also reads `README.rst` to generate the PyPI description.
- `conf.py`
    + Sphinx configuration file for Coconut's documentation.
- coconut
    - `__coconut__.py`
        + Mimics the Coconut header by generating and executing it when imported. Used by the REPL.
    - `__init__.py`
        + Includes the implementation of the `%coconut` IPython magic.
    - `__main__.py`
        + Imports and runs `main` from `main.py`.
    - `constants.py`
        + All constants used across Coconut are defined here, including dependencies, magic numbers/strings, etc.
    - `convenience.py`
        + Contains `cmd`, `version`, `setup`, and `parse` functions as convenience utilities when using Coconut as a module. Documented in `DOCS.md`.
    - `exceptions.py`
        + All of the exceptions raised by Coconut are defined here, both those shown to the user and those used only internally.
    - `highlighter.py`
        + Contains Coconut's Pygments syntax highlighter, as well as modified Python highlighters that don't fail if they encounter unknown syntax.
    - `main.py`
        + Contains `main` and `main_run`, the entry points for the `coconut` and `coconut-run` commands, respectively.
    - `requirements.py`
        + Processes Coconut's requirements from `constants.py` into a form `setup.py` can use, as well as checks for updates to Coconut's dependencies.
    - `root.py`
        + `root.py` creates and executes the part of Coconut's header that normalizes Python built-ins across versions. Whenever you are writing a new file, you should always add `from coconut.root import *` to ensure compatibility with different Python versions. `root.py` also sets basic version-related constants.
    - `terminal.py`
        + Contains utilities for displaying messages to the console, mainly `logger`, which is Coconut's primary method of logging a message from anywhere.
    - command
        - `__init__.py`
            + Imports everything in `command.py`.
        - `cli.py`
            + Creates the `ArgumentParser` object used to parse Coconut command-line arguments.
        - `command.py`
            + Contains `Command`, whose `start` method is the main entry point for the Coconut command-line utility.
        - `util.py`
            + Contains utilities used by `command.py`, including `Prompt` for getting syntax-highlighted input, and `Runner` for executing compiled Python.
        - `watch.py`
            + Contains classes necessary for Coconut's `--watch` flag.
    - compiler
        - `__init__.py`
            + Imports everything in `compiler.py`.
        - `compiler.py`
            + Contains `Compiler`, the class that actually compiles Coconut code. `Compiler` inherits from `Grammar` in `grammar.py` to get all of the basic grammatical definitions, then extends them with all of the handlers that depend on the compiler's options (e.g. the current `--target`). `Compiler` also does pre- and post-processing, including replacing strings with markers (pre-processing) and adding the header (post-processing).
        - `grammar.py`
            + Contains `Grammar`, the class that specifies Coconut's grammar in PyParsing. Coconut performs one-pass compilation by attaching "handlers" to specific grammar objects to transform them into compiled Python. `grammar.py` contains all basic (non-option-dependent) handlers.
        - `header.py`
            + Contains `getheader`, which generates the header at the top of all compiled Coconut files.
        - `matching.py`
            + Contains `Matcher`, which handles the compilation of all Coconut pattern-matching, including `match` statements, destructuring assignment, and pattern-matching functions.
        - `util.py`
            + Contains utilities for working with PyParsing objects that are primarily used by `grammar.py`.
    - icoconut
        - `__init__.py`
            + Imports everything from `icoconut/root.py`.
        - `__main__.py`
            + Contains the main entry point for Coconut's Jupyter kernel.
        - `root.py`
            + Contains the implementation of Coconut's Jupyter kernel, made by subclassing the IPython kernel.
    - stubs
        - `__coconut__.pyi`
            + A MyPy stub file for specifying the type of all the objects defined in Coconut's package header (which is saved as `__coconut__.py`).
- tests
    - `__init__.py`
        + Imports everything in `main_test.py`.
    - `__main__.py`
        + When run, compiles all of the test source code, but _does not run any tests_. To run the tests, the command `make test`, or a  `pytest` command to run a specific test, is necessary.
    - `main_test.py`
        + Contains `TestCase` subclasses that run all of the commands for testing the Coconut files in `src`.
    - src
        - `extras.coco`
            + Directly imports and calls functions in the Coconut package, including from `convenience.py` and icoconut.
        - `runnable.coco`
            + Makes sure the argument `--arg` was passed when running the file.
        - `runner.coco`
            + Runs `main` from `cocotest/agnostic/main.py`.
        - cocotest
            + _Note: Files in the folders below all get compiled into the top-level cocotest directory. The folders are only for differentiating what files to compile on what Python version._
            - agnostic
                - `__init__.coco`
                    + Contains a docstring that `main.coco` asserts exists.
                - `main.coco`
                    + Contains the main test entry point as well as many simple, one-line tests.
                - `specific.coco`
                    + Tests to be run only on a specific Python version, but not necessarily only under a specific `--target`.
                - `suite.coco`
                    + Tests objects defined in `util.coco`.
                - `tutorial.coco`
                    + Tests all the examples in `TUTORIAL.md`.
                - `util.coco`
                    + Contains objects used in `suite.coco`.
            - python2
                - `py2_test.coco`
                    + Tests to be run only on Python 2 with `--target 2`.
            - python3
                - `py3_test.coco`
                    + Tests to be run only on Python 3 with `--target 3`.
            - python35
                - `py35_test.coco`
                    + Tests to be run only on Python 3.5 with `--target 3.5`.
