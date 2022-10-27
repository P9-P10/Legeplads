class Column:
    def __init__(self, name, alias=None):
        self.alias = alias
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Column):
            if str(other) == str(self):
                return True
        return False

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.name)

    def add_alias(self, alias):
        self.alias = alias

    def get_alias(self):
        return self.alias
