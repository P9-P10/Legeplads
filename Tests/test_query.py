import pytest

from Applications.DatabaseRepresenations.Query import Query
from Applications.DatabaseRepresenations.Table import Table
from Applications.DatabaseRepresenations.Column import Column
from Helpers.Change import Change


def test_query_to_string():
    query = Query("SELECT * FROM testTable JOIN other_table")
    assert str(query) == "SELECT * FROM testTable JOIN other_table"


def test_query_comparison_succeeds_on_same_query():
    query1 = Query("SELECT * FROM some_table")
    query2 = Query("SELECT * FROM some_table")

    assert query1 == query2


def test_query_comparison_fails_on_different_queries():
    query1 = Query("SELECT * FROM some_table")
    query2 = Query("SELECT * FROM some_other_table")

    assert not query1 == query2


def test_query_comparison_is_not_case_sensitive_with_keywords():
    query1 = Query("SELECT * FROM some_table")
    query2 = Query("select * from some_table")

    assert query1 == query2


def test_query_comparison_is_case_sensitive_about_identifiers():
    query1 = Query("SELECT * FROM some_table")
    query2 = Query("SELECT * FROM SOME_TABLE")

    assert not query1 == query2


def test_query_comparison_succeeds_when_keywords_can_be_inferred():
    query1 = Query("SELECT * FROM some_table ST")
    query2 = Query("SELECT * FROM some_table AS ST")

    assert query1 == query2


def test_query_to_string_raises_error_if_not_valid_sql():
    with pytest.raises(ValueError) as error:
        Query("This is not valid SQL")
        assert error.value == "The query is not valid SQL"
