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

from typing import List, Optional, Tuple, Dict

Translation = Tuple[str, str, str, str]
Card = Tuple[int, List[Translation]]
Group = Tuple[str, Optional[str], List[Card]]


class DatabaseManager(DatabaseOpenHelper):
    """
    Responsible for all database interactions not concerning user data.
    """

    def __init__(self):
        """
        Initialize the DatabaseManager to use the database db_name
        """
        super().__init__("data.sqlite3")

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

    def add_card(self, translations: List[Translation], cursor: Cursor = None) -> int:
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
            parent_id = self.add_group(parent_name, cursor=cursor) if parent_name else None

            # try to add the group to the database
            try:
                cursor.execute("INSERT INTO " + TABLE_GROUP + "("
                               + ",".join((GROUP_ID, GROUP_NAME, GROUP_PARENT))
                               + ") VALUES (?,?,?);", (self.group_id + 1, group_name, parent_id))

                # insert succeeded
                self.group_id += 1
                return self.group_id

            # group name did already exist
            except IntegrityError:

                # load the existing groups's id
                return cursor.execute("SELECT " + GROUP_ID + " FROM " + TABLE_GROUP + " WHERE "
                                      + GROUP_NAME + "=?;", (group_name,)).fetchone()[0]

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
            db.commit()
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

    def phrase_exists(self, phrase_description: str, language: str, cursor: Cursor = None):
        """
        Checks whether a group_name exists.
        :param phrase_description: the phrases description
        :param language: the phrases language
        :param cursor: the cursor to be used to access the database
        :return: True/False
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            presence = self.phrase_exists(phrase_description, language, cur)
            db.close()
            return presence

        # a cursor was passed on
        else:
            return cursor.execute("SELECT * FROM " + TABLE_PHRASE
                                  + " WHERE " + PHRASE_DESCRIPTION + "=? AND " + PHRASE_LANGUAGE + "=?;",
                                  (phrase_description, language)).fetchone() is not None

    #######
    # retrieve entries from the database

    def get_card(self, card_id: int, cursor: Cursor = None) -> Card:
        """
        Loads a card from the database.
        :param card_id: the cards id
        :param cursor: the cursor to be used to access the database
        :return: id, a list of str-4-Tuples representing the cards translations
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
                raise ValueError("Card {} does not exist.".format(card_id))

            cursor.execute("SELECT " + ",".join(["l1." + PHRASE_DESCRIPTION, "l1." + PHRASE_LANGUAGE,
                                                 "l2." + PHRASE_DESCRIPTION, "l2." + PHRASE_LANGUAGE])
                           + " FROM " + TABLE_CARD + " AS c"
                           + " JOIN " + TABLE_TRANSLATION + " AS t ON c." + TRANSLATION_ID + "=t." + TRANSLATION_ID
                           + " JOIN " + TABLE_PHRASE + " AS l1 ON t." + TRANSLATION_PHRASE_1 + "=l1." + PHRASE_ID
                           + " JOIN " + TABLE_PHRASE + " AS l2 ON t." + TRANSLATION_PHRASE_2 + "=l2." + PHRASE_ID
                           + " WHERE c." + CARD_ID + "=?;", (card_id,))

            return card_id, cursor.fetchall()

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
            subgroup_ids = map(str, self.get_subgroup_ids(group_id, cursor))
            cursor.execute("SELECT " + CARD_ID + " FROM " + TABLE_CARD_GROUP + " WHERE " + GROUP_ID
                           + " IN (" + ",".join(subgroup_ids) + ");")

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

            return cursor.execute("SELECT " + GROUP_ID + " FROM " + TABLE_GROUP + " WHERE " + GROUP_NAME + "=?",
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

    def get_group_names_for_card(self, card_id: int, cursor: Cursor = None) -> List[str]:
        """
        Loads the names of all groups a card is in.
        :param card_id: the cards id
        :param cursor: the cursor to be used to access the database
        :return: a list of group_names
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            group_names = self.get_group_names_for_card(card_id, cur)
            db.close()
            return group_names

        # a cursor was passed on
        else:
            if not self.card_exists(card_id, cursor):
                raise ValueError("Card '{}' does not exist.".format(card_id))

            return list(map(lambda row: row[0],
                            cursor.execute("SELECT " + GROUP_NAME + " FROM " + TABLE_GROUP + " AS g"
                                           + " JOIN " + TABLE_CARD_GROUP + " AS cg ON cg." + GROUP_ID + "=g." + GROUP_ID
                                           + " WHERE cg." + CARD_ID + "=?",
                                           (card_id,)).fetchall()))

    def get_all_phrases(self, language: str) -> List[str]:
        """
        Returns all phrases of a language.
        :param language: the language of the phrases
        :return: a list of strings
        """
        db = self.get_connection()
        phrases = list(map(lambda row: row[0],
                           db.execute("select " + PHRASE_DESCRIPTION + " FROM " + TABLE_PHRASE
                                      + " WHERE " + PHRASE_LANGUAGE + "=?;", (language,)).fetchall()))
        db.close()
        return phrases

    def find_cards_with(self, string: str, language: str, cursor: Cursor = None) -> List[Card]:
        """
        Returns all cards with a phrase in language like <string> on them
        :param string: the string to be searched for
        :param language: the strings language
        :param cursor: the cursor to be used to access the database
        :return: a list of cards
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            db.create_function("REGEXP", 2, regexp)
            cur = db.cursor()
            cards = self.find_cards_with(string, language, cur)
            db.close()
            return cards

        # a cursor was passed on
        else:
            # add sqlite3 wildcards to match string
            # string = "%{}%".format(string)

            # find matching card_ids
            cursor.execute("SELECT DISTINCT " + CARD_ID + " FROM " + TABLE_CARD + " AS c"
                           + " JOIN " + TABLE_TRANSLATION + " AS t ON t." + TRANSLATION_ID + "=c." + TRANSLATION_ID
                           + " JOIN " + TABLE_PHRASE + " AS p ON p." + PHRASE_ID + "=t." + TRANSLATION_PHRASE_1
                           + " JOIN " + TABLE_PHRASE + " AS p2 ON p2." + PHRASE_ID + "=t." + TRANSLATION_PHRASE_2
                           + " WHERE p." + PHRASE_DESCRIPTION + " REGEXP ?"
                           + " AND p." + PHRASE_LANGUAGE + "=?"
                           + " OR p2." + PHRASE_DESCRIPTION + " REGEXP ?"
                           + " AND p2." + PHRASE_LANGUAGE + "=?", (string, language, string, language))

            # load cards
            cards = []
            for card_id, in cursor.fetchall():
                cards.append(self.get_card(card_id, cursor))
            return cards

    #######
    # update entries in the database

    def update_card(self, card_id: int,
                    added_translations: List[Translation],
                    removed_translations: List[Translation],
                    cursor: Cursor = None):
        """
        Updates a card in the database.
        :param card_id: the cards_id
        :param added_translations: the translations that were added to the card
        :param removed_translations: the translation that were removed from the card
        :param cursor: the cursor to be used to access the database
        """
        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            self.update_card(card_id, added_translations, removed_translations, cur)
            db.commit()
            db.close()

        # a cursor was passed on
        else:
            if not self.card_exists(card_id):
                raise ValueError("Card {} does not exist.".format(card_id))

            for translation in removed_translations:
                t_id = self.remove_translation(translation, cursor)
                cursor.execute("DELETE FROM " + TABLE_CARD + " WHERE " + CARD_ID + "=? AND " + TRANSLATION_ID + "=?",
                               (card_id, t_id))

            for translation in added_translations:
                t_id = self.add_translation(translation[0], translation[1], translation[2], translation[3], cursor)
                cursor.execute("INSERT INTO " + TABLE_CARD + " (" + ",".join((CARD_ID, TRANSLATION_ID))
                               + ") VALUES (?,?);", (card_id, t_id))

            self.remove_obsolete_phrases(cursor)

    def edit_translation(self, old_translation: Translation, new_translation: Translation, cursor: Cursor = None):
        """
        Edits a translation.
        :param old_translation: the old data
        :param new_translation: the new data
        :param cursor: the cursor to be used to access the database
        """
        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            self.edit_translation(old_translation, new_translation, cur)
            db.commit()
            db.close()

        # a cursor was passed on
        else:
            if not self.phrase_exists(old_translation[0], old_translation[1]) \
                    or not self.phrase_exists(old_translation[2], old_translation[3]):
                raise ValueError("old translation does not exist.")

            phrase_1 = self.add_phrase(old_translation[0], old_translation[1], cursor)
            phrase_2 = self.add_phrase(old_translation[2], old_translation[3], cursor)

            # update phrase 1
            if old_translation[0] != new_translation[0] or old_translation[1] != new_translation[1]:
                cursor.execute("UPDATE " + TABLE_PHRASE + " SET " + PHRASE_DESCRIPTION + "=?," + PHRASE_LANGUAGE + "=?"
                               + " WHERE " + PHRASE_ID + "=?;",
                               (new_translation[0], new_translation[1], phrase_1))

            # update phrase 2
            if old_translation[2] != new_translation[2] or old_translation[3] != new_translation[3]:
                cursor.execute("UPDATE " + TABLE_PHRASE + " SET " + PHRASE_DESCRIPTION + "=?," + PHRASE_LANGUAGE + "=?"
                               + " WHERE " + PHRASE_ID + "=?;",
                               (new_translation[2], new_translation[3], phrase_2))

    def remove_translation(self, translation: Translation, cursor: Cursor = None):
        """
        Removes a translation from the database and returns its previous id.
        :param translation: the translation data
        :param cursor: the cursor to used to access the database
        :return: the translations previous id
        """
        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            t_id = self.remove_translation(translation, cur)
            db.commit()
            db.close()
            return t_id

        # a cursor was passed on
        else:
            # get translation id
            t_id = self.add_translation(translation[0], translation[1], translation[2], translation[3])

            # delete translation
            cursor.execute("DELETE FROM " + TABLE_TRANSLATION + " WHERE " + TRANSLATION_ID + "=?", (t_id,))
            return t_id

    def remove_obsolete_phrases(self, cursor: Cursor = None):
        """
        Removes phrases that are not part of a translation from the database
        :param cursor: the cursor to be used to access the database
        """
        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            self.remove_obsolete_phrases(cur)
            db.commit()
            db.close()

        # a cursor was passed on
        else:
            cursor.execute("DELETE FROM " + TABLE_PHRASE + " WHERE " + PHRASE_ID + " NOT IN "
                           + "(SELECT " + TRANSLATION_PHRASE_1 + " FROM " + TABLE_TRANSLATION + ")"
                           + " AND " + PHRASE_ID + " NOT IN "
                           + "(SELECT " + TRANSLATION_PHRASE_2 + " FROM " + TABLE_TRANSLATION + ");")


def regexp(expr: str, string: str):
    """
    Provides a re support to the sqlite3 database
    :param expr: the regexp
    :param string: the string to be searched
    :return: True/False
    """
    from re import compile
    reg = compile(expr)
    return reg.search(string) is not None
