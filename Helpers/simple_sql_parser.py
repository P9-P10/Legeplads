import re


class SqlParser:
    def __init__(self):
        self.keywords = ["join", "into", "from"]
        self.query_types = ["SELECT","DELETE","UPDATE"]

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

    def get_query_type(self,query):
        query_without_spaces = query.split(" ")
        if query_without_spaces[0] in self.query_types:
            return query_without_spaces[0].upper()