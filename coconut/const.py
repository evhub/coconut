#!/usr/bin/env python

#-----------------------------------------------------------------------------------------------------------------------
# INFO:
#-----------------------------------------------------------------------------------------------------------------------

"""
Authors: Evan Hubinger, Fred Buchanan
License: Apache 2.0
Description: Constants for use in the main command module.
"""

#-----------------------------------------------------------------------------------------------------------------------
# CONSTANTS:
#-----------------------------------------------------------------------------------------------------------------------

code_exts = [".coco", ".coc", ".coconut"] # in order of preference
comp_ext = ".py"

main_sig = "Coconut: "
debug_sig = ""

default_prompt = ">>> "
default_moreprompt = "    "

watch_interval = .05 # seconds

color_codes = { # unix/ansii color codes, underscores in names removed
    "bold": 1,
    "dim": 2,
    "underlined": 4,
    "blink": 5,
    "reverse": 7,
    "default": 39,
    "black": 30,
    "red": 31,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "lightgray": 37,
    "darkgray": 90,
    "lightred": 91,
    "lightgreen": 92,
    "lightyellow": 93,
    "lightblue": 94,
    "lightmagenta": 95,
    "lightcyan": 96,
    "white": 97,
    "defaultbackground": 49,
    "blackbackground": 40,
    "redbackground": 41,
    "greenbackground": 42,
    "yellowbackground": 43,
    "bluebackground": 44,
    "magentabackground": 45,
    "cyanbackground": 46,
    "lightgraybackground": 47,
    "darkgraybackground": 100,
    "lightredbackground": 101,
    "lightgreenbackground": 102,
    "lightyellowbackground": 103,
    "lightbluebackground": 104,
    "lightmagentabackground": 105,
    "lightcyanbackground": 106,
    "whitebackground": 107
    }
end_color_code = 0

version_long = "Version " + VERSION_STR + " running on Python " + " ".join(sys.version.splitlines())
version_banner = "Coconut " + VERSION_STR
if DEVELOP:
    version_tag = "develop"
else:
    version_tag = VERSION_TAG
tutorial_url = "http://coconut.readthedocs.org/en/" + version_tag + "/HELP.html"
documentation_url = "http://coconut.readthedocs.org/en/" + version_tag + "/DOCS.html"

icoconut_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icoconut")
icoconut_kernel_dirs = [
    os.path.join(icoconut_dir, "coconut"),
    os.path.join(icoconut_dir, "coconut2"),
    os.path.join(icoconut_dir, "coconut3")
]