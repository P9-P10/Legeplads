import re


class SqlParser:
    def __init__(self):
        self.keywords = ["join", "into", "from"]
        self.end_of_table_list_keywords = ["where", "join"]
        self.keywords_before_tables = ["join", "from"]
        self.query_types = ["SELECT", "DELETE", "UPDATE"]

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

    def get_variables(self, query):
        return

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
        if query_without_spaces[0] in self.query_types:
            return query_without_spaces[0].upper()
