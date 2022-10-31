from Applications.DatabaseRepresenations.Column import Column
from Applications.DatabaseRepresenations.DatabaseStructure import DatabaseStructure
from Applications.DatabaseRepresenations.Table import Table
import pytest

@pytest.fixture
def default_structure():
    return DatabaseStructure(default_tables())

def default_tables():
    table_a = create_default_table("A")
    table_b = create_default_table("B")
    table_c = create_default_table("C")
    return [table_a, table_b, table_c]

def create_default_table(name, column_number = 4):
    return create_table(name, [name + '_' + str(val) for val in range(1, column_number + 1)])

def create_table(name, columns):
    return Table(name, [create_column(col) for col in columns])

def create_column(name):
    return Column(name)

def test_get_columns_in_table(default_structure):
    expected = [Column("A_1"), Column("A_2"), Column("A_3"), Column("A_4")]

    assert default_structure.get_columns_in_table("A") == expected

def test_get_columns_in_table_throws_if_there_is_no_such_table(default_structure):
    with pytest.raises(ValueError) as e_info:
        default_structure.get_columns_in_table("D")

def test_get_all_tables_returns_tables_in_structure(default_structure):
    assert default_structure.get_all_tables() == default_tables()

def test_get_table_return_table(default_structure):
    assert default_structure.get_table("A") == create_default_table("A")

def test_get_table_throws_if_there_is_no_such_table(default_structure):
    with pytest.raises(ValueError) as e_info:
        default_structure.get_table("D")