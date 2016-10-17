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
Responsible for all database interactions concerning user data.
"""

from data.databaseOpenHelper import *
from data.userDatabaseConstants import *
from time import strftime

from typing import List, Tuple

Card = Tuple[int, int, str]  # id, shelf, due_date


class CardNotUsedError(ValueError):
    """
    Raised when a card not used by the current user is tried to access.
    """


class CardAlreadyUsedError(ValueError):
    """
    Raised when a card that is already used is tried to be added.
    """


class UserDatabaseManager(DatabaseOpenHelper):
    """
    Responsible for all database interactions concerning user data.
    """

    def __init__(self, user_name: str):
        """
        Initializes the UserDatabaseManager to use the database user/<user_name>.sqlite3.
        :param user_name: the user_name
        """
        super().__init__(user_name + ".sqlite3")
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

    #######
    # add entries to the database

    def add_card(self, card_id: int, shelf: int, due_date: str = "today", cursor: Cursor = None):
        """
        Tries to add a card to the database.
        :raises ValueError: if the card already exists
        :param card_id: the cards id
        :param shelf: the cards shelf
        :param due_date: the cards due date
        :param cursor: the cursor to be used to access the database.
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            self.add_card(card_id, shelf, due_date, cur)
            db.commit()
            db.close()

        # a cursor was passed on
        else:
            if self.card_is_used(card_id, cursor):
                raise CardAlreadyUsedError("Card {} is already used by user {}.".format(card_id, self.user_name))

            if due_date == "today":
                due_date = strftime("%Y-%m-%d")

            cursor.execute("INSERT INTO " + TABLE_USED_CARD + "("
                           + ",".join((CARD_ID, USED_CARD_SHELF, USED_CARD_DUE_DATE))
                           + ") VALUES (?,?,?);", (card_id, shelf, due_date))

    #######
    # look for entries in the database

    def card_is_used(self, card_id: int, cursor: Cursor = None) -> bool:
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
            presence = self.card_is_used(card_id, cur)
            db.close()
            return presence

        # a cursor was passed on
        else:
            return cursor.execute("SELECT * FROM " + TABLE_USED_CARD + " WHERE " + CARD_ID + "=?;",
                                  (card_id,)).fetchone() is not None

    #######
    # retrieve entries from the database

    def get_card(self, card_id: int, cursor: Cursor = None) -> Card:
        """
        Loads a card from the database.
        :param card_id: the card_id
        :param cursor: the cursor to be used to access the database
        :return: the cards id, its shelf and its due_date in format '%Y-%m-%d'
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
            if not self.card_is_used(card_id, cursor):
                raise CardNotUsedError("Card {} is not used by user {}.".format(card_id, self.user_name))

            shelf, due_date = cursor.execute("SELECT " + ",".join((USED_CARD_SHELF, USED_CARD_DUE_DATE))
                                             + " FROM " + TABLE_USED_CARD + " WHERE " + CARD_ID + "=?;",
                                             (card_id,)).fetchone()
            return card_id, shelf, due_date

    def get_due_cards(self, due_date: str = "today", cursor: Cursor = None) -> List[Card]:
        """
        Fetches all due cards from the database.
        :param due_date: a date in format '%Y-%m-%d' or 'today'
        :param cursor: the cursor to be used to access the database.
        :return: a list of 3-tuples representing the cards (id, shelf, due_date)
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            cards = self.get_due_cards(due_date, cur)
            db.close()
            return cards

        # a cursor was passed on
        else:
            if due_date == "today":
                due_date = strftime('%Y-%m-%d')

            return cursor.execute("SELECT " + ",".join((CARD_ID, USED_CARD_SHELF, USED_CARD_DUE_DATE))
                                  + " FROM " + TABLE_USED_CARD + " WHERE " + USED_CARD_DUE_DATE + "<=?;",
                                  (due_date,)).fetchall()

    def get_cards_on_shelf(self, shelf:int, cursor: Cursor = None) -> List[Card]:
        """
        Fetches the all cards on a shelf from the database.
        :param shelf: the shelf
        :param cursor: the cursor to be used to access the database.
        :return: a list of 3-tuples representing the cards (id, shelf, due_date)
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            cards = self.get_cards_on_shelf(shelf, cur)
            db.close()
            return cards

        # a cursor was passed on
        else:
            return cursor.execute("SELECT " + ",".join((CARD_ID, USED_CARD_SHELF, USED_CARD_DUE_DATE))
                                  + " FROM " + TABLE_USED_CARD + " WHERE " + USED_CARD_SHELF + "=?;",
                                  (shelf,)).fetchall()

    #######
    # update the entries in the database

    def update_card(self, card: Card, cursor: Cursor = None):
        """
        Updates the card in the database to the new values.
        :param card: a 3-tuple (id, shelf, due_date) representing the card
        :param cursor: the cursor to be used to access the database
        """

        # if no cursor was passed on, open the database and call the method recursively with a new cursor object
        if cursor is None:
            db = self.get_connection()
            cur = db.cursor()
            self.update_card(card, cur)
            db.commit()
            db.close()

        # a cursor was passed on
        else:
            card_id, shelf, due_date = card

            if not self.card_is_used(card_id, cursor):
                raise CardNotUsedError("Card {} is not used by user {}.".format(card_id, self.user_name))

            cursor.execute("UPDATE " + TABLE_USED_CARD + " SET " + USED_CARD_SHELF + "=?, "
                           + USED_CARD_DUE_DATE + "=? WHERE " + CARD_ID + "=?;", (shelf, due_date, card_id))
