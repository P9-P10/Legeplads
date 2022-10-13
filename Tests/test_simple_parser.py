from Helpers.simple_sql_parser import SqlParser as sp


def test_get_table_names_select():
    query = "select * from Users"
    parser = sp()
    result = parser.get_table_names(query)
    assert result == ["Users"]


def test_get_table_names_join():
    query = "join Users"
    parser = sp()
    result = parser.get_table_names(query)
    assert result == ["Users"]


def test_get_table_names_into():
    query = "INSERT INTO Users"
    parser = sp()
    result = parser.get_table_names(query)
    assert result == ["Users"]


def test_get_table_names_select_and_join():
    query = "SELECT * FROM Users JOIN Orders O on Users.id = O.owner"
    parser = sp()
    result = parser.get_table_names(query)
    assert result == ["Users", "Orders"]


def test_get_where_clause():
    query = "SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'"
    parser = sp()
    result = parser.get_where_clause(query)
    assert result == " O.owner = 'bob'"


def test_get_query_type_select():
    query = "SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'"
    parser = sp()
    assert parser.get_query_type(query) == "SELECT"


def test_get_table_alias():
    query = "SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'"
    parser = sp()
    assert parser.get_table_alias(query) == [('Users', ''), ('Orders', 'O')]


def test_get_variabels():
    query = "SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'"
    parser = sp()
    assert parser.get_variables_without_table_prefixes(query) == ['*']


def test_get_variables_without_table_predix():
    query = "SELECT U.email, UD.name, question, P.name,SUM(quantity) as total_quantity, wants_letter FROM"
    parser = sp()
    assert parser.get_variables_without_table_prefixes(query) == ["email", "name", "question", "total_quantity",
                                                                  "wants_letter"]


def test_get_query_type_update():
    query = "UPDATE Users SET Users.password = 'secure' WHERE Users.email =='test' "
    parser = sp()
    assert parser.get_query_type(query) == "UPDATE"


def test_get_query_type_delete():
    query = "DELETE FROM Users WHERE Users.email =='test' "
    parser = sp()
    assert parser.get_query_type(query) == "DELETE"
