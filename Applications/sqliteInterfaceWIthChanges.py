import sqlite3

from Applications.DatabaseRepresenations.Query import Query
from Applications.sqliteinterface import SqLiteInterface
from Helpers.Change import TableChange
from Helpers.database_change_store import DatabaseChangeStore


class SqLiteInterfaceWithChanges(SqLiteInterface):
    def __init__(self, path_to_database, change_store: DatabaseChangeStore):
        super().__init__(path_to_database)
        self.change_store = change_store
        self.sql = sqlite3.connect(path_to_database)

    def run_query(self, query: Query):
        return self.run_super_query(query)

    def run_super_query(self, query: Query):
        self.apply_changes(query)
        return super().run_query(query)

    def apply_changes(self, query: Query):
        query.apply_changes(self.change_store)
