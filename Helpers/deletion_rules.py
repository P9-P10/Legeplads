class DeletionRule():
    def __init__(self, set_to_null=False, should_not_change=False, set_to_empty_string=False,
                 set_to_custom=(False, "")):
        self.set_to_custom = set_to_custom
        self.set_to_null = set_to_null
        self.should_not_change = should_not_change
        self.set_to_empty = set_to_empty_string
        if sum([set_to_null, should_not_change, set_to_empty_string,
                set_to_custom[0] or set_to_custom[1] != ""]) > 1:
            raise Exception("Argument error: Please specify at most one argument.")

    def deletion_query(self, table_name, variable, where_clause):
        # TODO: Implement case where variables have been moved to different tables.
        if self.should_not_change:
            raise NotImplemented
        if self.set_to_custom[0]:
            return "UPDATE {} SET {}='{}' WHERE {}".format(table_name, variable, self.set_to_custom[1], where_clause)
        if self.set_to_null:
            return "UPDATE {} SET {}=null WHERE {}".format(table_name, variable, where_clause)
        if self.set_to_empty:
            return "UPDATE {} SET {}='' WHERE {}".format(table_name, variable, where_clause)
