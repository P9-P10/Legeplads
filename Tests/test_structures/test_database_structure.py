from Structures.Column import Column
from Structures.DatabaseStructure import DatabaseStructure
from Structures.Table import Table
from Tests.test_structures.helpers import default_tables, create_default_table
import pytest

@pytest.fixture
def default_structure():
    return DatabaseStructure(default_tables())

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

def test_get_table_for_column_returns_none_if_there_is_no_table_with_the_column(default_structure):
    default_structure.get_table_for_column(Column("D_1")) == None

def test_get_table_for_column_returns_table_containing_given_column(default_structure):
    assert default_structure.get_table_for_column(Column("B_2")) == create_default_table("B")

