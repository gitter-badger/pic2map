# -*- coding: utf-8 -*-
"""Test database functionality."""

import sqlite3
import tempfile
import unittest

from contextlib import closing

from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.types import (
    INTEGER,
    TEXT,
)


from pic2map.db import Database

class DatabaseTest(unittest.TestCase):

    """Database wrapper test cases."""

    def test_get_table_metadata(self):
        """Table metadata can be retrieved using index notation."""
        with tempfile.NamedTemporaryFile() as db_file:
            with closing(sqlite3.connect(db_file.name)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(
                        'CREATE TABLE messages (id INTEGER, message TEXT)')

            database = Database(db_file.name)
            table = database['messages']
            schema = {column.name: type(column.type)
                      for column in table.columns}
            self.assertDictEqual(
                schema,
                {'id': INTEGER, 'message': TEXT})

    def test_get_unknown_table_metadata(self):
        """NoSuchTableError raised when table name is not found."""
        with tempfile.NamedTemporaryFile() as db_file:
            with closing(sqlite3.connect(db_file.name)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(
                        'CREATE TABLE messages (id INTEGER, message TEXT)')

            database = Database(db_file.name)

            with self.assertRaises(NoSuchTableError):
                database['unknown']

    def test_type_error_on_wrong_table_name(self):
        """TypeError raised when table name is not a string."""
        with tempfile.NamedTemporaryFile() as db_file:
            with closing(sqlite3.connect(db_file.name)) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(
                        'CREATE TABLE messages (id INTEGER, message TEXT)')

            database = Database(db_file.name)

            with self.assertRaises(TypeError):
                database[0]

    def test_context_manager(self):
        """Connection is opened/closed when used as a context manager."""
        database = Database(':memory:')

        # Connection is None when database object is created
        self.assertIsNone(database.connection)

        with database:
            # Connection is not closed inside the context
            self.assertFalse(database.connection.closed)

        # Connection is closed outside the context
        self.assertTrue(database.connection.closed)