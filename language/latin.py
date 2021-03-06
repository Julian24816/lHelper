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
Manages the parsing of latin phrases.
"""

from language.abc import Language, Phrase

from re import match
from typing import List

Latin = Language("latin")


class LatinPhrase(Phrase):
    """
    Holds a Latin phrase.
    """

    def __init__(self, phrase_description: str):
        super(LatinPhrase, self).__init__(phrase_description, Latin)

    @staticmethod
    def parse_phrase(phrase: str):
        """
        Parses a phrase string
        :param phrase: the phrase to parse
        """
        if phrase.find("...") != -1:
            return WordGroup(phrase)

        m = match("^(\w+re|\w+ri)(, \w+)+( sum)?", phrase)
        if m:
            return Verb(phrase[:len(m.group())], phrase[len(m.group()):])

        # todo parse for other kinds of words
        return WordGroup(phrase)

    @staticmethod
    def get_possible_root_forms_for(string: str) -> List[str]:
        """
        Returns all root forms that belong to words that could when bend result in the given string.
        :param string: the string to find root forms for
        :return: a list of strings
        """
        raise NotImplementedError
        # todo implement get possible root forms

    def is_word(self):
        """
        :return: True if self is word.
        """
        return isinstance(self, Word)


class WordGroup(LatinPhrase):
    """
    A group of latin words.
    """


class Word(LatinPhrase):
    """
    A latin word.
    """
    def __init__(self, root_forms: str, context: str):
        self.root_forms = root_forms.strip(" ")
        self.context = context.strip(" ")
        super(Word, self).__init__(root_forms + " " + context)

    def is_verb(self):
        """
        :return: True if self is a Verb.
        """
        return isinstance(self, Verb)


class InflectedWord(Word):
    """
    A inflected latin word.
    """


class Verb(InflectedWord):
    """
    A latin verb.
    """


'''
class Noun(InflectedWord):
    """
    A latin noun.
    """


class Name(Noun):
    """
    A latin name. (=noun)
    """


class Adjective(InflectedWord):
    """
    A latin adjective.
    """


class Pronoun(InflectedWord):
    """
    A latin pronoun.
    """


class Numeral(InflectedWord):
    """
    A latin numeral.
    """


class NotInflectedWord(Word):
    """
    A not inflected latin Word.
    """


class Adverb(NotInflectedWord):
    """
    A latin adverb.
    """


class Preposition(NotInflectedWord):
    """
    A latin preposition.
    """


class Connective(NotInflectedWord):
    """
    A latin connective.
    """


class Conjunction(Connective):
    """
    A latin conjunction.
    """


class Subjunction(Connective):
    """
    A latin subjunction.
    """


class Interjection(NotInflectedWord):
    """
    A latin interjection.
    """
'''
