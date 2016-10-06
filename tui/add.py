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
Provides methods for the 'add' cycle.
Call add_cards to prompt the user for ney cards.
"""

from data import database_manager


def add_cards():
    """
    Prompts the user for new cards.
    """

    # init variables
    rf = None
    context = None
    translations = []
    last_group = None

    # start input cycle
    choice = input("root forms > ").strip(" ")
    while choice != "break":

        # last choice asked for root forms
        if rf is None:
            if choice != "":
                rf = choice
            # otherwise ask again

        # last choice asked for context
        elif context is None:
            # if 'y' was given, save card
            if choice == 'y':
                if len(translations) > 0:

                    # print translations
                    for translation in translations:
                        print("{} -> {}".format(translation[0], translation[2]))

                    # ask whether the card should be saved
                    if input("Save card? [y] > ").strip(" ").lower().endswith("y"):
                        card_id = database_manager.add_card(translations)

                        print("card_id: {}".format(card_id))

                        # ask for group to put the card in
                        group = input("group? ({}) > ".format(last_group)).strip(" ")
                        if group == "":
                            group = last_group
                        elif group == "None":
                            group = None

                        if group is not None:
                            database_manager.add_card_to_group(card_id, group)
                            print("added card {} to group {}".format(card_id, group))

                        last_group = group

                else:
                    print("no translations to save.")

                print()

                # reset variables
                rf = None
                context = None
                translations = []

            # otherwise continue with given context
            else:
                context = choice

        # last choice asked for translations
        # if nothing was given, go back to context level
        elif choice == "":
            context = None
        # otherwise safe given translation
        else:
            translations.append(["{} {}".format(rf, context), "latin", choice, "german"])

        # todo enable input of synonyms

        # ask for next choice
        if rf is None:
            choice = input("root forms > ").strip(" ")
        elif context is None:
            choice = input("y|context > ").strip(" ")
        else:
            choice = input("translation > ").strip(" ")
