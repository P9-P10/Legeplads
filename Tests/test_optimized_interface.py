from Applications.optimizedSqlInterface import OptimizedSqliteInterface as OSi
from Helpers.changes_class import Changes as Ch


def test_replace_occurrences():
    connection = OSi("")
    query = "SELECT * FROM testTable JOIN other_table"
    result = connection.replace_occurrences(query, "other_table", "correct_table")
    assert result == "SELECT * FROM testTable JOIN correct_table "


def test_replace_occurrences_does_not_replace_substring():
    connection = OSi("")
    query = "SELECT * FROM testTable JOIN other_table_with_longer_name"
    result = connection.replace_occurrences(query, "other_table", "correct_table")
    assert result == "SELECT * FROM testTable JOIN other_table_with_longer_name"


def test_remove_occurrences_in_joins():
    connection = OSi("")
    query = "SELECT * FROM testTable JOIN other_table"
    result = connection.remove_occurrences_in_joins(query, "other_table")
    assert result == "SELECT * FROM testTable "


def test_remove_occurrences_in_joins_lower_case_JOIN():
    connection = OSi("")
    query = "SELECT * FROM testTable join other_table"
    result = connection.remove_occurrences_in_joins(query, "other_table")
    assert result == "SELECT * FROM testTable "


def test_remove_occurrences_in_joins_mixed_case_JOIN():
    connection = OSi("")
    query = "SELECT * FROM testTable Join other_table"
    result = connection.remove_occurrences_in_joins(query, "other_table")
    assert result == "SELECT * FROM testTable "


def test_find_and_remove_alias():
    connection = OSi("")
    query = "SELECT name, ot.other_value FROM testTable JOIN other_table ot"
    result = connection.find_and_remove_alias(query, "other_table")
    assert result == "SELECT name, other_value FROM testTable JOIN other_table ot"


def test_modify_query_with_change_remove_value():
    connection = OSi("")
    connection.add_database_change('other_table', Ch())
    query = "SELECT name, ot.other_value FROM testTable JOIN other_table ot"
    result = connection.modify_query_with_changes(query)
    assert result == "SELECT name, other_value FROM testTable "


def test_modify_query_with_change_replace_value():
    connection = OSi("")
    connection.add_database_change('other_table', Ch(new_name="correct_table"))
    query = "SELECT name, ot.other_value FROM testTable JOIN other_table ot"
    result = connection.modify_query_with_changes(query)
    assert result == "SELECT name, ot.other_value FROM testTable JOIN correct_table ot"
