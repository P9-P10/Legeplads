from Structures.Table import Table
from Structures.Relation import Relation

class Change:
    def __init__(self, old, new, constraint=None):
        self.old = old
        self.new = new
        self.constraint = constraint

    def __repr__(self):
        return f'Old: ({self.old[0].name}, {self.old[1].name}) New: ({self.new[0].name}, {self.new[1].name})'

    def get_constraint(self):
        return self.constraint

    def get_old_table(self):
        return self.old[0]

    def get_new_table(self):
        return self.new[0]

    def get_old_column(self):
        return self.old[1]

    def get_new_column(self):
        return self.new[1]

    def table_changed(self):
        return not self.get_old_table() == self.get_new_table()

    def column_changed(self):
        return not self.get_old_column() == self.get_new_column()
