from Structures.Schema import Schema


class ChangesParser:
    def __init__(self, changes: str):
        self.changes = changes

    def get_changes(self, old_structure: Schema, new_structure: Schema):
        raise NotImplemented
