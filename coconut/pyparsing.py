#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Wrapper around PyParsing that selects the best available implementation.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

try:
    from cPyparsing import *  # NOQA
    if DEVELOP:
        from cPyparsing import _trim_arity  # NOQA
except ImportError:
    from pyparsing import *  # NOQA
    if DEVELOP:
        from pyparsing import _trim_arity  # NOQA
