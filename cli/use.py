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
    if not database_manager.group_name_exists(group_name):
        print("Group {} does not exist.".format(group_name))
        return

    cards = database_manager.load_group(database_manager.get_group_id_for_name(group_name))[2]

    if len(cards) > 100 and not (
            input("Do you really want to add {} cards? [y] ".format(len(cards))).strip(" ").lower().endswith("y")):
        return

    for card_id, _ in cards:
        if not udm_handler.get_udm().card_is_used(card_id):
            udm_handler.get_udm().add_card(card_id, CardManager.DEFAULT_SHELF, "today")
            print("Added card {} to shelf {}".format(card_id, CardManager.DEFAULT_SHELF))
