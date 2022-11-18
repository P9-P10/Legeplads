import json

from Graph.changes_parser import ChangesParser
from Structures.Column import Column
from Structures.DataStore import DataStore
from Structures.Schema import Schema
from Structures.Table import Table


class JsonChangesParser(ChangesParser):
    def __init__(self):
        super().__init__()

    def get_changes(self, old_structure: DataStore, new_structure: DataStore, changes: str) -> [(Schema, Schema)]:

        def find_element(database_structure, uri_to_find):
            for schema in database_structure.schemas:
                for table in schema.tables:
                    for column in table.columns:
                        if column.URI == uri_to_find:
                            return Schema(name=schema.name,
                                          tables=[Table(table.name, columns=[Column(column.name)])])

        output = []
        for change in json.loads(changes):
            if "MOVE" in change:
                change = change.replace("MOVE(", "")
                change = change.replace(")", "")
                old_uri, new_uri = change.split(",")
                old_uri = old_uri.strip()
                new_uri = new_uri.strip()
                old_element = find_element(old_structure, old_uri)
                new_element = find_element(new_structure, new_uri)
                if old_element and new_element:
                    old_new_tuple = (old_element,new_element)
                    output.append(old_new_tuple)
        return output
