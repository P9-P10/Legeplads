from Applications.DatabaseRepresenations.Table import Table
from Applications.DatabaseRepresenations.Column import Column

class Change:
    def __init__(self, old, new):
        self.old = old
        self.new = new

class ColumnChange:
    def __init__(self, old_name:str, new_name:str, new_table:Table):
        super().__init__()
        self.old_name = old_name
        self.new_name = new_name
        self.new_table = new_table


class TableChange:
    def __init__(self, old_name, column_changes: list[ColumnChange]):
        super().__init__()
        self.old_name = old_name
        self.column_changes = column_changes
        self.should_be_deleted = False

    def get_column_changes(self) -> list[ColumnChange]:
        return self.column_changes
