class Change:
    def __init__(self, old, new, should_replace_table=False):
        self.should_replace_table = should_replace_table
        self.old = old
        self.new = new
