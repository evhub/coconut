#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: MyPy stub file for convenience.py.
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
    Union,
)

from coconut.command.command import Command

class CoconutException(Exception):
    ...

#-----------------------------------------------------------------------------------------------------------------------
# COMMAND:
#-----------------------------------------------------------------------------------------------------------------------

GLOBAL_STATE: Optional[Command] = None


def get_state(state: Optional[Command]=None) -> Command: ...


def cmd(args: Union[Text, bytes, Iterable], interact: bool=False) -> None: ...


VERSIONS: Dict[Text, Text] = ...


def version(which: Optional[Text]=None) -> Text: ...


#-----------------------------------------------------------------------------------------------------------------------
# COMPILER:
#-----------------------------------------------------------------------------------------------------------------------


def setup(
    target: Optional[str]=None,
    strict: bool=False,
    minify: bool=False,
    line_numbers: bool=False,
    keep_lines: bool=False,
    no_tco: bool=False,
    no_wrap: bool=False,
) -> None: ...


PARSERS: Dict[Text, Callable] = ...


def parse(
    code: Text,
    mode: Text=...,
    state: Optional[Command]=...,
    keep_internal_state: Optional[bool]=None,
) -> Text: ...


def coconut_eval(
    expression: Text,
    globals: Optional[Dict[Text, Any]]=None,
    locals: Optional[Dict[Text, Any]]=None,
    state: Optional[Command]=...,
    keep_internal_state: Optional[bool]=None,
) -> Any: ...


# -----------------------------------------------------------------------------------------------------------------------
# ENABLERS:
# -----------------------------------------------------------------------------------------------------------------------


def use_coconut_breakpoint(on: bool=True) -> None: ...


class CoconutImporter:
    ext: str

    @staticmethod
    def run_compiler(path: str) -> None: ...

    def find_module(self, fullname: str, path: Optional[str]=None) -> None: ...


coconut_importer = CoconutImporter()


def auto_compilation(on: bool=True) -> None: ...


def get_coconut_encoding(encoding: str=...) -> Any: ...
