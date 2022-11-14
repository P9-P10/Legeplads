
class AddTable:
    def __init__(self, table_name: str):
        self.table_name = table_name

class RemoveTable:
    def __init__(self, table_name: str):
        self.table_name = table_name

class MoveColumn:
    def __init__(self, column_name: str, src_table_name: str, dst_table_name: str):
        self.column_name = column_name
        self.src_table_name = src_table_name
        self.dst_table_name = dst_table_name

class ReplaceTable:
    def __init__(self, old_table_name: str, new_table_name: str):
        self.old_table_name = old_table_name
        self.new_table_name = new_table_name
        
class RemoveColumn:
    pass

class AddColumn:
    pass

