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
Provides constants for the UserDatabases.
"""

from data.databaseConstants import CARD_ID


TABLE_USED_CARD = "used_card"
USED_CARD_SHELF = "shelf"
USED_CARD_NEXT_QUESTIONING = "next_questioning"

CREATE_TABLE_USED_CARD = "CREATE TABLE IF NOT EXISTS " + TABLE_USED_CARD + "(" + \
                         CARD_ID + " INTEGER PRIMARY KEY, " + \
                         USED_CARD_SHELF + " INTEGER DEFAULT 0, " + \
                         USED_CARD_NEXT_QUESTIONING + " DATE DEFAULT CURRENT_DATE);"
