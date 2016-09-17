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
Provides data classes.
"""

from typing import List, Tuple
from time import strftime, localtime, time


class Word:
    """
    Contains a word.
    """
    words = {}  # todo assert that no word is instantiated twice

    def __new__(cls, stammformen: str, anmerkungen: str, sprache: str):
        if stammformen not in Word.words:
            Word.words[stammformen] = object.__new__(cls)
            Word.words[stammformen].init(stammformen, anmerkungen, sprache)
        return Word.words[stammformen]

    def __init__(self, stammformen: str, anmerkungen: str, sprache: str):
        pass

    def init(self, stammformen: str, anmerkungen: str, sprache: str):
        self.root_forms = stammformen.strip(" ")
        self.annotations = anmerkungen.strip(" ")
        self.language = sprache

    def get_root_forms(self) -> str:
        """
        :return: the words root forms
        """
        return self.root_forms

    def get_anmerkungen(self) -> str:
        """
        :return: the words annotations
        """
        return self.annotations

    def get_language(self) -> str:
        """
        :return: the words language
        """
        return self.language

    def __str__(self):
        if self.annotations == "":
            return str(self.root_forms)
        return str(self.root_forms) + " " + self.annotations

    def get_root_forms_to_question(self) -> Tuple[str]:
        """
        If self is a Verb request questioning of the root_forms
        :return: a tuple of the root_forms to print out and the root_forms to question (may be None)
        """
        infinitive, *rest = self.root_forms.split(', ')
        if self.language == 'latin' and len(rest) > 1 and (
                    infinitive.endswith('re') or infinitive.endswith('ri')):  # Verb
            return infinitive, ', '.join(rest)
        return self.root_forms, None


class Usage:
    """
    Contains a Usage of a Word
    """

    usages = {}  # todo assert that no usage is instantiated twice

    def __new__(cls, word: Word, context: str):
        if (word, context) not in Usage.usages:
            Usage.usages[(word, context)] = object.__new__(cls)
            Usage.usages[(word, context)].init(word, context)
        return Usage.usages[(word, context)]

    def __init__(self, word: Word, context: str): pass

    def init(self, word: Word, context: str):
        self.word = word
        self.context = context.strip(" ")

    def get_word(self) -> Word:
        """
        :return: the usages word
        """
        return self.word

    def get_context(self) -> str:
        """
        :return: the usages context
        """
        return self.context

    def __str__(self):
        return (str(self.word) + " " + self.context).strip(" ")


class Translation:
    """
    Contains a translation
    """

    def __init__(self, latin_usage: Usage, german_usage: Usage):
        self.latinUsage = latin_usage
        self.germanUsage = german_usage

    def get_latin_usage(self) -> Usage:
        """
        :return: the translations latin usage
        """
        return self.latinUsage

    def get_german_usage(self) -> Usage:
        """
        :return: the translations german usage
        """
        return self.germanUsage

    def __str__(self):
        return str(self.latinUsage) + " -> " + str(self.germanUsage)


class Card:
    """
    Contains a Vocabulary Card.
    """

    def __init__(self, translations: List[Translation], card_id: int):
        self.Id = card_id
        self.translations = translations

    def get_id(self) -> int:
        """
        :return: the cards ID.
        """
        return self.Id

    def get_translations(self) -> List[Translation]:
        """
        :return: the cards list of translations
        """
        return self.translations

    def __str__(self):
        to_return = []
        for t in self.translations:
            to_return.append(str(t))
        return "\n".join(to_return)


class UsedCard(Card):
    """
    Contains a Card that is used by a User.
    """
    MAX_SHELF = 7

    def __init__(self, card_id: int, shelf: int, next_questioning: str, translations: List[Translation]):
        Card.__init__(self, translations, card_id=card_id)
        self.shelf = shelf
        self.next_questioning = next_questioning

    def get_shelf(self):
        """
        :return: return the shelf the card is on
        """
        return self.shelf

    def get_next_questioning(self):
        """
        :return: return the date of the cards next questioning
        """
        return self.next_questioning

    def __str__(self):
        return "{}\n shelf: {}, next questioning: {}".format(
            Card.__str__(self), self.shelf, self.next_questioning)
