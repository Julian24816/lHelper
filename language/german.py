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
Manages the parsing of german phrases.
"""

from language.abc import Language, Phrase
from typing import List

German = Language("german")


class GermanPhrase(Phrase):
    """
    Holds a German phrase.
    """
    def __init__(self, phrase_description: str):
        super(GermanPhrase, self).__init__(phrase_description, German)

    @staticmethod
    def parse_phrase(phrase: str):
        """
        Parses a phrase string into a german phrase.
        :param phrase: the phrase string.
        :return: the Phrase
        """
        return GermanPhrase(phrase)

    @staticmethod
    def get_possible_root_forms_for(string: str) -> List[str]:
        """
        Returns all root forms that belong to words that could when bend result in the given string.
        :param string: the string to find root forms for
        :return: a list of strings
        """
        return string

