import re

class QueryTransformation():
    def __init__(self):
        pass
    
    def apply(self, query: str) -> str:
        pass

class RemoveTable(QueryTransformation):
    def __init__(self, table):
        super().__init__()
        self.table = table

    def apply(self, query: str) -> str:
        if self.table not in query:
            return query
        
        query = self.remove_alias(query)
        query = self.remove_table(query)

        return query

    def remove_alias(self, query):
        query_without_whitespace = query.split(' ')
        alias_position = query_without_whitespace.index(self.table) + 1
        if len(query_without_whitespace) > alias_position and query_without_whitespace[alias_position].lower() != "on":
            alias = query_without_whitespace[alias_position]
            return query.replace(alias + ".", "")
        return query

    def remove_table(self, query):
        query_list_without_removed_table = [x for x in re.split(r"join", query, flags=re.IGNORECASE) if
                                            self.table not in x]
        for i, item in enumerate(query_list_without_removed_table):
            if not i == 0:
                query_list_without_removed_table[i] = "JOIN" + item
        return ''.join(query_list_without_removed_table).rstrip()

class ChangeTable(QueryTransformation):
    def __init__(self, old_table, new_table):
        super().__init__()
        self.old_table = old_table
        self.new_table = new_table

    def apply(self, query: str) -> str:
        return re.sub(r'%s(\W|;|$)' % self.old_table, self.new_table + " ", query).rstrip()
