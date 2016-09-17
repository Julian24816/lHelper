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

from typing import List
from data import UsedCard, card_manager
from random import choice


def print_shelf_counts(counts):
    """
    Prints the amount of cards in the shelves to the console.
    :param counts: counts[i] amount of cards in shelf i
    """
    for i in range(len(counts)):
        if counts[i] != 0:
            print("Shelf {}: {} cards".format(i, counts[i]))
    print("Sum: {} cards".format(sum(counts)))


def question_all(cards: List[UsedCard]):
    """
    Questions the User over the vocabulary cards.
    :param cards: vocabulary cards
    """
    counts = []
    for card in cards:
        if card.get_shelf() > len(counts) - 1:
            counts += [0 for _ in range(card.get_shelf() - len(counts) + 1)]
        counts[card.get_shelf()] += 1
    print_shelf_counts(counts)

    while len(cards) > 0:
        print()

        card = choice(cards)
        if question(card):
            print("Correct +1")
            card_manager.correct(card)
            cards.remove(card)
        else:
            card_manager.wrong(card)

        print('New shelf:', card.get_shelf())
        print('Next questioning:', card.get_next_questioning())
        print(len(cards), "cards left.")

    print("Done ^^")


def question(card: UsedCard) -> bool:
    """
    Question the User over card.
    :param card: the vocabulary card.
    :return: True if the User succeeded.
    """
    all_answers_correct = True

    #######
    # retrieving Data from Card-object

    latin_word = None  # the latin word on the card
    meanings_with_context = {}  # dictionary of usages of the latin word and associated meanings (german words)

    for translation in card.get_translations():
        latin_usage = translation.get_latin_usage()

        if latin_word is None:  # true for first translation in card.get_translations()
            latin_word = latin_usage.get_word()

        if latin_usage not in meanings_with_context:  # assert the current usage is in the dictionary
            meanings_with_context[latin_usage] = set()

        # add the meaning to the dictionary
        meanings_with_context[latin_usage].add(translation.get_german_usage().get_word())

    #######
    # printing/asking for root forms

    expected = latin_word.get_root_forms_to_question()
    if expected[1] is None:
        print(expected[0], end="")
    else:
        answer = input(expected[0] + ", ").strip(" ")
        if answer != expected[1]:
            print(", ".join(expected), "would be correct")
            all_answers_correct = False

    #######
    # asking for meanings per context

    for latin_usage in meanings_with_context:

        # ask for meanings
        if latin_usage.get_context() == "":
            answer = input(": ").strip(" ")
        else:
            answer = input(latin_usage.get_context() + ": ").strip(" ")

        # convert answer to set
        answer = set([el.strip(" ") for el in answer.split(",")])
        if "" in answer:  # remove emtpy answer from set
            answer.remove("")

        # fetch correct meanings
        meanings = set([word.get_root_forms() for word in meanings_with_context[latin_usage]])

        # comparing the 2 answer-sets
        if answer != meanings:
            all_answers_correct = False
            if len(answer - meanings) > 0:
                print("incorrect meanings: " + ", ".join(answer - meanings))
            if len(meanings - answer) > 0:
                print("missing meanings: " + ", ".join(meanings - answer))

    #######
    # return True/False according to answers
    if all_answers_correct:
        return True
    elif input("Your answers haven't all been correct. Forward anyway? [y] ") == "y":
        return True  # allow for typos to be forwarded anyway
    return False
