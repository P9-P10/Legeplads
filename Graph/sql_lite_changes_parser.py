import json

from Graph.changes_parser import ChangesParser
from Structures.Column import Column
from Structures.DatabaseStructure import DatabaseStructure
from Structures.Table import Table


class JsonChangesParser(ChangesParser):
    def __init__(self, changes: str):
        changes = json.loads(changes)
        super().__init__(changes)

    def get_changes(self, old_structure: DatabaseStructure, new_structure: DatabaseStructure) -> [(Table, Table)]:
        def find_column_in_database(database_structure, uri_to_find):
            for table_name, columns in database_structure.column_dict.items():
                for column in columns:
                    if column.URI == uri_to_find:
                        return Table(table_name, [Column(column.name)])

        output = []
        for change in self.changes:
            if "MOVE" in change:
                change = change.replace("MOVE(", " ")
                change = change.replace(")", " ")
                old_URI, new_URI = change.split(",")
                print(old_URI + new_URI)
                old_new_tuple = (
                    find_column_in_database(old_structure, int(old_URI)),
                    find_column_in_database(new_structure, int(new_URI)))
                output.append(old_new_tuple)
        return output
