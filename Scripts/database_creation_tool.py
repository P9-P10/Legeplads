import os.path
import sqlite3


def database_creation(database_name, database_dir="../Databases/", script_dir="../SQL/"):
    if not os.path.exists(database_dir):
        os.mkdir(database_dir)
    with sqlite3.connect(database_dir + database_name + ".sqlite") as conn:
        with open(script_dir + database_name + ".sql") as f:
            conn.executescript(read_file_to_string(f))
    conn.close()


def read_file_to_string(file):
    return str(file.read())


database_creation("AdvancedDatabase")
database_creation("AdvancedDatabaseButBad")
database_creation("OptimizedAdvancedDatabase")
database_creation("SimpleDatabase")
