from pyshacl import validate
from rdflib import Graph

data_graph = Graph()
shapes_graph = Graph()

data_graph.parse("./Graph/data_graph.ttl")
shapes_graph.parse("./Graph/datastore-description-language.ttl")

r = validate(ont_graph=shapes_graph, data_graph=data_graph, shacl_graph=shapes_graph, abort_on_first=False)

conforms, results_graph, results_text = r

print(results_text)
