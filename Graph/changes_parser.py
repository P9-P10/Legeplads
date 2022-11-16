from Structures.DatabaseStructure import DatabaseStructure


class ChangesParser:
    def __init__(self, changes: str):
        self.changes = changes

    def get_changes(self, old_structure: DatabaseStructure, new_structure: DatabaseStructure):
        raise NotImplemented
