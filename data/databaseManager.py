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
from data.classes import *
from typing import Dict
from time import strftime


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
        self.group_id = 0
        self.card_id = 0
        self.translation_id = 0
        self.usage_id = 0
        self.word_id = 0
        self.load_ids()

    def load_ids(self):
        """
        loads the current max ids from the database.
        """
        db = self.get_connection()
        cur = db.cursor()
        group_id = cur.execute("SELECT MAX(" + GROUP_ID + ") FROM " + TABLE_GROUP).fetchone()[0]
        card_id = cur.execute("SELECT MAX(" + CARD_ID + ") FROM " + TABLE_CARD).fetchone()[0]
        translation_id = cur.execute("SELECT MAX(" + TRANSLATION_ID + ") FROM " + TABLE_TRANSLATION).fetchone()[0]
        usage_id = cur.execute("SELECT MAX(" + USAGE_ID + ") FROM " + TABLE_USAGE).fetchone()[0]
        word_id = cur.execute("SELECT MAX(" + WORD_ID + ") FROM " + TABLE_WORD).fetchone()[0]
        db.close()
        if group_id is not None:
            self.group_id = group_id
        if card_id is not None:
            self.card_id = card_id
        if translation_id is not None:
            self.translation_id = translation_id
        if usage_id is not None:
            self.usage_id = usage_id
        if word_id is not None:
            self.word_id = word_id

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
        cur.execute(CREATE_TABLE_GROUP)
        cur.execute(CREATE_TABLE_CARD_GROUP)
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
        for l_root, l_annotation, l_context, g_root, g_annotation, g_context in cur:
            translations.append(Translation(Usage(Word(l_root, l_annotation, "latin"), l_context),
                                            Usage(Word(g_root, g_annotation, "german"), g_context)))

        db.close()
        return Card(translations, card_id)

    def add_card(self, card: Card) -> int:
        """
        Adds a card to the database and returns its new id.
        :param card: the Card to be added
        :return: the cards new id
        """
        self.card_id += 1

        db = self.get_connection()
        cur = db.cursor()

        for translation in card.get_translations():
            translation_id = self.add_translation(translation, cur)
            cur.execute("INSERT INTO " + TABLE_CARD + "("
                        + ",".join((TRANSLATION_ID, CARD_ID))
                        + " ) VALUES (" + ",".join((str(translation_id), str(self.card_id)))
                        + ")")

        db.commit()
        db.close()
        return self.card_id

    def add_translation(self, translation: Translation, cursor: sqlite3.Cursor) -> int:
        """
        Tries to add a translation to the database accessed with cursor and returns the translations id anyways.
        :param translation: the translation to be added
        :param cursor: the cursor to be used
        :return: the translations id
        """
        # fetch the usage ids
        latin_usage_id = self.add_usage(translation.latinUsage, cursor)
        german_usage_id = self.add_usage(translation.germanUsage, cursor)

        # try to insert the translation into the database
        try:
            cursor.execute("INSERT INTO " + TABLE_TRANSLATION + "("
                           + ",".join((TRANSLATION_ID, TRANSLATION_LATIN_USAGE_ID, TRANSLATION_GERMAN_USAGE_ID))
                           + ") VALUES (?,?,?)", (self.translation_id + 1, latin_usage_id, german_usage_id))

            # up the global max translation id upon success
            self.translation_id += 1
            return self.translation_id

        # translation already exists:
        except sqlite3.IntegrityError:
            # return the existing translation's id
            return cursor.execute("SELECT " + TRANSLATION_ID + " FROM " + TABLE_TRANSLATION
                                  + " WHERE " + TRANSLATION_LATIN_USAGE_ID + "= ? AND "
                                  + TRANSLATION_GERMAN_USAGE_ID + "= ?",
                                  (latin_usage_id, german_usage_id)).fetchone()[0]

    def add_usage(self, usage: Usage, cursor: sqlite3.Cursor) -> int:
        """
        Tries to add a usage to the database accessed with cursor and returns the usages id anyways.
        :param usage: the usage to be added
        :param cursor: the cursor to be used
        :return: the usages id
        """
        # fetch the word id
        word_id = self.add_word(usage.word, cursor)

        # try to insert the usage into the database
        try:
            cursor.execute("INSERT INTO " + TABLE_USAGE + "("
                           + ", ".join((USAGE_ID, WORD_ID, USAGE_CONTEXT))
                           + ") VALUES (?,?,?)", (self.usage_id + 1, word_id, usage.context))

            # up the global max usage id upon success
            self.usage_id += 1
            return self.usage_id

        # usage already exists
        except sqlite3.IntegrityError:
            # return the existing usage's id
            return cursor.execute("SELECT " + USAGE_ID + " FROM " + TABLE_USAGE
                                  + " WHERE " + WORD_ID + "= ? AND " + USAGE_CONTEXT + "= ?",
                                  (word_id, usage.context)).fetchone()[0]

    def add_word(self, word: Word, cursor: sqlite3.Cursor) -> int:
        """
        Tries to add a word to the database accessed with cursor and returns the words id anyways.
        :param word: the word to be added
        :param cursor: the cursor to be used
        :return: the words id
        """
        # try to insert the word into the database
        try:
            cursor.execute("INSERT INTO " + TABLE_WORD + "("
                           + ", ".join((WORD_ID, WORD_ROOT_FORMS, WORD_ANNOTATIONS, WORD_LANGUAGE))
                           + ") VALUES (?,?,?,?)", (self.word_id + 1, word.root_forms, word.annotations,
                                                    word.language))

            # up the global max word id upon success
            self.word_id += 1
            return self.word_id

        # word already exists
        except sqlite3.IntegrityError:
            # return the existing word's id
            return cursor.execute("SELECT " + WORD_ID + " FROM " + TABLE_WORD
                                  + " WHERE " + WORD_ROOT_FORMS + "= ?", (word.root_forms,)).fetchone()[0]

    def add_group(self, group: CardGroup, cursor: sqlite3.Cursor=None) -> int:
        """
        Tries to add the group to the database accessed by cursor and returns the groups id anyways.
        :param group: the group to be added
        :param cursor:
        :return: the groups id
        """
        if cursor is None:
            db = self.get_connection()
            cursor = db.cursor()
            group_id = self.add_group(group, cursor)
            db.commit()
            db.close()
            return group_id
        else:
            # fetch parent_id
            parent_id = None
            if group.parent is not None:
                parent_id = self.add_group(group.parent, cursor)

            # try to insert the word into the database
            try:
                cursor.execute("INSERT INTO " + TABLE_GROUP + "("
                               + ", ".join((GROUP_ID, GROUP_NAME, GROUP_PARENT))
                               + ") VALUES (?,?,?)", (self.group_id + 1, group.name, parent_id))

                # up the global max word id upon success
                self.group_id += 1
                return self.group_id

            # group (name) already exists
            except sqlite3.IntegrityError:
                # return the existing group's id
                return cursor.execute("SELECT " + GROUP_ID + " FROM " + TABLE_GROUP
                                      + " WHERE " + GROUP_NAME + "=?", (group.name,)).fetchone()[0]


@Singleton
class UserDatabaseManager(DatabaseOpenHelper):
    """
    Responsible for all database interactions concerning user data.
    """

    def __init__(self, user_name: str, dbm: DatabaseManager):
        super().__init__(user_name + ".sqlite3")
        self.user_name = user_name
        self.dbm = dbm

    def create_tables(self):
        """
        Creates the database tables if not present.
        """
        db = self.get_connection()
        cur = db.cursor()
        cur.execute(CREATE_TABLE_USED_CARD)
        db.commit()
        db.close()

    def get_due_card_ids_and_shelves(self, max_shelf: int) -> Dict[int, int]:
        """
        Fetches all cards from the database, that are due today ore earlier.
        :return: a list of UsedCards
        """
        db = self.get_connection()
        cur = db.cursor()
        today = strftime('%Y-%m-%d')
        cur.execute("SELECT " + CARD_ID + ", " + USED_CARD_SHELF + " FROM " + TABLE_USED_CARD +
                    " WHERE " + USED_CARD_NEXT_QUESTIONING + "<= ?" +
                    " AND " + USED_CARD_SHELF + "<= ?", (today, max_shelf))

        cards = {}
        for (card_id, shelf) in cur:
            cards[card_id] = shelf

        db.close()
        return cards

    def load_card(self, card_id: int) -> UsedCard:
        """
        Loads a Card from the user's database and the general database.
        :param card_id: the card's id
        :return: a UsedCard object
        """
        db = self.get_connection()
        cur = db.cursor()
        cur.execute("SELECT " + USED_CARD_SHELF + ", " + USED_CARD_NEXT_QUESTIONING +
                    " FROM " + TABLE_USED_CARD +
                    " WHERE " + CARD_ID + "= ?", (str(card_id),))

        shelf, next_questioning = cur.fetchone()

        card = self.dbm.load_card(card_id)

        return UsedCard(card_id, shelf, next_questioning, card.get_translations())

    def add_card(self, card: UsedCard):
        """
        Adds a used card to the database.
        :param card: the card to be added
        """
        card_id = self.dbm.add_card(card)

        db = self.get_connection()
        cur = db.cursor()
        cur.execute("INSERT INTO " + TABLE_USED_CARD + "(" + ", ".join((CARD_ID, USED_CARD_SHELF,
                                                                        USED_CARD_NEXT_QUESTIONING))
                    + ") VALUES (?,?,?)", (card_id, card.get_shelf(), card.get_next_questioning()))
        db.commit()
        db.close()

    def update_db(self, card_id: int, shelf: int, next_questioning: str):
        """
        Update the database with the new values.
        :param card_id: the card to be updated
        :param shelf: the new shelf
        :param next_questioning: the new date
        """
        db = self.get_connection()
        cur = db.cursor()
        cur.execute("UPDATE " + TABLE_USED_CARD
                    + " SET " + USED_CARD_NEXT_QUESTIONING + "=?"
                    + ", " + USED_CARD_SHELF + "=?"
                    + " WHERE " + CARD_ID + "=?", (next_questioning, shelf, card_id))
        db.commit()
        db.close()
