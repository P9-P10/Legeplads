import sqlite3

from Applications.DatabaseRepresenations.Query import Query
from Applications.Database_intefaces.sqliteinterface import SqLiteInterface
from Helpers.Change import Change
from Applications.query_transformer import transform


class SqLiteInterfaceWithChanges(SqLiteInterface):
    def __init__(self, path_to_database, changes: list[Change], tables=None):
        super().__init__(path_to_database)
        if tables is None:
            tables = []
        self.tables = tables
        self.changes = changes
        self.sql = sqlite3.connect(path_to_database)

    def run_query(self, query: Query):
        return self.run_super_query(query)

    def run_super_query(self, query: Query):
        self.apply_changes(query)
        return super().run_query(query)

    def apply_changes(self, query: Query):
        transform(query, self.changes, self.tables)
