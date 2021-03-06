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

from cli.menu import MenuOptionsRegistry, Command

from cli.add import add_cards, add_card
from cli.edit import edit_card

from data import database_manager


@MenuOptionsRegistry
class Add(Command):
    """
    The 'add' command.
    """
    usage = "add (cards|card|<card_id>|group) [<group_name>]"
    description = "provides methods for adding cards"

    def __init__(self, mode: str, group_name: str = None):
        if group_name is not None and mode == "group" and database_manager.group_name_exists(group_name):
            print("Group {} already exists.".format(group_name))
            return
        elif group_name is not None and mode != "group" and not database_manager.group_name_exists(group_name):
            print("Group {} does not exist.".format(group_name))
            return

        # add many cards
        if mode == "cards":
            add_cards(group_name)

        # add 1 card
        elif mode == "card":
            add_card(group_name)

        elif mode == "group":
            database_manager.add_group(group_name)
            print("Added group {}.".format(group_name))

        # add card to group
        else:

            # convert card_id to integer
            try:
                card_id = int(mode)
            except ValueError:
                print(self.usage_notice())
                print("card_id must be an integer.")
                return

            # look for card in the database
            if not database_manager.card_exists(card_id):
                print("Card {} does not exist.".format(card_id))
                return

            # add card to group
            database_manager.add_card_to_group(card_id, group_name)
            print("Added card {} to group {}.".format(card_id, group_name))


@MenuOptionsRegistry
class Edit(Command):
    """
    The 'edit' command.
    """
    usage = "edit <card_id>"
    description = "lets the user edit the card with id card_id"

    def __init__(self, card_id):
        try:
            card_id = int(card_id)
            if not database_manager.card_exists(card_id):
                print("Card {} does not exist.".format(card_id))
            else:
                edit_card(card_id)
        except ValueError:
            print("Argument card_id must be an integer.")
            print(self.usage_notice())
