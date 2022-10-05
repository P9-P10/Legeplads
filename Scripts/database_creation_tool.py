import sqlite3


def database_creation(database_name):
    sql = sqlite3.connect("../Databases/" + database_name + ".sqlite")
    conn = sql.cursor()
    f = open("../SQL/" + database_name + ".sql")
    conn.executescript(str(f.read()))
    sql.commit()


database_creation("AdvancedDatabase")
database_creation("AdvancedDatabaseButBad")
database_creation("SimpleDatabase")
