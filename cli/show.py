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
Provides methods for the 'show' command.
"""

from data import database_manager
from typing import Tuple, List


def show_group(group_name: str):
    """
    Prints all cards in card-group group_name.
    :param group_name: the groups name
    """

    # assert the group exists
    if not database_manager.group_name_exists(group_name):
        print("Group {} does not exist.".format(group_name))
        return

    for card_id, translations in database_manager.load_group(database_manager.get_group_id_for_name(group_name))[2]:
        print_card(card_id, translations, database_manager.get_group_names_for_card(card_id))


def show_card(card_id: int):
    """
    Loads a card from the database and prints it.
    :param card_id: the cards id
    """

    # assert the card exists
    if not database_manager.card_exists(card_id):
        print("Card {} does not exist.".format(card_id))
        return

    _, translations = database_manager.get_card(card_id)
    print_card(card_id, translations, database_manager.get_group_names_for_card(card_id))


def print_card(card_id: str, translations: Tuple[str, str, str, str], group_names: List[str] = list()):
    """
    Print a card as loaded from database_manager
    :param card_id: the cards id
    :param translations: the cards translations
    :param group_names: the groups the card is in
    """
    print("[{}]".format(card_id) if not group_names else "[{}, {}]".format(card_id, ", ".join(group_names)))
    for translation in translations:
        print("{} -> {}".format(translation[0], translation[2]))  # phrase1, phrase2
