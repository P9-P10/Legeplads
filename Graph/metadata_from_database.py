from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, FOAF, XSD, OWL
import sqlite3 as sq

# TODO: Check if the resulting graph (metadata.ttl) uses the
#  Data Privacy Vocabulary (dpv) correctly (Maybe using shapes?)

dbo = Namespace("http://dbpedia.org/ontology/")
dbp = Namespace("http://dbpedia.org/property/")
dbpedia = Namespace("http://dbpedia.org/resource/")
dpv = Namespace("https://w3id.org/dpv#")
dpvo = Namespace("https://w3id.org/dpv/dpv-owl#")

# Custom metadata ontology. Find specification in metadata_ontology.owl. Modify using Protege
md = Namespace("http://metadata-ontology.org/")

g = Graph()

# For the top of the turtle file, all the prefixes
g.bind('rdf', RDF)
g.bind('rdfs', RDFS)
g.bind('foaf', FOAF)
g.bind('owl', OWL)
g.bind('dbo', dbo)
g.bind('dbp', dbp)
g.bind('dbpedia', dbpedia)
g.bind('dpv', dpv)
g.bind('dpvo', dpvo)
g.bind('md', md)

path = '../Databases/'
dbs = ['SimpleDatabase', 'AdvancedDatabase', 'AdvancedDatabaseButBad']
extension = '.sqlite'

conn = sq.connect(path + dbs[0] + extension)

cursor = conn.execute('''
    SELECT id, email FROM Users;
''')

for row in cursor:
    user = URIRef(str(row[0]))
    mail = URIRef(str(row[1]))

    g.add((
        user, RDF.type, dpv.NaturalPerson
    ))
    g.add((
        mail, RDF.type, dpv.Entity
    ))
    g.add((
        user, dpv.hasEntity, mail
    ))
    g.add((
        mail, dpv.hasPurpose, dpv.Marketing
    ))

cursor = conn.execute('''
    SELECT id, address, phone, birthday FROM UserData;
''')

for row in cursor:
    user = URIRef(str(row[0]))

    g.add((
        user, dpv.hasAddress, Literal(row[1], datatype=XSD.string)
    ))
    g.add((
        user, dpv.hasContact, Literal(row[2], datatype=XSD.integer)
    ))
    # TODO: Birthday

# Print all triples (subject, object, predicate) in the graph
for s, p, o in g:
    print(s, p, o)

g.serialize(destination="metadata.ttl", format="turtle")

conn.close()
