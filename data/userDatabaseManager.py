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
from data.databaseManager import DatabaseManager


class UserDatabaseManager(DatabaseOpenHelper):
    """
    Responsible for all database interactions concerning user data.
    """

    def __init__(self, user_name: str, dbm: DatabaseManager):
        super().__init__(user_name + ".sqlite3")
        self.user_name = user_name
        self.dbm = dbm

'''
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

    def load_card(self, card_id: int, cursor: sqlite3.Cursor = None) -> UsedCard:
        """
        Loads a Card from the user's database and the general database.
        :param card_id: the card's id
        :param cursor: the cursor to be used
        :return: a UsedCard object
        """
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            card = self.load_card(card_id, cur)
            db.close()
            return card
        else:
            cursor.execute("SELECT " + USED_CARD_SHELF + ", " + USED_CARD_NEXT_QUESTIONING +
                           " FROM " + TABLE_USED_CARD +
                           " WHERE " + CARD_ID + "= ?", (str(card_id),))

            shelf, next_questioning = cursor.fetchone()
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

    def get_all_cards(self):
        """
        Loads all cards from the database and returns them
        """
        db = self.get_connection()
        cur = db.cursor()
        cur.execute("SELECT " + CARD_ID + " FROM " + TABLE_USED_CARD)

        cards = []
        for card_id, in cur.fetchall():
            cards.append(self.load_card(card_id, cur))

        db.close()
        return cards

    def set_card_shelf(self, card: UsedCard, new_shelf: int):
        """
        Sets a cards shelf in the database
        :param card: the card
        :param new_shelf: the new shelf
        """
        db = self.get_connection()
        db.execute("UPDATE " + TABLE_USED_CARD + " SET " + USED_CARD_SHELF + "=? WHERE " + CARD_ID + "=?",
                   (new_shelf, card.Id))
        db.commit()
        db.close()

    def set_next_questioning(self, card: UsedCard, next_questioning: str):
        """
        Sets the date of next questioning
        :param card: the card to be updated
        :param next_questioning: the new date
        """
        db = self.get_connection()
        db.execute("UPDATE " + TABLE_USED_CARD + " SET " + USED_CARD_NEXT_QUESTIONING + "=? WHERE " + CARD_ID + "=?",
                   (next_questioning, card.Id))
        db.commit()
        db.close()

    def card_exists(self, card_id):
        """
        Returns True if a Card with id card_id exist.
        :param card_id: the Cards id
        :return: whether the card exists
        """
        db = self.get_connection()
        result = db.execute("SELECT * FROM "+TABLE_USED_CARD+" WHERE "+CARD_ID+"=?", (card_id,)).fetchone() is not None
        db.close()
        return result'''
