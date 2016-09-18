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
Provides methods for the 'walk' command.
"""

from data import card_manager


def assign_group_all(gt=None):
    """
    Assigns all cards to a user-specified group.
    """
    print("loading cards ...")
    if gt is not None:
        cards = card_manager.get_all_cards(gt)
    else:
        cards = card_manager.get_all_cards()

    cards = sorted(cards,
                   key=lambda c: c.get_translations()[0].latinUsage.word.root_forms)

    current_group = None
    for card in cards:
        print("\n{}".format(card))
        new_group = input("{} $ ".format(current_group)).strip(" ").split(" ")
        if new_group != [""]:
            if new_group[0] == "None":
                current_group = None
            elif len(new_group) > 1:
                group_id = card_manager.add_card_group(new_group[0], new_group[1])
                current_group = card_manager.get_card_group(group_id)
            elif len(new_group) == 1:
                group_id = card_manager.add_card_group(new_group[0])
                current_group = card_manager.get_card_group(group_id)
        if current_group is not None:
            print("add card to group...")
            card_manager.add_card_to_group(card, current_group)
            print(current_group, "has", len(current_group.cards), "cards.")
