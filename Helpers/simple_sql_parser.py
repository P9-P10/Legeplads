import re


class SqlParser:
    def __init__(self):
        self.keywords = ["join", "into", "from"]
        self.end_of_table_list_keywords = ["where", "join", "from", "select"]
        self.keywords_before_tables = ["join", "from"]
        self.query_types = ["select", "delete", "update"]

    def get_table_names(self, query: str):
        output = []
        query_without_spaces = query.split(" ")
        for i in range(len(query_without_spaces)):
            if query_without_spaces[i].lower() in self.keywords:
                output.append(query_without_spaces[i + 1])
        return output

    @staticmethod
    def get_where_clause(query):
        return re.split(r"where", query, 1, flags=re.IGNORECASE)[1]

    def get_variables_with_prefix(self, query):
        output = []
        query_without_spaces = self.split_query_components(query)
        in_variable_section = False
        index = 0
        while index < len(query_without_spaces):
            if query_without_spaces[index].lower() in self.query_types:
                in_variable_section = True
                index += 1
                continue
            current_variable = query_without_spaces[index]
            cleaned_current_var = self.split_prefix(current_variable)
            next_element = self.get_n_element(query_without_spaces, 1, index)
            if next_element.lower() in self.end_of_table_list_keywords:
                output.append(cleaned_current_var)
                index += 1
                break
            elif next_element == "as":
                element_after_as = self.get_n_element(query_without_spaces, 2, index)
                output.append(self.split_prefix(element_after_as))
                index += 3
            else:
                output.append(cleaned_current_var)
                index += 1
            if index + 1 >= len(query_without_spaces):
                break
        return output

    @staticmethod
    def get_n_element(list, n, index):
        return list[index + n]

    @staticmethod
    def split_prefix(input_string: str):

        if '.' in input_string:
            split_string = input_string.split('.')
            return split_string[0], split_string[1]
        else:
            return '', input_string

    def get_table_alias(self, query):
        output = []
        query_without_spaces = self.split_query_components(query)
        for index, item in enumerate(query_without_spaces):
            if item.lower() in self.keywords_before_tables:
                index += 1
                current_table_name = query_without_spaces[index]
                next_element = query_without_spaces[index + 1]
                if next_element.lower() in self.end_of_table_list_keywords:
                    output.append((current_table_name, ""))
                    index += 1
                elif next_element == "as":
                    alias = query_without_spaces[index + 2]
                    output.append((current_table_name, alias))
                    index += 2
                else:
                    output.append((current_table_name, next_element))
                    index += 1
        return output

    def get_query_type(self, query):
        query_without_spaces = query.split(" ")
        if query_without_spaces[0].lower() in self.query_types:
            return query_without_spaces[0].upper()

    @staticmethod
    def split_query_components(query):
        return re.split(r', | |,', query)
