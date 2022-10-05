import sqlite3
import pytest

database_name = "AdvancedDatabase"


def test_simple_select():
    sql = sqlite3.connect("../Databases/" + database_name + ".sqlite")
    conn = sql.cursor()
    conn.execute("SELECT email FROM Users")
    result = conn.fetchall()
    sql.commit()
    assert result == [('test@mail.mail',),
                      ('bob@fancydomain.com',),
                      ('JJonahJameson@JustTheFacts.com',),
                      ('Egon@olsenbanden.net',)]


def test_basic_select_with_join():
    sql = sqlite3.connect("../Databases/" + database_name + ".sqlite")
    conn = sql.cursor()
    conn.execute("SELECT U.email,phone,birthday "
                 "FROM UserData "
                 "JOIN Users U on U.id = UserData.id ORDER BY birthday")
    result = conn.fetchall()
    assert result == [('Egon@olsenbanden.net', 57, '1962-10-05 06:38:29'),
                      ('bob@fancydomain.com', 12345, '1966-10-05 06:38:29'),
                      ('JJonahJameson@JustTheFacts.com', 54646576786, '1970-10-05 06:38:29'),
                      ('test@mail.mail', 1234, '2001-10-05 06:38:29')]


def test_select_with_sum():
    sql = sqlite3.connect("../Databases/" + database_name + ".sqlite")
    conn = sql.cursor()
    conn.execute(
        "SELECT name, email,SUM(o.quantity) as Total_quantity "
        "FROM Users join Orders O on Users.id = O.owner "
        "JOIN UserData UD on Users.id = UD.user_id GROUP BY name")
    result = conn.fetchall()
    assert result == [('Egon Olsen', 'Egon@olsenbanden.net', 19),
                      ('J.Jonah Jameson', 'JJonahJameson@JustTheFacts.com', 2),
                      ('Test User', 'test@mail.mail', 8)]
