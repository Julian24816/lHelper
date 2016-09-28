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

from data import database_manager, udm_handler
from random import choice
from time import localtime, strftime, time

from typing import Iterable, List, Set, Tuple


class Card:
    """
    Holds a vocabulary Card.
    """
    def __init__(self, card_id: int, shelf: int, due_date: str, translations: List[Tuple[str, str, str, str]],
                 groups: Iterable[str]):
        """
        Initialize the Card.
        :param card_id: the cards id in the database.
        :param shelf: the shelf the cards sits on
        :param due_date: the date the card is due
        :param translations: the translations on the card
        :param groups: the groups the card is in
        """
        self.card_id = card_id
        self.shelf = shelf
        self.due_date = due_date

        # todo do sth with the translation objects
        self.translations = translations
        self.groups = set(groups)

    def get_id(self):
        """
        :return: the cards id
        """
        return self.card_id

    def get_shelf(self):
        """
        :return: the shelf the card is on
        """
        return self.shelf

    def get_due_date(self):
        """
        :return: the cards due date
        """
        return self.due_date

    def get_translations(self) -> List[Tuple[str, str, str, str]]:  # todo change return type
        """
        :return: the translations on the card
        """
        return self.translations


class CardGroup:
    """
    A group of cards.
    """
    def __init__(self, cards: Iterable[Card], name: str, parent_name: str = None):
        """
        Initialize the Group.
        :param cards: the cards in the group
        :param name: the groups name
        :param parent_name: the parents name
        """
        self.cards = set(cards)
        self.name = name
        self.parent_name = parent_name

    def get_cards(self) -> Set[Card]:
        """
        :return: the cards in the group
        """
        return self.cards


class CardManager:
    """
    Manages the loading and saving of vocabulary cards.
    """
    CARD_PORTION = 100
    MIN_SHELF = 0
    DEFAULT_SHELF = 1
    MAX_SHELF = 7

    groups = {}

    @classmethod
    def load_card_group(cls, group_id: int) -> CardGroup:
        """
        Loads a card group from the database
        :param group_id: the groups id
        :return: the card group
        """
        name, parent_name, cards = database_manager.load_group(group_id)
        cards = list(map(lambda c: Card(*udm_handler.get_udm().get_card(c[0]), c[1],
                                        database_manager.get_group_names_for_card(c[0])),
                         cards))  # cards = List[Tuple[int, List[Translation]]]
        cls.groups[group_id] = CardGroup(cards, name, parent_name)

    #######
    # add methods

    @staticmethod
    def add_card_to_group(card: Card, group: CardGroup):
        """
        Adds a card to a card_group.
        :param card: the card to be added
        :param group: the group the card should be added to
        """
        if group.name not in card.groups:
            database_manager.add_card_to_group(card.card_id, group.name)
            card.groups.add(group.name)
            group.cards.add(card)

    @staticmethod
    def add_card_group(group_name, parent_name=None) -> CardGroup:
        """
        Adds a card group to the database.
        :param group_name: the groups name
        :param parent_name: the groups parents name.
        """
        return CardManager.get_group(database_manager.add_group(group_name, parent_name))

    #######
    # get methods

    @classmethod
    def get_due_cards(cls, due_date: str = "today") -> List[Card]:
        """
        Loads self.CARD_PORTION many due cards from the database.
        :param due_date: a date in format %Y-%m-%d or 'today'
        :return: a list of UsedCards
        """

        # load data for due cards
        due_cards = [[], []]
        for card in udm_handler.get_udm().get_due_cards(due_date):
            if card[1] <= 2:  # shelf
                due_cards[0].append(card)
            else:
                due_cards[1].append(card)

        # limit card amount by using all cards in shelf 1 and 2 and using as much as possible random others
        while len(due_cards[0]) < cls.CARD_PORTION and len(due_cards[1]) > 0:
            card = choice(due_cards[1])
            due_cards[0].append(card)
            due_cards[1].remove(card)

        # load translations from database
        cards = []
        for card in due_cards[0]:
            cards.append(Card(card[0], card[1], card[2],
                              database_manager.get_card(card[0])[1], database_manager.get_group_names_for_card(card[0])
                              ))
        return cards

    @classmethod
    def get_group(cls, group_id: int) -> CardGroup:
        """
        Loads the group from the database if necessary and returns it.
        :param group_id: the groups id
        :return: the CardGroup
        """
        if group_id not in cls.groups:
            cls.load_card_group(group_id)
        return cls.groups[group_id]

    @classmethod
    def get_group_for_name(cls, group_name: str) -> CardGroup:
        """
        Returns the CardGroup with name group_name.
        :param group_name: the groups name
        :return: the CardGroup
        """
        return cls.get_group(database_manager.get_group_id_for_name(group_name))

    #######
    # card manipulation methods

    @classmethod
    def correct(cls, card: Card):
        """
        Modifies the card and saves it to the database.
        :param card: the card to be modified.
        """
        card.shelf = card.shelf + 1 if card.shelf < cls.MAX_SHELF else cls.MAX_SHELF

        days = 2**card.shelf - 1
        card.due_date = strftime("%Y-%m-%d", localtime(time() + 86400 * days))  # in *days* days

        udm_handler.get_udm().update_card((card.card_id, card.shelf, card.due_date))

    @classmethod
    def wrong(cls, card: Card):
        """
        Modifies the cards and saves it to the database.
        :param card: the card to be modified.
        """
        card.shelf = cls.MIN_SHELF
        card.due_date = strftime('%Y-%m-%d')  # today

        udm_handler.get_udm().update_card((card.card_id, card.shelf, card.due_date))
