import re
import sqlite3

from Applications.dbinterface import DBInterface
from Helpers.changes_class import Changes as Ch
from Helpers.simple_sql_parser import SqlParser as Sp


class OptimizedSqliteInterface(DBInterface):
    def __init__(self, connection):
        super().__init__(connection)
        # {table_name:changes_class}
        # {string    :changes      }
        self.changes: dict = {}
        self.sql = sqlite3.connect(connection)
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
                    query = self.remove_occurrences_in_joins(self.find_and_remove_alias(query, table), table)
                else:
                    query = self.replace_occurrences(query, table, current_changes.new_name)
        return query

    @staticmethod
    def remove_occurrences_in_joins(query: str, table_name: str):
        query_list_without_removed_table = [x for x in re.split(r"join", query, flags=re.IGNORECASE) if
                                            table_name not in x]
        for i, item in enumerate(query_list_without_removed_table):
            if not i == 0:
                query_list_without_removed_table[i] = "JOIN" + item
        return ''.join(query_list_without_removed_table)

    @staticmethod
    def replace_occurrences(query: str, table_name: str, new_table_name: str):
        return re.sub(r'%s(\W|;|$)' % table_name, new_table_name + " ", query)

    @staticmethod
    def find_and_remove_alias(query: str, table_name: str):
        query_without_whitespace = query.split(' ')
        alias_position = query_without_whitespace.index(table_name) + 1
        if query_without_whitespace[alias_position].lower() != "on":
            alias = query_without_whitespace[alias_position]
            return query.replace(alias + ".", "")
        return query
