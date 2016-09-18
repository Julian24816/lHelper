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
from random import choice
from time import localtime, time, strftime


@Singleton
class CardManager:
    """
    Manages the loading and saving of vocabulary cards.
    """
    CARD_PORTION = 100

    def __init__(self, user_database_manager: UserDatabaseManager):
        self.user_database_manager = user_database_manager

    def get_due_cards(self, max_shelf: int) -> List[UsedCard]:
        """
        Loads self.CARD_PORTION many due cards from the database.
        :return: a list of UsedCards
        """
        card_ids = self.user_database_manager.get_due_card_ids_and_shelves(max_shelf)

        shelves = set(card_ids.values())
        if 0 in shelves:
            shelves.remove(0)
        if 1 in shelves:
            shelves.remove(1)

        # weighed list of shelves to choose from
        shelf_choices = []
        for i in shelves:
            shelf_choices += [i]*(i-2)*2

        while len(card_ids) > self.CARD_PORTION and len(shelf_choices) > 0:

            # choose random shelf to remove corresponding card from list
            shelf = choice(shelf_choices)

            # remove first card to be found to be in shelf
            for c in card_ids:
                if card_ids[c] == shelf:
                    card_ids.pop(c)
                    break

            # remove shelf from shelf_choices if no card in shelf is left
            if shelf not in card_ids.values():
                while shelf in shelf_choices:
                    shelf_choices.remove(shelf)

        cards = []
        for card in card_ids:
            cards.append(self.user_database_manager.load_card(card))
        return cards

    def correct(self, card: UsedCard):
        """
        Modifies the cards fields upon being answered correct on questioning and saves it to the database.
        :param card: the card to be modified.
        """
        card.shelf = card.shelf+1 if card.shelf < UsedCard.MAX_SHELF else card.shelf
        card.next_questioning = strftime('%Y-%m-%d', localtime(time() + 86400 * (2 ** card.shelf - 1)))

        self.user_database_manager.update_db(card.Id, card.shelf, card.next_questioning)

    def wrong(self, card: UsedCard):
        """
        Modifies the cards fields upon being answered wrong on questioning and saves it to the database.
        :param card: the card to be modified.
        """
        card.shelf = 0
        card.next_questioning = strftime('%Y-%m-%d')

        self.user_database_manager.update_db(card.Id, card.shelf, card.next_questioning)
