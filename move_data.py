# coding=utf-8

"""
moves the word_data to a new database
"""

from data import database_manager, user_database_manager
from data.oldDatabaseManager import OldDatabaseManager, OldUserDatabaseManager
from data.classes import Translation
from tui.menu import choose_option
from typing import Tuple

old_database_manager = OldDatabaseManager("old_data.sqlite3")
old_user_database_manager = OldUserDatabaseManager("old_julian", old_database_manager)


start = "labor"


# move cards
for used_card in sorted(old_user_database_manager.get_all_cards(),
                        key=lambda card: card.get_translations()[0].latinUsage.word.root_forms):

    if used_card.get_translations()[0].latinUsage.word.root_forms < start:
        continue

    # get group names
    groups = list(map(old_database_manager.get_group_name, old_database_manager.get_groups_for_card(used_card.Id)))
    print(groups)

    shelf = used_card.shelf
    print(shelf)
    due_date = used_card.next_questioning

    def parse_translation(translation: Translation)->Tuple[str, str, str, str]:
        """
        Parses the translation into the new format
        :param translation: a Translation object
        :return: a 4-tuple
        """
        return str(translation.latinUsage), "latin", str(translation.germanUsage), "german"

    translations = list(map(parse_translation, used_card.translations))
    print("translations:")
    print(*translations, sep="\n")

    if choose_option(["y", ""], "edit? ")[0] == "y":
        new_translations = []

        for translation in translations:
            new = input(str(translation)+" > ")
            if new == "":
                new_translations.append(translation)
            elif new == "remove":
                continue
            else:
                new_translations.append(tuple(map(lambda e: e.strip(" "), new.split(";"))))

        res = " "
        while res != "":
            res = input("add: ")
            if res != "":
                new_translations.append(tuple(map(lambda e: e.strip(" "), res.split(";"))))

        print("new translations:")
        translations = new_translations
        print(*translations, sep="\n")

    if choose_option(["y", "n"], "input to database? ")[0] == "n":
        continue

    card_id = database_manager.add_card(translations)
    for group in groups:
        database_manager.add_card_to_group(card_id, group)
    user_database_manager.add_card(card_id, shelf, due_date)

    print(card_id)
    print()
