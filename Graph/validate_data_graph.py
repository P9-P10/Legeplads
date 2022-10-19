from pyshacl import validate
from database_schema_graph import graph_to_triples
from rdflib import Graph, Namespace

data_graph = Graph()
shapes_graph = Graph()

data_graph.parse("./data_graph.ttl")
shapes_graph.parse("./Graph/datastore-description-language.ttl")

r = validate(ont_graph=shapes_graph, data_graph=data_graph, shacl_graph=shapes_graph, abort_on_first=False)

conforms, results_graph, results_text = r

print(results_text)


ddl = Namespace("http://www.cs-22-dt-9-03.org/datastore-description-language#")
organisation = "www.test-organisation.org/"

org = Namespace(organisation)


print(graph_to_triples(shapes_graph))
