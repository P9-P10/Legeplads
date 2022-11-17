from Structures.Table import Table
from Structures.Column import Column


class Schema:
    def __init__(self, tables: list[Table], name=None, uri: str = None):
        self.tables = tables
        self.table_names = [table.name for table in self.tables]
        self.column_dict = self.create_column_dict()
        self.name = name
        self.URI = uri

    def __eq__(self, other):
        if not isinstance(other, Schema):
            return False
        return all([self_table == other_table for self_table, other_table in zip(self.tables, other.tables)])

    def create_column_dict(self):
        column_dict = {}
        for table in self.tables:
            column_dict[table.name] = table.columns
        return column_dict

    def get_columns_in_table(self, table_name: str) -> list[Column]:
        self.raise_error_on_invalid_table(table_name)
        return self.column_dict[table_name]

    def get_all_tables(self) -> list[Table]:
        return self.tables

    def get_table(self, table_name: str) -> Table:
        self.raise_error_on_invalid_table(table_name)
        for table in self.tables:
            if table.name == table_name:
                return table

    def get_table_for_column(self, column: Column) -> Table:
        for table in self.tables:
            if table.has_column(column):
                return table
        return None

    def raise_error_on_invalid_table(self, table_name: str):
        if table_name not in self.table_names:
            raise ValueError(f'Table {table_name} is not in the structure')
