class Change:
    def __init__(self, old, new, should_replace_table=False):
        self.should_replace_table = should_replace_table
        self.old = old
        self.new = new

    def get_old_table(self):
        return self.old[0]

    def get_new_table(self):
        return self.new[0]

    def get_old_column(self):
        return self.old[1]

    def get_new_column(self):
        return self.new[1]