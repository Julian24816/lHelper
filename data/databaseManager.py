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

from data.databaseOpenHelper import *
from data.databaseConstants import *
from typing import List, Optional, Tuple


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
        loads the current max ids from the database.
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
        Overrides DatabaseOpenHelper.create_tables()
        Creates the database tables if not present.
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

    def add_card(self, translations: List[Tuple[str, str, str, str]], cursor: Cursor = None) -> int:
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

    def add_group(self, group: Tuple[str, Optional[str]], cursor: Cursor = None) -> int:
        """
        Tries to add a group to the database and returns the groups id independent of success.
        :param group: the group to be added
        :param cursor: the cursor to be used to access the database
        :return: the groups id
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            group_id = self.add_group(group, cur)
            db.commit()
            db.close()
            return group_id

        # a cursor was passed on
        else:
            # retrieve the parent_id
            parent = self.add_group((group[1], None), cursor) if group[1] else None

            # try to add the group to the database
            try:
                cursor.execute("INSERT INTO " + TABLE_GROUP + "("
                               + ",".join((GROUP_ID, GROUP_NAME, GROUP_PARENT))
                               + ") VALUES (?,?,?);", (self.group_id + 1, group[0], parent))

                # insert succeeded
                self.group_id += 1
                return self.group_id

            # group name did already exist
            except IntegrityError:

                # load the existing groups's id
                return cursor.execute("SELECT " + GROUP_ID + " FROM " + TABLE_GROUP + " WHERE "
                                      + GROUP_NAME + "=?;", (group[0],)).fetchone()[0]


'''
    def load_card(self, card_id: int, cursor: sqlite3.Cursor = None) -> Card:
        """
        Loads a card from the database accessed by cursor.
        :param card_id: the card's id
        :param cursor: the cursor to be used
        :return: the loaded Card
        """
        if cursor is None:
            db = self.get_connection()
            curs = db.cursor()
            card = self.load_card(card_id, curs)
            db.close()
            return card
        else:
            cursor.execute("SELECT " + ", ".join(["l." + WORD_ROOT_FORMS, "l." + WORD_ANNOTATIONS,
                                                  "lu." + USAGE_CONTEXT, "g." + WORD_ROOT_FORMS,
                                                  "g." + WORD_ANNOTATIONS, "gu." + USAGE_CONTEXT]) +
                           " FROM " + TABLE_CARD + " AS c" +
                           " JOIN " + TABLE_TRANSLATION + " AS t ON c." + TRANSLATION_ID + "=t." + TRANSLATION_ID +
                           " JOIN " + TABLE_USAGE + " AS lu ON t." + TRANSLATION_LATIN_USAGE_ID + "=lu." + USAGE_ID +
                           " JOIN " + TABLE_WORD + " AS l ON lu." + WORD_ID + "=l." + WORD_ID +
                           " JOIN " + TABLE_USAGE + " AS gu ON t." + TRANSLATION_GERMAN_USAGE_ID + "=gu." + USAGE_ID +
                           " JOIN " + TABLE_WORD + " AS g ON gu." + WORD_ID + "=g." + WORD_ID +
                           " WHERE c." + CARD_ID + "=" + str(card_id)
                           )

            translations = []
            for l_root, l_annotation, l_context, g_root, g_annotation, g_context in cursor.fetchall():
                translations.append(Translation(Usage(Word(l_root, l_annotation, "latin"), l_context),
                                                Usage(Word(g_root, g_annotation, "german"), g_context)))

            return Card(translations, card_id)

    def load_group(self, group_id: int, cursor: sqlite3.Cursor = None) -> CardGroup:
        """
        Loads a CardGroup from the database
        :param group_id: the groups id
        :return: the CardGroup
        """
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            group = self.load_group(group_id, cur)
            db.close()
            return group
        else:
            cursor.execute("SELECT " + GROUP_NAME + " FROM " + TABLE_GROUP
                           + " WHERE " + GROUP_ID + "=?", (group_id,))
            group_name = cursor.fetchone()
            if group_name is None:
                raise ValueError("group_id does not exist.")
            group = CardGroup(group_name[0], [])
            cursor.execute("SELECT " + CARD_ID +
                           " FROM " + TABLE_CARD_GROUP +
                           " WHERE " + GROUP_ID + " IN (" + ",".join(
                map(str, self.get_subgroup_ids(group_id, cursor))) + ")")
            for card_id, in cursor.fetchall():
                group.add_card(self.load_card(card_id, cursor))
            return group

    # noinspection PyMethodMayBeStatic
    def get_subgroup_ids(self, group_id: int, cursor: sqlite3.Cursor) -> List[int]:
        """
        Loads all subgroups of group_id from the database and subgroups of these ...
        :param group_id: the starting group_id
        :param cursor: the database cursor to be used
        :return: a list of group_ids
        """
        ids = [group_id]
        for group in ids:
            cursor.execute("SELECT " + GROUP_ID + " FROM " + TABLE_GROUP
                           + " WHERE " + GROUP_PARENT + "=?", (group,))
            for el, in cursor:
                if el not in ids:
                    ids.append(el)
        return ids

    def add_card_to_group(self, card: Card, group: CardGroup):
        """
        Adds a card to a group in the database. Adds the group if needed.
        :param card: the card to be added to the group
        :param group: the group the card should be added to
        """
        db = self.get_connection()
        cur = db.cursor()
        group_id = self.add_group(group, cur)

        cur.execute("INSERT INTO " + TABLE_CARD_GROUP + "("
                    + ",".join((GROUP_ID, CARD_ID))
                    + ") VALUES (?,?)", (group_id, card.Id))

        db.commit()
        db.close()

    def get_all_group_names(self) -> List[str]:
        """
        Loads all card group names
        :return: a list of card group names
        """
        db = self.get_connection()
        cur = db.cursor()
        cur.execute("SELECT " + GROUP_NAME + " FROM " + TABLE_GROUP)
        names = list(map(lambda e: e[0], cur.fetchall()))
        db.close()
        return names

    def get_group_for_name(self, group_name) -> CardGroup:
        """
        Loads the group with name group_name
        :param group_name: the group's name
        :return: a CardGroup
        """
        db = self.get_connection()
        cur = db.cursor()
        cur.execute("SELECT " + GROUP_ID + " FROM " + TABLE_GROUP + " WHERE " + GROUP_NAME + "=?", (group_name,))
        group_id = cur.fetchone()
        if group_id is not None:
            group_id = group_id[0]
        else:
            raise ValueError("group {} does not exist".format(group_name))
        group = self.load_group(group_id, cur)
        db.close()
        return group
'''
