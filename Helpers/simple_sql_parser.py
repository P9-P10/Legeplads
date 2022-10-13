import re


class SqlParser:
    def __init__(self):
        self.keywords = ["join", "into", "from"]
        self.end_of_table_list_keywords = ["where", "join","from"]
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

    def get_variables_without_table_prefixes(self, query):
        output = []
        query_without_spaces = query.split(" ")
        in_variable_section = False
        for index, item in enumerate(query_without_spaces):
            if item.lower() in self.query_types or in_variable_section:
                in_variable_section = True
                index += 1
                current_variable = query_without_spaces[index]
                cleaned_current_var = self.remove_seperator(self.split_prefix(current_variable)[1])
                if query_without_spaces[index + 1].lower() in self.end_of_table_list_keywords:
                    output.append(cleaned_current_var)
                    index += 1
                    break
                elif query_without_spaces[index + 1].lower() == "as":
                    element_after_as = query_without_spaces[index+2]
                    output.append(self.remove_seperator(self.split_prefix(element_after_as)[1]))
                    index += 2
                else:
                    output.append(cleaned_current_var)
                    index += 1
            if index + 1 >= len(query_without_spaces):
                break
        return output

    @staticmethod
    def remove_seperator(input_string: str):
        if ',' in input_string:
            return input_string.replace(',', '')
        else:
            return input_string

    @staticmethod
    def split_prefix(input_string: str):
        if '.' in input_string:
            return input_string.split('.')
        else:
            return ['', input_string]

    def get_table_alias(self, query):
        output = []
        query_without_spaces = query.split(" ")
        for index, item in enumerate(query_without_spaces):
            if item.lower() in self.keywords_before_tables:
                index += 1
                current_table_name = query_without_spaces[index]
                if query_without_spaces[index + 1].lower() in self.end_of_table_list_keywords:
                    output.append((current_table_name, ""))
                    index += 1
                elif query_without_spaces[index + 1].lower() == "as":
                    output.append((current_table_name, query_without_spaces[index + 2]))
                    index += 2
                else:
                    output.append((current_table_name, query_without_spaces[index + 1]))
                    index += 1
        return output

    def get_query_type(self, query):
        query_without_spaces = query.split(" ")
        if query_without_spaces[0].lower() in self.query_types:
            return query_without_spaces[0].upper()
