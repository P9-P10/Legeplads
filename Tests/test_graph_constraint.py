import pytest
from pyshacl import validate

from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD, OWL, SH

data_graph_prefixes = '''
    @prefix cs:   <http://www.cs-22-dt-9-03.org/concrete-structure-ontology#> .
    @prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
'''

constraints_graph_prefixes = '''
    @prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
    @prefix sh:   <http://www.w3.org/ns/shacl#> .
    @prefix cs:   <http://www.cs-22-dt-9-03.org/concrete-structure-ontology#> .
    @prefix cc:   <http://www.cs-22-dt-9-03.org/concrete-structure-constraints#> .
'''


def test_does_not_conform():
    c = Graph()
    d = Graph()

    data_string = data_graph_prefixes + '''
            <DB> a cs:Relational .
        '''

    constraints_string = constraints_graph_prefixes + '''
            cc:RelationalShape a sh:NodeShape ;
                sh:targetClass cs:Relational ;
                sh:property [ sh:path cs:hasA ; sh:minCount 1 ; sh:class cs:Table ; ] ;
                sh:property [ sh:path cs:name ; sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:string ; ] ; .
        '''

    d.parse(data=data_string, format="turtle")
    c.parse(data=constraints_string, format="turtle")

    r = validate(data_graph=d, shacl_graph=c,
                 abort_on_first=False, meta_shacl=False)

    conforms, results_graph, results_text = r

    assert conforms is False


def test_does_conform():
    c = Graph()
    d = Graph()

    data_string = data_graph_prefixes + '''
            <DB> a cs:Relational ;
                cs:hasA <T> ;
                cs:name "DB" .

            <T> a cs:Table .
        '''

    constraints_string = constraints_graph_prefixes + '''
            cc:RelationalShape a sh:NodeShape ;
                sh:targetClass cs:Relational ;
                sh:property [ sh:path cs:hasA ; sh:minCount 1 ; sh:class cs:Table ; ] ;
                sh:property [ sh:path cs:name ; sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:string ; ] ; .
        '''

    d.parse(data=data_string, format="turtle")
    c.parse(data=constraints_string, format="turtle")

    r = validate(data_graph=d, shacl_graph=c,
                 abort_on_first=False, meta_shacl=False)

    conforms, results_graph, results_text = r

    assert conforms is True
