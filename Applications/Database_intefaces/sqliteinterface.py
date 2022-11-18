import sqlite3
import pathlib
from os.path import exists

from Structures.Query import Query
from Applications.Database_intefaces.dbinterface import DBInterface


class SqLiteInterface(DBInterface):
    def __init__(self, path):
        super().__init__(path)
        if not exists(self.path_to_database):
            raise FileNotFoundError("File not found: " + self.path_to_database)
        self.sql = sqlite3.connect(self.path_to_database)

    def run_query(self, query: Query):
        conn = self.sql.cursor()
        conn.execute(str(query))
        response = conn.fetchall()
        self.sql.commit()
        return response
