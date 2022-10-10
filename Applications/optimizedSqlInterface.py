import re
import sqlite3

from Applications.dbinterface import DBInterface


class OptimizedSqliteInterface(DBInterface):
    def __init__(self, path_to_database):
        super().__init__(path_to_database)
        # {table_name:(should_be_renamed,rename_value)}
        # {string    :(bool             , string     )}
        self.changes: dict = {}
        self.sql = sqlite3.connect(self.path_to_database)

    def run_query(self, query: str):
        query = self.modify_query_with_changes(query)
        conn = self.sql.cursor()
        conn.execute(query)
        response = conn.fetchall()
        self.sql.commit()
        return response

    def add_database_change(self, table_name: str, should_be_renamed: bool = False, rename_value: str = ""):
        self.changes.update({table_name: (should_be_renamed, rename_value)})

    def modify_query_with_changes(self, query: str):
        for key, value in self.changes.items():
            should_be_replaced: bool = value[0]
            replacement_value: str = value[1]
            if key in query:
                if not should_be_replaced:
                    query = self.remove_occurrences_in_joins(self.find_and_remove_alias(query, key), key)
                else:
                    query = self.replace_occurrences(query, key, replacement_value)
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
