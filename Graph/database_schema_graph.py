from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, FOAF, XSD, OWL
import sqlite3


# Could not figure out how to import from Applications folder, so I copied what I needed
conn = sqlite3.connect('./Databases/AdvancedDatabaseButBad.sqlite')

def run_query(query):
    response = conn.execute(query).fetchall()
    return response

md = Namespace("http://database-ontology.example/")

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

graph = Graph()

def add_triples_for_tables(graph, rows):
  unique_table_names = set([row[0] for row in rows])

  for table in unique_table_names:
    graph.add((URIRef(table), RDF.type, Literal("table")))


def add_triples_for_columns(graph, columns):
  for column in columns:
    (table, column, is_primary_key) = column
    graph.add((URIRef(table), md.column, URIRef(table+'/'+column)))
    if is_primary_key:
      graph.add((URIRef(table+'/'+column), RDF.type, URIRef("primary_key")))

def add_triples_for_foreign_keys(graph, foreign_keys):
  for from_table, from_column, to_table, to_column in foreign_keys:
    graph.add((URIRef(from_table+'/'+from_column), md.references, URIRef(to_table+'/'+to_column)))

add_triples_for_tables(graph, tables)
add_triples_for_columns(graph, tables)
add_triples_for_foreign_keys(graph, foreign_keys)


graph.serialize(destination="database3.ttl", format="turtle")