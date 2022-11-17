from rdflib import Graph

from Graph.graph_parser import GraphParser
from Structures.Column import Column
from Structures.DataStore import DataStore
from Structures.Schema import Schema
from Structures.Table import Table


class TurtleParser(GraphParser):
    class TurtleRepresentation:
        def __init__(self):
            self.hasName = None
            self.hasStore = None
            self.hasStructure = []
            self.primaryKey = None
            self.type = None
            self.columnOptions = None
            self.isNotNull = False

    def __init__(self, database_contents: str, changes_as_string: str = ""):
        super().__init__(database_contents, changes_as_string)

    def get_structure(self) -> [DataStore]:
        return self.turtle_parser()

    def turtle_parser(self) -> [Schema]:

        graph = Graph()
        parsed = graph.parse(data=self.input_string)

        turtle_map = self.turtle_map_from_parsed_ttl(parsed)

        return self.turtle_map_to_database_structures(turtle_map)

    def turtle_map_from_parsed_ttl(self, parsed):
        turtle_map = {}

        def clean_subject(current_subject):
            subject_elements = current_subject.split("/")
            return subject_elements[len(subject_elements) - 1]

        def prefix_remover(current_input):
            if "#" in current_input:
                return current_input.split("#")[1]
            else:
                return current_input

        def update_turtle_rep():
            if predicate == "hasStructure":
                turtle_rep.hasStructure.append(clean_subject(str(parsed_object)))
            elif predicate == "hasStore":
                setattr(turtle_rep, predicate, clean_subject(str(parsed_object)))

            else:
                setattr(turtle_rep, predicate, str(parsed_object))

        for subject, predicate, parsed_object in parsed:
            predicate = prefix_remover(predicate)
            parsed_object = prefix_remover(parsed_object)
            subject = clean_subject(subject)
            if subject in turtle_map:
                turtle_rep = turtle_map[subject]
                update_turtle_rep()

            else:
                turtle_rep = self.TurtleRepresentation()
                update_turtle_rep()
                turtle_map.update({subject: turtle_rep})

        return turtle_map

    def turtle_map_to_database_structures(self, turtle_map) -> [DataStore]:
        output = []
        for key, value in turtle_map.items():
            if not value.hasStore:
                output.append(DataStore(self.get_schemas(turtle_map, value),name=value.hasName))

        return output

    def get_schemas(self, turtle_map, data_store):
        output = []
        for schema_uri in data_store.hasStructure:
            schema = turtle_map[schema_uri]
            schema_name = schema.hasName
            output.append(Schema(self.get_tables(turtle_map,schema), name=schema_name))
        return output

    def get_tables(self, turtle_map:dict, schema):
        output = []
        for table_uri in schema.hasStructure:
            current_table = turtle_map[table_uri]
            columns = self.get_columns(turtle_map, current_table)
            table = Table(current_table.hasName, columns, uri=table_uri)
            output.append(table)
        return output

    def get_columns(self, turtle_map, current_structure):
        output = []
        for column_uri in current_structure.hasStructure:
            column_representation = turtle_map[column_uri]
            column = Column(column_representation.hasName, uri=column_uri)
            output.append(column)
        return output
