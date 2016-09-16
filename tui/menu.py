# menu.py - menu module of tui: framework for a TUI mainloop menu
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

from typing import Iterable


class Command:
    usage = ""
    description = ""

    @classmethod
    def get_help(cls):
        return cls.usage_notice() + "\n" + cls.description

    @classmethod
    def usage_notice(cls):
        return "Usage: " + cls.usage

    def __call__(self, *args, **kwargs):
        print("action undefined")


class MenuOptionsRegistry:
    __registry = {}

    def __init__(self, command: Command):
        self.__registry[command.usage.split(" ")[0]] = command

    @classmethod
    def get_options(cls):
        return sorted(cls.__registry.keys())

    @classmethod
    def run(cls, command, *args) -> Command:
        if cls.has_option(command):
            try:
                cls.__registry[command](*args)
            except TypeError:
                print(command.usage_notice())
        else:
            raise KeyError("command not registered")

    @classmethod
    def get(cls, command) -> Command:
        if cls.has_option(command):
            return cls.__registry[command]
        else:
            raise KeyError("command not registered")

    @classmethod
    def has_option(cls, command):
        return command in cls.__registry


@MenuOptionsRegistry
class Help(Command):
    usage = "help [command]"
    description = "get help (on command)"

    def __init__(self, *args):
        if len(args) == 0:
            commands = []
            max_usage_len = 0
            for command in MenuOptionsRegistry.get_options():
                command = MenuOptionsRegistry.get(command)
                commands.append((command.usage, command.description))
                if len(command.usage) > max_usage_len:
                    max_usage_len = len(command.usage)

            print("The following commands are available:\nUse 'help command' for more in-depth help.\n")
            for item in commands:
                print(item[0].ljust(max_usage_len), item[1])

        elif len(args) == 1:
            if MenuOptionsRegistry.has_option(args[0]):
                print(MenuOptionsRegistry.get(args[0]).get_help())
        else:
            print(self.usage_notice())


@MenuOptionsRegistry
class Exit(Command):
    usage = "exit"
    description = "exit the program"

    def __init__(self):
        exit()


def choose_option(options: Iterable, prompt):
    choice = [None]
    while choice[0] not in options:
        if choice[0] == "":
            print("Options:", ", ".join(options))
        choice = input(prompt).strip(" ").split(" ")
    return choice


def mainloop(prompt="$ "):
    while True:
        MenuOptionsRegistry.run(*choose_option(MenuOptionsRegistry.get_options(), prompt))