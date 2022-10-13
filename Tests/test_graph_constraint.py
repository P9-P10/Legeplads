import pytest
from pyshacl import validate

from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD, OWL, SH


# cs = Namespace("http://www.cs-22-dt-9-03.org/concrete-structure-ontology#")
# e = Namespace("https://www.example.org/")


def test_does_not_conform():
    constraints = Graph()
    data = Graph()

    constraints.parse("./Graph/concrete-structure-constraints.ttl")
    data.parse("./Tests/constraints-test-not-conformed.ttl")

    r = validate(data_graph=data, shacl_graph=constraints,
                 abort_on_first=False, meta_shacl=False)

    conforms, results_graph, results_text = r

    assert conforms is False


def test_does_conform():
    constraints = Graph()
    data = Graph()

    constraints.parse("./Graph/concrete-structure-constraints.ttl")
    data.parse("./Tests/constraints-test-conformed.ttl")

    r = validate(data_graph=data, shacl_graph=constraints,
                 abort_on_first=False, meta_shacl=False)

    conforms, results_graph, results_text = r

    assert conforms is True
