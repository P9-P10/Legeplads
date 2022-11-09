class EqualityConstraint:
    def __init__(self, left_table, left_column, right_table, right_column):
        self.left_table = left_table
        self.left_column = left_column
        self.right_table = right_table
        self.right_column = right_column

    def __eq__(self, other):
        return self.left_table == other.left_table \
               and self.left_column == other.left_column \
               and self.right_table == other.right_table \
               and self.right_column == other.right_column
