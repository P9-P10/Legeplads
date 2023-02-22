from Graph.changes_parser import ChangesParser
from Structures.DataStore import DataStore
from Structures.Schema import Schema


class ChangesGraphParser(ChangesParser):
    def __init__(self):
        super().__init__()

    def get_changes(self, old_structure: DataStore, new_structure: DataStore, changes: str) -> [(Schema, Schema)]:
        


        return None, None
