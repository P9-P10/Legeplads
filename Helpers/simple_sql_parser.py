from Helpers.query import Query as Q


class SqlParser:
    def __init__(self):
        self.table_prefix = ["join", "into", "from"]
        self.SQL_keywords = ["where", "join", "from", "select", "on", "="]

    def get_table_names(self, query: str):
        output = []
        query = Q(query)
        for i in range(len(query.query)):
            if query.query[i].lower() in self.table_prefix:
                output.append(query.query[i + 1])
        return output

    def get_variables_with_prefix(self, query: str):
        output = []
        query = Q(query)
        in_variable_section = False
        while query.index < query.max:
            if query.current().lower() in query.query_types:
                in_variable_section = True
                query.next()
                continue
            elif in_variable_section:
                cleaned_current_var = self.split_prefix(query.current())
                next_element = query.peek(1)
                if next_element.lower() in self.SQL_keywords:
                    output.append(cleaned_current_var)
                    return output
                elif next_element == "as":
                    element_after_as = query.peek(2)
                    output.append(self.split_prefix(element_after_as))
                    query.next(3)
                else:
                    output.append(cleaned_current_var)
                    query.next()
            else:
                if query.next() is None:
                    break
        return output

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
