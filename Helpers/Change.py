from Applications.DatabaseRepresenations.Table import Table


class ColumnChange:
    def __init__(self, old_name:str, new_name:str, new_table:Table):
        super().__init__()
        self.old_name = old_name
        self.new_name = new_name
        self.new_table = new_table


class TableChange:
    def __init__(self, old_name, column_changes: [ColumnChange]):
        super().__init__()
        self.old_name = old_name
        self.column_changes = column_changes
        self.should_be_deleted = False

    def get_column_changes(self) -> [ColumnChange]:
        return self.column_changes
