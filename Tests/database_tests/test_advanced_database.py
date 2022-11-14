from Structures.Query import Query
from Structures.Table import Table
from Structures.Column import Column
from Applications.Database_intefaces.sqliteInterfaceWIthChanges import SqLiteInterfaceWithChanges
from Applications.Database_intefaces.sqliteinterface import SqLiteInterface as Si
import pytest

from Helpers.Change import *
from Helpers.database_map import DBMapper
from Scripts.database_creation_tool import run_all_databases
from Tests.test_helpers.DBConfig import DBConfig

database_name = "AdvancedDatabase"
database_path = "./Databases/"
o_database_name = "OptimizedAdvancedDatabase"
db_conf = DBConfig(database_name)
db_conf_o = DBConfig(o_database_name)
old_dbmap = DBMapper(Si(db_conf.get_path_to_database()))
new_dbmap = DBMapper(Si(db_conf_o.get_path_to_database()))


def create_connection_with_changes():
    # Changes
    newsletter = Table('NewsLetter')
    userdata = Table('UserData')
    wants_letter = Column('wants_letter')
    user_id = Column('user_id')
    wants_letter_change = Change((newsletter, wants_letter), (userdata, wants_letter))
    user_id_change = Change((newsletter, user_id), (userdata, user_id))
    changes = [wants_letter_change, user_id_change]

    # Tables
    new_tables = new_dbmap.create_database_map()
    old_tables = old_dbmap.create_database_map()

    return SqLiteInterfaceWithChanges(db_conf_o.get_path_to_database(), changes, old_tables, new_tables)


def create_connection_without_changes():
    return Si(db_conf.get_path_to_database())


connection_without_changes = create_connection_without_changes()
connection_with_changes = create_connection_with_changes()


@pytest.fixture(scope="session")
def set_up():
    run_all_databases()


@pytest.mark.parametrize("input_connection", [connection_without_changes, connection_with_changes])
def test_simple_select(input_connection):
    result = input_connection.run_query(Query("SELECT email FROM Users"))
    assert result == [('test@mail.mail',),
                      ('bob@fancydomain.com',),
                      ('JJonahJameson@JustTheFacts.com',),
                      ('Egon@olsenbanden.net',)]


@pytest.mark.parametrize("input_connection", [connection_without_changes, connection_with_changes])
def test_basic_select_with_join(input_connection):
    result = input_connection.run_query(Query("SELECT U.email,phone,birthday "
                                              "FROM UserData "
                                              "JOIN Users U on U.id = UserData.id "
                                              "ORDER BY birthday"))

    assert result == [('Egon@olsenbanden.net', 57, '1962-10-05 06:38:29'),
                      ('bob@fancydomain.com', 12345, '1966-10-05 06:38:29'),
                      ('JJonahJameson@JustTheFacts.com', 54646576786, '1970-10-05 06:38:29'),
                      ('test@mail.mail', 1234, '2001-10-05 06:38:29')]


@pytest.mark.parametrize("input_connection", [connection_without_changes, connection_with_changes])
def test_select_with_sum(input_connection):
    result = input_connection.run_query(Query(
        "SELECT name, email,SUM(O.quantity) as Total_quantity "
        "FROM Users "
        "JOIN Orders O on Users.id = O.owner "
        "JOIN UserData UD on Users.id = UD.user_id "
        "GROUP BY name"))

    assert result == [('Bob The Builder', 'bob@fancydomain.com', 5),
                      ('Egon Olsen', 'Egon@olsenbanden.net', 19),
                      ('J.Jonah Jameson', 'JJonahJameson@JustTheFacts.com', 2),
                      ('Test User', 'test@mail.mail', 8)]


@pytest.mark.parametrize("input_connection", [connection_without_changes, connection_with_changes])
def test_select_with_joins_from_all_databases_not_all_values_have_alias(input_connection):
    result = input_connection.run_query(Query(
        "SELECT U.email, UD.name, question, P.name,SUM(quantity) as total_quantity, wants_letter "
        "from Users U "
        "JOIN UserData UD on U.id = UD.user_id "
        "JOIN NewsLetter NL on UD.id = NL.user_id "
        "JOIN Orders O on U.id = O.owner "
        "JOIN Products P on P.product_id = O.product "
        "JOIN RecoveryQuestions RQ on U.id = RQ.user_id "
        "GROUP BY UD.name,P.name"))

    assert result == [
        ('bob@fancydomain.com', 'Bob The Builder', 'First pet name', 'Hammer', 5, 0),
        ('Egon@olsenbanden.net', 'Egon Olsen', 'What do i have when i get out of prison?', 'Cigar', 10, 1),
        ('Egon@olsenbanden.net', 'Egon Olsen', 'What do i have when i get out of prison?', 'fith', 8, 1),
        ('Egon@olsenbanden.net', 'Egon Olsen', 'What do i have when i get out of prison?', 'pilsner', 1, 1),
        (
            'JJonahJameson@JustTheFacts.com', 'J.Jonah Jameson', 'What is my most hated "superhero?"', 'Daily Bugle', 2,
            1),
        ('test@mail.mail', 'Test User', 'Animal?', 'Cigar', 1, 1),
        ('test@mail.mail', 'Test User', 'Animal?', 'Hammer', 6, 1),
        ('test@mail.mail', 'Test User', 'Animal?', 'second', 1, 1)]


@pytest.mark.parametrize("input_connection", [connection_without_changes, connection_with_changes])
def test_insert_into_users(input_connection):
    try:
        input_connection.run_query(Query("INSERT INTO Users(email, password) "
                                         "VALUES ('TestMail@TestingTest.test', 'Password12345');"))

        result = input_connection.run_query(Query("SELECT email,password FROM Users "
                                                  "WHERE email == 'TestMail@TestingTest.test' "
                                                  "AND password == 'Password12345';"))

    finally:
        input_connection.run_query(Query("DELETE FROM Users WHERE email== 'TestMail@TestingTest.test';"))

    assert len(result) == 1
    assert result == [('TestMail@TestingTest.test', 'Password12345')]


@pytest.mark.parametrize("input_connection", [connection_without_changes,
                                              connection_with_changes])
def test_select_with_joins_and_aliases_on_all_tables(input_connection):
    query = Query("SELECT NL.user_id, UD.user_id, NL.wants_letter "
                  "FROM Users "
                  "JOIN NewsLetter AS NL ON Users.id = NL.user_id "
                  "JOIN UserData UD ON UD.id = NL.user_id")
    result = input_connection.run_query(query)
    assert result == [(1, 1, 1), (2, 2, 0), (3, 3, 1), (4, 4, 1)]


@pytest.mark.parametrize("input_connection", [connection_without_changes,
                                              connection_with_changes])
def test_select_with_subquery_and_join_with_same_properties_as_query(input_connection):
    query = Query("SELECT user_id,wants_letter "
                  "FROM Users "
                  "JOIN NewsLetter O on Users.id = O.user_id "
                  "WHERE Users.id IN "
                  "("
                  "SELECT id "
                  "FROM UserData "
                  "WHERE 3 > user_id"
                  ")")
    result = input_connection.run_query(query)
    assert result == [(1, 1), (2, 0)]


@pytest.mark.parametrize("input_connection", [connection_without_changes,
                                              connection_with_changes])
def test_select_with_star(input_connection):
    query = Query("SELECT * "
                  "FROM Users "
                  "JOIN NewsLetter NL on Users.id = NL.user_id")
    result = input_connection.run_query(query)
    assert result == [(1, 'test@mail.mail', 'Securepass', '2020-10-05 06:38:29', 1, 1),
                      (2, 'bob@fancydomain.com', 'BobTheBodyBuilder', '2022-10-05 06:38:29', 2, 0),
                      (3, 'JJonahJameson@JustTheFacts.com', 'ScrewYouSpiderMan', '2020-10-05 06:38:29', 3, 1),
                      (4, 'Egon@olsenbanden.net', 'Hundehoveder', '2001-10-05 06:38:29', 4, 1)]
