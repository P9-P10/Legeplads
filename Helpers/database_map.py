from Structures.Query import Query
from Applications.Database_intefaces.sqliteinterface import SqLiteInterface
from Structures.Table import Table
from Structures.Column import Column

class DBMapper:
    def __init__(self, dbinterface: SqLiteInterface):
        self.dbinterface = dbinterface

    def create_database_map(self):
        table_details = self.get_table_details()
        map = {}
        for row in table_details:
            table = row[1]
            column = row[2]
            if table not in map.keys():
                map[table] = [column]
            else:
                map[table].append(column)

        tables = []
        for key, value in map.items():
            tables.append(Table(key, [Column(col) for col in value]))
        self.tables = tables
        self.map = map
        return tables

    def get_table_details(self):
        return self.dbinterface.run_query(Query(""" 
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
        """))
