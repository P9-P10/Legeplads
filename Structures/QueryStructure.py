from Structures.Structure import Structure
from Structures.Table import Table
from Structures.Column import Column

class QueryStructure(Structure):
    def __init__(self, tables: list[Table], columns: list[Column]):
        self.tables = tables
        self.columns = columns

    
    def copy(self):
        pass