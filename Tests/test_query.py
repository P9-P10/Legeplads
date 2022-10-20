import pytest

from Applications.DatabaseRepresenations.Query import Query
from Applications.DatabaseRepresenations.Table import Table
from Applications.DatabaseRepresenations.Column import Column
from Helpers.Change import Change


def test_query_to_string():
    query = Query(query_as_string="SELECT * FROM testTable JOIN other_table")
    assert str(query) == "SELECT * FROM testTable JOIN other_table"


def test_query_to_string_raises_error_if_not_valid_sql():
    with pytest.raises(ValueError) as error:
        Query(query_as_string="This is not valid SQL")
        assert error.value == "The query is not valid SQL"


def test_apply_changes_should_not_update_if_there_are_no_changes():
    query_string = "SELECT * FROM testTable JOIN other_table"
    expected = "SELECT * FROM testTable JOIN other_table"

    query = Query(query_string)
    query.apply_changes([])
    assert str(query) == expected


def test_apply_changes_occurrences_of_table():
    query_string = "SELECT col1 FROM testTable JOIN other_table"
    expected = "SELECT col1 FROM testTable JOIN correct_table"

    query = Query(query_string)

    change = Change((Table('other_table'), Column('col1')), (Table('correct_table'), Column('col1')))

    query.apply_changes([change])

    assert str(query) == expected


def test_apply_changes_does_not_create_duplicates():
    query_string = "SELECT name, wants_letter FROM Users JOIN UserData AS UD ON Users.id " \
                   "= UD.user_id JOIN NewsLetter NL ON UD.id = NL.user_id "
    expected = "SELECT name, wants_letter FROM Users JOIN UserData AS UD ON Users.id = UD.user_id"
    query = Query(query_string)

    change = Change((Table('NewsLetter'), Column('wants_letter')), (Table('UserData'), Column('wants_letter')))

    query.apply_changes([change])
    assert str(query) == expected
