from Helpers.query import Query as Q


class SqlParser:
    def __init__(self):
        self.table_prefix = ["join", "into", "from"]
        self.SQL_keywords = ["where", "join", "from", "select", "on", "=", "inner", "left", "right", "full"]

    def get_table_names(self, string: str):
        output = []
        query = Q(string)
        for component in query:
            if self.is_prefix(component):
                output.append(query.next())
        return output

    def is_prefix(self, string: str) -> bool:
        return string.lower() in self.table_prefix

    def get_variables_with_prefix(self, query: str):
        output = []
        query = Q(query)

        for component in query:
            # Skip keyword specifying the query type
            if query.is_query_type(component):
                continue
                
            prefix_and_variable = self.get_next_variable_and_prefix(query, component)
            output.append(self.split_prefix_and_variable(prefix_and_variable))

            if self.is_keyword(query.peek()):
                return output
   
        return output

    def get_next_variable_and_prefix(self, query, component):
        if query.peek() == "as":
            prefix_and_variable = query.next(2)
        else:
            prefix_and_variable = component
        return prefix_and_variable

    def is_keyword(self, string: str) -> bool:
        return string.lower() in self.SQL_keywords

    @staticmethod
    def split_prefix_and_variable(input_string: str):
        if '.' in input_string:
            return tuple(input_string.split('.'))
        else:
            return ('', input_string)

    def get_table_alias(self, query: str):
        output = []
        query = Q(query)

        for component in query:
            if self.is_prefix(component):
                output.append(self.get_table_and_alias(query))

        return output

    def get_table_and_alias(self, query):
        table = self.get_table(query)
        value = self.get_alias(query)
        return table, value

    def get_table(self, query):
        return query.next()

    def get_alias(self, query):
        next_value = query.peek()
        return "" if self.is_keyword(next_value) else next_value
  

