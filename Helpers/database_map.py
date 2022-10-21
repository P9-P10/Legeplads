import sqlite3

class SqLiteInterface:
    def __init__(self, path_to_database):
        self.path_to_database = path_to_database
        self.sql = sqlite3.connect(self.path_to_database)

    def run_query(self, query:str):
        conn = self.sql.cursor()
        conn.execute(query)
        response = conn.fetchall()
        self.sql.commit()
        return response

def get_table_details(db_callback):
    return db_callback(""" 
        SELECT
        tl.schema as schema_name,
        m.name as table_name, 
        p.name as column_name,
        p.pk as primary_key
        FROM 
        sqlite_master AS m
        JOIN 
        pragma_table_info(m.name) AS p
        JOIN
        pragma_table_list(m.name) AS tl
        ORDER BY 
        m.name, 
        p.cid; 
    """)

def create_database_map(database):
    conn = SqLiteInterface('./Databases/' + database + '.sqlite')
    table_details = get_table_details(conn.run_query)
    map = {}
    for row in table_details:
        table = row[1]
        column = row[2]
        if table not in map.keys():
            map[table] = [column]
        else:
            map[table].append(column)

    return map

if __name__ == '__main__':
    create_database_map('OptimizedAdvancedDatabase')


