from Structures.Column import Column
from Structures.Structure import Structure


class Table(Structure):
    def __init__(self, name, columns=None):
        if columns is None:
            columns = []
        self.name = name
        self.columns = columns
        self.alias = None

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Table):
            if str(other) == str(self):
                if set(self.columns) == set(other.columns):
                    if self.alias and other.alias:
                        return self.alias == other.alias
                    else:
                        return True
        return False

    def __repr__(self):
        return f'Table(name: {self.name}, alias: {self.alias}, columns: {[repr(col) for col in self.columns]})'

    def has_column(self, column: Column):
        return column in self.columns

    def has_column_with_alias(self,column:Column,alias):
        for current_column in self.columns:
            if current_column == column:
                if current_column.alias:
                    return current_column.alias == alias
                else:
                    return True

        return False

    def set_alias(self, alias):
        self.alias = alias

    def get_alias(self):
        return self.alias

    def get_column(self,column_name):
        for column in self.columns:
            if column.name == column_name:
                return column

    def copy(self):
        if self.columns:
            new_columns = [col.copy() for col in self.columns]
        else:
            new_columns = None
            
        new_table = Table(self.name, new_columns)
        new_table.set_alias(self.alias)
        return new_table

    def transform_columns(self, column_transformation):
        def transformation(table):
            table.columns = [column.transform(column_transformation) for column in table.columns]

        return self.transform(transformation)
