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
Provides data to other modules.
"""

from data.databaseManager import DatabaseManager, UserDatabaseManager
from data.cardManager import CardManager
from data.classes import UsedCard

database_manager = DatabaseManager("data_new.sqlite3")
user_database_manager = UserDatabaseManager("julian", database_manager)

card_manager = CardManager(user_database_manager)


def port_data():
    """
    Ports the data from the old system to the new one.
    """
    from data.datamanager import Datamanager
    dm = Datamanager("old_data.sqlite3")
    cur = dm.cursor.connection.cursor()
    cards = [dm.getUsedCard(1, card_id) for card_id, in cur.execute("SELECT cardId FROM usedCard")]
    for card in cards:
        user_database_manager.add_card(card)

#port_data()
