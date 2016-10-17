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
from language import Phrase, phrase_classes
from random import choice
from time import localtime, strftime, time
from re import match

from typing import Iterable, List, Set, Tuple


class Card:
    """
    Holds a vocabulary Card.
    """

    def __init__(self, card_id: int, translations: List[Tuple[str, str, str, str]], groups: Iterable[str]):
        """
        Initialize the UsedCard.
        :param card_id: the cards id in the database.
        :param translations: the translations on the card
        :param groups: the groups the card is in
        """
        self.card_id = card_id

        self.translations = []
        for phrase1, language1, phrase2, language2 in translations:
            self.translations.append((phrase_classes[language1].parse_phrase(phrase1),
                                      phrase_classes[language2].parse_phrase(phrase2)))

        self.groups = set(groups)

    def get_id(self):
        """
        :return: the cards id
        """
        return self.card_id

    def get_translations(self) -> List[Tuple[Phrase, Phrase]]:
        """
        :return: the translations on the card
        """
        return self.translations

    def get_groups(self):
        """
        :return: the groups the card is in
        """
        return self.groups


class UsedCard(Card):
    """
    Holds a used vocabulary Card.
    """

    def __init__(self, card_id: int, shelf: int, due_date: str, translations: List[Tuple[str, str, str, str]],
                 groups: Iterable[str]):
        """
        Initialize the UsedCard.
        :param card_id: the cards id in the database.
        :param shelf: the shelf the cards sits on
        :param due_date: the date the card is due
        :param translations: the translations on the card
        :param groups: the groups the card is in
        """
        super(UsedCard, self).__init__(card_id, translations, groups)
        self.shelf = shelf
        self.due_date = due_date

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


class CardGroup:
    """
    A group of cards.
    """

    def __init__(self, cards: Iterable[UsedCard], name: str, parent_name: str = None):
        """
        Initialize the Group.
        :param cards: the cards in the group
        :param name: the groups name
        :param parent_name: the parents name
        """
        self.cards = set(cards)
        self.name = name
        self.parent_name = parent_name

    def get_cards(self) -> Set[UsedCard]:
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
        cards = list(map(lambda c: UsedCard(*udm_handler.get_udm().get_card(c[0]), c[1],
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
    def lookup(cls, string, language) -> List[Card]:
        """
        Returns a list of Card-objects, that match the string.
        :param string: the string to be looked up
        :param language: the language of the string
        :return: a list of cards.
        """
        raise NotImplementedError("WIP")

        # get possible root forms for string
        rfs = phrase_classes[language].get_possible_root_forms_for(string)

        # load corresponding cards
        cards = []

        for rf in rfs:
            matching_cards = [c[0] for c in database_manager.find_cards_with(rf, language)]

            for card in matching_cards:
                if udm_handler.get_udm().card_is_used(card[0]):
                    cards.append(UsedCard(*udm_handler.get_udm().get_card(card[0]), card[1],
                                          database_manager.get_group_names_for_card(card[0])))
                else:
                    cards.append(Card(card[0], card[1], database_manager.get_group_names_for_card(card[0])))

                    # todo implement checking whether each card really corresponds to the string

    @classmethod
    def get_due_cards(cls, due_date: str = "today") -> List[UsedCard]:
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

        if len(due_cards[0]) < cls.CARD_PORTION < len(due_cards[0]) + len(due_cards[1]) and len(due_cards[1]) > 0:
            print("Selecting {} of {} cards.".format(max(cls.CARD_PORTION, len(due_cards[0])),
                                                     len(due_cards[0]) + len(due_cards[1])))

        # limit card amount by using all cards in shelf 1 and 2 and using as much as possible random others
        while len(due_cards[0]) < cls.CARD_PORTION and len(due_cards[1]) > 0:
            card = choice(due_cards[1])
            due_cards[0].append(card)
            due_cards[1].remove(card)

        # load translations from database
        cards = []
        for card in due_cards[0]:
            cards.append(UsedCard(card[0], card[1], card[2],
                                  database_manager.get_card(card[0])[1],
                                  database_manager.get_group_names_for_card(card[0])))
        return cards

    @staticmethod
    def get_cards_on_shelf(shelf: int) -> List[UsedCard]:
        """
        Returns all Cards on the shelf
        :param shelf: the shelf
        :return: a list of UsedCards
        """
        cards = []
        for card in udm_handler.get_udm().get_cards_on_shelf(shelf):
            cards.append(UsedCard(card[0], card[1], card[2],
                                  database_manager.get_card(card[0])[1],
                                  database_manager.get_group_names_for_card(card[0])))
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
        name, lt = CardManager._parse_group_name(group_name)
        if name in ("s{}".format(i) for i in range(CardManager.MIN_SHELF, CardManager.MAX_SHELF + 1)):
            group = CardGroup(CardManager.get_cards_on_shelf(int(name[1:])), name)
        else:
            group = cls.get_group(database_manager.get_group_id_for_name(group_name))

        if lt is not None:
            return CardGroup(filter(lambda c: c.get_translations()[0][0].phrase < lt[1:],
                                    group.get_cards()), group.name, group.parent_name)

    @staticmethod
    def group_name_exists(group_description: str) -> bool:
        """
        Checks whether a group exists.
        :param group_description: the groups name + optional modifiers
        :return: the groups existence
        """
        name, lt = CardManager._parse_group_name(group_description)

        # s1, s2, s3, s4, ...
        if name in ("s{}".format(i) for i in range(CardManager.MIN_SHELF, CardManager.MAX_SHELF + 1)) \
                or database_manager.group_name_exists(name):
            return True
        return False

    @staticmethod
    def _parse_group_name(group_name: str) -> List[str]:
        """
        Splits a group_name into name and modifiers.
        :param group_name: the raw group names
        :return: name, lt  # lt is None or a string starting with '<'
        """
        m = match("([\w-]+)(<\w+)?", group_name)
        if m:
            return m.groups()
        return group_name, None

    @staticmethod
    def get_card(card_id: int) -> UsedCard:
        """
        Loads a card from the database
        :param card_id: the cards id
        :return: a UsedCard
        """
        return UsedCard(*udm_handler.get_udm().get_card(card_id), database_manager.get_card(card_id)[1],
                        database_manager.get_group_names_for_card(card_id))

    #######
    # card manipulation methods

    @classmethod
    def correct(cls, card: UsedCard):
        """
        Modifies the card and saves it to the database.
        :param card: the card to be modified.
        """
        card.shelf = card.shelf + 1 if card.shelf < cls.MAX_SHELF else cls.MAX_SHELF

        days = 2 ** card.shelf - 1
        card.due_date = strftime("%Y-%m-%d", localtime(time() + 86400 * days))  # in *days* days

        udm_handler.get_udm().update_card((card.card_id, card.shelf, card.due_date))

    @classmethod
    def wrong(cls, card: UsedCard):
        """
        Modifies the cards and saves it to the database.
        :param card: the card to be modified.
        """
        card.shelf = cls.MIN_SHELF
        card.due_date = strftime('%Y-%m-%d')  # today

        udm_handler.get_udm().update_card((card.card_id, card.shelf, card.due_date))
