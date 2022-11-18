import json

from Graph.changes_parser import ChangesParser
from Graph.graph_parser import GraphParser
from Graph.version_manager import version_manager
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

    old_ds = DataStore([old_schema])
    new_ds = DataStore([new_schema])
    old_tuple = (12123123, old_ds, "Id")
    new_tuple = (13131313, new_ds, "Id")
    parsed_change = [(old_schema, new_schema)]
    changes_tuple = (12123123, parsed_change, "Id")
    return version_manager(gp, cp, [old_tuple, new_tuple], [changes_tuple])


def test_version_manager_init():
    old_schema = Schema([Table("TableName", [Column("TestName", uri="1")])], name="SchemaName")
    new_schema = Schema([Table("TableName", [Column("NewColumnName", uri="2")])], name="SchemaName")
    vm = create_version_manager(old_schema, new_schema)
    assert version_manager.Change(12123123, old_schema, new_schema, "Id") in vm.changes


def test_version_manager_get_changes_for_column():
    old_schema = Schema([Table("TableName", [Column("TestName", uri="1")])], name="SchemaName")
    new_schema = Schema([Table("TableName", [Column("NewColumnName", uri="2")])], name="SchemaName")
    vm = create_version_manager(old_schema, new_schema)

    assert vm.get_change_for_column("SchemaName", "TableName", "TestName") == new_schema


def test_version_manager_get_changes_for_column_wrong_value_returns_none():
    old_schema = Schema([Table("TableName", [Column("TestName", uri="1")])], name="SchemaName")
    new_schema = Schema([Table("TableName", [Column("NewColumnName", uri="2")])], name="SchemaName")
    vm = create_version_manager(old_schema, new_schema)

    assert vm.get_change_for_column("Non Existing", "Non Existing", "Non Existing") == None
