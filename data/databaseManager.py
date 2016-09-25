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
Responsible for all database interactions not concerning user data.
Instantiate DatabaseManager to get access to the functionality.
"""

from data.databaseOpenHelper import *
from data.databaseConstants import *
from typing import List, Optional, Tuple

Card = List[Tuple[str, str, str, str]]
Group = Tuple[str, Optional[str], List[Card]]


class DatabaseManager(DatabaseOpenHelper):
    """
    Responsible for all database interactions not concerning user data.
    """

    def __init__(self, db_name: str):
        """
        Initialize the DatabaseManager to use the database db_name
        :param db_name: the filename of the sqlite3-database
        """
        super().__init__(db_name)

        # init database ids with default values ...
        self.phrase_id = 0
        self.translation_id = 0
        self.card_id = 0
        self.group_id = 0

        # ... and load the actual values from the database - if they exist
        self.load_ids()

    def load_ids(self):
        """
        Loads the current max ids from the database.
        """
        db = self.get_connection()
        cur = db.cursor()
        phrase_id = cur.execute("SELECT MAX(" + PHRASE_ID + ") FROM " + TABLE_PHRASE).fetchone()[0]
        translation_id = cur.execute("SELECT MAX(" + TRANSLATION_ID + ") FROM " + TABLE_TRANSLATION).fetchone()[0]
        card_id = cur.execute("SELECT MAX(" + CARD_ID + ") FROM " + TABLE_CARD).fetchone()[0]
        group_id = cur.execute("SELECT MAX(" + GROUP_ID + ") FROM " + TABLE_GROUP).fetchone()[0]
        db.close()
        if phrase_id is not None:
            self.phrase_id = phrase_id
        if translation_id is not None:
            self.translation_id = translation_id
        if card_id is not None:
            self.card_id = card_id
        if group_id is not None:
            self.group_id = group_id

    def create_tables(self):
        """
        Creates the database tables if not present.
        Overrides DatabaseOpenHelper.create_tables().
        """
        db = self.get_connection()
        cur = db.cursor()
        cur.execute(CREATE_TABLE_PHRASE)
        cur.execute(CREATE_TABLE_TRANSLATION)
        cur.execute(CREATE_TABLE_CARD)
        cur.execute(CREATE_TABLE_GROUP)
        cur.execute(CREATE_TABLE_CARD_GROUP)
        db.commit()
        db.close()

    #######
    # add entries to the database

    def add_phrase(self, phrase: str, language: str, cursor: Cursor = None) -> int:
        """
        Tries to add a phrase to the database and returns the phrases id independent of success.
        :param phrase: the phrase-description
        :param language: the phrase-language
        :param cursor: the cursor to be used to access the database
        :return: the phrases id
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            phrase_id = self.add_phrase(phrase, language, cur)
            db.commit()
            db.close()
            return phrase_id

        # a cursor was passed on
        else:

            # try to add the phrase to the database
            try:
                cursor.execute("INSERT INTO " + TABLE_PHRASE + "("
                               + ",".join((PHRASE_ID, PHRASE_DESCRIPTION, PHRASE_LANGUAGE))
                               + ") VALUES (?,?,?);", (self.phrase_id + 1, phrase, language))

                # insert succeeded
                self.phrase_id += 1
                return self.phrase_id

            # phrase-language tuple did already exist
            except IntegrityError:

                # load the existing phrase's id
                return cursor.execute("SELECT " + PHRASE_ID + " FROM " + TABLE_PHRASE + " WHERE "
                                      + PHRASE_DESCRIPTION + "=? AND " + PHRASE_LANGUAGE + "=?;",
                                      (phrase, language)).fetchone()[0]

    def add_translation(self, phrase1: str, language1: str, phrase2: str, language2: str, cursor: Cursor = None) -> int:
        """
        Tries to add a translation from phrase1 to phrase2 to the database
        and returns the translations id independent of success.
        :param phrase1: the first phrase
        :param language1: the first phrases language
        :param phrase2: the second phrase
        :param language2: the second phrases language
        :param cursor: the cursor to be used to access the database
        :return: the translations id
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            translation_id = self.add_translation(phrase1, language1, phrase2, language2, cur)
            db.commit()
            db.close()
            return translation_id

        # a cursor was passed on
        else:
            # retrieve the phrase_ids
            phrase_id_1 = self.add_phrase(phrase1, language1, cursor)
            phrase_id_2 = self.add_phrase(phrase2, language2, cursor)

            # try to add the translation to the database
            try:
                cursor.execute("INSERT INTO " + TABLE_TRANSLATION + "("
                               + ",".join((TRANSLATION_ID, TRANSLATION_PHRASE_1, TRANSLATION_PHRASE_2))
                               + ") VALUES (?,?,?);", (self.translation_id + 1, phrase_id_1, phrase_id_2))

                # insert succeeded
                self.translation_id += 1
                return self.translation_id

            # phrase1-phrase2 tuple did already exist
            except IntegrityError:

                # load the existing translation's id
                return cursor.execute("SELECT " + TRANSLATION_ID + " FROM " + TABLE_TRANSLATION + " WHERE "
                                      + TRANSLATION_PHRASE_1 + "=? AND " + TRANSLATION_PHRASE_2 + "=?;",
                                      (phrase_id_1, phrase_id_2)).fetchone()[0]

    def add_card(self, translations: Card, cursor: Cursor = None) -> int:
        """
        Adds a card with translations to the database and returns the cards id.
        :param translations: a list of str-4-tuples describing the translations on the card
        :param cursor: the cursor to be used to access the database
        :return: the cards id
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            card_id = self.add_card(translations, cur)
            db.commit()
            db.close()
            return card_id

        # a cursor was passed on
        else:
            self.card_id += 1
            for phrase1, language1, phrase2, language2 in translations:
                translation_id = self.add_translation(phrase1, language1, phrase2, language2, cursor)
                cursor.execute("INSERT INTO " + TABLE_CARD + "("
                               + ",".join((CARD_ID, TRANSLATION_ID))
                               + ") VALUES (?,?);", (self.card_id, translation_id))
            return self.card_id

    def add_group(self, group_name: str, parent_name: str = None, cursor: Cursor = None) -> int:
        """
        Tries to add a group to the database and returns the groups id independent of success.
        :param group_name: the groups name
        :param parent_name: the groups parent
        :param cursor: the cursor to be used to access the database
        :return: the groups id
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            group_id = self.add_group(group_name, parent_name, cur)
            db.commit()
            db.close()
            return group_id

        # a cursor was passed on
        else:
            # retrieve the parent_id
            parent_name = self.add_group(parent_name, cursor=cursor) if parent_name else None

            # try to add the group to the database
            try:
                cursor.execute("INSERT INTO " + TABLE_GROUP + "("
                               + ",".join((GROUP_ID, GROUP_NAME, GROUP_PARENT))
                               + ") VALUES (?,?,?);", (self.group_id + 1, group_name[0], parent_name))

                # insert succeeded
                self.group_id += 1
                return self.group_id

            # group name did already exist
            except IntegrityError:

                # load the existing groups's id
                return cursor.execute("SELECT " + GROUP_ID + " FROM " + TABLE_GROUP + " WHERE "
                                      + GROUP_NAME + "=?;", (group_name[0],)).fetchone()[0]

    def add_card_to_group(self, card_id: int, group_name: str, cursor: Cursor = None):
        """
        Adds a card to a group in the database. Adds the group if needed.
        :param card_id: the id of the card to be added
        :param group_name: the name of the group the card will be added to
        :param cursor: the cursor to be used to access the database
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            self.add_card_to_group(card_id, group_name, cur)
            db.close()

        # a cursor was passed on
        else:
            # retrieve the group_id
            group_id = self.add_group(group_name)

            try:
                cursor.execute("INSERT INTO " + TABLE_CARD_GROUP + "(" + ",".join((GROUP_ID, CARD_ID)) + ")"
                               + " VALUES (?,?);", (group_id, card_id))

            # the card is already in group group_name
            except IntegrityError:
                pass

    #######
    # look for entries in the database

    def card_exists(self, card_id: int, cursor: Cursor = None) -> bool:
        """
        Checks whether a card_id exists.
        :param card_id: the card_id
        :param cursor: the cursor to be used to access the database
        :return: True/False
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            presence = self.card_exists(card_id, cur)
            db.close()
            return presence

        # a cursor was passed on
        else:
            return cursor.execute("SELECT * FROM " + TABLE_CARD + " WHERE " + CARD_ID + "=?;",
                                  (card_id,)).fetchone() is not None

    def group_exists(self, group_id: int, cursor: Cursor = None) -> bool:
        """
        Checks whether a group_id exists.
        :param group_id: the group_id
        :param cursor: the cursor to be used to access the database
        :return: True/False
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            presence = self.group_exists(group_id, cur)
            db.close()
            return presence

        # a cursor was passed on
        else:
            return cursor.execute("SELECT * FROM " + TABLE_GROUP + " WHERE " + GROUP_ID + "=?;",
                                  (group_id,)).fetchone() is not None

    def group_name_exists(self, group_name: str, cursor: Cursor = None) -> bool:
        """
        Checks whether a group_name exists.
        :param group_name: the group_name
        :param cursor: the cursor to be used to access the database
        :return: True/False
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            presence = self.group_name_exists(group_name, cur)
            db.close()
            return presence

        # a cursor was passed on
        else:
            return cursor.execute("SELECT * FROM " + TABLE_GROUP + " WHERE " + GROUP_NAME + "=?;",
                                  (group_name,)).fetchone() is not None

    #######
    # retrieve entries from the database

    def get_card(self, card_id: int, cursor: Cursor = None) -> Card:
        """
        Loads a card from the database.
        :param card_id: the cards id
        :param cursor: the cursor to be used to access the database
        :return: a list of str-4-Tuples representing the cards translations
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            card = self.get_card(card_id, cur)
            db.close()
            return card

        # a cursor was passed on
        else:
            if not self.card_exists(card_id, cursor):
                raise ValueError("Card {} does not exist".format(card_id))

            cursor.execute("SELECT " + ",".join(["l1." + PHRASE_DESCRIPTION, "l1." + PHRASE_LANGUAGE,
                                                 "l2." + PHRASE_DESCRIPTION, "l2." + PHRASE_LANGUAGE])
                           + " FROM " + TABLE_CARD + " AS c"
                           + " JOIN " + TABLE_TRANSLATION + " AS t ON c." + TRANSLATION_ID + "=t." + TRANSLATION_ID
                           + " JOIN " + TABLE_PHRASE + " AS l1 ON t." + TRANSLATION_PHRASE_1 + "=l1." + PHRASE_ID
                           + " JOIN " + TABLE_PHRASE + " AS l2 ON t." + TRANSLATION_PHRASE_2 + "=l2." + PHRASE_ID
                           + " WHERE c." + CARD_ID + "=?;", (card_id,))

            return cursor.fetchall()

    def load_group(self, group_id: int, cursor: Cursor = None) -> Group:
        """
        Loads a group from the database.
        :param group_id: the groups id
        :param cursor: the cursor to be used to access the database.
        :return: a tuple with the group_name, the groups parent_name or None, and  a list of cards
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            group = self.load_group(group_id, cur)
            db.close()
            return group

        # a cursor was passed on
        else:
            if not self.group_exists(group_id, cursor):
                raise ValueError("Group {} does not exist.".format(group_id))

            # load group name and parent name
            cursor.execute("SELECT " + ",".join((GROUP_NAME, GROUP_PARENT)) + " FROM " + TABLE_GROUP + " WHERE "
                           + GROUP_ID + "=?;", (group_id,))
            name, parent = cursor.fetchone()

            # load cards
            cursor.execute("SELECT " + CARD_ID + " FROM " + TABLE_CARD_GROUP + " WHERE " + GROUP_ID
                           + " IN (" + ",".join(map(str, self.get_subgroup_ids(group_id, cursor))) + ");")

            cards = [self.get_card(row[0], cursor) for row in cursor.fetchall()]

            return name, parent, cards

    def get_subgroup_ids(self, parent: int, cursor: Cursor = None) -> List[int]:
        """
        Loads the ids of all subgroups of parent and their subgroups recursively.
        :param parent: the parents id
        :param cursor: the cursor to be used to access the database
        :return: a list of group_ids
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            group_ids = self.get_subgroup_ids(parent, cur)
            db.close()
            return group_ids

        # a cursor was passed on
        else:
            group_ids = [parent]
            for group_id in group_ids:
                cursor.execute("SELECT " + GROUP_ID + " FROM " + TABLE_GROUP + " WHERE " + GROUP_PARENT + "=?;",
                               (group_id,))
                group_ids.extend(map(lambda row: row[0], cursor.fetchall()))
            return group_ids

    def get_group_id_for_name(self, group_name: str, cursor: Cursor = None) -> str:
        """
        Loads a groups id from the database.
        :param group_name: the groups name
        :param cursor: the cursor to be used to access the database
        :return: the groups id
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            group_id = self.get_group_id_for_name(group_name, cur)
            db.close()
            return group_id

        # a cursor was passed on
        else:
            if not self.group_name_exists(group_name, cursor):
                raise ValueError("Group name '{}' does not exist.".format(group_name))

            return cursor.execute("SELECT "+GROUP_ID+" FROM "+TABLE_GROUP+" WHERE "+GROUP_NAME+"=?",
                                  (group_name,)).fetchone()[0]

    def get_all_group_names(self) -> List[str]:
        """
        Loads all card group names.
        :return: a list of card group names
        """
        db = self.get_connection()
        names = list(map(lambda row: row[0],
                         db.execute("SELECT " + GROUP_NAME + " FROM " + TABLE_GROUP).fetchall()))
        db.close()
        return names
