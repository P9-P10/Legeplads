from os.path import exists

from Graph.graph_reader import GraphReader
from rdflib import Graph

from Structures.Column import Column
from Structures.DatabaseStructure import DatabaseStructure
from Structures.Table import Table


class TurtleFileReader(GraphReader):
    class TurtleRepresentation:
        def __init__(self):
            self.hasName = None
            self.hasStore = None
            self.hasStructure = []
            self.primaryKey = None
            self.type = None
            self.columnOptions = None
            self.isNotNull = False

    def __init__(self, database_contents, changes=None):
        super().__init__(database_contents, changes)

    def get_changes(self):
        pass

    def get_structure(self) -> [DatabaseStructure]:
        return self.turtle_parser()

    def turtle_parser(self) -> [DatabaseStructure]:

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

    def turtle_map_to_database_structures(self, turtle_map) -> [DatabaseStructure]:
        output = []
        for key, value in turtle_map.items():
            i = 0
            for structure in value.hasStructure:
                structure_representation = turtle_map[structure]
                if structure_representation.type == "Schema":
                    database_name = turtle_map[structure_representation.hasStore].hasName
                    tables = self.get_tables(turtle_map, structure_representation)
                    output.append(DatabaseStructure(tables, database_name))

        return output

    def get_tables(self, turtle_map, structure_representation):
        output = []
        for structure in structure_representation.hasStructure:
            current_structure = turtle_map[structure]
            columns = self.get_columns(turtle_map, current_structure)
            table = Table(current_structure.hasName, columns)
            output.append(table)
        return output

    def get_columns(self, turtle_map, current_structure):
        output = []
        for structure in current_structure.hasStructure:
            representation = turtle_map[structure]
            column = Column(representation.hasName)
            output.append(column)
        return output
