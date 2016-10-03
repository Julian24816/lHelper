# coding=utf-8

"""
Lets the user assign groups to all cards, which have no group yet.
"""

import data

cards = [data.database_manager.get_card(card_id) for card_id, in data.database_manager.get_connection().execute(
    "SELECT card_id FROM card WHERE card_id NOT IN (SELECT card_id FROM card_group_membership)").fetchall()]

print(len(cards))
new_cards = []
for card in cards:
    if card not in new_cards:
        new_cards.append(card)
print(len(new_cards))
cards = new_cards

group_name = "adeo-11"
for card_id, translations in cards:
    for translation in translations:
        print(translation)
    group = input("group_name? {} > ".format(group_name)).strip(" ")
    if group != "":
        group_name = group
    data.database_manager.add_card_to_group(card_id, group_name)
