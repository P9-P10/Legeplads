import re
import sqlite3

from Applications.dbinterface import DBInterface
from Helpers.changes_class import Changes as Ch
from Helpers.simple_sql_parser import SqlParser as Sp
from Applications.querytransformation import RemoveTable, ChangeTable


class OptimizedSqliteInterface(DBInterface):
    def __init__(self, path_to_database):
        super().__init__(path_to_database)
        # {table_name:changes_class}
        # {string    :changes      }
        self.changes: dict = {}
        self.sql = sqlite3.connect(self.path_to_database)
        self.parser = Sp()

    def run_query(self, query: str):
        query = self.modify_query_with_changes(query)
        conn = self.sql.cursor()
        conn.execute(query)
        response = conn.fetchall()
        self.sql.commit()
        return response

    def add_database_change(self, table_name: str, changes: Ch):
        self.changes.update({table_name: changes})

    def modify_query_with_changes(self, query: str):
        for table in self.parser.get_table_names(query):
            if table in self.changes:
                current_changes: Ch = self.changes[table]
                if not current_changes.should_rename:
                    query = RemoveTable(table).apply(query)
                else:
                    query = ChangeTable(table, current_changes.new_name).apply(query)
        return query
