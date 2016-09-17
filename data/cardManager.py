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
Manages the loading and saving of vocabulary cards.
Instantiate CardManager to get access to the functionality.
"""

from singleton import Singleton
from typing import List
from data.classes import UsedCard
from data.databaseManager import UserDatabaseManager


@Singleton
class CardManager:
    """
    Manages the loading and saving of vocabulary cards.
    """
    def __init__(self, user_database_manager: UserDatabaseManager):
        self.user_database_manager = user_database_manager

    def get_due_cards(self, max_shelf) -> List[UsedCard]:
        """
        Loads all due cards from the database.
        :return: a list of UsedCards
        """
        return self.user_database_manager.get_due_cards(max_shelf)