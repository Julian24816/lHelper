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
Inherit from DatabaseOpenHelper to access functionality.
"""

from sqlite3 import connect, Connection, Cursor, IntegrityError


class DatabaseOpenHelper:
    """
    Responsible for opening the database.
    """

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.create_tables()

    def get_connection(self) -> Connection:
        """
        Opens the database and returns a Cursor
        :return: a Cursor
        """
        return connect(self.db_name)

    def create_tables(self):
        """
        Creates the database tables if not present.
        :raises RuntimeError: when not implemented in inherited classes
        """
        raise RuntimeError("{} has not implemented the create_tables method".format(self.__class__))
