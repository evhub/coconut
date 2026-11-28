# Coconut Contributing Guidelines

_By contributing to Coconut, you agree to your contribution being released under [Coconut's Apache 2.0 license](https://github.com/evhub/coconut/blob/develop/LICENSE.txt)._

**Anyone is welcome to submit an issue or pull request!** This document explains the contribution process, how Coconut works internally, how to test changes, and how releases are made.

Contributions are made against the [`develop` branch](https://github.com/evhub/coconut/tree/develop), so make sure you're reading [the `develop` version of these guidelines](https://coconut.readthedocs.io/en/develop/CONTRIBUTING.html).

## Getting Started

### Asking Questions

The best place to ask a question, including about contributing, understanding the source code, or figuring out how to implement something, is to [open a GitHub issue](https://github.com/evhub/coconut/issues/new). Questions are always welcome there. (Coconut's old Gitter chat room is no longer used.)

### Good First Issues

Want to help out but don't know what to work on? Look through the [issues labeled "good first issue"](https://github.com/evhub/coconut/labels/good%20first%20issue). They need less knowledge of Coconut's internals, so new contributors can take them on.

### Contribution Process

1. Fork Coconut on [GitHub](https://github.com/evhub/coconut) and make a branch off of `develop`.
2. Make your changes, including tests (see [Testing](#testing)) and, for any user-facing change, documentation in [`DOCS.md`](./DOCS.md).
3. Open a pull request against `develop`.

_Note: Don't forget to add yourself to the `Author:`/`Authors:` line in the module docstring of any file you modify!_

### Using AI Coding Assistants

If you use an AI coding assistant, these resources help it work on Coconut:

- [`.claude/CLAUDE.md`](https://github.com/evhub/coconut/blob/develop/.claude/CLAUDE.md) has project instructions (commands, architecture, conventions) that Claude Code loads automatically. Point other assistants at it.
- `coconut --ai-docs` prints Coconut's condensed guide to writing idiomatic Coconut ([`coconut/llms.txt`](https://github.com/evhub/coconut/blob/develop/coconut/llms.txt), also served at [coconut.readthedocs.io/en/latest/llms.txt](https://coconut.readthedocs.io/en/latest/llms.txt)). It's useful when writing `.coco` tests. `test_ai_docs` runs its code examples, so keep them working when you change syntax.
- This repository is also a Claude Code plugin marketplace (`.claude-plugin/`, `editors/claude-code/`) that gives Claude the Coconut language server and MCP tools; see [AI Coding Assistant Support](./DOCS.md#ai-coding-assistant-support).
- On GitHub, `.github/workflows/claude.yml` runs Claude Code when `@claude` is mentioned in an issue or PR comment, and `.github/workflows/claude-code-review.yml` posts an automated Claude code review on pull requests.

## Development Setup

Use a Python 3 virtual environment (`.venv` is gitignored), then run `make dev`:

```bash
git clone https://github.com/<your-username>/coconut.git
cd coconut
git checkout develop
python -m venv .venv && . .venv/bin/activate
make dev
```

`make dev` does the following:

1. `make clean`: deletes build and docs output, `coconut/tests/dest`, and all `__coconut_cache__` directories.
2. `make setup`: runs `ensurepip` and upgrades `setuptools`, `wheel`, `pip`, and `cython`.
3. `pip install --upgrade -e .[dev]`: an editable install of `coconut-develop` with every optional dependency (Jupyter, MyPy, Pyright, the language server, xonsh, numpy/pandas/xarray, watchdog, Sphinx, pytest, ...), plus pure-Python `pyparsing` and the dev tools `pre-commit`, `requests`, `vprof`, and `py-spy`. If a release `coconut` is installed in the same environment, `pip uninstall coconut` first.
4. `pre-commit install -f --install-hooks`: runs autopep8, flake8, and the [pre-commit](https://pre-commit.com/) hooks in `.pre-commit-config.yaml` on every `git commit`.
5. `coconut --site-install`: adds `zcoconut.pth` to `site-packages` so that `coconut.api` is imported at startup, which makes `.coco` files importable. Undo it with `coconut --site-uninstall`.

Other setup targets:

- `make install`: `pip install -e .[tests]`, which installs only the dependencies the test suite needs on the current Python. This is what CI runs. `install-py2`, `install-py3`, `install-pypy`, and `install-pypy3` do the same with `python2`, `python3`, `pypy`, and `pypy3`. `make install-purepy` installs with `--no-deps` plus `pyparsing<3`.
- `make dev-py2` and `make dev-py3` are `make dev` for `python2` and `python3`.
- `make format`: runs `make dev`, then `pre-commit autoupdate` and every hook on every file.
- `make docs`: builds the documentation into `docs/` with Sphinx and MyST (needs the `docs` extra, which `.[dev]` includes).
- `make check-reqs`: checks PyPI for newer versions of Coconut's dependencies.
- `make clean` removes test and build output. `make wipe` also removes `*.egg-info`, `__pycache__`, and `.pyc` files, runs `--site-uninstall`, and `pip uninstall`s `coconut` and `coconut-develop` (it asks for confirmation).
- Profiling: `make profile`, `make pyspy` (plus `pyspy-purepy`, `pyspy-native`, `pyspy-runtime`), `make vprof-time`, and `make vprof-memory`.

Once you're set up, `python -m coconut -c "<code>"` compiles and runs a snippet, and `coconut` gives you the interpreter.

## Architecture

### Compilation Pipeline

Compilation happens in `Compiler.parse` in `coconut/compiler/compiler.py`:

1. **Pre-processing** (`Compiler.preprocs`): `str_proc` replaces every string and comment with a marker that refers to its stored contents, so the grammar never sees what's inside them. `passthrough_proc` does the same for `\(...)` code passthroughs, `operator_proc` handles custom `operator` declarations, and `ind_proc` turns indentation into explicit open/close indentation marker characters.
2. **Parsing**: a single pass of the PyParsing grammar in `coconut/compiler/grammar.py`. Handlers that transform Coconut into Python are attached to grammar elements with `attach` from `coconut/compiler/util.py`. Handlers that depend on compiler options such as `--target` are bound in `Compiler.bind`. A handler doesn't run as soon as its element matches: it creates a node in a **computation graph**, and the graph is only evaluated once the parse is certain (`final`/`evaluate_tokens`). That way backtracking doesn't repeat handler work, and parse results can be cached. Parsing uses [cPyparsing](https://github.com/evhub/cpyparsing) when it's available, or pure-Python `pyparsing` otherwise (`coconut/_pyparsing.py`). On CPython 3.8+ with cPyparsing, parse results are also saved to `__coconut_cache__/*.pkl` next to the source file, so recompiling a slightly changed file is faster.
3. **Post-processing** (`Compiler.postprocs`): inserts deferred code, puts back passthroughs, indentation, strings, and comments, adds the line-number comments that point back to the Coconut source, prepends the header (`coconut/compiler/header.py`, which fills in `templates/header.py_template`), and polishes the result. `run_final_checks` then reports any remaining errors and warnings.

### File Layout

Top level:

- `DOCS.md`: documentation for every Coconut feature. Document new features here.
- `HELP.md`: the tutorial. `test_tutorial` checks its examples.
- `FAQ.md`: frequently asked questions. If you had a question you wish had been answered earlier when learning Coconut, add it here.
- `README.rst`: the PyPI description. `conf.py` also turns it into the documentation's `index.rst`.
- `Makefile`: targets for setup, testing, docs, releases, and profiling.
- `setup.py`, `setup.cfg`, `pyproject.toml`, `MANIFEST.in`: packaging. Requirements are defined in `coconut/constants.py`.
- `conf.py`, `.readthedocs.yaml`: the Sphinx/MyST configuration for [readthedocs](https://coconut.readthedocs.io). The docs also serve `coconut/llms.txt` and an interactive version of the tutorial.
- `interactive_tutorial.py`: generates the interactive tutorial, which runs every example in the browser with Pyodide.
- `.gitattributes`: tells git and GitHub to treat `.coco` and `.py_template` files as Python (`diff=python`, `linguist-language=python`). If you add a new file extension containing Python-like code, add the same rules for it here.
- `__coconut__/`, `_coconut/`: type stubs for the compiled header. `__coconut__/__init__.pyi` must match every built-in the header defines. `--mypy` and `--pyright` link these directories, along with the `coconut` package, into `$COCONUT_HOME/.coconut_stubs`.
- `xontrib/coconut.py`: the xonsh xontrib.
- `editors/claude-code/`, `.claude-plugin/marketplace.json`: the Claude Code plugin.
- `.claude/CLAUDE.md`: instructions for AI coding assistants.
- `.github/workflows/`, `.appveyor.yml`: CI (see [What CI Covers](#what-ci-covers)).

`coconut/`:

- `root.py`: version constants (`VERSION`, `VERSION_NAME`, `DEVELOP`, `ALPHA`) and the header code that makes Python 2 and 3 built-ins behave alike. Every module starts with `from coconut.root import *`.
- `constants.py`: every global constant, including platform flags (`PY39`, `PYPY`, `WINDOWS`, `MYPY`, ...), dependencies and version bounds, supported targets, built-in lists, and environment variables.
- `requirements.py`: turns the requirements in `constants.py` into `setup.py` requirements and extras, and implements `make check-reqs`.
- `api.py`: the external API (`cmd`, `parse`, `setup`, `auto_compilation`, the import hook, ...). `convenience.py` is a deprecated alias for it.
- `main.py`: the entry points for `coconut` and `coconut-run`.
- `__init__.py` and `integrations.py`: `embed`, the `%coconut` IPython extension, and the xonsh integration.
- `__coconut__.py`: does what a compiled `__coconut__.py` header module would do (used by the interpreter).
- `_pyparsing.py`: chooses between cPyparsing and pyparsing and sets up packrat/incremental parsing and the computation graph.
- `exceptions.py`, `terminal.py` (`logger`, used for all console output), `util.py`, and `highlighter.py` (Pygments lexers).
- `project_config.py`: the `[tool.coconut]` table in `pyproject.toml`.
- `pytest_plugin.py`: the opt-in `pytest -p coconut.pytest_plugin` plugin.
- `llms.txt`: the AI guide that `coconut --ai-docs` prints.
- `command/`: the command-line tool. `command.py` holds `Command`, whose `start` method is the CLI entry point. `cli.py` defines the arguments. `util.py` has `Prompt`, `Runner`, stub installation, and subprocess helpers. `mypy.py` and `watch.py` implement `--mypy` and `--watch`, and `resources/zcoconut.pth` is used by `--site-install`.
- `compiler/`: `compiler.py` (`Compiler`, which inherits the grammar from `Grammar` in `grammar.py`), `matching.py` (`Matcher`, which compiles all pattern matching), `exhaustiveness.py` (exhaustiveness checks of pattern matching that only type checkers see), `header.py` and `templates/header.py_template` (the header), and `util.py` (PyParsing utilities and the computation graph).
- `icoconut/`: the Jupyter kernel (`root.py`, `embed.py`, `__main__.py`, and the kernel specs).
- `lsp/`: the language server (`coconut --lsp`), its command line (`python -m coconut.lsp`), and the MCP server (`coconut --mcp`). The hover documentation in `data/docs.json` is generated from `DOCS.md` by `python -m coconut.lsp.generate_docs`, and `lsp_test.py` fails if it's out of date.
- `tests/`: the test suite (see [Testing](#testing)).

## Testing

### Writing Tests

Most of Coconut's tests are written in Coconut, as `assert` statements in `.coco` files under `coconut/tests/src/`. `make test` compiles them with `--strict` (except `non_strict/`), so test code has to pass strict mode.

- `cocotest/agnostic/` is compiled with whichever target the run uses:
  - `primary_1.coco`, `primary_2.coco`: most simple tests of syntax and built-ins.
  - `util.coco` and `suite.coco`: larger definitions go in `util.coco`, and the tests that use them go in `suite.coco`.
  - `specific.coco`: tests that depend on the Python version running them rather than on `--target`.
  - `tutorial.coco`: examples from the website and the tutorial.
  - `main.coco`: the entry point. `run_main` decides which sub-suites run on which Python version.
- `cocotest/target_<N>/` (`target_2`, `target_3`, `target_35`, `target_36`, `target_38`, `target_311`, `target_314`) is compiled with `--target <N>` and only run on Python versions that support it. Use these folders for syntax that needs a specific target.
- `cocotest/target_sys/` is compiled with `--target sys`. `builtins_typing_test.coco` checks that the built-in type stubs are precise, so update it along with `__coconut__/__init__.pyi` when you add or change a built-in.
- `cocotest/non_strict/` is compiled without `--strict`, for code that strict mode disallows.
- `extras.coco` uses Coconut's API directly. It holds tests of compile errors and warnings (e.g. `assert_raises(-> parse("..."), CoconutSyntaxError)`), `parse`/`setup`/`cmd`, incremental parsing, the Jupyter kernel, and numpy/pandas/xarray support.
- `runner.coco` runs the compiled `cocotest` package. `runnable.coco` and `importable.coco` are used for the `coconut-run`, import hook, and `--and` tests.
- `coconut/tests/main_test.py` holds the Python-level pytest tests. `TestShell` covers command-line behavior and integrations such as MyPy/Pyright output, Jupyter, xonsh, the pytest plugin, and the tutorial. `TestCompilation` compiles and runs the whole suite with different flags. `TestExternal` compiles other projects written in Coconut. CLI-level tests go here.
- `coconut/tests/lsp_test.py` tests the language server, its CLI, and the MCP server. `coconut/tests/constants_test.py` checks `constants.py`.

All the folders under `cocotest/` are compiled into a single `coconut/tests/dest/cocotest` package. To add a new `target_<N>` folder, add a `comp_<N>` function to `main_test.py`, call it from both `run()` and `comp_all()`, and import the new tests in `run_main` in `main.coco`.

When you change `DOCS.md`, run `python -m coconut.lsp.generate_docs`. When you change syntax, keep the examples in `HELP.md` and `coconut/llms.txt` working, since tests run both.

### Makefile Test Targets

Most targets first run `make clean`, then compile the test sources with `python ./coconut/tests <flags>` (which only compiles; see `coconut/tests/__main__.py`), and then run `coconut/tests/dest/runner.py` and `coconut/tests/dest/extras.py`. **These targets never run `main_test.py`, `lsp_test.py`, or `constants_test.py`. Only `make test-all` (pytest) does.** Times are rough: `make test` takes a few minutes on a 4-core Linux machine, and `make test-all` takes 20 to 60 minutes per Python version on CI.

| Target | What it does |
| --- | --- |
| `make test` | The default while developing. Same as `make test-mypy`: `--target sys`, `--strict --keep-lines --force --no-cache`, and `--mypy`. Use it to test any compiler change. |
| `make test-tests` | `make test` without `make clean` or `--force`, so only test files that changed are recompiled. Use it only when you've changed nothing but the tests: unchanged test files aren't recompiled with your modified compiler. |
| `make test-all` | `make clean`, then `pytest --strict-markers -s ./coconut/tests`. Runs all three test files, and is what CI runs. |
| `make test-univ` | Universal target, no MyPy. `make test-univ-tests` skips `--force`, like `test-tests`. |
| `make test-mypy-univ` | Universal target with `--mypy`. |
| `make test-mypy-all` | `make test` plus `--check-untyped-defs`. |
| `make test-pyright` | `--target sys --pyright`. |
| `make test-py2`, `test-py3`, `test-pypy`, `test-pypy3` | `make test-univ` with `python2`, `python3 ... --target 3`, `pypy`, or `pypy3`. |
| `make test-easter-eggs` | `make test-univ` with `runner.py --test-easter-eggs`. |
| `make test-minify`, `make test-no-wrap` | `make test-univ` with `--minify` or `--no-wrap`. |
| `make test-purepy` | `make test-univ` with `COCONUT_PURE_PYTHON=TRUE`: pure-Python `pyparsing` instead of cPyparsing. Several times slower. |
| `make test-no-computation-graph` | `make test-univ` with `COCONUT_USE_COMPUTATION_GRAPH=FALSE`. |
| `make test-any-of` | `make test-univ` with `COCONUT_ADAPTIVE_ANY_OF=TRUE` and `COCONUT_REVERSE_ANY_OF=TRUE`, which reverses the alternatives in every `any_of` grammar element (their order shouldn't matter). |
| `make test-univ-debug` | `make test-univ` with `COCONUT_TEST_DEBUG_PYTHON=TRUE`, which compiles under `python -X dev`. |
| `make test-verbose` | `make test-univ` with `--verbose`. Variants: `-cache` (reuses the incremental cache), `-no-cache`, `-sync` (`--jobs 0`), and `test-mypy-verbose`. |
| `make test-watch` | Compiles, then runs `make just-watch` (`--watch` on `cocotest/agnostic`, which blocks until you press Ctrl-C), then runs the tests. |
| `make test-mini` | Only compiles `cocotest/agnostic` with `coconut` and runs nothing. The fastest check that the compiler can handle the suite. Variants: `-verbose`, `-cache` (doesn't save to the cache), `-sync` (`--jobs 0 --fail-fast`), `-debug` (`python -X dev`, `--jobs 0`), and `-debug-purepy`. |
| `make debug-test-crash` | Runs the already-compiled `runner.py` under `python -X dev`. |

After any of these, `python coconut/tests/dest/runner.py` reruns the compiled suite without recompiling.

### Running Individual Tests

Run pytest tests from the repository root by file and node ID:

```bash
pytest --strict-markers -s "coconut/tests/main_test.py::TestCompilation::test_no_wrap"
pytest --strict-markers -s coconut/tests/main_test.py -k mypy
pytest --strict-markers -s coconut/tests/lsp_test.py
```

Each `TestCompilation` test compiles and runs the entire suite, so each one takes minutes. Set `COCONUT_KEEP_TEST_FILES=TRUE` to keep `coconut/tests/dest` and the cloned external projects afterwards so you can inspect them.

Pitfalls:

- **Run one suite at a time per checkout.** Every target and pytest test uses the same `coconut/tests/dest`, the same `__coconut_cache__` directories in `coconut/tests/src`, and the same clone directories in the repository root (`coconut-prelude/`, `bbopt/`, ...), and they delete these when they start. To run suites in parallel, use separate checkouts (e.g. `git worktree add`).
- **Use a separate `COCONUT_HOME` for each checkout you type-check from at the same time.** `--mypy` and `--pyright` link the current checkout's stubs into `$COCONUT_HOME/.coconut_stubs`, and `--pyright` writes `$COCONUT_HOME/.coconut_pyrightconfig.json`. `COCONUT_HOME` defaults to your home directory.
- **Don't point pytest at `coconut/tests` while `coconut/tests/dest` exists.** The compiled suite contains files such as `py314_test.py` that match pytest's `*_test.py` pattern, so collection fails with syntax errors. Pass the test file paths, or run `make clean` first (`make test-all` does).
- **The gates check the interpreter, not what's installed.** For example, the MyPy tests exist on every non-Windows CPython 3.9+, whether or not MyPy is installed. Install `.[tests]` (whose contents follow the same conditions) with the Python you're testing.
- **Caching.** Without `--force`, Coconut skips files whose source and compiler options haven't changed. That's why the `*-tests` targets miss compiler changes. The incremental parsing cache in `__coconut_cache__` is used unless you pass `--no-cache`, and `make clean` deletes it.
- **`make test-all` touches the network and your environment.** `TestExternal` clones projects from GitHub, and on CPython 3.9+ `test_prelude` runs coconut-prelude's `make base-install`, which `pip install`s pytest and coconut-prelude into the active environment. Only run it in a virtual environment.
- `constants_test.py::test_imports` needs a complete standard library (e.g. `tkinter` and `dbm.gnu` on CPython), so it fails on minimal Python builds.

### Running Every Test Configuration

To save time, many tests only run on some Python versions, platforms, or settings, and some configurations are only reachable through a Makefile target or a constant. `make test` on one Python version misses a lot. For example, `test_no_wrap` and `test_standalone` only exist on Python versions below 3.12, so `make test` (or even `make test-all`) on Python 3.13 never runs the suite with `--no-wrap`.

These are the conditions that decide which tests run, with the flag definitions in `coconut/constants.py`:

| Condition | Tests | How to enable | Run by CI? |
| --- | --- | --- | --- |
| `COCONUT_TEST_ALL` (on by default except on Windows) | `test_strict_keep_lines`, `test_and`, `test_run_arg`, `test_run_dir`, `test_any_of` (CPython only), `test_jobs_zero` and `test_incremental` (not PyPy), and all of `TestExternal` | `COCONUT_TEST_ALL=TRUE` (or `FALSE` to skip them) | Yes |
| Python < 3.12 | `test_standalone`, and also `test_no_wrap` on Python 3.5+ | Run pytest with Python 3.11 or older. `make test-no-wrap` works on any version, but there's no Makefile target for `--standalone`. | `test_standalone`: 2.7, 3.7 to 3.11, and all PyPy versions; `test_no_wrap`: the same minus Python 2. `--standalone` is never tested on 3.12+. |
| Python 3.12+ | `TestExternal.test_bbopt` and `test_pyston` (compile only, with `COCONUT_TEST_ALL`) | Python 3.12+ | CPython 3.12 to 3.15 |
| Python 2 or 3 | Python 2 compiles `target_2` and uses `--target 2` in `test_target`. Python 3 compiles `target_3` and runs `test_pickle_main`, `test_target_3_snip`, and `test_pytest_plugin` (which also needs pytest 7+). | Both a Python 2 and a Python 3 interpreter | 2.7, PyPy 2.7, and 3.x |
| Python 3.5, 3.6, 3.8, 3.11, or 3.14+ | The matching `target_<N>` folder, plus `specific.coco` tests gated on the version. `make test` compiles every folder but only runs those the current Python supports. `target_314` is only MyPy-checked on 3.14+, and `target_2` never is. `test_zipapp` needs 3.5+, and `test_tutorial` needs 3.7+. | The newest Python, plus older ones | 2.7 and 3.7 to 3.15 |
| `always_sys_versions` (the newest Python 2 and the two newest Python 3 versions: currently 2.7, 3.14, and 3.15) | `test_always_sys` (every folder compiled with `--target sys`) | One of those versions | Yes |
| Python at least the oldest version the PSF still supports (currently 3.11; set by the dates in `py_vers_with_eols`) | `test_simple_psf` | 3.11+ | 3.11+, including PyPy 3.11 |
| `MYPY`: CPython 3.9+, not on Windows | The MyPy and Pyright snippet tests in `TestShell` (`test_*_mypy_snip`, `test_mypy_source_lines`, `test_exhaustiveness`, `test_addpattern_redefinition`, `test_pyright`), `test_mypy_sys`, and running coconut-prelude's tests in `test_prelude`. The `tests` extra only installs MyPy and Pyright when this holds. | CPython 3.9+ on Linux or macOS | CPython 3.9 to 3.15 |
| `LSP`: Python 3.9+ | `test_lsp`. `lsp_test.py` skips itself below 3.8. Some of its checks also need `pyflakes` or `mypy` installed. | 3.9+ with `.[tests]` | `lsp_test.py`: 3.8+; `test_lsp`: 3.9+ |
| `IPY`: 3.6+, but not 3.7, not PyPy below 3.11, and not PyPy on Windows | `test_ipython_extension`, `test_kernel_run_cell_kwargs`, `test_kernel_installation`, `test_jupyter_console` (not on Windows or PyPy), and the kernel tests in `extras.coco` | CPython 3.8+ | CPython 3.8 to 3.15, PyPy 3.11 |
| `XONSH`: 3.5 or 3.8+, excluding PyPy 3.9+, and not on Windows | `test_xontrib` | CPython 3.8+ on Linux or macOS | CPython 3.8 to 3.15 |
| `NUMPY`: CPython 2.7 or 3.4+ | The numpy tests in `extras.coco`, plus pandas (3.6+) and xarray (3.10+) | CPython | CPython |
| `CPYTHON` or `PYPY` | cPyparsing is only installed on CPython, so PyPy uses pure-Python `pyparsing` and never uses incremental parsing or the parse cache. PyPy also compiles with `--jobs 0` and takes different branches in the `.coco` tests. | PyPy 2 and 3 | Yes |
| `WINDOWS` | Turns off `COCONUT_TEST_ALL` (by default), `MYPY`, `test_xontrib`, `test_jupyter_console`, and `test_import_hook_preserves_stdin` | Windows | **No**: `.appveyor.yml` still exists, but AppVeyor hasn't run a build since March 2024 |
| `markdown_it` importable | The interactive tutorial part of `test_tutorial` (otherwise silently skipped) | `pip install markdown-it-py` (included in `.[docs]` and `.[dev]`) | **No**: `.[tests]` doesn't include it |
| Running from a source checkout | `test_tutorial` needs `HELP.md`. `lsp_test.py`'s plugin and docs checks need `.claude-plugin/` and `DOCS.md`. | A git checkout | Yes |
| `COCONUT_TEST_VERBOSE` or `COCONUT_TEST_TRACE` | `test_verbose` (`--verbose`) or `test_trace` (`--trace`) | Set the variable to `TRUE` | **No** |
| `--test-easter-eggs` | `easter_egg_test` in `main.coco` | `make test-easter-eggs` | **No** |
| Makefile-only compiler settings | The full suite with `--pyright`, `--check-untyped-defs`, `--minify`, or `--watch`, with pure-Python pyparsing, or without the computation graph | `make test-pyright`, `test-mypy-all`, `test-minify`, `test-watch`, `test-purepy`, `test-no-computation-graph` | **No**, except that PyPy jobs use pure-Python pyparsing |
| `test_computation_graph_pickling` in `constants.py` | Checks that every computation graph action can be pickled, for every handler the suite exercises | Temporarily set it to `True` and run `make test`. `constants_test.py` fails until you set it back. | **No** |

The `.coco` tests also branch on `sys.version_info`, PyPy, and the platform internally, so every extra interpreter tests more code paths. External projects come from GitHub: `test_prelude` and `test_imp_issue` run everywhere `TestExternal` does (except that `test_prelude` doesn't run on PyPy 3), and the pyprover test is commented out.

#### Testing on Multiple Python Versions

The simplest approach is one virtual environment per interpreter, each with Coconut's test dependencies installed, and then `PYTHONPATH` pointed at the checkout you want to test. That way you can reuse the same environments for any checkout or worktree. With [uv](https://docs.astral.sh/uv/):

```bash
cd /path/to/coconut
for v in 3.11 3.13 3.15 pypy@3.11; do
    uv venv -p "$v" "$HOME/.venvs/coconut-$v"
    uv pip install -p "$HOME/.venvs/coconut-$v/bin/python" ".[tests]" markdown-it-py
done
```

uv can't create Python 2 environments (and may not have Python 3.7 builds). For those, use pyenv, conda, or a system interpreter with `virtualenv`, and `pip install ".[tests]"`.

To run the suite with one of those environments, put its `bin` directory first on `PATH`. The tests run `coconut`, `coconut-run`, `pytest`, `jupyter`, `ipython`, and `xonsh` from `PATH`. Then set `PYTHONPATH` to the checkout:

```bash
cd /path/to/coconut
PATH="$HOME/.venvs/coconut-3.11/bin:$PATH" PYTHONPATH="$PWD" COCONUT_TEST_ALL=TRUE make test-all
```

To run several versions in a row (one at a time, since they share `coconut/tests/dest`):

```bash
for v in 3.11 3.13 3.15 pypy@3.11; do
    PATH="$HOME/.venvs/coconut-$v/bin:$PATH" PYTHONPATH="$PWD" COCONUT_TEST_ALL=TRUE \
        make test-all > "test-all-$v.log" 2>&1 || echo "FAILED on $v"
done
```

To run versions in parallel, give each one its own worktree and `COCONUT_HOME`. If you only have one checkout, `uv pip install -e ".[tests]"` works too and doesn't need `PYTHONPATH`.

#### Full Test Checklist

CI covers every Python version on Linux, so passing CI covers everything above except the rows marked **No**. Before a release, or after a change that could affect one of those configurations, also run:

1. `make test-all` on CI, or locally on Python 3.11 *and* the newest Python, and on PyPy and Python 2.7 if you touched compatibility code. This covers both the below-3.12 side (`test_no_wrap`, `test_standalone`) and the 3.12+ side of the gates.
2. `make test-pyright`, `make test-easter-eggs`, `make test-purepy`, `make test-no-computation-graph`, `make test-minify`, and `make test-no-wrap` (which also covers `--no-wrap` on 3.12+).
3. `pytest --strict-markers -s "coconut/tests/main_test.py::TestShell::test_tutorial"` with `markdown-it-py` installed.
4. Set `test_computation_graph_pickling = True` in `coconut/constants.py`, run `make test`, and set it back.
5. Check that `coconut --watch` recompiles files when they change (`make test-watch`).
6. On Windows, if your change could behave differently there, since CI doesn't cover it.

### What CI Covers

- **`.github/workflows/run-tests.yml`** runs on every push to `evhub/coconut` (it has no `pull_request` trigger, so for a pull request from a fork, enable Actions on your fork to run it there). Superseded runs on the same branch are cancelled. It runs on Linux with CPython 2.7 and 3.7 to 3.15 and PyPy 2.7, 3.9, 3.10, and 3.11. Each job runs `make install` (`pip install -e .[tests]`), `make test-all` with the default environment (so `COCONUT_TEST_ALL` is on), and `make build`. On `master` and `develop`, it then uploads to PyPI ("Publish to PyPI", `continue-on-error`). Jobs time out after 150 minutes.
- **`.github/workflows/codeql-analysis.yml`** runs CodeQL on pushes and pull requests to `master` and `gh-pages`, and weekly.
- **`.github/workflows/claude.yml`** and **`claude-code-review.yml`** run Claude Code on `@claude` mentions and review pull requests.
- **`.appveyor.yml`** would run `make test-all` on Windows (Python 2.6, 2.7, 3.5, 3.9, 3.10, and 3.11), but the AppVeyor project hasn't built since March 2024.
- **readthedocs** builds the documentation from `.readthedocs.yaml` (Python 3.11, `.[docs]`).

CI doesn't catch: anything Windows- or macOS-specific; Python 2.6 and 3.2 to 3.6, which are supported targets but have no CI interpreter; the configurations marked **No** above; and anything that only shows up with a dirty `__coconut_cache__` or `coconut/tests/dest`, since CI always starts clean.

## Release Process

`DEVELOP = N` in `coconut/root.py` makes the version `VERSION-post_devN`. Every push to `develop` that passes CI publishes that version as [`coconut-develop`](https://pypi.org/project/coconut-develop/), so bump `DEVELOP` whenever you want to publish a new development build (PyPI won't accept the same version twice).

_Steps marked **(confirm)** couldn't be verified from the repository; the maintainer should confirm whether they're still done._

1. Preparation:
    1. Run `make check-reqs` and update the version bounds in `coconut/constants.py` as necessary.
    2. Run `make format`.
    3. If a new Python version has come out or one has reached end of life, update `supported_py3_vers`, `py_vers_with_eols`, and `specific_targets` in `coconut/constants.py`, the list of targets in `DOCS.md`, and the CI matrix in `.github/workflows/run-tests.yml`.
    4. Go through the [full test checklist](#full-test-checklist). The `test-purepy`, `test-no-computation-graph`, `test-minify`, `test-no-wrap`, interactive tutorial, and Windows checks are new to this list **(confirm they pass today)**.
    5. Run `make docs` and make sure the local documentation looks good (`docs/index.html`). If `DOCS.md` changed, make sure `python -m coconut.lsp.generate_docs` was run.
    6. Check all the tooling:
        1. Make sure the [`coconut-develop`](https://pypi.org/project/coconut-develop/) package looks good.
        2. Check changes in [`compiled-cocotest`](https://github.com/evhub/compiled-cocotest), [`pyprover`](https://github.com/evhub/pyprover) (its test in `TestExternal` is commented out), and [`coconut-prelude`](https://github.com/evhub/coconut-prelude).
    7. Make sure the [GitHub Actions](https://github.com/evhub/coconut/actions) and [readthedocs](https://readthedocs.org/projects/coconut/builds/) builds are passing.
    8. Make sure the [develop documentation](https://coconut.readthedocs.io/en/develop/) looks good.
    9. In `coconut/root.py`, set `VERSION` to the new version and `DEVELOP = False` (`ALPHA` must be `False` too). Optionally set `VERSION_NAME` for a major release (v2.0.0 had one; v3.0.0 didn't).

2. Pull Request:
    1. Move unresolved issues to the next [milestone](https://github.com/evhub/coconut/milestones).
    2. Create a pull request to merge `develop` into `master`, titled "Release vX.Y.Z", with the `release` label and the release's milestone. Put the release notes, linking every resolved issue, in its description.
    3. Link contributors on the pull request.
    4. Wait until everything is passing.

3. Release:
    1. If applicable, release a new version of [`sublime-coconut`](https://github.com/evhub/sublime-coconut), which also provides the VS Code extension:
        1. Update the version in its [`package.json`](https://github.com/evhub/sublime-coconut/blob/master/package.json).
        2. Run `make publish`, which publishes to the VS Code Marketplace and Open VSX.
        3. [Release a new version on GitHub](https://github.com/evhub/sublime-coconut/releases).
    2. Merge the pull request (with a merge commit) and label it `resolved`.
    3. [Release `master` on GitHub](https://github.com/evhub/coconut/releases/new): tag `vX.Y.Z`, title "Coconut vX.Y.Z", and the release notes from the pull request.
    4. `git fetch`, `git checkout master`, and `git pull`.
    5. Run `make upload`, which runs `make wipe` and `make dev`, then builds and uploads to PyPI with `twine` (it asks for a PyPI token) **(confirm)**. CI's "Publish to PyPI" step would also upload `master` once a job passes, but past releases were uploaded by hand within minutes of merging, after which the CI upload fails harmlessly.
    6. `git checkout develop`, `git rebase master` (a fast-forward, since `master` is now `develop` plus the merge commit), and `git push`. `make fix-develop` (`git merge master -s ours`) records a merge of `master` into `develop` without changing `develop`'s files, for when the two have diverged.
    7. Set `DEVELOP = 1` in `coconut/root.py`.
    8. Run `make dev`.
    9. Push to `develop`.
    10. Wipe all updated versions on [readthedocs](https://readthedocs.org/projects/coconut/versions/) **(confirm)**.
    11. Build all updated versions on [readthedocs](https://readthedocs.org/projects/coconut/builds/).
    12. Copy the [PyPI](https://pypi.org/project/coconut/) keywords to the [readthedocs tags](https://readthedocs.org/dashboard/coconut/edit/) **(confirm)**.
    13. Get the SHA-256 hash of the `.tar.gz` file from [PyPI](https://pypi.org/project/coconut/#files), and use it along with the current version requirements in [`constants.py`](https://github.com/evhub/coconut/blob/master/coconut/constants.py) to update the [local feedstock](https://github.com/evhub/coconut-feedstock) **(confirm)**.
    14. Submit a pull request to update [Coconut's `conda-forge` feedstock](https://github.com/conda-forge/coconut-feedstock), or review the one conda-forge's bot opens **(confirm)**.
    15. Update the [website](https://github.com/evhub/coconut/tree/gh-pages) if it needs updating.
    16. Wait until the feedstock pull request is passing, then merge it.
    17. Close the release [milestone](https://github.com/evhub/coconut/milestones?direction=asc&sort=due_date).
