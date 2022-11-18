#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------------------------------------------------
# INFO:
# -----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Mimics what a compiled __coconut__.py would do.

Must match __coconut__.__init__.
"""

# -----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
# -----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.constants import coconut_kernel_kwargs as _coconut_kernel_kwargs
from coconut.compiler import Compiler as _coconut_Compiler

# -----------------------------------------------------------------------------------------------------------------------
# HEADER:
# -----------------------------------------------------------------------------------------------------------------------

# executes the __coconut__.py header for the current Python version
exec(_coconut_Compiler(**_coconut_kernel_kwargs).getheader("code"))
