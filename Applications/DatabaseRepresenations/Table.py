from Applications.DatabaseRepresenations.Column import Column

class Table:
    def __init__(self, name, columns=None):
        if columns is None:
            columns = []
        self.name = name
        self.columns = columns

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Table):
            if str(other) == str(self):
                if set(self.columns) == set(other.columns):
                    return True
        return False

    def __repr__(self):
        return str(self)

    def has_column(self, column: Column):
        return column in self.columns
