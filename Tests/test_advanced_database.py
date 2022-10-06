from Applications.sqliteinterface import SqLiteInterface as Si
import pytest

database_name = "AdvancedDatabase"
database_path = "./Databases/"


@pytest.fixture
def connection():
    return Si(database_path + database_name + ".sqlite")

def test_simple_select(connection):
    result = connection.run_query("SELECT email FROM Users")
    assert result == [('test@mail.mail',),
                      ('bob@fancydomain.com',),
                      ('JJonahJameson@JustTheFacts.com',),
                      ('Egon@olsenbanden.net',)]


def test_basic_select_with_join(connection):
    result = connection.run_query("SELECT U.email,phone,birthday "
                                  "FROM UserData "
                                  "JOIN Users U on U.id = UserData.id "
                                  "ORDER BY birthday")

    assert result == [('Egon@olsenbanden.net', 57, '1962-10-05 06:38:29'),
                      ('bob@fancydomain.com', 12345, '1966-10-05 06:38:29'),
                      ('JJonahJameson@JustTheFacts.com', 54646576786, '1970-10-05 06:38:29'),
                      ('test@mail.mail', 1234, '2001-10-05 06:38:29')]


def test_select_with_sum(connection):
    result = connection.run_query(
        "SELECT name, email,SUM(o.quantity) as Total_quantity "
        "FROM Users "
        "JOIN Orders O on Users.id = O.owner "
        "JOIN UserData UD on Users.id = UD.user_id "
        "GROUP BY name")

    assert result == [('Bob The Builder', 'bob@fancydomain.com', 5),
                      ('Egon Olsen', 'Egon@olsenbanden.net', 19),
                      ('J.Jonah Jameson', 'JJonahJameson@JustTheFacts.com', 2),
                      ('Test User', 'test@mail.mail', 8)]


def test_select_with_joins_from_all_databases(connection):
    result = connection.run_query(
        "SELECT U.email, UD.name, question, P.name,SUM(quantity) as total_quantity,wants_letter "
        "from Users U "
        "JOIN UserData UD on U.id = UD.user_id "
        "JOIN NewsLetter NL on UD.id = NL.user_id "
        "JOIN Orders O on U.id = O.owner "
        "JOIN Products P on P.product_id = O.product "
        "JOIN RecoveryQuestions RQ on U.id = RQ.user_id "
        "GROUP BY UD.name,P.name")

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


def test_insert_into_users():
    connection = Si(database_path + database_name + ".sqlite")
    connection.run_query("INSERT INTO Users(email, password) "
                         "VALUES ('TestMail@TestingTest.test', 'Password12345');")

    result = connection.run_query("SELECT email,password FROM Users "
                                  "WHERE email == 'TestMail@TestingTest.test' "
                                  "AND password == 'Password12345';")

    connection.run_query("DELETE FROM Users WHERE email== 'TestMail@TestingTest.test';")
    assert len(result) == 1
    assert result == [('TestMail@TestingTest.test', 'Password12345')]
