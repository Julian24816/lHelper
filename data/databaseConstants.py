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
Provides constants for the data.sqlite3 database.
"""

TABLE_PHRASE = "phrase"
PHRASE_ID = "phrase_id"
PHRASE_DESCRIPTION = "description"
PHRASE_LANGUAGE = "language"

CREATE_TABLE_PHRASE = "CREATE TABLE IF NOT EXISTS " + TABLE_PHRASE + "(" + \
                      PHRASE_ID + " INTEGER PRIMARY KEY, " + \
                      PHRASE_DESCRIPTION + " TEXT UNIQUE, " + \
                      PHRASE_LANGUAGE + " TEXT);"


TABLE_TRANSLATION = "translation"
TRANSLATION_ID = "translation_id"
TRANSLATION_PHRASE_1 = "phrase_1"
TRANSLATION_PHRASE_2 = "phrase_2"

CREATE_TABLE_TRANSLATION = "CREATE TABLE IF NOT EXISTS " + TABLE_TRANSLATION + "(" + \
                           TRANSLATION_ID + " INTEGER PRIMARY KEY, " + \
                           TRANSLATION_PHRASE_1 + " INTEGER, " + \
                           TRANSLATION_PHRASE_2 + " INTEGER, " + \
                           "UNIQUE (" + TRANSLATION_PHRASE_1 + "," + TRANSLATION_PHRASE_2 + "));"


TABLE_CARD = "card"
CARD_ID = "card_id"

CREATE_TABLE_CARD = "CREATE TABLE IF NOT EXISTS " + TABLE_CARD + "(" + \
                    CARD_ID + " INTEGER, " + \
                    TRANSLATION_ID + " INTEGER, " + \
                    "UNIQUE (" + CARD_ID + "," + TRANSLATION_ID + "));"


TABLE_GROUP = "card_group"
GROUP_ID = "group_id"
GROUP_NAME = "name"
GROUP_PARENT = "parent"

CREATE_TABLE_GROUP = "CREATE TABLE IF NOT EXISTS " + TABLE_GROUP + " (" + \
                     GROUP_ID + " INTEGER PRIMARY KEY, " + \
                     GROUP_NAME + " TEXT UNIQUE, " + \
                     GROUP_PARENT + " INTEGER DEFAULT NULL);"


TABLE_CARD_GROUP = "card_group_map"  # card - group map

CREATE_TABLE_CARD_GROUP = "CREATE TABLE IF NOT EXISTS " + TABLE_CARD_GROUP + "(" + \
                          GROUP_ID + " INTEGER, " + \
                          CARD_ID + " INTEGER, " + \
                          "UNIQUE (" + GROUP_ID + "," + CARD_ID + "));"
