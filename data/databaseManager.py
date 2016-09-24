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

'''
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

    def add_group(self, group: CardGroup, cursor: sqlite3.Cursor = None) -> int:
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
