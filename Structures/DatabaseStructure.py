from Structures.Table import Table

class DatabaseStructure:
    def __init__(self, tables_in_database: list[Table]):
        """ 
        The constructor expects a list of tables that are in the database.
        The columns of the tables in the list, should correspond to their columns in the database.
        """
        self.tables = tables_in_database

    def column_in_tables(self, column_name: str, table_names: list[str]):
        for table in self.tables:
            if table.name in table_names:
                if table.has_column_with_name(column_name):
                    return True
        return False