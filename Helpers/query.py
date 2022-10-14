import re


class Query:
    def __init__(self, input_query):
        self.query_as_string = input_query
        self.query = self.split_query_components()
        self.query_types = ["select", "delete", "update"]
        self.index = 0
        self.max = len(self.query)

    def get_where_clause(self):
        return re.split(r"where", self.query_as_string, 1, flags=re.IGNORECASE)[1]

    def split_query_components(self):
        return re.split(r'[ ,\n\r]+', self.query_as_string)

    def get_query_type(self):
        if self.query[0].lower() in self.query_types:
            return self.query[0].upper()

    def next(self, n=1):
        if self.index + n < self.max:
            self.index += n
            return self.query[self.index]
        else:
            return None

    def peek(self, n=1):
        if self.index + n < self.max:
            return self.query[self.index + n]
        else:
            return None

    def current(self):
        return self.query[self.index]
