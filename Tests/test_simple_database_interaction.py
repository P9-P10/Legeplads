import sqlite3
import pytest

database_name = "SimpleDatabase"





def test_basic_select():
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
    conn.execute("SELECT U.email,phone,birthday FROM UserData JOIN Users U on U.id = UserData.id ORDER BY birthday")
    result = conn.fetchall()
    assert result == [('test@mail.mail', 1234, '22-22-22'), ('Egon@olsenbanden.net', 57, '22-22-22'),
                     ('bob@fancydomain.com', 12345, '33-33-33'),
                     ('JJonahJameson@JustTheFacts.com', 54646576786, '99-99-99')]