from Applications.DatabaseRepresenations.Table import Table
from Applications.DatabaseRepresenations.Column import Column

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

    def matching_tables_in_query(self, tables):
        return [table for table in tables if table.name in self.query_as_string]

    def tables_in_query(self):
        return [table.name for table in self.ast.find_all(exp.Table)]

    def columns_in_query(self):
        return [(column.name, column.table) for column in self.ast.find_all(exp.Column)]

    def transform_ast(self, transformer):
        self.ast = self.ast.transform(transformer)

    def replace_table(self, old_table: Table, new_table: Table):
        def transform(node):
            if isinstance(node, exp.Table) and node.name == str(old_table):
                return parse_one(str(new_table))
            if isinstance(node, exp.Column) and node.table == str(old_table):
                return node.replace(exp.Column(this=exp.Identifier(this=node.name),
                                               table=exp.Identifier(this=str(new_table))))
            return node


        self.transform_ast(transform)

    def replace_column(self, old_column: Column, new_column: Column):
        def transform(node):
            if isinstance(node, exp.Column) and node.name == str(old_column):
                if new_column.get_alias():
                    return node.replace(exp.Column(this=exp.Identifier(this=new_column.name),
                                                   table=exp.Identifier(this=new_column.get_alias())))
                else:
                    return node.replace(exp.Column(this=exp.Identifier(this=new_column.name)))
            return node

        self.transform_ast(transform)

    def get_aliases(self):
        return self.get_all_instances(exp.Alias)

    def get_all_instances(self, type):
        return self.ast.find_all(type)

    def get_table(self, object):
        return self.get_next_instance(object, exp.Table)

    def get_table_alias(self, object):
        return self.get_next_instance(object, exp.TableAlias)

    def get_next_instance(self, object, type):
        return object.find(type)

    def apply_missing_aliases(self, tables, alias_map):
        if not tables:
            return

        def transformer(node):
            if isinstance(node, exp.Column):
                if self.node_has_no_table(node):
                    alias = self.get_alias_for_column(tables, alias_map, node.name)
                    if alias is not None:
                        return self.apply_alias_to_node(node, alias)
                elif node.table in [table.name for table in tables]:
                    return self.apply_alias_to_node(node, self.get_alias_for_table(node.table, alias_map))
            return node

        self.transform_ast(transformer)

    def node_has_no_table(self, node):
        return node.table == ""

    def apply_alias_to_node(self, node, alias):
        return node.replace(self.create_column(node.name, alias))

    def create_column(self, name, table):
        return exp.Column(
            this=self.create_identifier(name),
            table=self.create_identifier(table)
        )

    def create_identifier(self, name: str):
        return exp.Identifier(this=name)

    def create_needed_aliases(self):
        def transform(node):
            if isinstance(node, exp.Table):
                if not isinstance(node.parent, exp.Alias):
                    return self.create_alias_on_node(node)
            return node

        self.transform_ast(transform)

    def create_alias_on_node(self, node):
        return node.replace(exp.Alias(
            this=exp.Table(
                this=exp.Identifier(this=node.name, quoted=False)),
            alias=exp.TableAlias(
                this=exp.Identifier(this=node.name + "1"))
        ))

    def get_alias_for_table(self, table_name, table_map):
        return table_map[table_name]

    def get_alias_for_column(self, tables, aliases, column_name):
        column_table = self.get_table_for_column(tables, column_name)
        if column_table is None:
            return None
        return aliases[column_table]

    def get_table_for_column(self, tables, column_name):
        for table in tables:
            if table.has_column(Column(column_name)):
                return table.name

    def change_column_in_comparisons(self, alias, old_column, new_column):

        def is_column_with_correct_table_and_name(node):
            return isinstance(node, exp.Column) and node.name == old_column.name and node.table == alias

        def create_node_with_alias_and_name(node):
            return exp.Column(this=exp.Identifier(this=new_column.name), table=exp.Identifier(this=node.table))

        def column_transform(node):
            if is_column_with_correct_table_and_name(node):
                return node.replace(create_node_with_alias_and_name(node))
            return node

        def transform(node):
            if isinstance(node, exp.EQ):
                return node.transform(column_transform)
            return node

        self.transform_ast(transform)
