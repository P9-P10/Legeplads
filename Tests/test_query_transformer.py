from Applications.query_transformer import Transformer
import pytest
from Structures.Query import Query
from Structures.Table import Table
from Structures.Column import Column
from Structures.DatabaseStructure import DatabaseStructure
from Structures.Changes import AddTable, RemoveTable, MoveColumn, RemoveColumn, AddColumn, ReplaceTable
from Applications.exceptions import InvalidSelectionException, InvalidTransformationException, InvalidQueryException

@pytest.fixture
def old_db():
    a = Table("A", [Column("a"), Column("b"), Column("c")])
    b = Table("B", [Column("d"), Column("e"), Column("f")])
    # Both A and C contain a column with the name "c"
    c = Table("C", [Column("c"), Column("g"), Column("h")])

    return DatabaseStructure([a, b, c])


@pytest.fixture
def new_db():
    b = Table("B", [Column("d"), Column("e"), Column("f")])
    c = Table("C", [Column("g"), Column("h")])
    # All columns from A have been moved to D, and table A has been removed. 
    # Also the column "c" from C has also been moved to column "c" in D.
    d = Table("D", [Column("a"), Column("b"), Column("c")])

    return DatabaseStructure([b, c, d])


@pytest.fixture
def transformer(old_db, new_db):
    return Transformer(old_db, new_db)

def test_transform_raises_error_when_selecting_unavailable_columns(transformer):
    query = Query("Select g from A")

    with pytest.raises(InvalidQueryException):
        transformer.transform(query, [])

# TODO: Add test for removing table containing selected columns when doing SELECT *

def test_transform_removes_table(transformer):
    actual = Query("Select d, e from A, B")
    expected = Query("Select d, e from B")
    changes = [RemoveTable("A")]

    transformer.transform(actual, changes)

    assert actual == expected

def test_transform_removes_table_in_join(transformer):
    actual = Query("Select d, e from B Join A")
    expected = Query("Select d, e from B")
    changes = [RemoveTable("A")]

    transformer.transform(actual, changes)

    assert actual == expected

@pytest.mark.skip(reason="This verification does not work correctly")
def test_transform_raises_error_if_column_from_removed_table_is_in_selection(transformer):
    actual = Query("Select a, d from A Join B")
    changes = [RemoveTable("B")]

    with pytest.raises(InvalidSelectionException):
        transformer.transform(actual, changes)


# TODO: Change how SELECT * is handled. It should not add more columns than are present in the original query
def test_transform_add_table_to_query_with_single_column(transformer):
    actual = Query("Select * from B")
    expected = Query("Select d, e, f from B join C")
    changes = [AddTable("C")]

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_add_table_to_query_with_multiple_columns(transformer):
    actual = Query("Select * from B Join C")
    expected = Query("Select d, e, f, c, g, h from B Join C Join D")
    changes = [AddTable("D")]

    transformer.transform(actual, changes)

    assert actual == expected

@pytest.mark.skip(reason="This can't happen with the current structure")
def test_transform_adds_alias_when_changes_cause_name_collisions(transformer):
    actual = Query("Select c, g from C")
    expected = Query("Select D.c, g from C Join D")
    changes = [MoveColumn("c", "C", "D")]

    transformer.transform(actual, changes)

    assert actual == expected


@pytest.mark.skip(reason="This can't happen, as the second instance of C is unused and therefore removed")
def test_transform_adds_alias_when_same_table_occurs_multiple_times(transformer):
    actual = Query("Select c from C")
    expected = Query("Select C1.c from C as C1 Join C as C2")
    changes = [AddTable("C")]

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_remove_existing_table_and_add_new_table(transformer):
    actual = Query("Select * from A")
    expected = Query("Select a, b, c from D")
    changes = [RemoveTable("A"), AddTable("D")]

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_move_column(transformer):
    actual = Query("Select a from A")
    expected = Query("Select a from D")
    changes = [MoveColumn("a", "A", "D")]
    # This is equivalent to 
    # changes = [RemoveTable("A"), AddTable("D")]

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_move_one_of_multiple_columns(transformer):
    actual = Query("Select a, d from A Join B")
    expected = Query("Select a, d from B Join D")
    changes = [MoveColumn("a", "A", "D"), RemoveTable("A")]
    # This is equivalent to 
    # changes = [AddTable("D"), RemoveTable("A")]

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_move_column_with_alias(transformer):
    actual = Query("Select Alias.a from A as Alias")
    expected = Query("Select a from D")
    changes = [MoveColumn("a", "A", "D")]
    # This is NOT equivalent to
    # changes = [AddTable("D"), RemoveTable("A")]
    # Because of the alias
    # When only doing add and remove, there is no way to determine alias equivalence.

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_move_column_that_is_used_in_join_condition_change_table_in_from(transformer):
    actual = Query("Select a, g from A Join C on A.c = C.c")
    expected = Query("Select a, g from C join D where D.c = C.c")
    changes = [MoveColumn("a", "A", "D"), MoveColumn("c", "A", "D"), RemoveTable("A")]
   # The changes below, produce the same result 
   # changes = [ReplaceTable("A", "D")]

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_move_column_from_table_that_is_not_used_does_nothing(transformer):
    actual = Query("Select * from C")
    expected = Query("Select c, g, h from C")
    changes = [MoveColumn("a", "A", "D")]

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_replace_table_that_is_used_in_join(transformer):
    actual = Query("Select a, g from C Join A on A.c = C.c")
    expected = Query("Select a, g from C join D on D.c = C.c")
    changes = [ReplaceTable("A", "D")]

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_replace_table_not_in_the_query_does_nothing(transformer):
    actual = Query("Select * from C")
    expected = Query("Select c, g, h from C")
    changes = [ReplaceTable("B", "D")]

    transformer.transform(actual, changes)

    assert actual == expected

# TODO: Handle the addition of another instance of a table that is already in the query

# TODO: Handle subqueries

# TODO: Ensure aliases are preserved