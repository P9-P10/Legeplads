from Applications.querytransformation import RemoveTable

def test_remove_table_returns_query_if_table_not_present():
    query = "SELECT * FROM testTable JOIN other_table"
    expected = "SELECT * FROM testTable JOIN other_table"

    transformation = RemoveTable('no_such_table')
    actual = transformation.apply(query)

    assert actual == expected

def test_remove_table_removes_table_from_join_clause():
    query = "SELECT * FROM testTable JOIN other_table"
    expected = "SELECT * FROM testTable"

    transformation = RemoveTable('other_table')
    actual = transformation.apply(query)

    assert actual == expected

def test_remove_table_is_not_case_sensitive():
    query1 = "SELECT * FROM testTable join other_table"
    query2 = "SELECT * FROM testTable Join other_table"
    query3 = "SELECT * FROM testTable jOiN other_table"
    expected = "SELECT * FROM testTable"

    transformation = RemoveTable('other_table')
    actual1 = transformation.apply(query1)
    actual2 = transformation.apply(query2)
    actual3 = transformation.apply(query3)

    assert actual1 == expected
    assert actual2 == expected
    assert actual3 == expected

def test_remove_table_also_removes_alias():
    query =    "SELECT name, ot.other_value FROM testTable JOIN other_table ot"
    expected = "SELECT name, other_value FROM testTable"

    transformation = RemoveTable('other_table')
    actual = transformation.apply(query)

    assert actual == expected