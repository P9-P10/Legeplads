import sqlite3

def database_creation(database_name, database_dir = "../Databases/", script_dir = "../SQL/"):
    sql = sqlite3.connect(database_dir + database_name + ".sqlite")
    conn = sql.cursor()
    with open(script_dir + database_name + ".sql") as f:
        conn.executescript(read_file_to_string(f))
    sql.commit()

def read_file_to_string(file):
    return str(file.read())

database_creation("AdvancedDatabase")
database_creation("AdvancedDatabaseButBad")
database_creation("SimpleDatabase")