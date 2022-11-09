import sqlite3
import pathlib
from os.path import exists

from Structures.Query import Query
from Applications.Database_intefaces.dbinterface import DBInterface


class DBConfig:
    def __init__(self, name, path = str(pathlib.Path(__file__).parent.parent.parent / 'Databases') + '\\', extension = '.sqlite'):
        self.path = path
        self.extension = extension
        self.name = name

    def get_path_to_database(self):
        return self.path + self.name + self.extension


class SqLiteInterface(DBInterface):
    def __init__(self, config: DBConfig):
        super().__init__(config.get_path_to_database())
        if not exists(self.path_to_database):
            raise FileNotFoundError("File not found: "+self.path_to_database)
        self.sql = sqlite3.connect(self.path_to_database)

    def run_query(self, query: Query):
        conn = self.sql.cursor()
        conn.execute(str(query))
        response = conn.fetchall()
        self.sql.commit()
        return response
