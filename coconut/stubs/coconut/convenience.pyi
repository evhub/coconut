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


CLI: Command = ...


def cmd(args: Union[Text, bytes, Iterable], interact: bool) -> None: ...


VERSIONS: Dict[Text, Text] = ...


def version(which: Text) -> Text: ...


#-----------------------------------------------------------------------------------------------------------------------
# COMPILER:
#-----------------------------------------------------------------------------------------------------------------------


setup: Callable[[Optional[str], bool, bool, bool, bool, bool], None] = ...


PARSERS: Dict[Text, Callable] = ...


def parse(code: Text, mode: Text) -> Text: ...


def coconut_eval(
    expression: Text,
    globals: Dict[Text, Any]=None,
    locals: Dict[Text, Any]=None,
) -> Any: ...


# -----------------------------------------------------------------------------------------------------------------------
# ENABLERS:
# -----------------------------------------------------------------------------------------------------------------------


def use_coconut_breakpoint(on: bool=True) -> None: ...


class CoconutImporter:
    ext: str

    @staticmethod
    def run_compiler(path: str) -> None: ...

    def find_module(self, fullname: str, path: str=None) -> None: ...


coconut_importer = CoconutImporter()


def auto_compilation(on: bool=True) -> None: ...
