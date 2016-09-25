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
Provides a text based UI for lHelper.
Start the mainloop by calling main.
"""

from tui.menu import Command, MenuOptionsRegistry, mainloop

from tui.questioning import question_all_due, question_all_group
from tui.show import show_group

from data import database_manager

# from re import match

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


@MenuOptionsRegistry
class Add(Command):
    """
    The 'add' command.
    """
    usage = "add cards"
    description = "starts the adding cycle"

    def __init__(self, mode):
        if mode == "cards":
            add_cards()
        else:
            print(self.usage_notice())


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
            if not card_manager.card_exists(card_id):
                print("card with card_id does not exist")
            else:
                edit_card(card_manager.get_card(card_id))
        except ValueError:
            print("argument card_id must be an integer")


@MenuOptionsRegistry
class LookUp(Command):
    """
    The 'lookup' command.
    """
    usage = "lookup string"
    description = "looks the string up in the database"

    def __init__(self, word):
        lookup(word)


# todo add command for learning new vocabs

# todo add option for starting other commands at the end of the previous
# or option to suggest the user a command
'''


@MenuOptionsRegistry
class Question(Command):
    """
    The 'question' command.
    """
    usage = "question [due|group_name]"
    description = "questions the user over all due cards or all cards in group_name"

    def __init__(self, group_name: str = "due"):
        if group_name == "due":
            question_all_due()
        elif database_manager.group_name_exists(group_name):
            question_all_group(group_name)
        else:
            print("group_name unknown.")

    @classmethod
    def get_help(cls):
        """
        Returns a help string for the 'question' command.
        :return: the help string
        """
        return "{}\n{}\n\n{}".format(cls.usage_notice(), cls.description, "group_name : the group to be used")


@MenuOptionsRegistry
class Show(Command):
    """
    The 'show c' and 'show w' commands.
    """
    usage = "show (c|w|group_name)"
    description = "show corresponding parts of LICENSE or all cards in card-group group_name"

    def __init__(self, group: str):
        if group == "c":
            print(self.get_copyright())
            return

        elif group == "w":
            print(self.get_warranty())
            return

        if database_manager.group_name_exists(group):
            show_group(group)
        else:
            print("group_name unknown")

    @staticmethod
    def get_warranty() -> str:
        """
        Reads the warranty part of the LICENSE.
        :return: the warranty text
        """
        try:
            f = open("LICENSE")
            lines = f.readlines()
            f.close()
            return "".join(lines[588:598])
        except FileNotFoundError:
            return "file LICENSE not found."

    @staticmethod
    def get_copyright() -> str:
        """
        Reads the copyright part of the LICENSE.
        :return: the copyright text
        """
        try:
            f = open("LICENSE")
            lines = f.readlines()
            f.close()
            return "".join(lines[194:433])
        except FileNotFoundError:
            return "file LICENSE not found."

    @classmethod
    def get_help(cls) -> str:
        """
        Returns a help string for the 'show' command.
        :return: the help string
        """
        to_return = "{}\n{}\n\n".format(cls.usage_notice(), cls.description)
        to_return += "  c          - show copyright\n"
        to_return += "  w          - show warranty\n"
        to_return += "  group_name - show all cards in card_group group_name"
        return to_return


def main():
    """
    The TextUIs main method.
    :return:
    """
    print("""lHelper Copyright (C) 2016 Julian Mueller
This program comes with ABSOLUTELY NO WARRANTY; for details type 'show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type 'show c' for details.""")

    mainloop(prompt="$ ")
