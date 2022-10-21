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

    def apply_changes(self, changes: list[Change], tables=None):
        if tables is not None:
            self.fully_qualify_column_names(
                [table for table in tables if table.name in self.query_as_string])
        if changes is not None:
            self.apply_each_change(changes)

    def apply_each_change(self, changes):
        for change in changes:
            new_table, new_column = change.new
            old_table, old_column = change.old

            self.replace_old_table_with_new_table(old_table, new_table)

    def query_contains_selection(self, table: Table, column: Column) -> bool:
        ast_string = repr(self.ast)

        if str(table) in ast_string and str(column) in ast_string:
            return True
        return False

    def replace_old_table_with_new_table(self, old_table: Table, new_table: Table):
        def transform(node):
            if isinstance(node, exp.Table) and node.name == str(old_table):
                return parse_one(str(new_table))
            return node

        self.ast = self.ast.transform(transform)

    def fully_qualify_column_names(self, tables: [Table]):
        self.create_needed_aliases()
        alias_map = self.create_alias_map()
        self.apply_missing_aliases(tables, alias_map)

    def apply_missing_aliases(self, tables, alias_map):
        def transformer(node):
            if isinstance(node, exp.Column):
                if self.node_has_no_table(node):
                    return self.apply_alias_to_node(node, self.get_alias_for_column(tables, alias_map, node.name))
                elif node.table in [table.name for table in tables]:
                    return self.apply_alias_to_node(node, self.get_alias_for_table(node.table, alias_map))
            return node

        self.ast = self.ast.transform(transformer)

    def node_has_no_table(self, node):
        return node.table == ""

    def apply_alias_to_node(self, node, alias):
        return node.replace(exp.Column(
            this=exp.Identifier(this=node.name),
            table=exp.Identifier(this=alias)))

    def get_table_for_column(self, tables, column_name):
        for table in tables:
            if self.is_current_column(table, column_name):
                return table.name

    def is_current_column(self, table, column_name):
        for column in table.columns:
            if column.name == column_name:
                return True

    def get_alias_for_table(self, table_name, table_map):
        return table_map[table_name]

    def get_alias_for_column(self, tables, aliases, column_name):
        column_table = self.get_table_for_column(tables, column_name)
        return aliases[column_table]

    def create_alias_map(self):
        alias_map = {}
        for alias in self.ast.find_all(exp.Alias):
            self.add_alias_if_exists(alias, alias_map)
        return alias_map

    def add_alias_if_exists(self, alias, alias_map):
        if alias.find(exp.Table) is not None:
            table = alias.find(exp.Table).name
            table_alias = alias.find(exp.TableAlias).name
            alias_map[table] = table_alias

    def create_needed_aliases(self):
        def transform(node):
            if isinstance(node, exp.Table):
                if not isinstance(node.parent, exp.Alias):
                    return self.create_alias_on_node(node)
            return node

        self.ast = self.ast.transform(transform)

    def create_alias_on_node(self, node):
        return node.replace(exp.Alias(this=exp.Table(this=exp.Identifier(this=node.name, quoted=False)),
                                      alias=exp.TableAlias(this=exp.Identifier(this=node.name + "1"))))
