import re


class Query:
    def __init__(self, input_query):
        self.query_as_string = input_query
        self.components = self.split_query_components()
        self.query_types = ["select", "delete", "update"]
        self.index = 0
        self.first = True
        self.max = len(self.components)

    def __iter__(self):
        return self

    def __next__(self):
        if self.first:
            self.first = False
            return self.current()

        res = self.next()
        if res is None:
            raise StopIteration
        else:
            return res

    def get_where_clause(self):
        return re.split(r"where", self.query_as_string, 1, flags=re.IGNORECASE)[1]

    def split_query_components(self):
        return re.split(r'[ ,\n\r]+', self.query_as_string)

    def get_query_type(self):
        if self.is_query_type(self.component_at(0)):
            return self.component_at(0).upper()

    def next(self, n=1):
        if self.within_size(n):
            self.index += n
            return self.current()
        else:
            return None

    def peek(self, n=1):
        if self.within_size(n):
            return self.component_at(self.index + n)
        else:
            return None

    def within_size(self, n):
        return self.index + n < self.max

    def current(self):
        return self.components[self.index]

    def is_query_type(self, string: str) -> bool:
        return string.lower() in self.query_types

    def component_at(self, index: int) -> str:
        return self.components[index]
