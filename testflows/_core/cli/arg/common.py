# Copyright 2019 Vitaliy Zakaznikov (TestFlows Test Framework http://testflows.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import functools

from datetime import datetime
from argparse import RawDescriptionHelpFormatter

from testflows._core import __version__
from testflows._core.cli.colors import color, white, blue, cyan

def description(description="", prog="Test Framework", version=None):
    if version is None:
        version = __version__

    """Return argument parser description.
          ---- o o o ----
         |   o       o   |
         | 1 o 10010 o 0 |
         |   o       o   |     TestFlows Test Framework v 1.2.3443.22343
         ---  o o oxx --
        /            xx   \
       /  ^^^         xx   \
        -------------------

    :param description: description
    :param prog: name of the program
    :param version: version
    """
    bold_white = functools.partial(white, attrs=["bold"])
    dim_white = functools.partial(white, attrs=["dim"])
    bold_blue = functools.partial(blue, attrs=["bold"])
    bold_cyan = functools.partial(cyan, attrs=["bold"])

    desc =  dim_white("  ---- ") + bold_blue("o o o") + dim_white(" ----") + "\n"
    desc += dim_white(" |   ") + bold_blue("o       o") + dim_white("   |") + "\n"
    desc += (dim_white(" | ") + bold_white("1") + bold_blue(" o ") + bold_white("10010")
                + bold_blue(" o ") + bold_white("0 ") + dim_white("|") + "\n")
    desc += (dim_white(" |   ") + bold_blue("o       o") + dim_white("   |")
             + dim_white("    TestFlows %s v%s" % (prog, version)) + "\n")
    desc += (dim_white("  ---  ") + bold_blue("o o o") + bold_cyan("xx ") + dim_white("--") + "\n")
    desc += (dim_white(" /           ") + bold_cyan("xx") + dim_white("   \\") + "\n")
    desc += (dim_white("/  ^^^        ") + bold_cyan("xx") + dim_white("   \\") + "\n")
    desc += (dim_white(" ------------------") + "\n")
    if description:
        desc += "\n\n" + description
    return desc

def epilog():
    """Return argument parser epilog"""
    return white("""Copyright %d, TestFlows Test Framework""" % datetime.now().year, attrs=["dim"])