from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, FOAF, XSD, OWL
import sqlite3

# Could not figure out how to import from Applications folder, so I copied what I needed
conn = sqlite3.connect('./Databases/AdvancedDatabase.sqlite')


# TODO: Add the database itself to the graph (Datastore/Database/Relational/SQLite)

def run_query(query):
    response = conn.execute(query).fetchall()
    return response


table_details = run_query(""" 
  SELECT
    m.name as table_name, 
    p.name as column_name,
    p.pk as primary_key
  FROM 
    sqlite_master AS m
  JOIN 
    pragma_table_info(m.name) AS p
  ORDER BY 
    m.name, 
    p.cid; 
""")


def remove_table_details(data, table):
    return [row for row in data if table not in row[0]]


foreign_keys = run_query("""
  SELECT 
      m.name, p."from", p."table", p."to"
  FROM
      sqlite_master as m
      JOIN pragma_foreign_key_list(m.name) as p ON m.name != p."table"
  WHERE m.type = 'table'
  ORDER BY m.name;
""")

tables = remove_table_details(table_details, 'sqlite')

print(tables)
print(foreign_keys)

ddl = Namespace("http://www.cs-22-dt-9-03.org/datastore-description-language#")

data_graph = Graph()
data_graph.bind("rdf", RDF)
data_graph.bind("ddl", ddl)


def add_triples_for_tables(graph, tables):
    unique_table_names = set([row[0] for row in tables])

    for table in unique_table_names:
        table_uri = URIRef(str(table))

        graph.add((table_uri, RDF.type, ddl.Table))
        graph.add((table_uri, ddl.hasName, Literal(str(table))))


def add_triples_for_columns(graph, tables):
    for t in tables:
        (table, column, is_primary_key) = t
        column_uri = URIRef(table + '/' + column)
        table_uri = URIRef(table)

        graph.add((column_uri, RDF.type, ddl.Column))
        graph.add((column_uri, ddl.hasName, Literal(str(column))))
        graph.add((table_uri, ddl.hasStructure, column_uri))

        if is_primary_key:
            graph.add((table_uri, ddl.primaryKey, column_uri))


def add_triples_for_foreign_keys(graph, foreign_keys):
    for from_table, from_column, to_table, to_column in foreign_keys:
        from_column_uri = URIRef(from_table + '/' + from_column)
        from_table_uri = URIRef(from_table)

        to_column_uri = URIRef(to_table + '/' + to_column)
        to_table_uri = URIRef(to_table)

        graph.add((from_table_uri, ddl.foreignKey, from_column_uri))
        graph.add((from_column_uri, ddl.references, to_column_uri))


add_triples_for_tables(data_graph, tables)
add_triples_for_columns(data_graph, tables)
add_triples_for_foreign_keys(data_graph, foreign_keys)

data_graph.serialize(destination="data_graph.ttl", format="turtle")
