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


def test_transform_add_ambiguous_table(transformer):
    actual = Query("Select * from B Join C")
    expected = Query("Select B1.d, B1.e, B1.f, c, g, h from B as B1 Join C Join B as B2")
    changes = [AddTable("B")]

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_add_ambiguous_table_where_alias_is_table_name(transformer):
    # I am not sure if the use of a tables name as its alias is a realistic case.
    # But should it ever occur, the case is covered
    actual = Query("Select * from B as B Join C")
    expected = Query("Select B1.d, B1.e, B1.f, c, g, h from B as B1 Join C Join B as B2")
    changes = [AddTable("B")]

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_remove_existing_table_and_add_new_table(transformer):
    actual = Query("Select * from A")
    expected = Query("Select a, b, c from D")
    changes = [RemoveTable("A"), AddTable("D")]

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_removes_multiple_occurences_of_table(transformer):
    actual = Query("Select g from C Join A as A1 on A1.c = C.c Join A as A2 on A2.c = C.c")
    expected = Query("Select g from C")
    changes = [RemoveTable("A")]

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_move_column(transformer):
    actual = Query("Select a from A")
    expected = Query("Select a from D")
    changes = [MoveColumn("a", "A", "D")]

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_move_one_of_multiple_columns(transformer):
    actual = Query("Select a, d from A Join B")
    expected = Query("Select a, d from B Join D")
    changes = [MoveColumn("a", "A", "D"), RemoveTable("A")]

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_move_column_with_alias(transformer):
    actual = Query("Select Alias.a from A as Alias")
    expected = Query("Select a from D")
    changes = [MoveColumn("a", "A", "D")]

    transformer.transform(actual, changes)

    assert actual == expected


def test_transform_move_column_that_is_used_in_join_condition_change_table_in_from(transformer):
    actual = Query("Select a, g from A Join C on A.c = C.c")
    expected = Query("Select a, g from C join D where D.c = C.c")
    changes = [MoveColumn("a", "A", "D"), MoveColumn("c", "A", "D")]

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


def test_transform_replace_table_that_is_used_in_from_clause(transformer):
    # Notice that since the change affects the 'FROM' clause, the condition is added
    # to the 'WHERE' clause rather than as an 'ON' clause on the join.
    actual = Query("Select a, g from A Join C on A.c = C.c")
    expected = Query("Select a, g from C join D where D.c = C.c")
    changes = [ReplaceTable("A", "D")]

    transformer.transform(actual, changes)

    assert actual == expected


# This is an alternative result of the functionality tested above.
# In this case the replacement table is added directly to the from clause, 
# rather than as a join
# def test_transform_replace_table_that_is_used_in_from_clause(transformer):
#     actual = Query("Select a, g from A Join C on A.c = C.c")
#     expected = Query("Select a, g from D join C on D.c = C.c")
#     changes = [ReplaceTable("A", "D")]

#     transformer.transform(actual, changes)

#     assert actual == expected


def test_transform_without_changes_removes_unused_tables(transformer):
    actual = Query("Select d, e from B join C")
    expected = Query("Select d, e from B")
    
    transformer.transform(actual, [])

    assert actual == expected

def test_transform_does_not_remove_tables_that_are_only_used_in_condition(transformer):
    actual = Query("Select d, e from C join B on B.d = C.c")
    expected = Query("Select d, e from C join B on B.d = C.c")

    transformer.transform(actual, [])

    assert actual == expected


def test_transform_does_not_change_insert_query(transformer):
    actual = Query("Insert into B(e, f) Values (1,3)")
    expected = Query("Insert into B(e, f) Values (1,3)")

    transformer.transform(actual, [])

    assert actual == expected


def test_transform_handles_subquery_that_is_unaffected_by_changes(transformer):
    actual = Query("SELECT a, d From B Join A WHERE B.d IN (Select d From B)")
    expected = Query("SELECT a, d From B Join D WHERE B.d IN (Select d From B)")
    changes = [MoveColumn("a", "A", "D")]

    transformer.transform(actual, changes)

    assert actual == expected

def test_transform_handles_aggregate_functions_in_selection(transformer):
    actual = Query("Select SUM(a) as sum, g from C Join A on A.c = C.c")
    expected = Query("Select SUM(D.a) as sum, g from C join D on D.c = C.c")
    changes = [ReplaceTable("A", "D")]

    transformer.transform(actual, changes)

    assert actual == expected

def test_transform_handles_multiple_occurences_of_the_same_table_and_preserves_aliases(transformer):
    actual = Query("Select A1.a, g from C Join A as A1 on A1.c = C.c Join A as A2 on A2.c = C.c")
    expected = Query("Select A1.a, g from C join D as A1 on A1.c = C.c Join D as A2 on A2.c = C.c")
    changes = [ReplaceTable("A", "D")]

    transformer.transform(actual, changes)

    assert actual == expected

def test_tranform_handles_attributes_in_group_by_clause(transformer):
    actual = Query("Select a, g from C Join A on A.c = C.c group by a, g")
    expected = Query("Select a, g from C join D on D.c = C.c group by a, g")
    changes = [ReplaceTable("A", "D")]

    transformer.transform(actual, changes)

    assert actual == expected

def test_tranform_handles_attributes_in_order_by_clause(transformer):
    pass