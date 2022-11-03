from Structures.Table import Table
from Structures.Column import Column

def default_tables():
    table_a = create_default_table("A")
    table_b = create_default_table("B")
    table_c = create_default_table("C")
    return [table_a, table_b, table_c]

def create_default_table(name, column_number = 4):
    return create_table(name, create_columns_for_table(name, column_number))

def create_table(name, columns):
    return Table(name, columns)

def create_columns_for_table(name, number):
    return [create_column(name + '_' + str(val)) for val in range(1, number + 1)]

def create_column(name):
    return Column(name)
