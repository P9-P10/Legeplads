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
                
            next_element = query.peek()
            if next_element == "as":
                variable = query.next(2)
            else:
                variable = component
            output.append(self.split_prefix(variable))

            if self.is_keyword(next_element):
                return output
   
        return output

    def is_keyword(self, string: str) -> bool:
        return string.lower() in self.SQL_keywords

    @staticmethod
    def split_prefix(input_string: str):

        if '.' in input_string:
            split_string = input_string.split('.')
            return split_string[0], split_string[1]
        else:
            return '', input_string

    def get_table_alias(self, query: str):
        output = []
        query = Q(query)

        while query.index < query.max:
            current = query.current()
            if current.lower() in self.table_prefix:
                table = query.next()
                alias_position = query.peek()
                if alias_position.lower() not in self.SQL_keywords:
                    output.append((table, alias_position))
                else:
                    output.append((table, ""))
            if query.next() is None:
                break
        return output
