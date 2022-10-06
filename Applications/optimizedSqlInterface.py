import sqlite3

from Applications.dbinterface import DBInterface


class OptimizedSqliteInterface(DBInterface):
    def __init__(self, connection):
        super().__init__(connection)
        self.sql = sqlite3.connect(self.connection)

    def run_query(self, query):
        conn = self.sql.cursor()
        conn.execute(query)
        response = conn.fetchall()
        self.sql.commit()
        return response

