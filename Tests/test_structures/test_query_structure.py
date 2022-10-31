from Structures.QueryStructure import QueryStructure
from Structures.Table import Table
from Structures.Column import Column
from Structures.DatabaseStructure import DatabaseStructure
from Tests.test_structures.helpers import default_tables

def test_query_structures_with_identical_columns_and_tables_are_equal():
    tables = [Table("A"), Table("B"), Table("C")]
    columns = [Column("A_1"), Column("B_1"), Column("C_1")]
    query_structure_1 = QueryStructure(tables, columns)
    query_structure_2 = QueryStructure(tables, columns)

    assert query_structure_1 == query_structure_2

def test_query_structures_with_different_tables_are_not_equal():
    tables1 = [Table("A"), Table("B"), Table("C")]
    tables2 = [Table("A"), Table("B"), Table("C"), Table("D")]
    columns = [Column("A_1"), Column("B_1"), Column("C_1")]
    query_structure_1 = QueryStructure(tables1, columns)
    query_structure_2 = QueryStructure(tables2, columns)

    assert not query_structure_1 == query_structure_2

def test_query_structures_with_different_column_are_not_equal():
    tables = [Table("A"), Table("B"), Table("C")]
    columns1 = [Column("A_1"), Column("B_1"), Column("C_1")]
    columns2 = [Column("A_1"), Column("B_1"), Column("C_1"), Column("C_2")]
    query_structure_1 = QueryStructure(tables, columns1)
    query_structure_2 = QueryStructure(tables, columns2)

    assert not query_structure_1 == query_structure_2

def test_query_copy_is_equal_to_original():
    tables = [Table("A"), Table("B"), Table("C")]
    columns = [Column("A_1"), Column("B_1"), Column("C_1")]
    original = QueryStructure(tables, columns)

    copy = original.copy()

    assert copy == original

def test_get_columns_with_name_returns_empty_list_if_no_matching_columns():
    tables = [Table("A"), Table("B"), Table("C")]
    columns = [Column("A_1"), Column("B_1"), Column("C_1")]
    query_structure = QueryStructure(tables, columns)

    assert query_structure.get_columns_with_name("D_1") == []

def test_get_columns_with_name_returns_matching_columns():
    tables = [Table("A"), Table("B"), Table("C")]
    columns = [Column("A_1"), Column("B_1"), Column("C_1"), Column("B_1")]
    query_structure = QueryStructure(tables, columns)

    assert query_structure.get_columns_with_name("B_1") == [Column("B_1"), Column("B_1")]

def test_resolve_columns_adds_table_name_to_columns_with_alias():
    tables = [Table("A", alias="alias_A"), Table("B", alias="alias_B"), Table("C")]
    columns = [Column("A_1", "alias_A"), Column("B_1", "alias_B"), Column("C_1", "C")]
    query_structure = QueryStructure(tables, columns)

    database_structure = DatabaseStructure([])

    query_structure.resolve_columns(database_structure)

    assert query_structure.get_columns_with_name("A_1")[0].table_name == "A"
    assert query_structure.get_columns_with_name("B_1")[0].table_name == "B"
    assert query_structure.get_columns_with_name("C_1")[0].table_name == "C"

def test_resolve_columns_adds_table_names_to_columns_without_alias_based_on_database_structure():
    tables = [Table("A", alias="alias_A"), Table("B", alias="alias_B"), Table("C")]
    columns = [Column("A_1", "alias_A"), Column("B_1", "alias_B"), Column("C_1")]
    query_structure = QueryStructure(tables, columns)

    database_structure = DatabaseStructure(default_tables())

    query_structure.resolve_columns(database_structure)

    assert query_structure.get_columns_with_name("A_1")[0].table_name == "A"
    assert query_structure.get_columns_with_name("B_1")[0].table_name == "B"
    assert query_structure.get_columns_with_name("C_1")[0].table_name == "C"

