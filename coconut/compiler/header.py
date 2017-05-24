#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Header utilities for the compiler.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

from coconut.root import *  # NOQA

import os.path

from coconut.constants import (
    get_target_info,
    hash_prefix,
    tabideal,
    default_encoding,
    template_ext,
)
from coconut.exceptions import CoconutInternalException

#-----------------------------------------------------------------------------------------------------------------------
# UTILITIES:
#-----------------------------------------------------------------------------------------------------------------------


def gethash(compiled):
    """Retrieves a hash from a header."""
    lines = compiled.splitlines()
    if len(lines) < 3 or not lines[2].startswith(hash_prefix):
        return None
    else:
        return lines[2][len(hash_prefix):]


def minify(compiled):
    """Performs basic minifications (fails on non-tabideal indentation or a string with a #)."""
    compiled = compiled.strip()
    if compiled:
        out = []
        for line in compiled.splitlines():
            line = line.split("#", 1)[0].rstrip()
            if line:
                ind = 0
                while line.startswith(" "):
                    line = line[1:]
                    ind += 1
                if ind % tabideal != 0:
                    raise CoconutInternalException("invalid indentation in", line)
                out.append(" " * (ind // tabideal) + line)
        compiled = "\n".join(out) + "\n"
    return compiled


template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")


def get_template(template):
    """Read the given template file."""
    with open(os.path.join(template_dir, template) + template_ext, "r") as template_file:
        return template_file.read()


def one_num_ver(target):
    """Returns the first number of the target version, if it has one."""
    return target[:1]  # "2", "3", or ""


def section(name, justify_len=80):
    """Generate a section break."""
    line = "# " + name + ": "
    return line + "-" * (justify_len - len(line)) + "\n\n"


#-----------------------------------------------------------------------------------------------------------------------
# HEADER GENERATION:
#-----------------------------------------------------------------------------------------------------------------------


allowed_headers = ("none", "initial", "__coconut__", "package", "sys", "code", "file")


def getheader(which, target="", usehash=None):
    """Generates the specified header."""
    if which not in allowed_headers:
        raise CoconutInternalException("invalid header type", which)

    if which == "none":
        return ""

    # initial, __coconut__, package, sys, code, file

    target_startswith = one_num_ver(target)

    if which == "initial" or which == "__coconut__":
        header = '''#!/usr/bin/env python{target_startswith}
# -*- coding: {default_encoding} -*-
{hash_line}{typing_line}
# Compiled with Coconut version {VERSION_STR}

{module_docstring}'''.format(
            target_startswith=target_startswith,
            default_encoding=default_encoding,
            hash_line=(hash_prefix + usehash + "\n" if usehash is not None else ""),
            typing_line=("# type: ignore\n" if which == "__coconut__" else ""),
            VERSION_STR=VERSION_STR,
            module_docstring=('"""Built-in Coconut utilities."""\n\n' if which == "__coconut__" else ""),
        )
    elif usehash is not None:
        raise CoconutInternalException("can only add a hash to an initial or __coconut__ header, not", which)
    else:
        header = ""

    if which == "initial":
        return header

    # __coconut__, package, sys, code, file

    target_info = get_target_info(target)

    header += section("Coconut Header")

    if target_startswith != "3":
        header += "from __future__ import print_function, absolute_import, unicode_literals, division\n"
    elif target_info >= (3, 5):
        header += "from __future__ import generator_stop\n"

    if which == "package":
        return header + '''import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import _coconut, _coconut_MatchError, _coconut_tail_call, _coconut_tco, _coconut_igetitem, _coconut_compose, _coconut_pipe, _coconut_starpipe, _coconut_backpipe, _coconut_backstarpipe, _coconut_bool_and, _coconut_bool_or, _coconut_minus, _coconut_map, _coconut_partial
from __coconut__ import *
_coconut_sys.path.remove(_coconut_file_path)

''' + section("Compiled Coconut")

    if which == "sys":
        return header + '''import sys as _coconut_sys
from coconut.__coconut__ import _coconut, _coconut_MatchError, _coconut_tail_call, _coconut_tco, _coconut_igetitem, _coconut_compose, _coconut_pipe, _coconut_starpipe, _coconut_backpipe, _coconut_backstarpipe, _coconut_bool_and, _coconut_bool_or, _coconut_minus, _coconut_map, _coconut_partial
from coconut.__coconut__ import *
'''

    # __coconut__, code, file

    header += "import sys as _coconut_sys\n"

    if target_startswith == "3":
        header += PY3_HEADER
    elif target_info >= (2, 7):
        header += PY27_HEADER
    elif target_startswith == "2":
        header += PY2_HEADER
    else:
        header += PYCHECK_HEADER

    header += get_template("header").format(
        object=("(object)" if target_startswith != "3" else ""),
        import_OrderedDict=(
            '''if _coconut_sys.version_info >= (2, 7):
        OrderedDict = collections.OrderedDict
    else:
        OrderedDict = dict''' if not target
            else "OrderedDict = collections.OrderedDict" if target_info >= (2, 7)
            else "OrderedDict = dict"
        ),
        import_collections_abc=(
            "abc = collections" if target_startswith == "2"
            else '''if _coconut_sys.version_info < (3, 3):
        abc = collections
    else:
        import collections.abc as abc'''
        ),
        comma_bytearray=(", bytearray" if target_startswith != "3" else ""),
        static_repr=("staticmethod(repr)" if target_startswith != "3" else "repr"),
        with_ThreadPoolExecutor=(
            '''with ThreadPoolExecutor()''' if target_info >= (3, 5)
            else '''from multiprocessing import cpu_count  # cpu_count() * 5 is the default Python 3.5 thread count
        with ThreadPoolExecutor(cpu_count() * 5)'''
        ),
        empty_dict="{}",
    )

    if which == "file":
        header += section("Compiled Coconut")

    return header
