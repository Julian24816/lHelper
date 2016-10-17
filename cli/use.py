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
Provides methods for the 'use group' command.
Call use_group(group_name) to assert that all cards in group <group_name> are used by the current user.
"""

from data import database_manager, udm_handler
from data.cardManager import CardManager


def use_group(group_name: str):
    """
    Asserts that all cards in the given group are being used by the user.
    :param group_name: the groups name
    """

    # assert the group exists
    name, lt = CardManager.parse_group_name(group_name)
    if not database_manager.group_name_exists(name):
        print("Group {} does not exist.".format(name))
        return

    cards = database_manager.load_group(database_manager.get_group_id_for_name(name))[2]
    if lt is not None:
        cards = list(filter(lambda c: c[1][0][0] < lt[1:], cards))

    if len(cards) > 100 and not (
            input("Do you really want to add {} cards? [y] ".format(len(cards))).strip(" ").lower().endswith("y")):
        return

    for card_id, _ in cards:
        use_card(card_id, verbosity=1)


def use_card(card_id: int, verbosity=2):
    """
    Adds a card to the used cards of the user.
    :param card_id: the cards id
    :param verbosity: 1 for 'card added' messages + 2 for 'card added' and 'card already used' messages
    """
    if not udm_handler.get_udm().card_is_used(card_id):
        udm_handler.get_udm().add_card(card_id, CardManager.DEFAULT_SHELF, "today")
        if verbosity >= 1:
            print("Added card {} to shelf {}".format(card_id, CardManager.DEFAULT_SHELF))
    elif verbosity >= 2:
        print("Card {} is already used.".format(card_id))
