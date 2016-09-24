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
from data.classes import UsedCard, Card, CardGroup
from data.oldDatabaseManager import OldDatabaseManager, OldUserDatabaseManager
from random import choice
from time import localtime, time, strftime


@Singleton
class CardManager:
    """
    Manages the loading and saving of vocabulary cards.
    """
    CARD_PORTION = 100

    def __init__(self, user_database_manager: OldUserDatabaseManager, database_manager: OldDatabaseManager):
        self.user_database_manager = user_database_manager
        self.database_manager = database_manager

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

    def add_card_to_group(self, card: Card, group: CardGroup):
        """
        Adds a card to a card_group.
        :param card: the card to be added
        :param group: the group the card should be added to
        """
        if group.has_card(card):
            return
        group.add_card(card)
        self.database_manager.add_card_to_group(card, group)

    def get_all_cards(self, gt: str=None) -> List[UsedCard]:
        """
        Fetches all used cards from the database.
        :return: a list of UsedCards
        """
        if gt is None:
            return self.user_database_manager.get_all_cards()
        else:
            all_cards = self.user_database_manager.get_all_cards()
            cards = []
            for card in all_cards:
                if card.get_translations()[0].latinUsage.word.root_forms > gt:
                    cards.append(card)
            return cards

    def add_card_group(self, group_name, parent_name=None):
        """
        Adds a card group to the database.
        :param group_name: the groups name
        :param parent_name: the groups parents name.
        :return: the groups id
        """
        if parent_name is not None:
            return self.database_manager.add_group(CardGroup(group_name, [], CardGroup(parent_name, [])))
        return self.database_manager.add_group(CardGroup(group_name, []))

    def get_card_group(self, group_id):
        """
        Loads a card group from the database
        :param group_id: the groups id
        :return: the card group
        """
        return self.database_manager.load_group(group_id)

    def get_card_group_for_name(self, group_name: str) -> CardGroup:
        """
        Loads a group from the database
        :param group_name: the group's name
        :return: the group
        """
        return self.database_manager.get_group_for_name(group_name)

    def get_all_group_names(self) -> List[str]:
        """
        Loads all group names from the database.
        :return: a list of group names
        """
        return self.database_manager.get_all_group_names()

    def repeat(self, card: UsedCard):
        """
        Sets the cards shelf to 1.
        :param card: a Card
        """
        self.user_database_manager.set_card_shelf(card, 1)
        self.user_database_manager.set_next_questioning(card, strftime('%Y-%m-%d'))

    def card_exists(self, card_id: int) -> bool:
        """
        Returns True if a Card with id card_id exist.
        :param card_id: the Cards id
        :return: True|False
        """
        return self.user_database_manager.card_exists(card_id)

    def get_card(self, card_id: int) -> UsedCard:
        """
        Returns the card with card_id
        :param card_id: the cards id
        :return: a Card
        """
        return self.user_database_manager.load_card(card_id)
