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
from tui.questioning import question_all
from data import card_manager


@MenuOptionsRegistry
class License(Command):
    """
    The 'show c' and 'show w' commands.
    """
    usage = "show c|w"
    description = "show appropriate parts of LICENSE"

    def __init__(self, part: str):
        if part == "c":
            print(self.get_copyright())
        elif part == "w":
            print(self.get_warranty())
        else:
            raise TypeError("unknown license part")

    @staticmethod
    def get_warranty():
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
    def get_copyright():
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


@MenuOptionsRegistry
class Question(Command):
    """
    The 'question' command.
    """
    usage = "question [max_shelf]"
    description = "starts the questioning cycle"

    def __init__(self, shelf=5):
        try:
            shelf = int(shelf)
        except ValueError:
            raise TypeError
        if shelf not in range(8):
            print("max_shelf must lay between 0 and 7.")
            return

        question_all(card_manager.get_due_cards(max_shelf=shelf))

    @classmethod
    def get_help(cls):
        """
        Returns a help string for the 'question' command.
        :return: the help string
        """
        return "{}\n{}\n\n{}".format(cls.usage_notice(), cls.description, "max_shelf : the max shelf id to be included")


@MenuOptionsRegistry
class Einspeichern(Command):
    """
    The 'einspeichern' command.
    """
    usage = "einspeichern"
    description = "starts the 'einspeichern' cycle"


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
