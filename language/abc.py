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
Provides abstract base classes for all languages.
"""


class Language:
    """
    Contains a language.
    """
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return 'Language("{}")'.format(self.name)

    def __str__(self):
        return self.name


class Phrase:
    """
    Contains a phrase.
    """
    def __init__(self, phrase: str, language: Language):
        self.phrase = phrase
        self.language = language

    def __repr__(self):
        return 'Phrase("{}","{}")'.format(self.phrase, self.language)

    def __str__(self):
        return self.phrase

    @staticmethod
    def parse_phrase(phrase: str):
        """
        Parses a phrase.
        :param phrase: the phrase to be parsed
        :return: a Phrase object
        """
        raise NotImplementedError

    def __eq__(self, other):
        return isinstance(other, Phrase) and self.phrase == other.phrase and self.language == other.language

    def __hash__(self):
        return hash(self.phrase)
