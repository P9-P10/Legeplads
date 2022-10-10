import sqlite3

from Applications.dbinterface import DBInterface


class SqLiteInterface(DBInterface):
    def __init__(self, path_to_database):
        super().__init__(path_to_database)
        self.sql = sqlite3.connect(self.path_to_database)

    def run_query(self, query):
        conn = self.sql.cursor()
        conn.execute(query)
        response = conn.fetchall()
        self.sql.commit()
        return response

