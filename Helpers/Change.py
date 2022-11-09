class Change:
    def __init__(self, old, new, constraint=None):
        self.old = old
        self.new = new
        self.constraint = constraint

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
