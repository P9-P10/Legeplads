import sqlite3

from Scripts.database_seeder import *


# This is a slightly different implementation of the SQLiteInterface, specifically used for this function.
# The change is that this uses executescript, rather than execute, and does not utilize changes.
class SeedingSqLiteInterface():
    def __init__(self, path):
        self.sql = sqlite3.connect(path)

    def run_query(self, query):
        conn = self.sql.cursor()
        conn.executescript(query)
        response = conn.fetchall()
        self.sql.commit()
        return response


def main(output_file, user_count, drop_existing_tables=True):
    si = SeedingSqLiteInterface(output_file)
    query = define_all_tables(user_count, should_drop_table=drop_existing_tables)
    si.run_query(query)


if __name__ == "__main__":
    user_count = 800
    main("output_file.sqlite", user_count)
