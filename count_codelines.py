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
Counts all code lines in a project.
"""

from re import match
import sys
import os

all_lines = 0

for root, subFolders, files in os.walk(sys.argv[1]):
    for filename in files:
        if not filename.endswith(".py") or filename in sys.argv[2:] or filename == os.path.split(sys.argv[0])[1]:
            continue
        with open(os.path.join(root, filename)) as f:
            lines = 0
            for line in f:
                if not match("^\s*(#.*)?$", line):  # 0 or more whitespace with optional comment afterwards
                    lines += 1
            print("{:4} {}".format(lines, os.path.join(root, filename)))
            all_lines += lines
print("---- -----\n{:4} total".format(all_lines))
