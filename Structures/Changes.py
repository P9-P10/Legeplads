
class AddTable:
    pass

class RemoveTable:
    def __init__(self, table_name: str):
        self.table_name = table_name

class MoveColumn:
    def __init__(self, column_name: str, src_table_name: str, dst_table_name: str):
        self.column_name = column_name
        self.src_table_name = src_table_name
        self.dst_table_name = dst_table_name