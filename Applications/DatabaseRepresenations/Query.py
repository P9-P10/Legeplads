import re

import sqlglot

from Helpers.Change import TableChange
from Helpers.database_change_store import DatabaseChangeStore
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

    def apply_changes(self, database_changes_store: DatabaseChangeStore):
        for table_change in database_changes_store.get_changes():
            for column_change in table_change.get_column_changes():
                if self.query_contains_selection(str(column_change.new_table), column_change.new_name):
                    self.remove_selection(table_change.old_name, column_change.new_name)
                else:
                    self.transform_table(column_change.new_table, table_change.old_name)

    def query_contains_selection(self, table, column):
        ast_string = repr(self.ast)
        if table in ast_string and column in ast_string:
            return True
        return False

    def remove_selection(self, table, column):
        ast_string = self.ast.sql()
        join_sections = [x for x in re.split(r"(?=join)", ast_string, flags=re.IGNORECASE) if
                         table not in x]

        self.ast = parse_one(''.join(join_sections))

    def transform_table(self, new_name, old_name):
        def transform(node):
            if isinstance(node, exp.Table) and node.name == old_name:
                return parse_one(str(new_name))
            return node

        self.ast = self.ast.transform(transform)
