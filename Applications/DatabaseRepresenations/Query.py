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


    def tables_in_query(self, tables):
        return [table for table in tables if table.name in self.query_as_string]

    def transform_ast(self, transformer):
        self.ast = self.ast.transform(transformer)

    def replace_table(self, old_table: Table, new_table: Table):
        def transform(node):
            if isinstance(node, exp.Table) and node.name == str(old_table):
                return parse_one(str(new_table))
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
                    return self.apply_alias_to_node(node, self.get_alias_for_column(tables, alias_map, node.name))
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
        return aliases[column_table]

    def get_table_for_column(self, tables, column_name):
        for table in tables:
            if table.has_column(Column(column_name)):
                return table.name
