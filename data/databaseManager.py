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
Responsible for all database interactions.
"""

import sqlite3
from singleton import Singleton
from data.databaseConstants import *
from data.classes import Card, UsedCard


class DatabaseOpenHelper:
    """
    Responsible for opening the database.
    """
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.create_tables()

    def get_connection(self) -> sqlite3.Connection:
        """
        Opens the database and returns a Cursor
        :return: a Cursor
        """
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        """
        Creates the database tables if not present.
        """
        print(self.__class__, "has not implemented the create_tables method")


@Singleton
class DatabaseManager(DatabaseOpenHelper):
    """
    Responsible for all database interactions not concerning user data.
    """

    def __init__(self, db_name: str):
        super().__init__(db_name)

    def create_tables(self):
        """
        Creates the database tables if not present.
        """
        db = self.get_connection()
        cur = db.cursor()
        cur.execute(CREATE_TABLE_WORD)
        cur.execute(CREATE_TABLE_USAGE)
        cur.execute(CREATE_TABLE_TRANSLATION)
        cur.execute(CREATE_TABLE_CARD)
        db.commit()
        db.close()

    def load_card(self, card_id: int) -> Card:
        """
        Loads a card from the database.
        :param card_id: the card's id
        """
        db = self.get_connection()
        cur = db.cursor()

        cur.execute("SELECT " + ", ".join(["l." + WORD_ROOT_FORMS, "l." + WORD_ANNOTATIONS, "lu." + USAGE_CONTEXT,
                                           "g." + WORD_ROOT_FORMS, "g." + WORD_ANNOTATIONS, "gu." + USAGE_CONTEXT]) +
                    " FROM " + TABLE_CARD + " AS c" +
                    " JOIN " + TABLE_TRANSLATION + " AS t ON c." + TRANSLATION_ID + "=t." + TRANSLATION_ID +
                    " JOIN " + TABLE_USAGE + " AS lu ON t." + TRANSLATION_LATIN_USAGE_ID + "=lu." + USAGE_ID +
                    " JOIN " + TABLE_WORD + " AS l ON lu." + WORD_ID + "=l." + WORD_ID +
                    " JOIN " + TABLE_USAGE + " AS gu ON t." + TRANSLATION_GERMAN_USAGE_ID + "=gu." + USAGE_ID +
                    " JOIN " + TABLE_WORD + " AS g ON gu." + WORD_ID + "=g." + WORD_ID +
                    " WHERE c." + CARD_ID + "=" + str(card_id)
                    )
        translations = []
        for l_root, l_annotation, l_context, g_root, g_annotation, g_context in cur.fetchall():
            print(l_root, l_annotation, l_context, g_root, g_annotation, g_context)

        db.close()
        return Card(translations, card_id)


@Singleton
class UserDatabaseManager(DatabaseOpenHelper):
    """
    Responsible for all database interactions concerning user data.
    """

    def __init__(self, user_name: str):
        super().__init__(user_name+".sqlite3")
        self.user_name = user_name

    def create_tables(self):
        """
        Creates the database tables if not present.
        """
        db = self.get_connection()
        cur = db.cursor()
        cur.execute(CREATE_TABLE_USED_CARD)
        db.commit()
        db.close()