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
Provides commands for governing the data in data.sqlite3.
"""

from tui.menu import MenuOptionsRegistry, Command

from tui.add import add_cards
from tui.edit import edit_card

from data import database_manager


# todo refactor walk
'''
@MenuOptionsRegistry
class WalkCards(Command):
    """
    The 'walk' command.
    """
    usage = "walk group action"
    description = "walk all cards in group and perform the action on them"

    def __init__(self, group, action):
        group_names = card_manager.get_all_group_names()

        # search for exactly one '>'
        if match("^[^>]+>[^>]+$",group):
            group, gt = group.split(">")
        else:
            gt = None

        # load group
        if group == "all":
            print("loading cards ...")
            all_cards = card_manager.get_all_cards()
            if gt:
                cards = []
                for card in all_cards:
                    if card.get_translations()[0].latinUsage.word.root_forms > gt:
                        cards.append(card)
            else:
                cards = all_cards

        elif group in group_names:
            print("loading cards ...")
            cards = card_manager.get_card_group_for_name(group).cards

        else:
            print("group unknown")
            return

        # determine action
        if action == "repeat":
            repeat(cards)
        elif action == "assign_group":
            assign_group(cards)
        else:
            print("action unknown")
            return

    @classmethod
    def get_help(cls):
        """
        Returns a help string for the 'walk' command.
        :return: the help string
        """
        to_return = cls.usage_notice() + "\n\n" + cls.description + "\n\n"
        to_return += "  group  : the group to be affected: a group_name or 'all'\n"
        to_return += "           a '>word' str may be appended to all for the command to only affect cards > word\n"
        to_return += "  action : the action to be performed: assign_group or repeat"
        return to_return
'''


@MenuOptionsRegistry
class Add(Command):
    """
    The 'add' command.
    """
    usage = "add cards"
    description = "starts the adding cycle"

    def __init__(self, mode: str):
        print("WIP")
        # todo implement add


@MenuOptionsRegistry
class Edit(Command):
    """
    The 'edit' command.
    """
    usage = "edit card_id"
    description = "lets the user edit the card with id card_id"

    def __init__(self, card_id):
        try:
            card_id = int(card_id)
            if not database_manager.card_exists(card_id):
                print("card with card_id does not exist")
            else:
                edit_card(card_id)
        except ValueError:
            print("argument card_id must be an integer")
