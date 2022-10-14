from Helpers.simple_sql_parser import SqlParser as sp
from Helpers.query import Query as Q


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


def test_get_table_alias():
    query = "SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'"
    parser = sp()
    assert parser.get_table_alias(query) == [('Users', ''), ('Orders', 'O')]


def test_get_variables():
    query = "SELECT * FROM Users JOIN Orders O on Users.id = O.owner WHERE O.owner = 'bob'"
    parser = sp()
    assert parser.get_variables_with_prefix(query) == [('', '*')]


def test_get_variables_with_prefix():
    query = "SELECT U.email, UD.name, question, P.name,SUM(quantity) as total_quantity, wants_letter FROM"
    parser = sp()
    assert parser.get_variables_with_prefix(query) == [('U', 'email'),
                                                       ('UD', 'name'),
                                                       ('', 'question'),
                                                       ('P', 'name'),
                                                       ('', 'total_quantity'),
                                                       ('', 'wants_letter')]
