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


def add_cards(group_name: str = None):
    """
    Prompts the user for multiple cards.
    :param group_name: the group the cards should be added to
    """
    while group_name == "break":
        group_name = add_card(group_name)


def add_card(group_name: str = None) -> str:
    """
    Prompts the user for a new card.
    :param group_name: the group the card should be added to
    :return: the name of the group the card was added to or 'break' if the input of the card was cancelled
    """

    # init variables
    rf = None
    context = None
    synonyms_done = False
    translations = []

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
                        group = input("group? ({}) > ".format(group_name)).strip(" ")
                        if group == "None":
                            group_name = None
                        elif group != "":
                            group_name = group

                        if group_name is not None:
                            database_manager.add_card_to_group(card_id, group_name)
                            print("Added card {} to group {}.".format(card_id, group_name))

                else:
                    print("no translations to save.")

                return group_name

            # otherwise continue with given context
            else:
                context = choice
                synonyms_done = False

        # last choice asked for synonyms
        elif not synonyms_done:
            # no synonyms for latin phrase
            if choice == "":
                synonyms_done = True
            # save synonym
            else:
                l_phrase = "{} {}".format(rf, context) if context else rf
                translations.append((l_phrase, "latin", choice, "latin"))

        # last choice asked for translations
        # if nothing was given, go back to context level
        elif choice == "":
            context = None
        # otherwise save given translation
        else:
            l_phrase = "{} {}".format(rf, context) if context else rf
            translations.append((l_phrase, "latin", choice, "german"))

        # ask for next choice
        if rf is None:
            choice = input("root forms > ").strip(" ")
        elif context is None:
            choice = input("y|context > ").strip(" ")
        elif not synonyms_done:
            choice = input("synonym > ").strip(" ")
        else:
            choice = input("translation > ").strip(" ")

    return "break"
