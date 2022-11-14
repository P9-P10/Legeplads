from Structures.DatabaseStructure import DatabaseStructure


class ChangesParser:
    def __init__(self, changes: str):
        self.changes = changes

    def get_changes(self,database_structure:DatabaseStructure):
        raise NotImplemented
