import sqlite3

from Applications.dbinterface import DBInterface


class OptimizedSqliteInterface(DBInterface):
    def __init__(self, connection):
        super().__init__(connection)
        self.changes = None
        self.sql = sqlite3.connect(self.connection)

    # TODO Make able to change join to another table as well.

    def run_query(self, query):
        query = self.modify_query_with_changes(query)
        conn = self.sql.cursor()
        conn.execute(query)
        response = conn.fetchall()
        self.sql.commit()
        return response

    def database_changes(self, changes: dict):
        self.changes = changes

    def modify_query_with_changes(self, query):
        for key, value in self.changes.items():
            if key in query:
                if not value[0]:
                    query = self.remove_occurrences_in_joins(self.find_and_remove_alias(query, key), key)
                else:
                    query = self.replace_occurrences(query, key, value[1])
        return query

    @staticmethod
    def remove_occurrences_in_joins(query, key):
        result_list = [x for x in query.split("JOIN") if key not in x]
        for i, item in enumerate(result_list):
            if not i == 0:
                result_list[i] = "JOIN" + item
        return ''.join(result_list)

    @staticmethod
    def replace_occurrences(query, key, value):
        return query.replace(key, value)

    @staticmethod
    def find_and_remove_alias(query, value):
        query_without_whitespace = query.split(' ')
        alias_position = query_without_whitespace.index(value) + 1
        if query_without_whitespace[alias_position].lower() != "on":
            alias = query_without_whitespace[alias_position]
            return query.replace(alias + ".", "")
        return query
