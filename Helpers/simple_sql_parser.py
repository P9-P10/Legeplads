import re


class SqlParser:
    def __init__(self):
        self.keywords = ["join", "into", "from"]

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
