from Applications.sqliteinterface import SqLiteInterface as Si

database_name = "SimpleDatabase"
database_path = "../Databases/"


def test_basic_select():
    connection = Si(database_path + database_name + ".sqlite")
    result = connection.run_query("SELECT email FROM Users")
    
    assert result == [('test@mail.mail',),
                      ('bob@fancydomain.com',),
                      ('JJonahJameson@JustTheFacts.com',),
                      ('Egon@olsenbanden.net',)]


def test_basic_select_with_join():
    connection = Si(database_path + database_name + ".sqlite")
    result = connection.run_query(
        "SELECT U.email,phone,birthday FROM UserData "
        "JOIN Users U on U.id = UserData.id "
        "ORDER BY birthday")

    assert result == [('test@mail.mail', 1234, '22-22-22'), ('Egon@olsenbanden.net', 57, '22-22-22'),
                      ('bob@fancydomain.com', 12345, '33-33-33'),
                      ('JJonahJameson@JustTheFacts.com', 54646576786, '99-99-99')]
