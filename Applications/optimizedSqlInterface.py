import re
import sqlite3

from Applications.dbinterface import DBInterface
from Helpers.changes_class import Changes as Ch
from Helpers.simple_sql_parser import SqlParser as Sp
from Applications.querytransformation import RemoveTable, ChangeTable
from Applications.sqliteinterface import DBConfig


class OptimizedSqliteInterface(DBInterface):
    def __init__(self, config: DBConfig):
        super().__init__(config.get_path_to_database())
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

    def modify_query_with_changes(self, query: str) -> str:
        for table in self.parser.get_table_names(query):
            if table in self.changes:
                changes = self.get_changes_for_table(table)
                query = self.apply_changes(query, table, changes)
        return query

    def get_changes_for_table(self, table: str) -> Ch:
        return self.changes[table]

    def apply_changes(self, query: str, table: str, current_changes: Ch) -> str:
        if current_changes.should_rename:
            query = ChangeTable(table, current_changes.new_name).apply(query)
        else:
            query = RemoveTable(table).apply(query)
        return query
