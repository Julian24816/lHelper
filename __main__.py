# coding=utf-8
#
# Copyright (C) 2016 Julian Mueller
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
lHelper project: python application for helping me learn Latin
"""

import argparse
from sys import path
from os import chdir
from os.path import dirname, abspath

ENABLE_DATA_COMMANDS = False

__version__ = "1.4.5"
__author__ = "Julian Mueller"

path_to_main = abspath(__file__)
path.append(dirname(path_to_main))
chdir(dirname(path_to_main))

parser = argparse.ArgumentParser()
parser.add_argument("-g", "--gui", action="store_const", const="gui", default="cli", dest="ui",
                    help="Run the program with a GUI instead of a CLI.")
ui_choice = parser.parse_args().ui
if ui_choice == "cli":
    import cli
    cli.main(__version__, enable_data_commands=ENABLE_DATA_COMMANDS)
elif ui_choice == "gui":
    import main
    main.main()
