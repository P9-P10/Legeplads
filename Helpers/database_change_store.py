from Helpers.Change import TableChange


class DatabaseChangeStore:
    def __init__(self):
        self.changes = []

    def add_new_change(self, change: TableChange):
        self.changes.append(change)

    def get_changes(self):
        return self.changes
