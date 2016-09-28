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

from tui.menu import choose_option, Command, MenuOptionsRegistry, MainloopExit

from tui.lookup import lookup
from tui.questioning import question_all_due, question_all_group
from tui.show import show_group

import tui.data_commands

from data import database_manager, udm_handler


@MenuOptionsRegistry
class LookUp(Command):
    """
    The 'lookup' command.
    """
    usage = "lookup string"
    description = "looks the string up in the database"

    def __init__(self, *word: str):
        if len(word) == 0:
            raise TypeError
        lookup(" ".join(word))


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


@MenuOptionsRegistry
class Use(Command):
    """
    The 'use' command
    """
    usage = "use group_name"
    description = "put all cards in card-group group_name in shelf 1"

    def __init__(self, group_name: str):
        print("WIP")
        # todo implement use


@MenuOptionsRegistry
class User(Command):
    """
    The 'user' command.
    """
    usage = "user user_name"
    description = "switch to user with name user_name"

    def __init__(self, name: str):
        global prompt
        if name not in udm_handler.get_user_names():
            if choose_option(["y", "n"], "Username does not exist. Create new user? [y|n] ")[0] == "n":
                return
        udm_handler.set_user(name)
        prompt = "{} $ ".format(name)


def mainloop():
    """
    Repeatedly prompts the user for a command until the command exit is invoked.
    """
    global prompt
    while True:
        try:
            MenuOptionsRegistry.run(*choose_option(MenuOptionsRegistry.get_options(), prompt))
        except MainloopExit:
            break


prompt = "$ "


def main(user: str = None):
    """
    The TextUIs main method.
    :param user: the user that should be active on start
    """
    print("""lHelper Copyright (C) 2016 Julian Mueller
This program comes with ABSOLUTELY NO WARRANTY; for details type 'show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type 'show c' for details.""")

    if user:
        udm_handler.set_user(user)

    global prompt
    if udm_handler.get_user() is not None:
        prompt = "{} $ ".format(udm_handler.get_user())

    mainloop()
