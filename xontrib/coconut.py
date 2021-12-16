#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Coconut xontrib to enable Coconut code in xonsh.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# ----------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

from types import MethodType

from coconut.constants import coconut_kernel_kwargs
from coconut.exceptions import CoconutException
from coconut.terminal import format_error
from coconut.compiler import Compiler
from coconut.command.util import Runner

# -----------------------------------------------------------------------------------------------------------------------
# MAIN:
# -----------------------------------------------------------------------------------------------------------------------

COMPILER = Compiler(**coconut_kernel_kwargs)
COMPILER.warm_up()

RUNNER = Runner(COMPILER)
RUNNER.update_vars(__xonsh__.ctx)


def new_parse(self, s, *args, **kwargs):
    try:
        compiled_python = COMPILER.parse_xonsh(s)
    except CoconutException as err:
        err_str = format_error(err).splitlines()[0]
        compiled_python = s + " # " + err_str
    return self.__class__.parse(self, compiled_python, *args, **kwargs)


main_parser = __xonsh__.execer.parser
main_parser.parse = MethodType(new_parse, main_parser)

ctx_parser = __xonsh__.execer.ctxtransformer.parser
ctx_parser.parse = MethodType(new_parse, ctx_parser)
