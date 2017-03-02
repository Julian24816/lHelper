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
Call question_all(<List[data.UsedCard]>) to question the user over these vocabs.
"""

from data.cardManager import CardManager, UsedCard
from language import German, Latin

from typing import Iterable
from random import shuffle, sample
from re import match

WRONG, AGAIN, CORRECT = range(3)


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
    group = CardManager.get_group_for_name(group_name)
    question_all(group.get_cards())


def question_all(cards: Iterable[UsedCard]):
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

    again = []
    wrong = []

    shuffle(cards)

    for card in cards:
        print("\nCard {} out of {}.".format(cards.index(card)+1, len(cards)))

        res = question(card)

        if res == CORRECT:
            CardManager.correct(card)
            print("Correct.")

        elif res == AGAIN and card.shelf >= CardManager.MIN_AGAIN_SHELF:
            CardManager.again(card)
            again.append(card)
            print("You get a second chance.")

        else:
            CardManager.wrong(card)
            wrong.append(card)
            print("Wrong.")

        print_card_info(card)

    if again:
        print("\nSecond chance for {} cards:".format(len(again)))

    for card in again:
        print("\nCard {} out of {}.".format(again.index(card)+1, len(again)))

        res = question(card)

        if res == CORRECT:
            CardManager.correct(card)
            print("Correct.")

        else:
            CardManager.wrong(card)
            wrong.append(card)
            print("Wrong.")

        print_card_info(card)

    if wrong:
        print("\nLearning of {} cards necessary.".format(len(wrong)))

    while len(wrong):

        # choose 7 cards:
        to_learn = sample(wrong, min(len(wrong), 7))
        for card in to_learn:
            wrong.remove(card)
        print("\nChosen {} cards for learning sequence.".format(len(to_learn)))

        consecutive_correct = 0
        while consecutive_correct < 2:
            shuffle(to_learn)
            all_correct = True

            for card in to_learn:
                print("\nCard {} out of {}.".format(to_learn.index(card)+1, len(to_learn)))
                if question(card) != CORRECT:
                    all_correct = False

            if all_correct:
                consecutive_correct += 1
            else:
                consecutive_correct = 0

            if consecutive_correct < 2:
                print("\nand again :P")

        for card in to_learn:
            CardManager.correct(card)

        print("\n{} cards left for learning.".format(len(wrong)))

    print("Done.")


def print_card_info(card: UsedCard):
    """
    Prints a cards shelf and due date.
    :param card: the card to be printed
    """
    print('New shelf:', card.get_shelf())
    print('Next questioning:', card.get_due_date())


def print_shelf_counts(counts):
    """
    Prints the amount of cards in the shelves to the console.
    :param counts: counts[i] amount of cards in shelf i
    """
    for i in range(len(counts)):
        if counts[i] != 0:
            print("Shelf {}: {} cards".format(i, counts[i]))
    print("Sum: {} cards".format(sum(counts)))


def question_single_card(card_id):
    """
    Questions the user over a card
    :param card_id: the cards id.
    """
    card = CardManager.get_card(card_id)
    done = False
    while not done:

        # and question the user about it
        if question(card):
            print("Correct +1")
            CardManager.correct(card)
            done = True
        else:
            CardManager.wrong(card)

        # print the cards new shelf and next questioning date
        print('New shelf:', card.get_shelf())
        print('Next questioning:', card.get_due_date())
        print()


def question(card: UsedCard) -> int:
    """
    Question the User over card.
    :param card: the vocabulary card.
    :return: CORRECT, AGAIN or WRONG
    """

    #######
    # retrieve data from card

    synonyms = {}  # todo fix synonym recognition
    translations = {}
    for phrase1, phrase2 in card.get_translations():

        # switch pairs if pair 1 is a german phrase
        if phrase1.language == German:
            phrase1, phrase2 = phrase2, phrase1

        # german-german
        if phrase1.language == German:
            continue

        # latin-?
        elif phrase1.language == Latin:

            # latin-latin == synonym
            if phrase2.language == Latin:

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
            elif phrase2.language == German:

                # if there's a synonym for phrase1 registered already, use that phrase instead
                for phrase in synonyms:
                    if phrase1 in synonyms[phrase]:
                        phrase1 = phrase
                        break

                if phrase1 not in translations:
                    translations[phrase1] = set()

                translations[phrase1].add(phrase2.phrase)

            else:
                raise Exception("Unknown language: {}".format(phrase2.language))
        else:
            raise Exception("Unknown language: {}".format(phrase1.language))

    #######
    # question user over the data

    # print general card information
    groups = sorted(card.get_groups())
    print("[{}, {}, {}]".format(card.get_id(), card.get_shelf(), ", ".join(groups) if groups else "None"))

    wrong_answers = 0

    last_word = None

    # ask for translations for each phrase
    for phrase in translations:

        if phrase.is_word():
            # don't print the root_forms again if they were already asked for
            if last_word is None or last_word.root_forms != phrase.root_forms:

                # print synonyms
                if phrase in synonyms:
                    for synonym in synonyms[phrase]:
                        print(synonym, "/", end=" ")

                # if the phrase is a verb with at least 3 root_forms, ask the user for the root_forms
                if phrase.is_verb() and match("\w+, \w+, .+", phrase.root_forms):
                    infinitive, *rest = (word.strip(" ") for word in phrase.root_forms.split(","))

                    forms = input(infinitive + ", ").strip(" ")
                    if not fuzzy_match(forms, ", ".join(rest)):
                        wrong_answers += 1
                    if forms != ", ".join(rest):
                        print(", ".join([infinitive] + rest), "would be correct!")

                # otherwise just print the root_forms
                else:
                    print(phrase.root_forms, end="")

            last_word = phrase

            # ask for translations:
            res = input((" " if phrase.context else "") + "{}: ".format(phrase.context))

        # phrase is no Word -> WordGroup
        else:
            # ask for translations:
            res = input(phrase.phrase + ": ")

        answer = set(word.strip(" ") for word in res.split(","))
        solution = translations[phrase]

        # todo expand brackets

        if "" in answer:
            answer.remove("")

        # remove correct answers from both sets
        answer, solution = answer.difference(solution), solution.difference(answer)

        # look for typos
        for answer_phrase in answer.copy():
            for correct_phrase in solution.copy():
                if fuzzy_match(answer_phrase, correct_phrase):
                    print("typo: {} -> {}".format(answer_phrase, correct_phrase))
                    answer.remove(answer_phrase)
                    solution.remove(correct_phrase)
                    break

        # check whether a missing solution has a comma
        for correct_phrase in solution.copy():
            if "," in correct_phrase and set(correct_phrase.split(",")).difference(answer) == 0:
                solution.remove(correct_phrase)
                for word in set(correct_phrase.split(",")):
                    answer.remove(word.strip(" "))

        if answer:  # wrong translations
            print("wrong:  ", ", ".join(answer))

        if solution:  # missing translations
            print("missing:", ", ".join(solution))

        wrong_answers += max(len(answer), len(solution))

    #######
    # return True/False according to answers

    if wrong_answers == 0:
        return CORRECT

    elif input("Your answers haven't all been correct. Forward anyway? [y] ").endswith("y"):
        return CORRECT

    elif wrong_answers == 1:
        return AGAIN

    return WRONG


def fuzzy_match(string: str, correct: str):
    """
    Returns True if the string has <= 1 typo in respect to <correct>.
    :param string: the string with a typo
    :param correct: the correct string
    :return: number of typos < 2
    """
    if string == correct:
        return True

    def fix(string_to_fix: str):
        """
        replaces the brackets
        :param string_to_fix: the string to be fixed
        :return: the fixed string
        """
        return string_to_fix.replace("(", "[(]").replace(")", "[)]")

    # character to much
    for i in range(len(correct) + 1):
        if match("^{}.{}$".format(fix(correct[:i]), fix(correct[i:])), string):
            return True

    # character missing or character wrong
    for i in range(len(correct)):
        if match("^{}.?{}$".format(fix(correct[:i]), fix(correct[i + 1:])), string):
            return True

    # 2 characters switched
    for i in range(len(correct) - 1):
        if match("^{}{}{}{}$".format(fix(correct[:i]), fix(correct[i + 1]),
                                     fix(correct[i]), fix(correct[i + 2:])), string):
            return True

    return False
