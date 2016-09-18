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
Provides constants for the Databases.
"""

TABLE_WORD = "word"
WORD_ID = "word_id"
WORD_ROOT_FORMS = "root_forms"
WORD_ANNOTATIONS = "annotations"
WORD_LANGUAGE = "language"

CREATE_TABLE_WORD = "CREATE TABLE IF NOT EXISTS " + TABLE_WORD + "(" + \
                    WORD_ID + " INTEGER PRIMARY KEY, " + \
                    WORD_ROOT_FORMS + " TEXT UNIQUE, " + \
                    WORD_ANNOTATIONS + " TEXT, " + \
                    WORD_LANGUAGE + " TEXT);"

TABLE_USAGE = "usage"
USAGE_ID = "usage_id"
USAGE_CONTEXT = "context"

CREATE_TABLE_USAGE = "CREATE TABLE IF NOT EXISTS " + TABLE_USAGE + "(" + \
                     USAGE_ID + " INTEGER PRIMARY KEY, " + \
                     WORD_ID + " INTEGER, " + \
                     USAGE_CONTEXT + " TEXT, " + \
                     "UNIQUE (" + WORD_ID + "," + USAGE_CONTEXT + "));"

TABLE_TRANSLATION = "translation"
TRANSLATION_ID = "translation_id"
TRANSLATION_LATIN_USAGE_ID = "latin_usage_id"
TRANSLATION_GERMAN_USAGE_ID = "german_usage_id"

CREATE_TABLE_TRANSLATION = "CREATE TABLE IF NOT EXISTS " + TABLE_TRANSLATION + "(" + \
                           TRANSLATION_ID + " INTEGER PRIMARY KEY, " + \
                           TRANSLATION_LATIN_USAGE_ID + " INTEGER, " + \
                           TRANSLATION_GERMAN_USAGE_ID + " INTEGER, " + \
                           "UNIQUE (" + TRANSLATION_LATIN_USAGE_ID + "," + TRANSLATION_GERMAN_USAGE_ID + "));"

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

TABLE_USED_CARD = "used_card"
USED_CARD_SHELF = "shelf"
USED_CARD_NEXT_QUESTIONING = "next_questioning"

CREATE_TABLE_USED_CARD = "CREATE TABLE IF NOT EXISTS " + TABLE_USED_CARD + "(" + \
                         CARD_ID + " INTEGER PRIMARY KEY, " + \
                         USED_CARD_SHELF + " INTEGER DEFAULT 0, " + \
                         USED_CARD_NEXT_QUESTIONING + " DATE DEFAULT CURRENT_DATE);"
