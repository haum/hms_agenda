import logging
import sqlite3

import random

from hms_agenda import strings

def get_logger():
    return logging.getLogger(__name__)

class DBGuard:

    """A with-block that will open DB, and commit changes and close DB before exiting."""

    def __init__(self, db_path):
        """Default constructor with a path to the sqlite database."""
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Method called when entering the with block."""
        get_logger().info('Openning database...')
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Method called when exiting the with block."""
        get_logger().info('Committing changes to database...')
        self.conn.commit()
        get_logger().info('Closing database...')
        self.conn.close()


class AgendaDB:

    """A class that will modify the agenda database."""

    def __init__(self, db_path):
        self.db_path = db_path

    def get_events(self, all=False):
        """A generator that will yield events registered in database."""
        query = 'select rowid,* from agenda where status=1 order by rowid asc'

        # Limit size of the result if required
        if not all:
            query += ' limit 5'

        with DBGuard(self.db_path) as cursor:
            # Yield each line of result
            for event in cursor.execute(query):
                yield event

    def remove_event(self, id):
        """Removes an event from the database."""
        with DBGuard(self.db_path) as cursor:
            cursor.execute('update agenda set status=0 where rowid=?', (id,))

    def add_event(self, date, location, title, desc):
        """Adds an event to the database."""
        with DBGuard(self.db_path) as cursor:
            cursor.execute('insert into agenda (titre,lieu,description,date,status) values (?,?,?,?,1)',
                           (title, location, desc, date))

    def add_sceance(self, date):
        """Adds a seance to the database.

        A seance is a recurring type of event that we can automatically fill using the date as input,
        using random messages for the description of the event.

        """
        self.add_event(
            date,
            strings.SCEANCE_LOCATION, strings.SCEANCE_NAME,
            random.choice(strings.SCEANCE_MESSAGES))

    def modify_event(self, id, field, new_value):
        """Modifies a specific field of an existing event."""
        with DBGuard(self.db_path) as cursor:
            cursor.execute('update agenda set {}=? where rowid=?'.format(field), (new_value, id))
