from Applications.DatabaseRepresenations.Column import Column


class Table:
    def __init__(self, name, columns=None):
        if columns is None:
            columns = []
        self.name = name
        self.columns = columns
        self.alias = None

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

    def has_column_with_alias(self,column:Column,alias):
        for current_column in self.columns:
            if current_column == column and current_column.alias == alias:
                return True
    def set_alias(self, alias):
        self.alias = alias

    def get_alias(self):
        return self.alias

    def get_column(self,column_name):
        for column in self.columns:
            if column.name == column_name:
                return column
