from Structures.Table import Table
from Structures.Column import Column
from Structures.Node import TableNode, ColumnNode

class Attribute:
    def __init__(self, column_node: ColumnNode, column: Column, use_alias=False):
        self.column_node = column_node
        self.column = column
        self.use_alias = use_alias

    def __repr__(self):
        return f'(Column: {repr(self.column)} Use_alias: {self.use_alias}'

    def get_name(self):
        return self.column.name

    def change_column(self, column: Column):
        self.column = column
        if self.column_node and self.column:
            self.column_node.set_name(self.get_name())
            self.column_node.get_query_node().replace(self.column_node.create_new_query_node())

    def set_use_alias(self, value: bool):
        self.use_alias = value
        # This can be simplified, a new node is created even if there are no changes
        if self.column_node and self.column:
            if self.use_alias:
                self.column_node.set_alias(self.column.get_alias())
                self.column_node.get_query_node().replace(self.column_node.create_new_query_node())
            else:
                self.column_node.set_alias(None)
                self.column_node.get_query_node().replace(self.column_node.create_new_query_node())


class Relation:
    def __init__(self, table_node: TableNode, table: Table, attributes: list[Attribute], alias: str = ""):
        self.table_node = table_node
        self.table = table
        self.attributes = attributes
        self.alias = alias

    def __repr__(self):
        return f'(Table: {repr(self.table)} Alias: {self.alias} Attributes: {[repr(attr) for attr in self.attributes]})'

    def get_name(self):
        return self.table.name

    def change_table(self, new_table: Table): 
        self.table = new_table
        if self.table_node:
            self.table_node.set_name(self.get_name())
            self.table_node.get_query_node().replace(self.table_node.create_new_query_node())