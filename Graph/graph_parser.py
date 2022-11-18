from Structures.DataStore import DataStore


class GraphParser:
    def __init__(self):
        self.graph = None

    def get_structure(self,string_to_parse:str) -> [DataStore]:
        raise NotImplemented
