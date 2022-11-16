from Structures.DataStore import DataStore


class GraphParser:
    def __init__(self, database_contents: str, changes: str):
        self.input_string = database_contents
        self.changes = changes
        self.graph = None

    def get_structure(self) -> [DataStore]:
        raise NotImplemented
