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
Provides methods for the 'show' command.
"""

from data import database_manager


def show_group(group_name: str):
    """
    Prints all cards in card-group group_name.
    :param group_name: the groups name
    """

    # assert the group exists
    if not database_manager.group_name_exists(group_name):
        print("Group {} does not exist.".format(group_name))
        return

    for card_id, translations in database_manager.load_group(database_manager.get_group_id_for_name(group_name))[2]:
        print("[{}]".format(card_id))
        for translation in translations:
            print("{} -> {}".format(translation[0], translation[2]))  # phrase1, phrase2
