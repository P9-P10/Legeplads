from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, SH
import sqlite3
import uuid
from typing import List


def run_query(conn, query):
    return conn.execute(query).fetchall()


class SQLiteDatastore:

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.conn = sqlite3.connect(connection_string)

    def get_foreign_keys(self):
        return run_query(self.conn, """
          SELECT 
              tl.schema, m.name, p."from", p."table", p."to"
          FROM
              sqlite_master as m
              JOIN pragma_foreign_key_list(m.name) as p ON m.name != p."table"
              JOIN pragma_table_list(m.name) AS tl
          WHERE m.type = 'table'
          ORDER BY m.name;
        """)

    def get_table_details(self):
        return run_query(self.conn, """ 
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

    def get_schema_list(self):
        return run_query(self.conn, """
            SELECT * FROM pragma_database_list()
        """)

    @staticmethod
    def remove_table_details(data, table):
        return [row for row in data if table not in row[1]]

    def to_graph(self, namespace_bindings: list[tuple], uuid_id: uuid.UUID, org: str) -> Graph:
        result_graph = Graph()

        for name, namespace in namespace_bindings:
            result_graph.bind(name, namespace)

        # Fetch the relevant data from the connection
        schemas = self.get_schema_list()
        tables = self.get_table_details()
        tables = SQLiteDatastore.remove_table_details(tables, 'sqlite')
        foreign_keys = self.get_foreign_keys()

        # Create a unique id for the database, based on the input UUID
        database_id = uuid.uuid5(uuid_id, self.connection_string)
        database_uri = URIRef(org + str(database_id))

        result_graph.add((database_uri, RDF.type, ddl.SQLite))
        result_graph.add((database_uri, ddl.withConnection, Literal(self.connection_string)))
        result_graph.add((database_uri, ddl.hasName, Literal(str.split(self.connection_string, '/')[-1])))

        # Add schemas to the graph
        for schema_id, name, location in schemas:
            schema_id = uuid.uuid5(database_id, name)
            schema_uri = URIRef(org + str(schema_id))

            result_graph.add((schema_uri, RDF.type, ddl.Schema))
            result_graph.add((schema_uri, ddl.hasName, Literal(str(name))))

            result_graph.add((database_uri, ddl.hasStructure, schema_uri))

        # Add tables to the graph
        for schema, table, column, is_primary_key in tables:
            schema_id = uuid.uuid5(database_id, schema)
            schema_uri = URIRef(org + str(schema_id))

            table_id = uuid.uuid5(schema_id, table)
            table_uri = URIRef(org + str(table_id))

            result_graph.add((table_uri, RDF.type, ddl.Table))
            result_graph.add((table_uri, ddl.hasName, Literal(str(table))))
            result_graph.add((schema_uri, ddl.hasStructure, table_uri))

        # Add columns to the graph
        for schema, table, column, is_primary_key in tables:
            schema_id = uuid.uuid5(database_id, schema)
            schema_uri = URIRef(org + str(schema_id))

            table_id = uuid.uuid5(schema_id, table)
            table_uri = URIRef(org + str(table_id))

            column_id = uuid.uuid5(table_id, column)
            column_uri = URIRef(org + str(column_id))

            result_graph.add((column_uri, RDF.type, ddl.Column))
            result_graph.add((column_uri, ddl.hasName, Literal(str(column))))
            result_graph.add((table_uri, ddl.hasStructure, column_uri))

            if is_primary_key:
                result_graph.add((table_uri, ddl.primaryKey, column_uri))

        # Add foreign keys
        for schema, from_table, from_column, to_table, to_column in foreign_keys:
            schema_id = uuid.uuid5(database_id, schema)

            from_table_id = uuid.uuid5(schema_id, from_table)
            from_table_uri = URIRef(org + str(from_table_id))

            from_column_id = uuid.uuid5(from_table_id, from_column)
            from_column_uri = URIRef(org + str(from_column_id))

            to_table_id = uuid.uuid5(schema_id, to_table)
            to_table_uri = URIRef(org + str(to_table_id))

            to_column_id = uuid.uuid5(to_table_id, to_column)
            to_column_uri = URIRef(org + str(to_column_id))

            result_graph.add((from_table_uri, ddl.foreignKey, from_column_uri))
            result_graph.add((from_column_uri, ddl.references, to_column_uri))

        return result_graph


def graph_to_triples(graph: Graph) -> str:
    result: List[str] = []

    for s, p, o in graph:
        result.append(f'{{subject:"{s}", predicate:"{p}", object:"{o}"}}')

    return str(result) \
        .replace('\'', "") \
        .replace(ddl, 'ddl:') \
        .replace(org, 'org:') \
        .replace(str(RDF), 'rdf:') \
        .replace(str(SH), 'sh:')


if __name__ == "__main__":
    ddl = Namespace("http://www.cs-22-dt-9-03.org/datastore-description-language#")
    organisation = "www.test-organisation.org/"

    org = Namespace(organisation)

    bindings = [("ddl", ddl),
                ("rdf", RDF),
                ("org", org)]

    uuid_id = uuid.uuid5(uuid.NAMESPACE_DNS, organisation)

    sqlite = SQLiteDatastore('./Databases/AdvancedDatabase.sqlite')

    data_graph = sqlite.to_graph(bindings, uuid_id, organisation)

    data_graph.serialize(destination="data_graph.ttl", format="turtle")

    print(graph_to_triples(data_graph))
