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
Framework for a TextUI mainloop menu.
"""

from typing import List, Iterable


class Command:
    """
    A command in the menu.
    Inherit from this class to create new commands.
    """
    usage = ""
    description = ""

    @classmethod
    def get_help(cls) -> str:
        """
        Returns help on the command.
        :return: a standard help string
        """
        return cls.usage_notice() + "\n" + cls.description

    @classmethod
    def usage_notice(cls) -> str:
        """
        Returns a usage notice.
        :return: a standard usage notice based on cls.usage.
        """
        return "Usage: " + cls.usage


class UnknownCommand(RuntimeError):
    """
    A unknown command was accessed.
    """


class MenuOptionsRegistry:
    """
    The Registry for all the options to be available.
    Use this class as a decorator for your Command classes to add them to the Registry.
    """
    __registry = {}

    def __init__(self, command: Command):
        """
        Registers a new command by the first word in command.usage
        :param command: the Command to be registered
        """
        self.__registry[command.usage.split(" ")[0]] = command

    @classmethod
    def get_options(cls):
        """
        Returns all registered commands as their registry keys.
        :return: a list of the registry keys
        """
        return sorted(cls.__registry.keys())

    @classmethod
    def run(cls, command: str, *args: Iterable[str]):
        """
        Runs the registered Command if it exists.
        :raises KeyError: when the command does not exist
        :param command: the registry key of the command to be invoked
        :param args: the arguments to be passed on to the command
        """
        if cls.has_option(command):
            try:
                cls.__registry[command](*args)
            # except Exception as e:
            #     raise e
            except TypeError:
                print(cls.__registry[command].usage_notice())
            except KeyboardInterrupt:
                print("Command aborted.")
            except Exception as e:
                print(e)
                print("Please contact support.")
        else:
            raise UnknownCommand(command)

    @classmethod
    def get(cls, command: str) -> Command:
        """
        Returns the Command associated with the registry key command.
        :param command: the registry key of the command to be returned
        :raises KeyError: when the registry key does not exist
        :return: the command
        """
        if cls.has_option(command):
            return cls.__registry[command]
        else:
            raise UnknownCommand(command)

    @classmethod
    def has_option(cls, command: str) -> bool:
        """
        Checks if a registry key exists.
        :param command: the key
        :return:
        """
        return command in cls.__registry


@MenuOptionsRegistry
class Help(Command):
    """
    The 'help' command.
    """
    usage = "help [command]"
    description = "get help (on command)"

    def __init__(self, command: str = None):
        if command is None:
            commands = []
            max_usage_len = 0
            for option in MenuOptionsRegistry.get_options():
                option = MenuOptionsRegistry.get(option)
                commands.append((option.usage, option.description))
                if len(option.usage) > max_usage_len:
                    max_usage_len = len(option.usage)

            print("The following commands are available:\nUse 'help command' for more in-depth help.\n")
            for item in commands:
                print(item[0].ljust(max_usage_len), item[1])

        else:
            if MenuOptionsRegistry.has_option(command):
                print(MenuOptionsRegistry.get(command).get_help())
            else:
                print("Command {} unknown".format(command))


@MenuOptionsRegistry
class Exit(Command):
    """
    The 'exit' command.
    """
    usage = "exit"
    description = "exit the program"

    def __init__(self):
        raise MainloopExit


class MainloopExit(SystemExit):
    """
    An exception to indicate the mainloop function to exit.
    Exits the Interpreter if no mainloop was used.
    """


def choose_option(options: Iterable, prompt: str) -> List[str]:
    """
    prompts the user for a choice until a string is entered with the first word being in options
    :param options: a list of options the user can choose
    :param prompt: the prompt the user is to be prompted with
    :return: the users choice as a list of words
    """
    choice = [None]
    while choice[0] not in options:
        if choice[0] == "":
            print("Options:", ", ".join(options))
        choice = input(prompt).strip(" ").split(" ")
    return choice
