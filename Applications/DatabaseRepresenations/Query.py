from Applications.DatabaseRepresenations.Table import Table
from Applications.DatabaseRepresenations.Column import Column
from Applications.DatabaseRepresenations.ast import AST

import sqlglot

from Helpers.Change import Change
from sqlglot import parse_one, exp

class Query:
    def __init__(self, query_as_string: str):
        self.query_as_string = query_as_string
        try:
            self.ast = AST(parse_one(query_as_string))
        except sqlglot.ParseError:
            raise ValueError("The query is not valid SQL")

    def __str__(self):
        return self.ast.sql()

    def __eq__(self, other):
        if isinstance(other, Query):
            if str(other) == str(self):
                return True
        return False

    def __repr__(self):
        return str(self)

    def apply_changes(self, changes: list[Change], tables=None):
        if tables:
            self.fully_qualify_column_names(self.tables_in_query(tables))
        self.apply_each_change(changes)

    def tables_in_query(self, tables):
        return [table for table in tables if table.name in self.query_as_string]

    def apply_each_change(self, changes):
        for change in changes:
            new_table = change.get_new_table()
            old_table = change.get_old_table()

            self.ast.replace_table(old_table, new_table)

    def fully_qualify_column_names(self, tables: list[Table]):
        self.ast.create_needed_aliases()
        alias_map = self.ast.create_alias_map()
        self.ast.apply_missing_aliases(tables, alias_map)

