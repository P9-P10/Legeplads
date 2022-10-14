import pytest
from pyshacl import validate
from rdflib import Graph

data_graph_prefixes = "@prefix ddl: <http://www.cs-22-dt-9-03.org/datastore-description-language#> ."


@pytest.fixture(scope="module")
def shapes_graph():
    return Graph().parse("./Graph/datastore-description-language.ttl")


def test_ontology_unknown_conforms(shapes_graph):
    data_graph = Graph()

    data_string = data_graph_prefixes + '''
        <DB> a ddl:Database ;
            ddl:hasStructure <T> .
        
        <T> a 1 .
    '''

    data_graph.parse(data=data_string, format="turtle")

    r = validate(data_graph=data_graph, shacl_graph=shapes_graph, abort_on_first=False)

    conforms, results_graph, results_text = r

    assert conforms is True


def test_ontology_known_conforms_not(shapes_graph):
    data_graph = Graph()

    data_string = data_graph_prefixes + '''
        <DB> a ddl:Database ;
            ddl:hasStructure <T> .

        <T> a 1 .
    '''

    data_graph.parse(data=data_string, format="turtle")

    r = validate(ont_graph=shapes_graph, data_graph=data_graph, shacl_graph=shapes_graph, abort_on_first=False)

    conforms, results_graph, results_text = r

    assert conforms is False
