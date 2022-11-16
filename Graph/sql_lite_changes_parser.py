import json

from Graph.changes_parser import ChangesParser
from Structures.Column import Column
from Structures.DataStore import DataStore
from Structures.Schema import Schema
from Structures.Table import Table


class JsonChangesParser(ChangesParser):
    def __init__(self, changes: str):
        changes = json.loads(changes)
        super().__init__(changes)

    def get_changes(self, old_structure: DataStore, new_structure: DataStore) -> [(Schema, Schema)]:

        def find_element(database_structure, uri_to_find):
            for schema in database_structure.schemas:
                if schema.URI == uri_to_find:
                    return Schema(schema.name)
                else:
                    for table in schema.tables:
                        if table.URI == uri_to_find:
                            return Schema(name=schema.name, tables=[Table(table.name)])
                        else:
                            for column in table.columns:
                                if column.URI == uri_to_find:
                                    return Schema(name=schema.name,
                                                  tables=[Table(table.name, columns=[Column(column.name)])])

        output = []
        for change in self.changes:
            if "MOVE" in change:
                change = change.replace("MOVE(", " ")
                change = change.replace(")", " ")
                old_uri, new_uri = change.split(",")
                print(old_uri + new_uri)
                old_new_tuple = (
                    find_element(old_structure, int(old_uri)),
                    find_element(new_structure, int(new_uri)))
                output.append(old_new_tuple)
        return output
