class Table:
    def __init__(self, name, columns=None):
        if columns is None:
            columns = []
        self.name = name
        self.columns = columns

    def __str__(self):
        return self.name
