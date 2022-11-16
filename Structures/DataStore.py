from Structures.Schema import Schema


class DataStore:
    def __init__(self, schemas: [Schema] = None, name=""):
        if schemas is None:
            schemas = []
        self.schemas: [Schema] = schemas
        self.name = name
