from Structures.QueryStructure import QueryStructure
from Structures.Table import Table
from Structures.Column import Column
from Structures.DatabaseStructure import DatabaseStructure
from Tests.test_structures.helpers import default_tables as create_default_tables
import pytest

@pytest.fixture
def default_tables():
    return [Table("A"), Table("B"), Table("C")]

@pytest.fixture
def default_columns(): 
    return [Column("A_1"), Column("B_1"), Column("C_1")]

@pytest.fixture
def default_query_structure(default_tables, default_columns):
    return QueryStructure(default_tables, default_columns)

@pytest.fixture
def default_db_structure():
    return DatabaseStructure(create_default_tables())


def test_query_structures_with_identical_columns_and_tables_are_equal(default_tables, default_columns):
    query_structure_1 = QueryStructure(default_tables, default_columns)
    query_structure_2 = QueryStructure(default_tables, default_columns)

    assert query_structure_1 == query_structure_2

def test_query_structures_with_different_tables_are_not_equal(default_tables, default_columns):
    query_structure_1 = QueryStructure(default_tables, default_columns)
    query_structure_2 = QueryStructure(default_tables + [Table("D")], default_columns)

    assert not query_structure_1 == query_structure_2

def test_query_structures_with_different_column_are_not_equal(default_tables, default_columns):
    query_structure_1 = QueryStructure(default_tables, default_columns)
    query_structure_2 = QueryStructure(default_tables, default_columns + [Column("C_2")])

    assert not query_structure_1 == query_structure_2

def test_query_copy_is_equal_to_original(default_query_structure):
    original = default_query_structure
    copy = original.copy()

    assert copy == original

def test_resolve_columns_adds_table_name_to_columns_with_alias(default_db_structure):
    tables = [Table("A", alias="alias_A"), Table("B", alias="alias_B"), Table("C")]
    columns = [Column("A_1", "alias_A"), Column("B_1", "alias_B"), Column("C_1", "C")]
    query_structure = QueryStructure(tables, columns)

    query_structure.resolve_columns(default_db_structure)

    assert query_structure.get_column("A_1").table_name == "A"
    assert query_structure.get_column("B_1").table_name == "B"
    assert query_structure.get_column("C_1").table_name == "C"

def test_resolve_columns_adds_table_names_to_columns_without_alias_based_on_database_structure(default_db_structure):
    tables = [Table("A", alias="alias_A"), Table("B", alias="alias_B"), Table("C")]
    columns = [Column("A_1", "alias_A"), Column("B_1", "alias_B"), Column("C_1")]
    query_structure = QueryStructure(tables, columns)

    query_structure.resolve_columns(default_db_structure)

    assert query_structure.get_column("A_1").table_name == "A"
    assert query_structure.get_column("B_1").table_name == "B"
    assert query_structure.get_column("C_1").table_name == "C"
