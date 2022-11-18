from Structures.Schema import Schema


class DataStore:
    def __init__(self, schemas: [Schema] = None, name=""):
        if schemas is None:
            schemas = []
        self.schemas: [Schema] = schemas
        self.name = name

    def __eq__(self, other):
        return self.schemas == other.schemas and self.name == other.name

    def __repr__(self):
        return "Name: " + self.name + "Schemas: " + str(self.schemas)
