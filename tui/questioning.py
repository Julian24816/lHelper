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
Provides methods for the 'question' cycle.
Call question_all(<List[data.Card]>) to question the user over these vocabs.
"""

from data.cardManager import CardManager, Card

from typing import Iterable
from random import choice
from re import match


def question_all_due():
    """
    Questions the user over all due cards.
    """
    question_all(CardManager.get_due_cards("today"))


def question_all_group(group_name: str):
    """
    Questions the user over all cards in card-group group_name.
    :param group_name: the groups name
    """
    question_all(CardManager.get_group_for_name(group_name).get_cards())


def question_all(cards: Iterable[Card]):
    """
    Questions the User over the vocabulary cards.
    :param cards: vocabulary cards
    """

    cards = list(cards)

    # prints the amount of cards in the different shelves
    counts = []
    for card in cards:
        # expand counts as far as needed
        if card.get_shelf() > len(counts) - 1:
            counts += [0 for _ in range(card.get_shelf() - len(counts) + 1)]

        # and count the card
        counts[card.get_shelf()] += 1
    print_shelf_counts(counts)

    # while the list contains a card
    while len(cards) > 0:
        print()

        # choose one of them
        card = choice(cards)

        # print(card.get_id())

        # and question the user about it
        if question(card):
            print("Correct +1")
            CardManager.correct(card)

            # when answered correct remove the card from the list
            cards.remove(card)
        else:
            CardManager.wrong(card)

        # print the cards new shelf and next questioning date
        print('New shelf:', card.get_shelf())
        print('Next questioning:', card.get_due_date())
        print(len(cards), "cards left.")

    print("Done ^^")


def print_shelf_counts(counts):
    """
    Prints the amount of cards in the shelves to the console.
    :param counts: counts[i] amount of cards in shelf i
    """
    for i in range(len(counts)):
        if counts[i] != 0:
            print("Shelf {}: {} cards".format(i, counts[i]))
    print("Sum: {} cards".format(sum(counts)))


def question(card: Card) -> bool:
    """
    Question the User over card.
    :param card: the vocabulary card.
    :return: True if the User succeeded.
    """

    #######
    # retrieve data from card

    synonyms = {}
    translations = {}
    for phrase1, language1, phrase2, language2 in card.get_translations():

        # switch pairs if pair 1 is a german phrase
        if language1 == "german":
            phrase1, language1, phrase2, language2 = phrase2, language2, phrase1, language1

        # german-german
        if language1 == "german":
            continue

        # latin-?
        elif language1 == "latin":

            # latin-latin == synonym
            if language2 == "latin":

                # if one of the synonyms is already registered ...
                for phrase in synonyms:
                    if phrase1 in synonyms[phrase]:
                        synonyms[phrase].add(phrase2)
                    elif phrase2 in synonyms[phrase]:
                        synonyms[phrase].add(phrase2)

                if phrase1 in synonyms:
                    synonyms[phrase1].add(phrase2)
                elif phrase2 in synonyms:
                    synonyms[phrase2].add(phrase1)

                # or if a translation for one of the phrases already exists, use that phrase as a key
                elif phrase2 in translations:
                    synonyms[phrase2] = set()
                    synonyms[phrase2].add(phrase1)

                else:  # or phrase1 in translations
                    synonyms[phrase1] = set()
                    synonyms[phrase1].add(phrase2)

            # latin-german == translation
            elif language2 == "german":

                # if there's a synonym for phrase1 registered already, use that phrase instead
                for phrase in synonyms:
                    if phrase1 in synonyms[phrase]:
                        phrase1 = phrase
                        break

                if phrase1 not in translations:
                    translations[phrase1] = set()

                translations[phrase1].add(phrase2)

            else:
                raise Exception("Unknown language: {}".format(language2))
        else:
            raise Exception("Unknown language: {}".format(language1))

    #######
    # question user over the data

    all_answers_correct = True

    already_asked = None

    for phrase in translations:

        # split into root_forms and context
        m = match("(.+[^,]) ", phrase)  # stuff + no comma + space + stuff
        if m:
            root_forms, context = phrase[:len(m.group())], phrase[len(m.group()):]
        else:
            root_forms, context = phrase, ""

        # don't print the root_forms again if they were already asked for
        if already_asked != root_forms:
            # print synonyms
            if phrase in synonyms:
                for synonym in synonyms[phrase]:
                    print(synonym, "/", end=" ")

            # if the root_forms belong to a verb with at least 3 forms, ask user for the root_forms
            if match(".+re, .+o, .+|.+i, .+or, .+", root_forms):
                infinitive, *rest = map(lambda word: word.strip(" "), root_forms.split(","))
                if input(infinitive+", ") != ", ".join(rest):
                    all_answers_correct = False
                    print(", ".join([infinitive]+rest), "would be correct!")

            # otherwise just print them out
            else:
                print(phrase, end="")

            already_asked = root_forms

        # ask for translations:
        answer = set(map(lambda word: word.strip(" "), input(": ").split(",")))

        if "" in answer:
            answer.remove("")

        if answer != translations[phrase]:
            all_answers_correct = False
            translations_missing = False
            if translations[phrase] - answer:  # missing translations
                translations_missing = True
                print("missing:", ", ".join(translations[phrase] - answer))
            if answer - translations[phrase]:  # wrong translations
                print("wrong:"+("  " if translations_missing else ""), ", ".join(answer - translations[phrase]))

    #######
    # return True/False according to answers

    if all_answers_correct:
        return True

    # allow for typos to be forwarded anyway
    elif input("Your answers haven't all been correct. Forward anyway? [y] ").endswith("y"):
        return True

    return False
