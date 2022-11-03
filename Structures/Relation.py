from Structures.Table import Table
from Structures.Column import Column

class Attribute:
    def __init__(self, column: Column, use_alias = False):
        self.column = column
        self.use_alias = use_alias

    def __repr__(self):
        return f'(Column: {repr(self.column)} Use_alias: {self.use_alias}'

class Relation:
    def __init__(self, table: Table, attributes: list[Attribute], alias: str = ""):
        self.table = table
        self.attributes = attributes
        self.alias = alias
    
    def __repr__(self):
        return f'(Table: {repr(self.table)} Alias: {self.alias} Attributes: {[repr(attr) for attr in self.attributes]})'
