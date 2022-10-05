import sqlite3

simpleDatabaseName = "simpleDatabase"


def basic_select_with_join(database_name):
    sql = sqlite3.connect("../Databases/" + database_name + ".sqlite")
    conn = sql.cursor()
    conn.execute("SELECT U.email,phone,birthday FROM UserData JOIN Users U on U.id = UserData.id ORDER BY birthday")
    result = conn.fetchall()
    sql.commit()
    print(result)


def basic_select(database_name):
    sql = sqlite3.connect("../Databases/" + database_name + ".sqlite")
    conn = sql.cursor()
    conn.execute("SELECT email FROM Users")
    result = conn.fetchall()
    sql.commit()
    print(result)


basic_select_with_join(simpleDatabaseName)
basic_select(simpleDatabaseName)
