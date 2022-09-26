#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Author: Evan Hubinger
License: Apache 2.0
Description: Highlights examples.coco for use in index.html.
"""

#-----------------------------------------------------------------------------------------------------------------------
# IMPORTS:
#-----------------------------------------------------------------------------------------------------------------------

from coconut.root import *

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name

#-----------------------------------------------------------------------------------------------------------------------
# MAIN:
#-----------------------------------------------------------------------------------------------------------------------


def highlight_examples():
    """Returns highlighted HTML for examples.coco"""
    with open("examples.coco", "r") as examples:
        return highlight(
            examples.read(),
            get_lexer_by_name("coconut"),
            get_formatter_by_name("html"),
        )


if __name__ == "__main__":
    with open("examples.html", "w") as examples:
        examples.write(highlight_examples())
