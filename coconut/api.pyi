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

from coconut.command.command import Command

class CoconutException(Exception):
    ...

#-----------------------------------------------------------------------------------------------------------------------
# COMMAND:
#-----------------------------------------------------------------------------------------------------------------------

GLOBAL_STATE: Optional[Command] = None


def get_state(state: Optional[Command] = None) -> Command: ...


def cmd(
    args: Text | bytes | Iterable,
    *,
    state: Command | None = ...,
    argv: Iterable[Text] | None = None,
    interact: bool = False,
    default_target: Text | None = None,
) -> None: ...


VERSIONS: Dict[Text, Text] = ...


def version(which: Optional[Text] = None) -> Text: ...


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
) -> None: ...


def warm_up(
    force: bool = False,
    enable_incremental_mode: bool = False,
    *,
    state: Optional[Command] = ...,
) -> None: ...


PARSERS: Dict[Text, Callable] = ...


def parse(
    code: Text,
    mode: Text = ...,
    state: Optional[Command] = ...,
    keep_internal_state: Optional[bool] = None,
) -> Text: ...


def coconut_exec(
    expression: Text,
    globals: Optional[Dict[Text, Any]] = None,
    locals: Optional[Dict[Text, Any]] = None,
    state: Optional[Command] = ...,
    keep_internal_state: Optional[bool] = None,
) -> None: ...


def coconut_eval(
    expression: Text,
    globals: Optional[Dict[Text, Any]] = None,
    locals: Optional[Dict[Text, Any]] = None,
    state: Optional[Command] = ...,
    keep_internal_state: Optional[bool] = None,
) -> Any: ...


# -----------------------------------------------------------------------------------------------------------------------
# ENABLERS:
# -----------------------------------------------------------------------------------------------------------------------


def use_coconut_breakpoint(on: bool = True) -> None: ...


coconut_importer: Any = ...


def auto_compilation(
    on: bool = True,
    args: Iterable[Text] | None = None,
    use_cache_dir: bool | None = None,
) -> None: ...


def get_coconut_encoding(encoding: Text = ...) -> Any: ...
