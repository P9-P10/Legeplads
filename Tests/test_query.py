import pytest

from Applications.DatabaseRepresenations.Query import Query
from Applications.DatabaseRepresenations.Table import Table
from Helpers.Change import TableChange, ColumnChange
from Helpers.database_change_store import DatabaseChangeStore


def test_query_to_string():
    query = Query(query_as_string="SELECT * FROM testTable JOIN other_table")
    assert str(query) == "SELECT * FROM testTable JOIN other_table"


def test_query_to_string_raises_error_if_not_valid_sql():
    with pytest.raises(ValueError) as error:
        Query(query_as_string="This is not valid SQL")
        assert error.value == "The query is not valid SQL"


def test_apply_changes_should_not_update():
    query_string = "SELECT * FROM testTable JOIN other_table"
    expected = "SELECT * FROM testTable JOIN other_table"

    query = Query(query_string)
    query.apply_changes(DatabaseChangeStore())
    assert str(query) == expected


def test_apply_changes_occurrences_of_table():
    query_string = "SELECT col1 FROM testTable JOIN other_table"
    expected = "SELECT col1 FROM testTable JOIN correct_table"

    query = Query(query_string)
    database_change_store = DatabaseChangeStore()
    column_changes = [ColumnChange("col1", "col1", Table("correct_table"))]
    database_change_store.add_new_change(
        TableChange("other_table", column_changes))
    query.apply_changes(database_change_store)

    assert str(query) == expected


def test_apply_changes_does_not_create_duplicates():
    query_string = "SELECT name, wants_letter FROM Users JOIN UserData AS UD ON Users.id " \
                   "= UD.user_id JOIN NewsLetter NL ON UD.id = NL.user_id "
    expected = "SELECT name, wants_letter FROM Users JOIN UserData AS UD ON Users.id = UD.user_id"
    query = Query(query_string)
    wants_letter_change = ColumnChange("wants_letter", "wants_letter", Table("UserData"))
    table_change = TableChange("NewsLetter", [wants_letter_change])
    database_change_store = DatabaseChangeStore()
    database_change_store.add_new_change(table_change)
    query.apply_changes(database_change_store)
    assert str(query) == expected
