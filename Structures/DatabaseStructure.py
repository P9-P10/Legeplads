from Structures.Table import Table
from Applications.exceptions import AmbiguousColumnException, ColumnNotFoundException, TableNotFoundException

class DatabaseStructure:
    def __init__(self, tables_in_database: list[Table], name=None):
        """ 
        The constructor expects a list of tables that are in the database.
        The columns of the tables in the list, should correspond to their columns in the database.
        """
        self.tables = tables_in_database
        self.table_names = [table.name for table in self.tables]
        self.name = name

    def is_column_in_tables(self, column_name: str, table_names: list[str]):
        for table in self.tables:
            if table.name in table_names:
                if table.has_column_with_name(column_name):
                    return True
        return False

    def table_containing_column(self, column_name: str, table_names: list[str] = None):
        if not table_names:
            table_names = self.table_names
        result_table = None
        for table in self.tables:
            if table.name in table_names and table.has_column_with_name(column_name):
                # Raise exception if another table has already been found
                if result_table:
                    raise AmbiguousColumnException(f'The column {column_name} is present in multiple tables')
                else:
                    result_table = table.name
                
        if result_table:
            return result_table
        else:
            raise ColumnNotFoundException(f'The column {column_name} was not found')

    def get_tables_containing_column(self, column_name: str):
        return [table.name for table in self.tables if table.has_column_with_name(column_name)]
        

    def get_columns_in_table(self, table_name: str):
        if table_name not in self.table_names:
            raise TableNotFoundException(f'The table {table_name} was not found')
        else:
            for table in self.tables:
                if table.name == table_name:
                    columns = table.columns
                    column_names = [column.name for column in columns]
                    return column_names
