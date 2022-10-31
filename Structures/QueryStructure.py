from Structures.DatabaseStructure import DatabaseStructure
from Structures.Structure import Structure
from Structures.Table import Table
from Structures.Column import Column

class QueryStructure(Structure):
    def __init__(self, tables: list[Table], columns: list[Column]):
        self.tables = self.copy_list(tables)
        self.columns = self.copy_list(columns)
        self.alias_map = {}

    def __eq__(self, other):
        if not isinstance(other, QueryStructure):
            return False
        
        return set(self.tables) == set(other.tables) and set(self.columns) == set(other.columns)

    def copy_list(self, list):
        return [elem.copy() for elem in list]

    def copy(self):
        return QueryStructure(self.tables, self.columns)

    def get_columns(self):
        return self.columns

    def get_columns_with_name(self, name: str) -> list[Column]:
        return [column for column in self.columns if column.name == name]

    def resolve_columns(self, db_structure: DatabaseStructure):
        # Populate dictionary to map aliases to table names
        for table in self.tables:
            if table.alias:
                self.alias_map[table.alias] = table.name
        
        def fun(column: Column):
            if column.alias:
                # If it has an alias, it should either be in the alias map, or it should be a table name
                if column.alias in self.alias_map.keys():
                    column.set_table_name(self.alias_map[column.alias])
                else:
                    column.set_table_name(column.alias)
            else:
                column.set_table_name(db_structure.get_table_for_column(column).name)

        self.columns = [column.transform(fun) for column in self.columns]