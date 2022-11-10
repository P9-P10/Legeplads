from Structures.DatabaseStructure import DatabaseStructure
import pytest
from Structures.Table import Table
from Structures.Column import Column

@pytest.fixture
def structure():
    a = Table("A", [Column("a"), Column("b"), Column("c")])
    b = Table("B", [Column("d"), Column("e"), Column("f")])
    c = Table("C", [Column("c"), Column("g"), Column("h")])

    return DatabaseStructure([a, b, c])


def test_column_in_tables_returns_true_if_column_in_given_tables(structure):
    assert structure.column_in_tables("b", ["A", "B"]) == True

def test_column_in_tables_returns_false_if_column_not_in_given_tables(structure):
    assert structure.column_in_tables("g", ["A", "B"]) == False

def test_column_in_tables_returns_false_if_column_not_in_any_tables(structure):
    assert structure.column_in_tables("no_such_column", ["A", "B"]) == False