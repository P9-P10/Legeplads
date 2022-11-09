from Applications.query_transformer import transform
from Structures.Query import Query
from Structures.Table import Table
from Structures.Column import Column
from Helpers.Change import Change
import pytest


def test_transform_changes_occurrences_of_table():
    actual = Query("SELECT col1 FROM testTable JOIN other_table")
    expected = Query("SELECT col1 FROM testTable JOIN correct_table")

    changes = [Change((Table('other_table'), Column('col1')), (Table('correct_table'), Column('col1')))]

    old_structure = [Table("testTable",[]), Table("other_table", [Column("col1")])]
    new_structure = [Table("correct_table", [])]
    transform(actual, changes, old_structure, new_structure)

    assert actual == expected

def test_transform_changes_occurrences_of_column():
    actual = Query("SELECT col1 FROM test_table")
    expected = Query("SELECT col2 FROM correct_table")

    changes = [Change((Table('test_table'), Column('col1')), (Table('correct_table'), Column('col2')))]
    old_structure = [Table("test_table",[Column("col1"),Column("col88")])]
    new_structure = [Table("correct_table", [Column("col2")])]
    transform(actual, changes, old_structure, new_structure)

    assert actual == expected

def test_transform_changes_occurrences_of_column_but_not_prefix():
    actual = Query("SELECT T.col1 FROM test_table as T")
    expected = Query("SELECT T.col2 FROM correct_table as T")

    changes = [Change((Table('test_table'), Column('col1')), (Table('correct_table'), Column('col2')))]
    old_structure = [Table("test_table",[Column("col1"),Column("col88")])]
    new_structure = [Table("correct_table", [Column("col2")])]
    transform(actual, changes, old_structure, new_structure)

    assert actual == expected

@pytest.mark.skip(reason="This needs to be reimplemented")
def test_transform_joins():
    actual = Query("SELECT col2, col3, col6 FROM T3 JOIN T1 on T1.col1 = T3.col5")

    expected = Query("SELECT col2,col3,col6 FROM T3 JOIN T2 on T2.col4 = T3.col5")
    t1 = Table("T1", [Column("col1"), Column("col2"), Column("col3")])
    t2 = Table("T2", [Column("col4"), Column("col2")])
    t3 = Table("T3", [Column("col5"), Column("col3"), Column("col6")])

    new_tables = [t2, t3]
    changes = [
        Change((t1, Column("col2")), (t2, Column("col2"))),
        Change((t1, Column("col3")), (t3, Column("col3"))),
        Change((t1, Column("col1")), (t2, Column("col4"))),
    ]
    old_tables = [t1, t3]
    transform(actual, changes, old_tables, new_tables)

    assert actual == expected

def test_transform_select_start_without_ambiguity():
    actual = Query("SELECT * FROM test_table")
    expected = Query("SELECT col1, col2 FROM test_table")

    changes = []
    old_structure = [Table("test_table",[Column("col1"),Column("col2")])]
    new_structure = old_structure

    transform(actual, changes, old_structure, new_structure)

    assert actual == expected


def test_transform_select_start_with_ambiguity():
    actual = Query("SELECT * FROM table_one join table_two on table_two.col2 = table_one.col2")
    expected = Query("SELECT col1, table_one.col2, table_two.col2, col3 "
                     "FROM table_one join table_two on table_two.col2 = table_one.col2")

    changes = []
    old_structure = [Table("table_one",[Column("col1"), Column("col2")]), Table("table_two",[Column("col2"), Column("col3")])]
    new_structure = old_structure

    transform(actual, changes, old_structure, new_structure)

    assert actual == expected
