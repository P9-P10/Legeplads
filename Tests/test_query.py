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


def test_apply_changes_with_multiple_joins_on_same_table_does_not_remove_duplicates():
    actual = Query("SELECT NL.user_id, UD.user_id "
                   "FROM Users "
                   "JOIN UserData AS UD ON Users.id= UD.user_id "
                   "JOIN main.UserData NL ON UD.id = NL.user_id")

    expected = Query("SELECT NL.user_id, UD.user_id "
                     "FROM Users "
                     "JOIN UserData AS UD ON Users.id= UD.user_id "
                     "JOIN main.UserData AS NL ON UD.id = NL.user_id")

    actual.apply_changes([])
    assert actual == expected


def test_apply_changes_adds_aliases():
    actual = Query(
        "SELECT U.email, UD.name, question, P.name,SUM(quantity) as total_quantity, wants_letter "
        "from Users U "
        "JOIN UserData UD on U.id = UD.user_id "
        "JOIN NewsLetter NL on UD.id = NL.user_id "
        "JOIN Orders O on U.id = O.owner "
        "JOIN Products P on P.product_id = O.product "
        "JOIN RecoveryQuestions RQ on U.id = RQ.user_id "
        "GROUP BY UD.name,P.name")

    expected = Query(
        "SELECT U.email, UD.name, RQ.question, P.name,SUM(O.quantity) as total_quantity, NL.wants_letter "
        "from Users U "
        "JOIN UserData UD on U.id = UD.user_id "
        "JOIN NewsLetter NL on UD.id = NL.user_id "
        "JOIN Orders O on U.id = O.owner "
        "JOIN Products P on P.product_id = O.product "
        "JOIN RecoveryQuestions RQ on U.id = RQ.user_id "
        "GROUP BY UD.name,P.name")

    news_letter = Table("NewsLetter", [Column("wants_letter")])
    orders = Table("Orders", [Column("quantity")])
    recovery_questions = Table("RecoveryQuestions", [Column("question")])
    tables = [news_letter, orders, recovery_questions]
    actual.apply_changes([], tables)
    assert actual == expected


def test_fully_qualify_column_names():
    actual = Query("SELECT name FROM UserData")

    expected = Query("SELECT UserData1.name FROM UserData AS UserData1")
    actual.fully_qualify_column_names([Table("UserData", [Column("name")])])

    assert actual == expected

def test_fully_qualify_column_names_creates_needed_alias():
    actual = Query("SELECT name FROM UserData")

    expected = Query("SELECT name FROM UserData AS UserData1")

    actual.fully_qualify_column_names([])

    assert actual == expected

def test_fully_qualify_column_names_creates_aliases_for_multiple_tables():
    actual = Query("SELECT name "
                   "FROM UserData "
                   "JOIN RecoveryQuestions on UserData.user_id = RecoveryQuestions.user_id")

    expected = Query("SELECT name "
                     "FROM UserData AS UserData1 "
                     "JOIN RecoveryQuestions as RecoveryQuestions1 on UserData.user_id = RecoveryQuestions.user_id")

    actual.fully_qualify_column_names([])

    assert actual == expected
