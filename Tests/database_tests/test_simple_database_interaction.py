from Applications.Database_intefaces.sqliteinterface import SqLiteInterface as Si
import pytest

from Tests.test_helpers.DBConfig import DBConfig

database_name = "SimpleDatabase"
database_path = "./Databases/"


@pytest.fixture
def connection():
    db_conf = DBConfig(database_name)
    return Si(db_conf.get_path_to_database())


def test_basic_select(connection):
    result = connection.run_query("SELECT email FROM UserData")

    assert result == [('test@mail.mail',),
                      ('bob@fancydomain.com',),
                      ('JJonahJameson@JustTheFacts.com',),
                      ('Egon@olsenbanden.net',)]


def test_basic_select_with_join(connection):
    result = connection.run_query(
        "SELECT email,phone,birthday FROM UserData "
        "JOIN Users U on U.id = UserData.id "
        "ORDER BY birthday")

    assert result == [('test@mail.mail', 1234, '22-22-22'), ('Egon@olsenbanden.net', 57, '22-22-22'),
                      ('bob@fancydomain.com', 12345, '33-33-33'),
                      ('JJonahJameson@JustTheFacts.com', 54646576786, '99-99-99')]
