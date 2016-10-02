import logging
import re
import sqlite3


def get_logger():
    return logging.getLogger(__name__)

class DBGuard:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        get_logger().info('Openning database...')
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        get_logger().info('Committing changes to database...')
        self.conn.commit()
        get_logger().info('Closing database...')
        self.conn.close()


class Agenda:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_events(self, all=False):
        query = 'select rowid,* from agenda where status=1 order by rowid asc'

        # Limit size of the result if required
        if not all:
            query += ' limit 5'

        with DBGuard(self.db_path) as cursor:
            # Yield each line of result
            for event in cursor.execute(query):
                yield event

    def remove_event(self, id):
        with DBGuard(self.db_path) as cursor:
            cursor.execute('update agenda set status=0 where rowid=?', (id,))

    def add_event(self, date, lieu, titre, desc):
        with DBGuard(self.db_path) as cursor:
            cursor.execute('insert into agenda (titre,lieu,description,date,status) values (?,?,?,?,1)',
                       (titre, lieu, desc, date))