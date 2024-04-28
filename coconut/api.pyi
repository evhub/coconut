#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: MyPy stub file for api.py.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Optional,
    Text,
)

from setuptools import find_packages as _find_packages

from coconut.command.command import Command

class CoconutException(Exception):
    """Coconut Exception."""

    def syntax_err(self) -> SyntaxError:
        ...

#-----------------------------------------------------------------------------------------------------------------------
# COMMAND:
#-----------------------------------------------------------------------------------------------------------------------

GLOBAL_STATE: Optional[Command] = None


def get_state(state: Optional[Command] = None) -> Command:
    """Get a Coconut state object; None gets a new state, False gets the global state."""
    ...


def cmd(
    args: Text | bytes | Iterable,
    *,
    state: Command | None = ...,
    argv: Iterable[Text] | None = None,
    interact: bool = False,
    default_target: Text | None = None,
    default_jobs: Text | None = None,
) -> None:
    """Process command-line arguments."""
    ...

cmd_sys = cmd


VERSIONS: Dict[Text, Text] = ...


def version(which: Optional[Text] = None) -> Text:
    """Get the Coconut version."""
    ...


#-----------------------------------------------------------------------------------------------------------------------
# COMPILER:
#-----------------------------------------------------------------------------------------------------------------------


def setup(
    target: Optional[str] = None,
    strict: bool = False,
    minify: bool = False,
    line_numbers: bool = True,
    keep_lines: bool = False,
    no_tco: bool = False,
    no_wrap: bool = False,
    *,
    state: Optional[Command] = ...,
) -> None:
    """Set up the given state object."""
    ...


def warm_up(
    streamline: bool = False,
    enable_incremental_mode: bool = False,
    *,
    state: Optional[Command] = ...,
) -> None:
    """Warm up the given state object."""
    ...


PARSERS: Dict[Text, Callable] = ...


def parse(
    code: Text,
    mode: Text = ...,
    state: Optional[Command] = ...,
    keep_internal_state: Optional[bool] = None,
) -> Text:
    """Compile Coconut code."""
    ...


def coconut_exec(
    expression: Text,
    globals: Optional[Dict[Text, Any]] = None,
    locals: Optional[Dict[Text, Any]] = None,
    state: Optional[Command] = ...,
    keep_internal_state: Optional[bool] = None,
) -> None:
    """Compile and evaluate Coconut code."""
    ...


def coconut_eval(
    expression: Text,
    globals: Optional[Dict[Text, Any]] = None,
    locals: Optional[Dict[Text, Any]] = None,
    state: Optional[Command] = ...,
    keep_internal_state: Optional[bool] = None,
) -> Any:
    """Compile and evaluate Coconut code."""
    ...


# -----------------------------------------------------------------------------------------------------------------------
# ENABLERS:
# -----------------------------------------------------------------------------------------------------------------------


def use_coconut_breakpoint(on: bool = True) -> None:
    """Switches the breakpoint() built-in (universally accessible via
    coconut.__coconut__.breakpoint) to use coconut.embed."""
    ...


coconut_importer: Any = ...


def auto_compilation(
    on: bool = True,
    args: Iterable[Text] | None = None,
    use_cache_dir: bool | None = None,
) -> None:
    """Turn automatic compilation of Coconut files on or off."""
    ...


def get_coconut_encoding(encoding: Text = ...) -> Any:
    """Get a CodecInfo for the given Coconut encoding."""
    ...


find_and_compile_packages = find_packages = _find_packages
