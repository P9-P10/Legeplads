from Graph.changes_parser import ChangesParser
from Graph.graph_parser import GraphParser
from Graph.operations_maker import OperationsMaker
from Graph.versionmanager import VersionManager
from Structures.Changes import MoveColumn
from Structures.Column import Column
from Structures.DataStore import DataStore
from Structures.Schema import Schema
from Structures.Table import Table


class Moc_GraphParser(GraphParser):
    def __init__(self):
        super().__init__()

    def get_structure(self, string_to_parse: str) -> [DataStore]:
        return string_to_parse


class Moc_Changes_parser(ChangesParser):
    def __init__(self):
        super().__init__()

    def get_changes(self, old_structure: Schema, new_structure: Schema, changes: str):
        return changes


def create_version_manager(old_schema, new_schema):
    gp = Moc_GraphParser()
    cp = Moc_Changes_parser()

    old_ds = DataStore([old_schema], name="Name")
    new_ds = DataStore([new_schema], name="Name")
    old_tuple = (1, old_ds, "Id")
    new_tuple = (2, new_ds, "Id")
    parsed_change = [(old_schema, new_schema)]
    changes_tuple = (1, parsed_change, "Id")
    return VersionManager(gp, cp, [old_tuple, new_tuple], [changes_tuple])


def test_get_operation_for_version():
    old_schema = Schema([Table("TableName", [Column("TestName", uri="1")])], name="SchemaName")
    new_schema = Schema([Table("NewName", [Column("TestName", uri="2")])], name="SchemaName")
    vm = create_version_manager(old_schema, new_schema)

    operation_maker = OperationsMaker(vm)
    result = operation_maker.get_operations_for_version(version=1, database_name="Id")
    assert result == [MoveColumn("TestName", "TableName", "NewName")]
