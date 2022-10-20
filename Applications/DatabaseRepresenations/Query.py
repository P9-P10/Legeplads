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

    def __repr__(self):
        return str(self)

    def apply_changes(self, changes: list[Change]):
        for change in changes:
            new_table, new_column = change.new
            old_table, old_column = change.old

            # self.remove_alias_for_table(str(old_table))
            self.replace_old_table_with_new_table(old_table, new_table)

    def query_contains_selection(self, table: Table, column: Column) -> bool:
        ast_string = repr(self.ast)

        if str(table) in ast_string and str(column) in ast_string:
            return True
        return False

    def remove_selection(self, table: Table):
        ast_string = self.ast.sql()
        join_sections = [x for x in re.split(r"(?=join)", ast_string, flags=re.IGNORECASE) if
                         str(table) not in x]

        self.ast = parse_one(''.join(join_sections))

    def remove_alias_for_table(self, table_name: str):
        alias_map = {}
        for alias in self.ast.find_all(exp.Alias):
            if alias.find(exp.Table) is not None:
                table = alias.find(exp.Table).name
                table_alias = alias.find(exp.TableAlias).name
                alias_map[table_alias] = table

        def transformer(node):
            if isinstance(node, exp.Column) and alias_map.get(node.table) == table_name:
                return node.replace(exp.Column(this=exp.Identifier(this=node.name, quoted=False), table=''))
            return node

        self.ast = self.ast.transform(transformer)

    def replace_old_table_with_new_table(self, old_table: Table, new_table: Table):
        def transform(node):
            if isinstance(node, exp.Table) and node.name == str(old_table):
                return parse_one(str(new_table))
            return node

        self.ast = self.ast.transform(transform)
