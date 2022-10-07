from Applications.optimizedSqlInterface import OptimizedSqliteInterface as OSi


def test_replace_occurrences():
    connection = OSi("")
    query = "SELECT * FROM testTable JOIN other_table"
    result = connection.replace_occurrences(query, "other_table", "correct_table")
    assert result == "SELECT * FROM testTable JOIN correct_table"


def test_remove_occurrences_in_joins():
    connection = OSi("")
    query = "SELECT * FROM testTable JOIN other_table"
    result = connection.remove_occurrences_in_joins(query, "other_table")
    assert result == "SELECT * FROM testTable "


def test_find_and_remove_alias():
    connection = OSi("")
    query = "SELECT name, ot.other_value FROM testTable JOIN other_table ot"
    result = connection.find_and_remove_alias(query, "other_table")
    assert result == "SELECT name, other_value FROM testTable JOIN other_table ot"


def test_modify_query_with_change_remove_value():
    connection = OSi("")
    connection.database_changes({'other_table': (False, None)})
    query = "SELECT name, ot.other_value FROM testTable JOIN other_table ot"
    result = connection.modify_query_with_changes(query)
    assert result == "SELECT name, other_value FROM testTable "


def test_modify_query_with_change_replace_value():
    connection = OSi("")
    connection.database_changes({'other_table': (True, "correct_table")})
    query = "SELECT name, ot.other_value FROM testTable JOIN other_table ot"
    result = connection.modify_query_with_changes(query)
    assert result == "SELECT name, ot.other_value FROM testTable JOIN correct_table ot"
