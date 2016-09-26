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
Provides data to other modules of lHelper.
"""

from data.databaseManager import DatabaseManager
from data.userDatabaseManager import UserDatabaseManager
import data.cardManager as cardManager


from typing import List


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


def set_user(name: str):
    """
    Sets the active user.
    :param name: the users name
    """
    global user_name, user_database_manager
    user_name = name
    user_database_manager = UserDatabaseManager(name)
    cardManager.user_database_manager = user_database_manager


database_manager = DatabaseManager("data.sqlite3")

user_name = None
user_database_manager = None

cardManager.database_manager = database_manager
cardManager.user_database_manager = user_database_manager


if len(get_user_names()) == 1:
    set_user(get_user_names()[0])
