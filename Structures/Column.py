class Column:
    def __init__(self, name, alias=None, uri: str = None):
        self.alias = alias
        self.name = name
        self.URI = uri

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Column):
            if str(other) == str(self):
                if self.alias and other.alias:
                    return self.alias == other.alias
                else:
                    return True
        return False

    def __repr__(self):
        return f'Column(name: {self.name}, alias: {self.alias})'

    def __hash__(self):
        return hash((self.name, self.alias))

    def add_alias(self, alias):
        self.alias = alias

    def get_alias(self):
        return self.alias
        
