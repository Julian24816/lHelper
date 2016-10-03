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
Handles the UserDatabaseManager-object.
"""

from data.userDatabaseManager import UserDatabaseManager
from typing import List


class NoUserError(RuntimeError):
    """
    Exception raised when a UserDatabaseManager is requested while no user is specified.
    """


class UDMHandler:
    """
    Handles the UserDatabaseManager-object.
    """

    def __init__(self, user_name: str = None):
        if user_name is None:
            self.udm = None
        else:
            self.udm = UserDatabaseManager(user_name)

    @staticmethod
    def get_user_names() -> List[str]:
        """
        Returns all available user_names.
        :return: a list of names
        """
        from os import listdir
        from re import match

        names = []
        for file_name in listdir("."):
            if match(".+[.]sqlite3", file_name):
                names.append(file_name[:-8])
        return names

    def set_user(self, name: str):
        """
        Sets the active user.
        :param name: the users name
        """
        self.udm = UserDatabaseManager(name)

    def get_user(self) -> str:
        """
        Returns the name of the current user or None.
        :return: the name of the current user or None if no user is active yet.
        """
        if self.udm is None:
            return None
        return self.udm.user_name

    def get_udm(self) -> UserDatabaseManager:
        """
        Returns the UserDatabaseManager-object.
        :return:
        """
        if self.udm is None:
            raise NoUserError("no user active yet.")
        else:
            return self.udm
