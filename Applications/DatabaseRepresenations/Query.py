from Applications.DatabaseRepresenations.Table import Table
from Applications.DatabaseRepresenations.Column import Column
import re

import sqlglot

from Helpers.Change import Change
from sqlglot import parse_one, exp


class Query:
    def __init__(self, query_as_string: str):
        self.query_as_string = query_as_string
        try:
            self.ast = parse_one(query_as_string)
        except sqlglot.ParseError:
            raise ValueError("The query is not valid SQL")

    def __str__(self):
        return self.ast.sql()

    def __eq__(self, other):
        if isinstance(other, Query):
            if str(other) == str(self):
                return True
        return False

    def apply_changes(self, changes: list[Change]):
        for change in changes:
            new_table, new_column = change.new
            old_table, old_column = change.old

            if self.query_contains_selection(new_table, new_column):
                self.remove_selection(old_table)
            else:
                self.transform_table(old_table, new_table)


    def query_contains_selection(self, table: Table, column: Column) -> bool:
        ast_string = repr(self.ast)
        
        if table in ast_string and column in ast_string:
            return True
        return False

    def remove_selection(self, table: Table):
        ast_string = self.ast.sql()
        join_sections = [x for x in re.split(r"(?=join)", ast_string, flags=re.IGNORECASE) if
                         str(table) not in x]

        self.ast = parse_one(''.join(join_sections))

    def transform_table(self, old_table: Table, new_table: Table):
        def transform(node):
            if isinstance(node, exp.Table) and node.name == str(old_table):
                return parse_one(str(new_table))
            return node

        self.ast = self.ast.transform(transform)
