from Applications.query_transformer import transform
from Structures.Query import Query
from Structures.Table import Table
from Structures.Column import Column
from Helpers.Change import Change
from Helpers.equality_constraint import EqualityConstraint


def test_transform_changes_occurrences_of_table():
    actual = Query("SELECT col1 FROM testTable JOIN other_table")
    expected = Query("SELECT col1 FROM testTable JOIN correct_table")

    changes = [Change((Table('other_table'), Column('col1')), (Table('correct_table'), Column('col1')))]
    transform(actual, changes, [], [])

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



def test_transform_fully_qualifies_known_column_names():
    actual = Query("SELECT name FROM UserData")

    expected = Query("SELECT name FROM UserData")
    transform(actual, [], [], [Table("UserData", [Column("name")])])

    assert actual == expected

def test_transform_joins():
    actual = Query("SELECT col2, col3, col6 FROM T3 JOIN T1 on T1.col1 = T3.col5")

    expected = Query("SELECT col2,col3,col6 FROM T3 JOIN T2 on T2.col4 = T3.col5")
    t1 = Table("T1", [Column("col1"), Column("col2"), Column("col3")])
    t2 = Table("T2", [Column("col4"), Column("col2")])
    t3 = Table("T3", [Column("col5"), Column("col3"), Column("col6")])
    equality_constraint = EqualityConstraint(t1, Column("col1"), t2, Column("col4"))

    new_tables = [t2, t3]
    changes = [Change((t1, Column("col2")), (t2, Column("col2")),
                      constraint=equality_constraint),
               Change((t1, Column("col3")), (t3, Column("col3")))]
    old_tables = [t1, t3]
    transform(actual, changes, old_tables, new_tables)

    assert actual == expected
