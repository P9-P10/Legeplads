from Applications.querytransformation import ChangeTable


def test_change_table_returns_query_if_table_not_present():
    query = "SELECT * FROM testTable JOIN other_table"
    expected = "SELECT * FROM testTable JOIN other_table"

    transformation = ChangeTable('no_such_table', 'new_table')
    actual = transformation.apply(query)

    assert actual == expected


def test_change_table_replaces_occurences_of_table():
    query = "SELECT * FROM testTable JOIN other_table"
    expected = "SELECT * FROM testTable JOIN correct_table"

    transformation = ChangeTable('other_table', 'correct_table')
    actual = transformation.apply(query)

    assert actual == expected


def test_change_table_does_not_replace_substring():
    query = "SELECT * FROM testTable JOIN other_table_with_longer_name"
    expected = "SELECT * FROM testTable JOIN other_table_with_longer_name"

    transformation = ChangeTable('other_table', 'correct_table')
    actual = transformation.apply(query)

    assert actual == expected
