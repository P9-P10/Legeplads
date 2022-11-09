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


class Relation:
    def __init__(self, table_node: TableNode, table: Table, attributes: list[Attribute], alias: str = ""):
        self.table_node = table_node
        self.table = table
        self.attributes = attributes
        self.alias = alias

    def __repr__(self):
        return f'(Table: {repr(self.table)} Alias: {self.alias} Attributes: {[repr(attr) for attr in self.attributes]})'
