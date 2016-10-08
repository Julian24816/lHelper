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
Provides methods for the 'edit' command.
"""

from data import database_manager


def edit_card(card_id: int):
    """
    Lets the user edit a card
    :param card_id: the id of the card to edit.
    """
    if not database_manager.card_exists(card_id):
        print("Card {} does not exist.".format(card_id))
        return

    # load old data
    translations = database_manager.get_card(card_id)[1]

    # print old data
    print("old:")
    print(*translations, sep="\n")

    # def next_translation():
    #     """
    #     :return: the next translation in the list.
    #     """
    #     t = translations.pop(0)
    #     if t[1] == "german":
    #         if t[3] == "german":
    #             raise RuntimeError(t)
    #         else:
    #             t = [t[2], t[3], t[0], t[1]]
    #     return t

    # input new data
    print("edit:")
    added_translations = []
    edited_translations = {}
    removed_translations = []

    i = 0
    while i <= len(translations):

        if i < len(translations):
            res = [el.strip(" ") for el in input("{} > ".format(translations[i])).split(";")]
            phrase1, language1, phrase2, language2 = translations[i]
            i += 1
        else:
            res = [el.strip(" ") for el in input("add > ").split(";")]
            if not res[0] or res[0] == "r":
                break
            phrase1, language1, phrase2, language2 = "None", "latin", "None", "german"

        if len(res) > 4:
            raise RuntimeError("to many arguments in edit")
        elif res[0] == "r":
            removed_translations.append(translations[i])
            continue

        if len(res) >= 4 and res[3]:
            language2 = res[3]
        if len(res) >= 3 and res[2]:
            phrase2 = res[2]
        if len(res) >= 2 and res[1]:
            language1 = res[1]
        if res[0]:
            phrase1 = res[0]

        if i < len(translations):
            edited_translations[translations[i]] = (phrase1, language1, phrase2, language2)
        else:
            added_translations.append((phrase1, language1, phrase2, language2))

    # print new translations
    print("new:")
    if edited_translations:
        print(*edited_translations.values(), sep="\n")
    if added_translations:
        print(*added_translations, sep="\n")

    if input("Save card? [y] ").strip(" ").lower().endswith("y"):
        database_manager.update_card(card_id, added_translations, edited_translations, removed_translations)
        print("Card saved.")

    # current_translation = next_translation()
    # last_phrase = None
    # current_phrase = None
    # synonyms_edited = False
    # synonyms_done = False
    # translations_edited = False
    #
    # res = input("{} > ".format(current_translation[0])).strip(" ")
    # while res != "break":
    #
    #     # if last input asked for a latin_phrase update
    #     if current_phrase is None:
    #
    #         # leave latin_phrase as is
    #         if res == "":
    #             current_phrase = current_translation[0]
    #
    #         # skip to next translation to remove the current latin_phrase
    #         elif res == "r":
    #             current_translation = next_translation()
    #
    #         # save the new phrase
    #         else:
    #             current_phrase = res
    #
    #     # if last input asked for the editing of a synonym
    #     elif not
    #
    #     # if last input asked for a new synonym
    #     elif not synonyms_done:
    #         if res == "":
    #             synonyms_done = True
    #         else:
    #             new_translations.append((current_phrase, "latin", res, "latin"))
    #
    #     # if last input asked for editing a translation
    #     elif :
    #         if res
