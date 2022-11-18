from Structures.DatabaseStructure import DatabaseStructure
import pytest
from Structures.Table import Table
from Structures.Column import Column
from Applications.exceptions import AmbiguousColumnException, ColumnNotFoundException, TableNotFoundException

@pytest.fixture
def structure():
    a = Table("A", [Column("a"), Column("b"), Column("c")])
    b = Table("B", [Column("d"), Column("e"), Column("f")])
    c = Table("C", [Column("c"), Column("g"), Column("h")])

    return DatabaseStructure([a, b, c])


def test_column_in_tables_returns_true_if_column_in_given_tables(structure):
    assert structure.is_column_in_tables("b", ["A", "B"]) == True

def test_column_in_tables_returns_false_if_column_not_in_given_tables(structure):
    assert structure.is_column_in_tables("g", ["A", "B"]) == False

def test_column_in_tables_returns_false_if_column_not_in_any_tables(structure):
    assert structure.is_column_in_tables("no_such_column", ["A", "B"]) == False


def test_table_containing_column_raises_if_column_in_multiple_tables(structure):
    with pytest.raises(AmbiguousColumnException):
        structure.table_containing_column("c")

def test_table_containing_column_checks_all_tables_by_default(structure):
    assert structure.table_containing_column("e") == "B"

def test_table_containing_column_checks_given_subset_of_tables(structure):
    assert structure.table_containing_column("c", ["B", "C"]) == "C"

def test_table_containing_column_raises_if_column_not_in_any_table(structure):
    with pytest.raises(ColumnNotFoundException):
        structure.table_containing_column("x")


def test_get_columns_in_table_raises_if_no_such_table(structure):
    with pytest.raises(TableNotFoundException):
        structure.get_columns_in_table("X")

def test_get_columns_in_table_returns_names_of_columns_in_the_table(structure):
    assert structure.get_columns_in_table("A") == ["a", "b", "c"]

def test_get_tables_containing_column(structure):
    assert structure.get_tables_containing_column("c") == ["A", "C"]