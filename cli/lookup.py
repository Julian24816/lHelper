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
Provides methods for the 'lookup' command.
"""

from data import database_manager
from data.cardManager import CardManager


def lookup(string: str):
    """
    Looks up word in the database.
    :param string: the string to be looked up
    """

    # retrieve cards form database
    cards = database_manager.find_cards_with(string)
    if len(cards) == 0:
        print("No cards found.")

    # print out cards
    for card_id, translations in cards:
        print("[{}]".format(card_id))
        for translation in translations:
            print("")
