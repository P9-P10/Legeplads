import pytest

from Applications.DatabaseRepresenations.Query import Query
from Applications.DatabaseRepresenations.Table import Table
from Applications.DatabaseRepresenations.Column import Column
from Helpers.Change import Change


def test_query_to_string():
    query = Query("SELECT * FROM testTable JOIN other_table")
    assert str(query) == "SELECT * FROM testTable JOIN other_table"

def test_query_equals():
    query1 = Query("SELECT * FROM some_table")
    query2 = Query("SELECT * FROM some_table")
    query3 = Query("select * from some_table")
    query4 = Query("SELECT * FROM some_other_table")

    assert query1 == query2
    assert query2 == query3
    assert not (query2 == query4)


def test_query_to_string_raises_error_if_not_valid_sql():
    with pytest.raises(ValueError) as error:
        Query("This is not valid SQL")
        assert error.value == "The query is not valid SQL"


def test_apply_changes_should_not_update_if_there_are_no_changes():
    actual = Query("SELECT * FROM testTable JOIN other_table")
    expected = Query("SELECT * FROM testTable JOIN other_table")

    actual.apply_changes([])
    assert actual == expected


def test_apply_changes_occurrences_of_table():
    actual = Query("SELECT col1 FROM testTable JOIN other_table")
    expected = Query("SELECT col1 FROM testTable JOIN correct_table")

    change = Change((Table('other_table'), Column('col1')), (Table('correct_table'), Column('col1')))

    actual.apply_changes([change])

    assert actual == expected


def test_apply_changes_does_not_create_duplicates():
    actual = Query("SELECT name, wants_letter FROM Users JOIN UserData AS UD ON Users.id " \
                   "= UD.user_id JOIN NewsLetter NL ON UD.id = NL.user_id ")
    expected = Query("SELECT name, wants_letter FROM Users JOIN UserData AS UD ON Users.id = UD.user_id")

    change = Change((Table('NewsLetter'), Column('wants_letter')), (Table('UserData'), Column('wants_letter')))

    actual.apply_changes([change])
    assert actual == expected
