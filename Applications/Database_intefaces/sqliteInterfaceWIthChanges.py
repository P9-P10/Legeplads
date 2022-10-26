import sqlite3

from Applications.DatabaseRepresenations.Query import Query
from Applications.Database_intefaces.sqliteinterface import SqLiteInterface
from Helpers.Change import Change
from Applications.query_transformer import transform


class SqLiteInterfaceWithChanges(SqLiteInterface):
    def __init__(self, path_to_database, changes: list[Change],old_tables=None, new_tables=None):
        super().__init__(path_to_database)
        if new_tables is None:
            new_tables = []
        if old_tables is None:
            old_tables = []
        self.old_tables = old_tables
        self.new_tables = new_tables
        self.changes = changes
        self.sql = sqlite3.connect(path_to_database)

    def run_query(self, query: Query):
        return self.run_super_query(query)

    def run_super_query(self, query: Query):
        self.apply_changes(query)
        return super().run_query(query)

    def apply_changes(self, query: Query):
        transform(query, self.changes, self.old_tables, self.new_tables)
