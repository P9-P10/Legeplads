import pytest
from pyshacl import validate
from rdflib import Graph


@pytest.fixture(scope="module")
def shapes_graph() -> Graph:
    return Graph().parse("./Graph/datastore-description-language.ttl")

def test_sqlite_to_graph():
    pass


def make_data_graph(data_string: str) -> Graph:
    data_graph_prefixes = "@prefix ddl: <http://www.cs-22-dt-9-03.org/datastore-description-language#> ."

    string_with_prefixes = data_graph_prefixes + data_string
    return Graph().parse(data=string_with_prefixes, format="turtle")


def test_subclass_of_named_entity_with_name_conforms(shapes_graph):
    data_graph = make_data_graph('''
        <T> a ddl:NamedEntity ; ddl:hasName "T" .
    ''')

    r = validate(ont_graph=shapes_graph, data_graph=data_graph, shacl_graph=shapes_graph, abort_on_first=False)

    conforms, results_graph, results_text = r

    assert conforms is True


def test_subclass_of_named_entity_without_name_conforms_not(shapes_graph):
    data_graph = make_data_graph('''
        <T> a ddl:NamedEntity .
    ''')

    r = validate(ont_graph=shapes_graph, data_graph=data_graph, shacl_graph=shapes_graph, abort_on_first=False)

    conforms, results_graph, results_text = r

    assert conforms is False


def test_subclass_of_datastore_with_structure_conforms(shapes_graph):
    data_graph = make_data_graph('''
        <T> a ddl:Datastore ; ddl:hasStructure <C> ; ddl:hasName "T".
        
        <C> a ddl:Column ; ddl:hasName "C" .
    ''')

    r = validate(ont_graph=shapes_graph, data_graph=data_graph, shacl_graph=shapes_graph, abort_on_first=False)

    conforms, results_graph, results_text = r

    assert conforms is True


def test_subclass_of_datastore_without_structure_conforms_not(shapes_graph):
    data_graph = make_data_graph('''
            <T> a ddl:Datastore ; ddl:hasName "T".

            <C> a ddl:Column ; ddl:hasName "C" .
        ''')

    r = validate(ont_graph=shapes_graph, data_graph=data_graph, shacl_graph=shapes_graph, abort_on_first=False)

    conforms, results_graph, results_text = r

    assert conforms is False


def test_ontology_unknown_conforms(shapes_graph):
    data_graph = make_data_graph('''
        <DB> a ddl:Database ;
            ddl:hasStructure <T> .
        
        <T> a 1 .
    ''')

    r = validate(data_graph=data_graph, shacl_graph=shapes_graph, abort_on_first=False)

    conforms, results_graph, results_text = r

    assert conforms is True


def test_ontology_known_conforms_not(shapes_graph):
    data_graph = make_data_graph('''
        <DB> a ddl:Database ;
            ddl:hasStructure <T> .

        <T> a 1 .
    ''')

    r = validate(ont_graph=shapes_graph, data_graph=data_graph, shacl_graph=shapes_graph, abort_on_first=False)

    conforms, results_graph, results_text = r

    assert conforms is False
